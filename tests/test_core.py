"""
POC: Test that yt-dlp can:
1. Fetch metadata (creator, duration, thumbnail) 
2. Download MP4
3. Extract MP3
For all 4 platforms: Instagram, TikTok, YouTube Shorts, Facebook Reels
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

OUT = Path("/tmp/poc_downloads")
OUT.mkdir(exist_ok=True)

TESTS = [
    ("IG",      "INF50",  "https://www.instagram.com/p/DZKu-UCMHTj/"),
    ("TikTok",  "INF171", "https://www.tiktok.com/@tukangoding/video/7652761143097707797"),
    ("YouTube", "INF174", "https://youtube.com/shorts/91gSgp1cmPM"),
    ("Facebook","INF175", "https://www.facebook.com/reel/1741171496878060"),
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fmt_duration(sec):
    if sec is None:
        return "[0:00:00]"
    sec = int(sec)
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"[{h}:{m:02d}:{s:02d}]"


def safe_name(name):
    if not name:
        return "unknown"
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name).strip("_") or "unknown"


def fetch_metadata(url):
    """Get metadata via yt-dlp --dump-json"""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-warnings",
        "--no-playlist",
        "--user-agent", UA,
        "--socket-timeout", "30",
        "--retries", "3",
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        return None, r.stderr.strip()[-500:]
    try:
        data = json.loads(r.stdout.strip().split("\n")[0])
    except Exception as e:
        return None, f"json parse: {e}"
    return data, None


def download_mp4(url, outfile):
    cmd = [
        "yt-dlp",
        "-f", "bv*+ba/b",
        "--merge-output-format", "mp4",
        "--user-agent", UA,
        "--socket-timeout", "60",
        "--retries", "3",
        "-o", str(outfile),
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return r.returncode == 0, r.stderr.strip()[-500:]


def download_mp3(url, outfile):
    """Download audio-only and convert to mp3"""
    tmp_template = str(outfile).replace(".mp3", ".%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", "ba/b",
        "-x", "--audio-format", "mp3", "--audio-quality", "0",
        "--user-agent", UA,
        "--socket-timeout", "60",
        "--retries", "3",
        "-o", tmp_template,
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return r.returncode == 0 and outfile.exists(), r.stderr.strip()[-500:]


def run_test(label, inf_id, url):
    print(f"\n=== {label} | {inf_id} | {url} ===")
    meta, err = fetch_metadata(url)
    if not meta:
        print(f"  [METADATA FAIL] {err}")
        return {"platform": label, "inf": inf_id, "ok": False, "step": "metadata", "err": err}

    creator = meta.get("uploader_id") or meta.get("uploader") or meta.get("channel") or "unknown"
    duration = meta.get("duration")
    thumb = meta.get("thumbnail")
    dur_str = fmt_duration(duration)
    print(f"  creator={creator!r} duration={duration}s ({dur_str}) thumb={'yes' if thumb else 'no'}")

    base = f"{safe_name(creator)}_{inf_id}_{dur_str}"
    mp4_path = OUT / f"{base}.mp4"
    mp3_path = OUT / f"{base}.mp3"

    ok_mp4, err_mp4 = download_mp4(url, mp4_path)
    print(f"  MP4: {'OK' if ok_mp4 else 'FAIL'} -> {mp4_path.name} ({mp4_path.stat().st_size if mp4_path.exists() else 0} bytes)")
    if not ok_mp4:
        print(f"    err: {err_mp4}")

    ok_mp3, err_mp3 = download_mp3(url, mp3_path)
    print(f"  MP3: {'OK' if ok_mp3 else 'FAIL'} -> {mp3_path.name} ({mp3_path.stat().st_size if mp3_path.exists() else 0} bytes)")
    if not ok_mp3:
        print(f"    err: {err_mp3}")

    return {
        "platform": label, "inf": inf_id, "creator": creator,
        "duration": duration, "mp4": ok_mp4, "mp3": ok_mp3,
        "err_mp4": err_mp4 if not ok_mp4 else None,
        "err_mp3": err_mp3 if not ok_mp3 else None,
    }


if __name__ == "__main__":
    results = []
    for label, inf, url in TESTS:
        try:
            results.append(run_test(label, inf, url))
        except Exception as e:
            results.append({"platform": label, "inf": inf, "ok": False, "err": str(e)})

    print("\n\n===== SUMMARY =====")
    for r in results:
        status = "OK" if r.get("mp4") and r.get("mp3") else "FAIL"
        print(f"  {r['platform']:10s} {r['inf']:6s} MP4={r.get('mp4')} MP3={r.get('mp3')}")
    print(f"\nFiles in {OUT}:")
    for f in sorted(OUT.iterdir()):
        print(f"  {f.name} ({f.stat().st_size} bytes)")
