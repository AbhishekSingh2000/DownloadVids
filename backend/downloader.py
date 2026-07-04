"""Downloader engine - fetches metadata + downloads MP4/MP3 for each platform.

Strategy per platform (POC-validated):
- Instagram  -> fastdl.app (Playwright)
- TikTok     -> tikwm.com JSON API
- YouTube    -> pytubefix for metadata + best-effort stream download
- Facebook   -> snapsave.app (Playwright)
"""
import os
import re
import time
import json
import subprocess
import tempfile
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import requests
from playwright.async_api import async_playwright

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/pw-browsers")

CHROMIUM_PATH = "/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# ---------- Utilities ----------

def format_duration(sec: Optional[float]) -> str:
    if sec is None:
        return "[0:00:00]"
    try:
        sec = int(round(float(sec)))
    except Exception:
        return "[0:00:00]"
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"[{h}:{m:02d}:{s:02d}]"


def safe_filename_part(name: Optional[str]) -> str:
    if not name:
        return "unknown"
    # Keep alnum, dot, underscore, dash; replace others with underscore
    cleaned = "".join(c if c.isalnum() or c in "._-" else "_" for c in name).strip("_")
    return cleaned or "unknown"


def detect_platform(url: str) -> str:
    u = url.lower()
    if "tiktok.com" in u:
        return "tiktok"
    if "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    if "facebook.com" in u or "fb.watch" in u:
        return "facebook"
    if "instagram.com" in u:
        return "instagram"
    if "linkedin.com" in u:
        return "linkedin"
    return "unknown"


# ---------- Playwright singleton ----------

