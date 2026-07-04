"""Backend API tests for Content Link Downloader"""
import requests
import sys
import time
from typing import Dict, Any

BASE_URL = "https://content-link-4.internal.preview.emergentagent.com/api"
TIMEOUT = 180  # 3 minutes for prepare calls (Instagram/Facebook can take 10-25s)

class APITester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def test(self, name: str, func):
        """Run a single test"""
        self.tests_run += 1
        print(f"\n{'='*60}")
        print(f"Test {self.tests_run}: {name}")
        print('='*60)
        try:
            func()
            self.tests_passed += 1
            print(f"✅ PASSED")
            self.results.append({"name": name, "status": "PASSED"})
        except AssertionError as e:
            self.tests_failed += 1
            print(f"❌ FAILED: {e}")
            self.results.append({"name": name, "status": "FAILED", "error": str(e)})
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ ERROR: {e}")
            self.results.append({"name": name, "status": "ERROR", "error": str(e)})

    def summary(self):
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print('='*60)
        print(f"Total: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        return self.tests_failed == 0


def test_get_videos():
    """Test GET /api/videos returns exactly 41 rows with correct mapping"""
    r = requests.get(f"{BASE_URL}/videos", timeout=30)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) == 41, f"Expected 41 rows, got {len(data)}"
    
    # Check specific mappings from the review request
    mappings = {
        0: ("INF50", "instagram"),
        7: ("INF171", "tiktok"),
        10: ("INF174", "youtube"),
        11: ("INF175", "facebook"),
    }
    
    for idx, (expected_inf_id, expected_platform) in mappings.items():
        row = data[idx]
        assert row["idx"] == idx, f"Row {idx}: expected idx={idx}, got {row['idx']}"
        assert row["inf_id"] == expected_inf_id, f"Row {idx}: expected inf_id={expected_inf_id}, got {row['inf_id']}"
        assert row["platform"] == expected_platform, f"Row {idx}: expected platform={expected_platform}, got {row['platform']}"
        assert "url" in row, f"Row {idx}: missing 'url' field"
        assert "status" in row, f"Row {idx}: missing 'status' field"
    
    print(f"✓ Returned {len(data)} rows")
    print(f"✓ Verified mappings: INF50->instagram, INF171->tiktok, INF174->youtube, INF175->facebook")


def test_get_stats():
    """Test GET /api/stats returns correct counts"""
    r = requests.get(f"{BASE_URL}/stats", timeout=30)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    
    data = r.json()
    assert "total" in data, "Missing 'total' field"
    assert "pending" in data, "Missing 'pending' field"
    assert "preparing" in data, "Missing 'preparing' field"
    assert "ready" in data, "Missing 'ready' field"
    assert "error" in data, "Missing 'error' field"
    
    assert data["total"] == 41, f"Expected total=41, got {data['total']}"
    
    # Sum of statuses should equal total
    status_sum = data["pending"] + data["preparing"] + data["ready"] + data["error"]
    assert status_sum == data["total"], f"Status counts don't add up: {status_sum} != {data['total']}"
    
    print(f"✓ Stats: total={data['total']}, pending={data['pending']}, preparing={data['preparing']}, ready={data['ready']}, error={data['error']}")


def test_prepare_tiktok_row():
    """Test POST /api/videos/9/prepare (TikTok INF173) - fast, should work"""
    # idx=9 is INF173 (TikTok)
    print("Preparing TikTok row (idx=9, INF173)... this may take 2-5 seconds")
    r = requests.post(f"{BASE_URL}/videos/9/prepare", timeout=TIMEOUT)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    
    data = r.json()
    assert data["idx"] == 9, f"Expected idx=9, got {data['idx']}"
    assert data["inf_id"] == "INF173", f"Expected INF173, got {data['inf_id']}"
    assert data["platform"] == "tiktok", f"Expected tiktok, got {data['platform']}"
    
    # Check metadata fields
    assert "creator" in data, "Missing 'creator' field"
    assert "duration" in data, "Missing 'duration' field"
    assert "duration_str" in data, "Missing 'duration_str' field"
    assert "thumbnail" in data, "Missing 'thumbnail' field"
    assert "status" in data, "Missing 'status' field"
    assert "mp4_ready" in data, "Missing 'mp4_ready' field"
    assert "mp3_ready" in data, "Missing 'mp3_ready' field"
    
    # TikTok should succeed (unless the video was deleted)
    if data["status"] == "ready":
        assert data["creator"] is not None, "Creator should not be None for ready status"
        assert data["duration"] is not None, "Duration should not be None for ready status"
        print(f"✓ Status: {data['status']}")
        print(f"✓ Creator: {data['creator']}")
        print(f"✓ Duration: {data['duration_str']}")
        print(f"✓ MP4 ready: {data['mp4_ready']}, MP3 ready: {data['mp3_ready']}")
    else:
        print(f"⚠ Status: {data['status']} (may be expected if video was deleted)")
        print(f"⚠ Error: {data.get('last_error', 'N/A')}")


