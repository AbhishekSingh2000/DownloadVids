"""POC v2: Use Playwright to interact with third-party downloader sites like a human."""
import os, sys, time, re, json, subprocess
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/pw-browsers")
from playwright.sync_api import sync_playwright

CHROMIUM = "/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell"

TESTS = [
    ("IG",      "INF50",  "https://www.instagram.com/p/DZKu-UCMHTj/",       "fastdl"),
    ("TikTok",  "INF171", "https://www.tiktok.com/@tukangoding/video/7652761143097707797", "indown"),
    ("YouTube", "INF174", "https://youtube.com/shorts/91gSgp1cmPM",         "yt"),
    ("Facebook","INF175", "https://www.facebook.com/reel/1741171496878060", "snapsave"),
]


def get_via_fastdl(page, url):
    """Instagram via fastdl.app"""
    page.goto("https://fastdl.app/en", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_selector("input#s_input", timeout=15000)
    page.fill("input#s_input", url)
    page.click("button.search-form__button, button#send")
    # Wait for result list
    page.wait_for_selector(".output-list, .search-result, .download-item, a.button--filled[href*='.mp4'], a[download]", timeout=60000)
    time.sleep(2)
    html = page.content()
    # Look for video URLs
    m = re.findall(r'href="(https?://[^"]+\.mp4[^"]*)"', html)
    thumb = None
    tm = re.search(r'src="(https?://[^"]+\.jpg[^"]*)"', html)
    if tm: thumb = tm.group(1)
    # try to find creator + duration
    creator = None
    return {"mp4_url": m[0] if m else None, "thumb": thumb, "creator": creator}


def get_via_indown(page, url):
    """TikTok via indown.io"""
    page.goto("https://indown.io/tiktok-downloader", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_selector("input[name='link']", timeout=15000)
    page.fill("input[name='link']", url)
    page.click("button[type='submit'], input[type='submit']")
    page.wait_for_selector("a[href*='.mp4'], video source, a.download", timeout=60000)
    time.sleep(2)
    html = page.content()
    urls = re.findall(r'href="(https?://[^"]+\.mp4[^"]*)"', html)
    if not urls:
        urls = re.findall(r'src="(https?://[^"]+\.mp4[^"]*)"', html)
    return {"mp4_url": urls[0] if urls else None}


def get_via_snapsave(page, url):
    """Facebook via snapsave.app"""
    page.goto("https://snapsave.app/", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_selector("input#url", timeout=15000)
    page.fill("input#url", url)
    page.click("button.btn-red, button[type='submit']")
    page.wait_for_selector("a[href*='.mp4'], a.abutton, a[download]", timeout=60000)
    time.sleep(2)
    html = page.content()
    urls = re.findall(r'href="(https?://[^"]+)"[^>]*(?:download|Download|HD|SD)', html)
    if not urls:
        urls = re.findall(r'href="(https?://[^"]+\.mp4[^"]*)"', html)
    if not urls:
        # snapsave uses fbcdn urls
        urls = re.findall(r'href="(https?://[^"]*fbcdn[^"]+)"', html)
    return {"mp4_url": urls[0] if urls else None, "html_snippet": html[:2000]}


def get_via_yt(page, url):
    """YouTube via ssyoutube.com / y2mate or similar"""
    for site, sel_input, sel_submit in [
        ("https://www.y2mate.com/en", "input#txt-url", "button#btn-submit"),
        ("https://ssyoutube.com/en19bg/youtube-video-downloader", "input#url", "button#send"),
    ]:
        try:
            page.goto(site, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector(sel_input, timeout=10000)
            page.fill(sel_input, url)
            page.click(sel_submit)
            page.wait_for_selector("a[href*='.mp4'], a[download], .download-items", timeout=45000)
            time.sleep(3)
            html = page.content()
            urls = re.findall(r'href="(https?://[^"]+\.mp4[^"]*)"', html)
            if urls:
                return {"mp4_url": urls[0], "via": site}
        except Exception as e:
            print(f"    {site} failed: {e}")
            continue
    return {"mp4_url": None}


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        for label, inf, url, method in TESTS:
            print(f"\n=== {label} | {inf} | {url} (via {method}) ===")
            page = ctx.new_page()
            try:
                if method == "fastdl":  res = get_via_fastdl(page, url)
                elif method == "indown": res = get_via_indown(page, url)
                elif method == "snapsave": res = get_via_snapsave(page, url)
                elif method == "yt":     res = get_via_yt(page, url)
                print("  result:", {k: (v[:120] if isinstance(v,str) else v) for k,v in res.items()})
            except Exception as e:
                print(f"  EXCEPTION: {e}")
            finally:
                page.close()
        b.close()


if __name__ == "__main__":
    main()