class BrowserPool:
    def __init__(self):
        self._pw = None
        self._browser = None
        self._lock = asyncio.Lock()

    async def get(self):
        async with self._lock:
            if self._browser is None or not self._browser.is_connected():
                self._pw = await async_playwright().start()
                self._browser = await self._pw.chromium.launch(
                    executable_path=CHROMIUM_PATH,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
            return self._browser

    async def close(self):
        if self._browser:
            try: await self._browser.close()
            except Exception: pass
        if self._pw:
            try: await self._pw.stop()
            except Exception: pass
        self._browser = None
        self._pw = None


browser_pool = BrowserPool()


async def new_page():
    b = await browser_pool.get()
    ctx = await b.new_context(user_agent=UA)
    page = await ctx.new_page()
    return page, ctx


# ---------- Metadata Extractors ----------

def _extract_ig_shortcode(url: str) -> Optional[str]:
    m = re.search(r'/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)', url)
    return m.group(1) if m else None


def _ig_creator_from_embed(url: str) -> Optional[str]:
    """Fetch instagram.com/p/{code}/embed/ and extract UsernameText."""
    try:
        base = url.rstrip("/") + "/"
        r = requests.get(base + "embed/", headers={"User-Agent": "facebookexternalhit/1.1"}, timeout=15, allow_redirects=True)
        if r.status_code != 200: return None
        m = re.search(r'class="UsernameText"[^>]*>([^<]+)', r.text)
        if m: return m.group(1).strip()
        # fallback: title
        m = re.search(r'<title>[^<]*?@([A-Za-z0-9._]{2,30})', r.text)
        if m: return m.group(1)
    except Exception:
        pass
    return None


async def meta_instagram(url: str) -> Dict[str, Any]:
    page, ctx = await new_page()
    try:
        await page.goto("https://fastdl.app/en", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_selector("input#search-form-input", timeout=15000)
        await page.fill("input#search-form-input", url)
        await page.click("button#searchFormButton")
        # Wait specifically for the download anchor
        await page.wait_for_selector("a.button__download[href*='fastdl.app/get']", timeout=60000)
        await page.wait_for_timeout(1200)
        # Extract MP4 URL from the actual download anchor (only source of video URL)
        dl_anchor = await page.query_selector("a.button__download[href*='fastdl.app/get']")
        mp4_url = None
        if dl_anchor:
            href = await dl_anchor.get_attribute("href")
            if href:
                # Skip if it's an image download (uri contains .jpg and NOT .mp4)
                if "%2Fo1%2Fv%2F" in href or "video" in href.lower() or ".mp4" in href:
                    mp4_url = href.replace("&amp;", "&")
        # Thumbnail from media-content__image
        thumb = None
        thumb_el = await page.query_selector(".media-content__image")
        if thumb_el:
            thumb = await thumb_el.get_attribute("src")
            if thumb: thumb = thumb.replace("&amp;", "&")

        # Duration ? not in fastdl - will probe file later
    finally:
        await ctx.close()

    # Creator from IG embed (fallback approach)
    creator = await asyncio.to_thread(_ig_creator_from_embed, url)
    if not creator:
        # last-resort fallback: use shortcode as identifier
        code = _extract_ig_shortcode(url) or "instagram"
        creator = f"instagram_{code}"[:30]

    return {
        "creator": creator,
        "duration": None,
        "thumbnail": thumb,
        "mp4_url": mp4_url,
    }


def meta_tiktok(url: str) -> Dict[str, Any]:
    r = requests.get(
        "https://www.tikwm.com/api/",
        params={"url": url, "hd": 1},
        headers={"User-Agent": UA, "Referer": "https://www.tikwm.com/"},
        timeout=30,
    )
    j = r.json()
    if j.get("code") != 0:
        raise RuntimeError(j.get("msg") or "tikwm error")
    d = j.get("data") or {}
    author = d.get("author") or {}
    play = d.get("hdplay") or d.get("play") or d.get("wmplay")
    if play and not play.startswith("http"):
        play = "https://www.tikwm.com" + play
    music = d.get("music")
    if music and not music.startswith("http"):
        music = "https://www.tikwm.com" + music
    return {
        "creator": author.get("unique_id") or author.get("nickname"),
        "duration": d.get("duration"),
        "thumbnail": d.get("cover") or d.get("origin_cover"),
        "mp4_url": play,
        "mp3_url": music,
    }


def meta_youtube(url: str) -> Dict[str, Any]:
    from pytubefix import YouTube
    yt = YouTube(url)
    # try to get a progressive mp4 stream url
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    audio = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    return {
        "creator": yt.author or yt.channel_id,
        "duration": yt.length,
        "thumbnail": yt.thumbnail_url,
        "title": yt.title,
        "mp4_url": stream.url if stream else None,
        "mp3_url": audio.url if audio else None,
        "channel_url": yt.channel_url,
    }


def _fb_creator_fallback(url: str) -> Optional[str]:
    """Best-effort FB creator extraction. Falls back to numeric owner id."""
    try:
        # Follow redirects to get final URL - share/v/xyz -> story.php?story_fbid=...&id=OWNER_ID
        r = requests.get(url, headers={"User-Agent": "facebookexternalhit/1.1"}, timeout=15, allow_redirects=True)
        final_url = r.url
        # Look for owner id in redirect URL
        m = re.search(r'[?&]id=(\d{6,})', final_url)
        if m: return m.group(1)
        # Look in HTML for owner/page id / actor name
        if r.status_code == 200:
            # Try actor name in JSON
            for pat in [
                r'"owning_profile":\s*\{[^}]*"name":\s*"([^"]{2,60})"',
                r'"owningProfile":\s*\{[^}]*"name":\s*"([^"]{2,60})"',
                r'"actor":\s*\{[^}]*"name":\s*"([^"]{2,60})"',
                r'"page":\s*\{[^}]*"name":\s*"([^"]{2,60})"',
            ]:
                m = re.search(pat, r.text)
                if m: return m.group(1)
    except Exception:
        pass
    return None


async def meta_facebook(url: str) -> Dict[str, Any]:
    page, ctx = await new_page()
    try:
        await page.goto("https://snapsave.app/", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_selector("input#url", timeout=15000)
        await page.fill("input#url", url)
        await page.click("button#send")
        try:
            await page.wait_for_function(
                "() => { const el = document.getElementById('download-section'); return el && el.innerHTML && (el.innerHTML.includes('rapidcdn') || el.innerHTML.includes('fbcdn') || el.innerHTML.includes('.mp4')); }",
                timeout=30000,
            )
        except Exception:
            pass
        await page.wait_for_timeout(1500)
        html = await page.content()
        # rapidcdn v2 = mp4 stream
        vids = re.findall(r'https?://d\.rapidcdn\.app/v2\?[^"\'<>\s]+', html)
        if not vids:
            vids = re.findall(r'https?://[^"\'<>\s]+fbcdn[^"\'<>\s]+\.mp4[^"\'<>\s]*', html)
        vids = [v.replace("&amp;", "&") for v in vids]

        # thumbnail via rapidcdn/thumb
        thumb = None
        tm = re.search(r'https?://d\.rapidcdn\.app/thumb\?[^"\'<>\s]+', html)
        if tm: thumb = tm.group(0).replace("&amp;", "&")
        if not thumb:
            tm = re.search(r'<img[^>]+src="(https?://[^"]+)"', html)
            if tm: thumb = tm.group(1)

    finally:
        await ctx.close()

    # Try to get real creator via FB page fetch (best-effort)
    creator = await asyncio.to_thread(_fb_creator_fallback, url)
    if not creator:
        m = re.search(r'/reel/(\d+)', url) or re.search(r'/share/[rv]/(\w+)', url)
        creator = f"facebook_{m.group(1)[:8]}" if m else "facebook"

    return {
        "creator": creator,
        "duration": None,
        "thumbnail": thumb,
        "mp4_url": vids[0] if vids else None,
    }


async def fetch_metadata(url: str) -> Dict[str, Any]:
    platform = detect_platform(url)
    if platform == "instagram":
        m = await meta_instagram(url)
    elif platform == "tiktok":
        m = await asyncio.to_thread(meta_tiktok, url)
    elif platform == "youtube":
        m = await asyncio.to_thread(meta_youtube, url)
    elif platform == "facebook":
        m = await meta_facebook(url)
    elif platform == "linkedin":
        m = await asyncio.to_thread(meta_linkedin, url)
    else:
        raise ValueError(f"Unsupported platform for {url}")

    m["platform"] = platform
    m["source_url"] = url
    m["duration_str"] = format_duration(m.get("duration"))
    return m


def meta_linkedin(url: str) -> Dict[str, Any]:
    """Scrape LinkedIn post HTML directly - embeds progressive MP4 URL."""
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120", "Accept-Language": "en-US"}, timeout=25)
    if r.status_code != 200:
        raise RuntimeError(f"linkedin http {r.status_code}")
    html = r.text

    # Extract MP4 URL (highest quality) - look for dms.licdn.com playlist URLs
    mp4_urls = re.findall(r'https://dms\.licdn\.com/playlist/vid/[^"\'<>\s&]+(?:&(?:amp;)?[^"\'<>\s&]+)*', html)
    # Clean HTML entities
    cleaned = []
    for u in mp4_urls:
        u = u.replace("&amp;", "&").replace("&quot;", "").replace("\\u0026", "&")
        # Trim after any obvious break chars
        u = re.split(r'[\"\'<>\s]', u)[0]
        cleaned.append(u)
    # Pick highest resolution (look for e.g. -720p or -1080p)
    def qkey(u):
        m = re.search(r'-(\d{3,4})p', u)
        return int(m.group(1)) if m else 0
    cleaned.sort(key=qkey, reverse=True)
    mp4_url = cleaned[0] if cleaned else None

    # Creator - from og:title (e.g. "hashtags | Charlie Sebastian Arellano")
    creator = None
    og_title = re.search(r'<meta[^>]+og:title[^>]+content="([^"]+)"', html)
    if og_title:
        title = og_title.group(1)
        # Format usually "<caption> | <Author Name>" or just "<Author>"
        parts = [p.strip() for p in title.split("|") if p.strip()]
        if parts:
            # Author is last segment (after final "|")
            creator = parts[-1]
    # Also try author meta
    if not creator:
        am = re.search(r'"authorName":\s*"([^"]+)"', html)
        if am: creator = am.group(1)

    # Thumbnail
    thumb = None
    og_img = re.search(r'<meta[^>]+og:image[^>]+content="([^"]+)"', html)
    if og_img: thumb = og_img.group(1)

    return {
        "creator": creator or "linkedin",
        "duration": None,  # will probe from downloaded mp4
        "thumbnail": thumb,
        "mp4_url": mp4_url,
    }


# ---------- Downloader ----------

def _download_direct(url: str, out_path: Path, referer: str = "", timeout: int = 180) -> Tuple[bool, str]:
    try:
        headers = {"User-Agent": UA}
        if referer: headers["Referer"] = referer
        with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
            if r.status_code != 200:
                return False, f"http {r.status_code}"
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(1024 * 128):
                    if chunk: f.write(chunk)
        return True, ""
    except Exception as e:
        return False, str(e)[:300]


def _ffmpeg_extract_mp3(mp4: Path, mp3: Path) -> bool:
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp4), "-vn", "-acodec", "libmp3lame", "-b:a", "192k", str(mp3)],
        capture_output=True,
    )
    return r.returncode == 0 and mp3.exists()