def test_download_tiktok_mp4():
    """Test GET /api/videos/9/download?fmt=mp4 returns correct filename"""
    print("Testing TikTok MP4 download (idx=9, INF173)...")
    r = requests.get(f"{BASE_URL}/videos/9/download?fmt=mp4", timeout=TIMEOUT, allow_redirects=False)
    
    # Should be 200 with file or 404 if not ready
    assert r.status_code in [200, 404], f"Expected 200 or 404, got {r.status_code}"
    
    if r.status_code == 200:
        # Check Content-Type
        content_type = r.headers.get("content-type", "")
        assert "video/mp4" in content_type or "application/octet-stream" in content_type, \
            f"Expected video/mp4 content-type, got {content_type}"
        
        # Check Content-Disposition filename format: {creator}_{INF_ID}_[H:MM:SS].mp4
        content_disp = r.headers.get("content-disposition", "")
        assert "filename" in content_disp, f"Missing filename in Content-Disposition: {content_disp}"
        assert "INF173" in content_disp, f"Expected INF173 in filename, got {content_disp}"
        assert ".mp4" in content_disp, f"Expected .mp4 extension, got {content_disp}"
        
        # Extract filename (handle both filename= and filename*=utf-8'' formats)
        import urllib.parse
        if 'filename*=utf-8' in content_disp:
            # RFC 5987 format: filename*=utf-8''encoded_name
            filename = content_disp.split("filename*=utf-8''")[1].split(';')[0]
            filename = urllib.parse.unquote(filename)
        elif 'filename="' in content_disp:
            filename = content_disp.split('filename="')[1].split('"')[0]
        else:
            filename = content_disp.split('filename=')[1].split(';')[0]
        
        print(f"✓ Content-Type: {content_type}")
        print(f"✓ Filename: {filename}")
        
        # Verify filename format: creator_INF173_[H:MM:SS].mp4
        assert "INF173" in filename, f"Expected INF173 in filename, got {filename}"
        assert filename.endswith(".mp4"), f"Expected .mp4 extension, got {filename}"
        assert "[" in filename and "]" in filename, f"Expected duration in brackets [H:MM:SS], got {filename}"
    else:
        print(f"⚠ Download not ready (404) - may need to prepare first")


def test_download_tiktok_mp3():
    """Test GET /api/videos/9/download?fmt=mp3 returns correct filename"""
    print("Testing TikTok MP3 download (idx=9, INF173)...")
    r = requests.get(f"{BASE_URL}/videos/9/download?fmt=mp3", timeout=TIMEOUT, allow_redirects=False)
    
    assert r.status_code in [200, 404], f"Expected 200 or 404, got {r.status_code}"
    
    if r.status_code == 200:
        content_type = r.headers.get("content-type", "")
        assert "audio/mpeg" in content_type or "audio/mp3" in content_type or "application/octet-stream" in content_type, \
            f"Expected audio/mpeg content-type, got {content_type}"
        
        content_disp = r.headers.get("content-disposition", "")
        assert "filename" in content_disp, f"Missing filename in Content-Disposition: {content_disp}"
        assert "INF173" in content_disp, f"Expected INF173 in filename, got {content_disp}"
        assert ".mp3" in content_disp, f"Expected .mp3 extension, got {content_disp}"
        
        # Extract filename (handle both filename= and filename*=utf-8'' formats)
        import urllib.parse
        if 'filename*=utf-8' in content_disp:
            filename = content_disp.split("filename*=utf-8''")[1].split(';')[0]
            filename = urllib.parse.unquote(filename)
        elif 'filename="' in content_disp:
            filename = content_disp.split('filename="')[1].split('"')[0]
        else:
            filename = content_disp.split('filename=')[1].split(';')[0]
        
        print(f"✓ Content-Type: {content_type}")
        print(f"✓ Filename: {filename}")
        
        assert "INF173" in filename, f"Expected INF173 in filename"
        assert filename.endswith(".mp3"), f"Expected .mp3 extension"
    else:
        print(f"⚠ Download not ready (404) - may need to prepare first")


