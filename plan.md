# plan.md

## 1) Objectives
- Prove the **core workflow** works reliably with real URLs: `yt-dlp` can (a) fetch metadata, (b) download MP4, (c) extract MP3 via `ffmpeg`.
- Build an MVP web app (FastAPI + React + MongoDB) that shows **41 preloaded rows** (URL + INF ID) and supports per-row:
  - **Prepare** (fetch metadata on-demand)
  - **Download MP4** and **Download MP3**
  - Correct filenames: `{creator_username}_{INF_ID}_[H:MM:SS].mp4/.mp3`
- Handle failure modes cleanly (IG/FB login walls, rate limits, extractor errors) with clear status + retry.

## 2) Implementation Steps

### Phase 1 — Core POC (isolation; do not proceed until stable)
**Goal:** Validate at least 1 working URL per platform (IG, TikTok, YT Shorts, FB) for both MP4 + MP3.

1. **Web research / best practices (short)**
   - Confirm current `yt-dlp` flags for IG/FB reliability (user-agent, geo-bypass, cookies usage, format selection, retries, sleep).
   - Confirm best method to extract MP3 (`ffmpeg` postprocessor vs separate transcode step).

2. **Install + verify tooling**
   - Ensure `yt-dlp` and `ffmpeg` available in runtime.

3. **Write a single Python POC script**
   - Input: 4 URLs (one per platform) + INF IDs.
   - For each URL:
     - Fetch metadata (`yt-dlp --dump-json` equivalent via python API or subprocess).
     - Parse: `uploader/uploader_id`, `duration`, `thumbnail`, `webpage_url`.
     - Download best MP4 (video+audio if possible).
     - Extract MP3 using ffmpeg.
     - Generate filenames using required format and a duration formatter that outputs `[H:MM:SS]`.

4. **POC acceptance gate (must pass)**
   - All 4 platforms: metadata fetch succeeds OR returns a clear actionable error.
   - At least one IG + one FB URL successfully downloads in this environment; if not:
     - Add retries/sleep + user-agent.
     - If still failing, implement optional **cookies.txt** support (but keep app usable without it).

5. **Lock core “download engine”**
   - Extract POC logic into a reusable backend module: `get_metadata(url)`, `download_mp4(url)`, `download_mp3(url)`.

**Phase 1 user stories (core validation)**
1. As a developer, I can run one script and see metadata (creator, duration, thumbnail) printed for each platform.
2. As a developer, I can download an MP4 for each test URL and the file plays.
3. As a developer, I can extract MP3 for each test URL and the audio plays.
4. As a developer, filenames exactly match `{creator}_{INF}_[H:MM:SS]`.
5. As a developer, failures show a precise reason (e.g., login required, rate limited, unsupported URL).

---

### Phase 2 — V1 App Development (build around proven core)
**Goal:** MVP web app that works end-to-end for the 41-row table.

1. **Backend (FastAPI)**
   - Data model (MongoDB): store 41 items with fields: `idx`, `inf_id`, `url`, `platform`, plus optional cached `creator`, `duration_sec`, `duration_str`, `thumbnail`, `status`, `last_error`, timestamps.
   - Endpoints:
     - `GET /api/videos` → returns all rows (preloaded mapping + cached metadata if present)
     - `POST /api/metadata/{idx}` → runs `get_metadata(url)`, saves results, returns updated row
     - `GET /api/download/{idx}/mp4` → streams MP4 with correct filename
     - `GET /api/download/{idx}/mp3` → streams MP3 with correct filename
   - Download behavior:
     - Prefer streaming response; if temp files are needed, store in a temp directory with cleanup.
     - Ensure safe filenames (strip/replace unsafe characters) while preserving “username” as provided.

2. **Frontend (React)**
   - Table with columns: `#`, `INF ID`, `Platform`, `URL`, `Creator`, `Duration`, `Thumbnail`, `Actions`, `Status`.
   - Row actions:
     - **Prepare** button (calls `/api/metadata/{idx}`)
     - **Download MP4** (enabled after metadata OR allow anyway)
     - **Download MP3** (enabled after metadata OR allow anyway)
     - **Retry** appears on error.
   - Bulk actions (MVP):
     - **Prepare All** (sequential to avoid rate limits)
     - **Download All MP4** (sequential, user-confirm)
     - **Download All MP3** (sequential, user-confirm)

3. **Preload the 41 mappings**
   - Seed on startup or via one-time seed script.
   - Store mapping order exactly as provided.

4. **Operational safeguards**
   - Global throttling for IG/FB requests (sleep between requests).
   - Timeout + retry policy.
   - Clear error messages surfaced to UI.

5. **V1 end-to-end testing**
   - Validate at least 1 URL per platform in-app: Prepare → MP4 download → MP3 download.
   - Validate naming, duration formatting, and UI states.

**Phase 2 user stories (V1 app)**
1. As a user, I open the app and immediately see a 41-row table pre-populated with URL + INF ID.
2. As a user, I click **Prepare** on a row and see creator username, duration, and thumbnail appear.
3. As a user, I click **Download MP4** and receive a correctly named `.mp4` file.
4. As a user, I click **Download MP3** and receive a correctly named `.mp3` file.
5. As a user, if a row fails (e.g., IG/FB blocks), I see an error and can click **Retry**.

---

### Phase 3 — Hardening + UX improvements (after V1 works)
1. **Caching + idempotency**
   - Cache metadata results; avoid re-fetch unless user forces refresh.
   - Cache downloaded outputs for a short TTL to reduce repeated platform hits.

2. **Improved bulk flows**
   - Bulk progress UI + cancel.
   - Concurrency controls (default sequential; optional small parallelism for YT/TikTok only).

3. **IG/FB reliability options**
   - Optional cookie file upload/config (admin-only setting) to improve success rate.
   - Per-platform request pacing settings.

4. **Comprehensive testing**
   - Run through multiple rows per platform.
   - Regression test: Prepare/Download works after refresh, and filenames remain correct.

**Phase 3 user stories (hardening)**
1. As a user, I can run **Prepare All** and see clear progress and per-row results.
2. As a user, I can restart the app and previously prepared metadata is still present.
3. As a user, repeated downloads don’t re-hit platforms unnecessarily.
4. As a user, IG/FB success rate improves when cookies are configured.
5. As a user, bulk operations don’t freeze the UI and can be cancelled.

## 3) Next Actions
1. Implement Phase 1 POC script (4 URLs) + run it until it passes.
2. If IG/FB fail, iterate with throttling/user-agent/retries; add optional cookies support if needed.
3. Once POC stable, implement FastAPI endpoints around the extracted download engine.
4. Build React table UI and wire to backend.
5. Run end-to-end V1 test: Prepare + MP4 + MP3 for at least one URL per platform.

## 4) Success Criteria
- POC proves: metadata + MP4 + MP3 work for at least one URL per platform in this runtime.
- V1 app shows 41 rows and supports Prepare + MP4/MP3 downloads with correct naming.
- Duration strings always formatted as `[H:MM:SS]`.
- Errors are actionable (shown per row) and retries work.
- Bulk actions execute sequentially without overwhelming platforms and provide visible progress.