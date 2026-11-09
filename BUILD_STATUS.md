# Build status — Release 2.3

Implemented in this codebase:
- Local Ollama text/production jobs and persisted job tracking.
- Configurable provider submission, polling, retry and output-import contracts for video, voice and music.
- ComfyUI image submission/status/output routes; scene image UI accepts a caller-supplied API workflow.
- Subtitle cue formatting endpoint (SRT/VTT) and production-pack subtitle text drafts.
- FFmpeg full-video rendering in 16:9/9:16, watermark placement and multi-track audio mixing.
- Individual Shorts trimming/rendering to 9:16, watermark, status refresh and download links.
- Local project backup and restore.
- Release 2.3 fixes: engine health checks use the configured API base; Shorts crop and watermark are applied in one FFmpeg filter chain; capability notice and service-worker cache version updated.

Verified in this build environment:
- Python syntax compilation passed.
- JavaScript syntax check passed.
- Standalone Shorts worker rendered a sample clip with audio and watermark; ffprobe confirmed 720x1280 output.

Not verified / requires external setup:
- Live deployment and connection to the user's Codespace.
- Actual ComfyUI model/workflow execution.
- Actual external video/TTS/music provider execution.
- Full production run with real project media.

Important: adapters are integration points, not bundled generation models. A configured endpoint is not represented as a functioning generator until it passes its own health and job tests.