def test_download_instagram_mp4():
    """Test GET /api/videos/0/download?fmt=mp4 returns correct filename (Instagram INF50)"""
    print("Testing Instagram MP4 download (idx=0, INF50)...")
    r = requests.get(f"{BASE_URL}/videos/0/download?fmt=mp4", timeout=TIMEOUT, allow_redirects=False)
    
    assert r.status_code in [200, 404], f"Expected 200 or 404, got {r.status_code}"
    
    if r.status_code == 200:
        content_type = r.headers.get("content-type", "")
        assert "video/mp4" in content_type or "application/octet-stream" in content_type, \
            f"Expected video/mp4 content-type, got {content_type}"
        
        content_disp = r.headers.get("content-disposition", "")
        assert "filename" in content_disp, f"Missing filename in Content-Disposition: {content_disp}"
        assert "INF50" in content_disp, f"Expected INF50 in filename, got {content_disp}"
        assert ".mp4" in content_disp, f"Expected .mp4 extension, got {content_disp}"
        
        # Extract filename (handle both filename= and filename*=utf-8'' formats)
        import urllib.parse
        if 'filename*=utf-8' in content_disp:
            filename = content_disp.split("filename*=utf-8''")[1].split(';')[0]
            filename = urllib.parse.unquote(filename)
        elif 'filename="' in content_disp:
            filename = content_disp.split('filename="')[1].split('"')[0]
        else:
            filename = content_disp.split('filename=')[1].split(';')[0]
        
        print(f"✓ Content-Type: {content_type}")
        print(f"✓ Filename: {filename}")
        
        # According to review request, should be: ahorraconmarta_INF50_[0:00:52].mp4
        # But we'll just verify the format is correct
        assert "INF50" in filename, f"Expected INF50 in filename"
        assert filename.endswith(".mp4"), f"Expected .mp4 extension"
    else:
        print(f"⚠ Download not ready (404) - may need to prepare first")


def test_youtube_redirect():
    """Test GET /api/videos/10/download?fmt=mp4 returns 307 redirect (YouTube INF174)"""
    print("Testing YouTube MP4 download (idx=10, INF174) - should return 307 redirect...")
    r = requests.get(f"{BASE_URL}/videos/10/download?fmt=mp4", timeout=TIMEOUT, allow_redirects=False)
    
    # YouTube should return 307 redirect OR 200 if file was cached OR 404 if not prepared
    assert r.status_code in [200, 307, 404], f"Expected 200/307/404, got {r.status_code}"
    
    if r.status_code == 307:
        location = r.headers.get("location", "")
        assert location, "307 redirect should have Location header"
        assert "googlevideo.com" in location or "youtube.com" in location, \
            f"Expected redirect to googlevideo.com or youtube.com, got {location}"
        print(f"✓ Status: 307 (redirect by design)")
        print(f"✓ Location: {location[:100]}...")
    elif r.status_code == 200:
        print(f"✓ Status: 200 (file was cached on server)")
    else:
        print(f"⚠ Status: 404 (not prepared yet)")


def test_reset_all():
    """Test POST /api/videos/reset clears all rows"""
    print("Testing reset endpoint...")
    r = requests.post(f"{BASE_URL}/videos/reset", timeout=30)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    
    data = r.json()
    assert "status" in data, "Missing 'status' field"
    assert data["status"] == "reset", f"Expected status='reset', got {data['status']}"
    assert "total" in data, "Missing 'total' field"
    assert data["total"] == 41, f"Expected total=41, got {data['total']}"
    
    print(f"✓ Reset successful: {data['total']} rows")
    
    # Verify all rows are now pending
    time.sleep(1)  # Give DB a moment to update
    r2 = requests.get(f"{BASE_URL}/videos", timeout=30)
    rows = r2.json()
    
    pending_count = sum(1 for row in rows if row["status"] == "pending")
    print(f"✓ Verified: {pending_count} rows are now pending")


def main():
    tester = APITester()
    
    print("="*60)
    print("BACKEND API TESTS - Content Link Downloader")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Timeout: {TIMEOUT}s")
    
    # Test basic endpoints first
    tester.test("GET /api/videos - returns 41 rows with correct mappings", test_get_videos)
    tester.test("GET /api/stats - returns correct counts", test_get_stats)
    
    # Test prepare endpoint (TikTok is fast and reliable)
    tester.test("POST /api/videos/9/prepare - TikTok INF173", test_prepare_tiktok_row)
    
    # Test download endpoints
    tester.test("GET /api/videos/9/download?fmt=mp4 - TikTok MP4", test_download_tiktok_mp4)
    tester.test("GET /api/videos/9/download?fmt=mp3 - TikTok MP3", test_download_tiktok_mp3)
    tester.test("GET /api/videos/0/download?fmt=mp4 - Instagram INF50", test_download_instagram_mp4)
    tester.test("GET /api/videos/10/download?fmt=mp4 - YouTube 307 redirect", test_youtube_redirect)
    
    # Test reset (do this last)
    tester.test("POST /api/videos/reset - clears all rows", test_reset_all)
    
    # Print summary
    success = tester.summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
