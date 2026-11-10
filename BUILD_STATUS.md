# Build status — Release 2.8

## Implemented in this codebase
- Local Ollama text/production jobs and persisted job tracking.
- Configurable provider submission, polling, retry and output-import contracts for video, voice and music.
- ComfyUI image submission/status/output routes with caller-supplied API workflows.
- Scene image generation now uses durable backend jobs; scene job IDs/status persist in project state and can be refreshed after reload. Completed image outputs import into managed project assets.
- Subtitle cue formatting endpoint (SRT/VTT) and production-pack subtitle text drafts.
- FFmpeg full-video rendering in 16:9/9:16, watermark placement and multi-track audio mixing.
- Individual Shorts trimming/rendering to 9:16, watermark, status refresh and download links.
- Local project backup and restore.
- Backend restart recovery for interrupted local jobs.
- Engine diagnostics distinguish configured endpoints from reachable services.

## Release 2.8 changes
- Replaced browser-only ComfyUI scene image submission with persistent backend image jobs.
- Added per-scene refresh and automatic asset import after successful completion.
- Updated service-worker cache and backend version to 2.8.0.

## Verified in this build environment
- Python syntax compilation.
- JavaScript syntax check.
- Persistent image-job lifecycle test using mocked ComfyUI responses.
- ZIP integrity.

## Not verified / requires external setup
- Live deployment and connection to the user's Codespace.
- Actual ComfyUI model/workflow execution.
- Actual external video/TTS/music provider execution.
- Full production run with real project media.

Adapters are integration points, not bundled generation models. A configured endpoint or passing mock test does not establish that a real media generator is operational.


## Release 2.9 update
- Bounded background worker pool (default 3, configurable 1–8).
- Real media models/providers remain external configuration requirements.
\n## Release 2.10\n- Queued media jobs recover as retryable failures after restart.\n- Processing media jobs without remote IDs recover as retryable failures.\n- Invalid worker-pool configuration safely falls back to three workers.\n\n## Release 2.11\n- Individual Shorts are atomically published only after a successful, non-empty FFmpeg output.\n- Actual sample Short render tested at 720x1280 with audio and watermark.\n
## Release 2.12
- Added completed provider-media import during saved-job refresh.
- Imported media asset IDs are attached to matching production-pack scenes and persisted.
- Validation: Python compile, JavaScript syntax, backend import/route count, ZIP integrity. Provider behavior remains dependent on an externally configured compatible service.


## Release 2.13
- Added full ZIP backup of browser project data, backend SQLite jobs, assets and rendered exports.
- Added a phone-friendly Full backup + media control while preserving the existing JSON project backup.
- Python/JavaScript syntax, backend import, endpoint smoke test and ZIP contents/integrity verified.


## Release 2.14
- Added validated full ZIP restore for projects plus missing media assets/exports.
- Preserves existing files and active jobs database.
- See RELEASE_NOTES_2.14.md.
