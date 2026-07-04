"""FastAPI backend for the multi-platform video downloader utility."""
import os
import logging
import uuid
import shutil
import tempfile
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ConfigDict

from seed_data import LINKS
from downloader import (
    detect_platform,
    fetch_metadata,
    prepare_downloads,
    format_duration,
    build_filename,
    browser_pool,
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Content Link Downloader")
api_router = APIRouter(prefix="/api")

logger = logging.getLogger("downloader")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# In-memory cache of prepared files (idx -> {mp4: path, mp3: path, meta: {...}})
# Also mirrored to Mongo for persistence across restarts (metadata only; files are re-fetched on demand).
CACHE_DIR = Path(tempfile.gettempdir()) / "content_dl_cache"
CACHE_DIR.mkdir(exist_ok=True)

# =========== Models ===========

class VideoRow(BaseModel):
    model_config = ConfigDict(extra="ignore")
    idx: int
    inf_id: str
    url: str
    platform: str
    creator: Optional[str] = None
    duration: Optional[int] = None  # seconds
    duration_str: Optional[str] = None
    thumbnail: Optional[str] = None
    status: str = "pending"  # pending | preparing | ready | error
    last_error: Optional[str] = None
    mp4_ready: bool = False
    mp3_ready: bool = False
    updated_at: Optional[str] = None

# =========== State helpers ===========

_rows_cache: Dict[int, VideoRow] = {}
_prepare_locks: Dict[int, asyncio.Lock] = {}


def _row_lock(idx: int) -> asyncio.Lock:
    if idx not in _prepare_locks:
        _prepare_locks[idx] = asyncio.Lock()
    return _prepare_locks[idx]


def _init_rows() -> None:
    for i, (inf_id, url) in enumerate(LINKS):
        platform = detect_platform(url)
        _rows_cache[i] = VideoRow(
            idx=i, inf_id=inf_id, url=url, platform=platform,
            status="pending", duration_str="[0:00:00]",
        )

_init_rows()


async def _load_from_db() -> None:
    """Restore cached metadata from Mongo on startup."""
    try:
        async for doc in db["videos"].find({}):
            idx = int(doc.get("idx", -1))
            if idx in _rows_cache:
                r = _rows_cache[idx]
                for k in ["creator", "duration", "duration_str", "thumbnail", "status", "last_error", "updated_at"]:
                    if k in doc and doc[k] is not None:
                        setattr(r, k, doc[k])
                # Only mark files ready if they still exist on disk
                cache_sub = CACHE_DIR / f"row_{idx}"
                r.mp4_ready = (cache_sub / "video.mp4").exists()
                r.mp3_ready = (cache_sub / "audio.mp3").exists()
                # If DB says ready but files gone, revert to pending? We keep metadata visible but require re-prepare for downloads.
                if r.status == "ready" and not (r.mp4_ready and r.mp3_ready):
                    # keep as ready-with-metadata; UI can still see creator/duration; user re-hits Prepare if they want fresh files
                    pass
    except Exception as e:
        logger.warning(f"failed to load from db: {e}")


async def _save_row(row: VideoRow) -> None:
    try:
        d = row.model_dump()
        await db["videos"].update_one({"idx": row.idx}, {"$set": d}, upsert=True)
    except Exception as e:
        logger.warning(f"save row {row.idx} err: {e}")


# =========== API ===========

@api_router.get("/")
async def root():
    return {"status": "ok", "total_links": len(LINKS)}


@api_router.get("/videos", response_model=List[VideoRow])
async def list_videos():
    # Return sorted by idx
    return [_rows_cache[i] for i in sorted(_rows_cache.keys())]


@api_router.post("/videos/{idx}/prepare", response_model=VideoRow)
async def prepare_video(idx: int):
    if idx not in _rows_cache:
        raise HTTPException(404, "row not found")
    row = _rows_cache[idx]

    async with _row_lock(idx):
        row.status = "preparing"
        row.last_error = None
        await _save_row(row)

        try:
            sub = CACHE_DIR / f"row_{idx}"
            if sub.exists():
                shutil.rmtree(sub, ignore_errors=True)
            result = await prepare_downloads(row.url, sub)
            meta = result["meta"]
            errs = result["errors"]

            row.creator = meta.get("creator") or row.creator
            row.duration = meta.get("duration")
            row.duration_str = meta.get("duration_str") or format_duration(row.duration)
            row.thumbnail = meta.get("thumbnail") or row.thumbnail
            row.mp4_ready = bool(result["mp4_path"])
            row.mp3_ready = bool(result["mp3_path"])
            row.updated_at = datetime.now(timezone.utc).isoformat()

            if row.mp4_ready or row.mp3_ready:
                row.status = "ready"
                if errs:
                    row.last_error = "; ".join(f"{k}: {v}" for k, v in errs.items())
            elif row.platform == "youtube" and (meta.get("creator") or meta.get("duration")):
                # YouTube special-case: metadata OK but server download 403'd (IP-blocked).
                # Mark as ready so user can trigger a direct redirect from their browser.
                row.status = "ready"
                row.mp4_ready = True
                row.mp3_ready = True
                row.last_error = (errs and "; ".join(f"{k}: {v}" for k, v in errs.items())) or None
            else:
                row.status = "error"
                row.last_error = "; ".join(f"{k}: {v}" for k, v in errs.items()) or "unable to prepare"
        except Exception as e:
            logger.exception(f"prepare row {idx} failed")
            row.status = "error"
            row.last_error = str(e)[:400]

        await _save_row(row)
        return row


@api_router.get("/videos/{idx}/download")
async def download_video(idx: int, fmt: str = "mp4"):
    if idx not in _rows_cache:
        raise HTTPException(404, "row not found")
    if fmt not in ("mp4", "mp3"):
        raise HTTPException(400, "fmt must be mp4 or mp3")
    row = _rows_cache[idx]
    sub = CACHE_DIR / f"row_{idx}"
    file_path = sub / ("video.mp4" if fmt == "mp4" else "audio.mp3")

    if not file_path.exists():
        # Try to prepare on demand
        await prepare_video(idx)
        if not file_path.exists():
            # YouTube fallback: fetch fresh direct stream URL and redirect the browser.
            # User's residential IP may succeed where our server IP was 403'd.
            if row.platform == "youtube":
                try:
                    from downloader import meta_youtube
                    meta = await asyncio.to_thread(meta_youtube, row.url)
                    target = meta.get("mp4_url") if fmt == "mp4" else meta.get("mp3_url")
                    if target:
                        from fastapi.responses import RedirectResponse
                        return RedirectResponse(url=target, status_code=307)
                except Exception as e:
                    logger.warning(f"youtube fallback failed idx={idx}: {e}")
            raise HTTPException(404, f"{fmt} not available: {row.last_error or 'download failed'}")

    fname = build_filename(row.creator, row.inf_id, row.duration, fmt)
    return FileResponse(str(file_path), media_type="video/mp4" if fmt == "mp4" else "audio/mpeg", filename=fname)


@api_router.post("/videos/reset")
async def reset_all():
    # Clear cache and reset in-memory state (keep URL/INF mapping)
    for i in list(_rows_cache.keys()):
        r = _rows_cache[i]
        r.status = "pending"; r.creator = None; r.duration = None; r.duration_str = "[0:00:00]"
        r.thumbnail = None; r.last_error = None; r.mp4_ready = False; r.mp3_ready = False; r.updated_at = None
        sub = CACHE_DIR / f"row_{i}"
        if sub.exists():
            shutil.rmtree(sub, ignore_errors=True)
    await db["videos"].delete_many({})
    return {"status": "reset", "total": len(_rows_cache)}


@api_router.get("/stats")
async def stats():
    counts = {"total": 0, "pending": 0, "preparing": 0, "ready": 0, "error": 0}
    for r in _rows_cache.values():
        counts["total"] += 1
        counts[r.status] = counts.get(r.status, 0) + 1
    return counts


# =========== App wiring ===========

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await _load_from_db()
    logger.info(f"seeded {len(_rows_cache)} rows")


@app.on_event("shutdown")
async def on_shutdown():
    await browser_pool.close()
    client.close()
