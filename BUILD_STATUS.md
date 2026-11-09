# Build status — Release 2.6

## Implemented in this codebase
- Local Ollama text/production jobs and persisted job tracking.
- Configurable provider submission, polling, retry and output-import contracts for video, voice and music.
- ComfyUI image submission/status/output routes; scene image UI accepts a caller-supplied API workflow.
- Persisted ComfyUI image jobs now support status refresh and importing generated images into managed project assets.
- Subtitle cue formatting endpoint (SRT/VTT) and production-pack subtitle text drafts.
- FFmpeg full-video rendering in 16:9/9:16, watermark placement and multi-track audio mixing.
- Individual Shorts trimming/rendering to 9:16, watermark, status refresh and download links.
- Local project backup and restore.
- Release 2.3 fixes: engine health checks use the configured API base; Shorts crop and watermark are applied in one FFmpeg filter chain.
- Release 2.4 hardening: ComfyUI image output path validation and bounded image retrieval.

## Release 2.5 changes
- Persisted ComfyUI image jobs can be refreshed from the standard jobs interface.
- Completed ComfyUI image outputs can be imported into MyTube's managed asset library.

## Verified in this build environment
- Python syntax compilation passed.
- JavaScript syntax check passed.
- FastAPI image-job refresh + image import integration test passed with mocked ComfyUI responses.
- FastAPI route registration: 27 routes.

## Not verified / requires external setup
- Live deployment and connection to the user's Codespace.
- Actual ComfyUI model/workflow execution.
- Actual external video/TTS/music provider execution.
- Full production run with real project media.

Important: adapters are integration points, not bundled generation models. A configured endpoint is not represented as a functioning generator until it passes its own health and job tests.

## Release 2.6 changes
- Backend startup now marks interrupted queued/processing local text and production jobs as failed with a retry instruction. This prevents jobs from appearing permanently active after Codespace/container restarts.
- Remote provider jobs are left intact for status refresh; the backend does not falsely mark them failed merely because its own process restarted.
- Backend version is 2.6.0.