def _ffprobe_duration(path: Path) -> Optional[int]:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return int(float(r.stdout.strip()))
    except Exception:
        pass
    return None


def _referer_for(platform: str) -> str:
    return {
        "instagram": "https://fastdl.app/",
        "tiktok": "https://www.tikwm.com/",
        "facebook": "https://snapsave.app/",
        "youtube": "https://www.youtube.com/",
        "linkedin": "https://www.linkedin.com/",
    }.get(platform, "")


async def prepare_downloads(url: str, tmp_dir: Path) -> Dict[str, Any]:
    """Fetch metadata + download both MP4 and MP3 into tmp_dir.
    Returns dict with paths (or None on failure) + error message."""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    meta = await fetch_metadata(url)
    platform = meta["platform"]

    mp4_path = tmp_dir / "video.mp4"
    mp3_path = tmp_dir / "audio.mp3"
    errors = {}

    # Download MP4
    mp4_url = meta.get("mp4_url")
    if mp4_url:
        ok, err = await asyncio.to_thread(_download_direct, mp4_url, mp4_path, _referer_for(platform))
        if not ok:
            errors["mp4"] = err
            mp4_path = None
    else:
        errors["mp4"] = "no mp4 url"
        mp4_path = None

    # Download MP3 - if platform provides a music_url (TikTok), use it directly; else extract from mp4
    audio_source_url = meta.get("mp3_url") if platform in ("tiktok", "youtube") else None
    if audio_source_url:
        # For YouTube, mp3_url points to an audio stream (usually webm/m4a) - we need to convert
        tmp_audio = tmp_dir / "audio.raw"
        ok, err = await asyncio.to_thread(_download_direct, audio_source_url, tmp_audio, _referer_for(platform))
        if ok:
            # Convert to mp3
            ok2 = await asyncio.to_thread(_ffmpeg_extract_mp3, tmp_audio, mp3_path)
            if not ok2:
                errors["mp3"] = "ffmpeg conversion failed"
                mp3_path = None
            try: tmp_audio.unlink()
            except: pass
        else:
            # Fallback to extracting from mp4
            audio_source_url = None
            errors_from_audio = err

    if not audio_source_url and mp4_path:
        ok2 = await asyncio.to_thread(_ffmpeg_extract_mp3, mp4_path, mp3_path)
        if not ok2:
            errors["mp3"] = "ffmpeg extraction failed"
            mp3_path = None
    elif not mp4_path and not audio_source_url:
        errors["mp3"] = "no source"
        mp3_path = None

    # If duration was unknown from metadata, probe file
    if not meta.get("duration") and mp4_path and mp4_path.exists():
        d = _ffprobe_duration(mp4_path)
        if d:
            meta["duration"] = d
            meta["duration_str"] = format_duration(d)

    return {
        "meta": meta,
        "mp4_path": str(mp4_path) if mp4_path and Path(mp4_path).exists() else None,
        "mp3_path": str(mp3_path) if mp3_path and Path(mp3_path).exists() else None,
        "errors": errors,
    }


def build_filename(creator: Optional[str], inf_id: str, duration_sec: Optional[int], ext: str) -> str:
    dur = format_duration(duration_sec)
    return f"{safe_filename_part(creator)}_{inf_id}_{dur}.{ext}"
