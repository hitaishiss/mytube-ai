# Build status — Release 1.6

## Implemented
- Local Ollama script and production-pack generation.
- Production-pack Shorts are imported into the Shorts planner.
- One-call production queue creates scene-level video and voice jobs plus an optional music job.
- Backend job status is polled and shown in the Production Workflow screen.
- Provider acceptance is distinguished from completed output (`submitted` != `completed`).
- Generic ComfyUI image submission and generic video/TTS/music HTTP adapters.
- Asset upload, SRT/VTT formatting, FFmpeg MP4 rendering, 16:9 and 9:16 outputs, configurable watermark, and multiple audio-track mixing.
- Browser-local project persistence and backup/restore.

## Checks performed
- Python syntax compilation.
- JavaScript syntax check.
- FastAPI route registration and queue schema smoke test.
- ZIP integrity check.

## Still external / incomplete
- No image/video/TTS/music model weights are bundled.
- ComfyUI requires a configured server and valid installed workflow/model.
- Video/TTS/music require compatible services implementing the documented HTTP contract.
- Provider-specific completion polling and automatic media-file retrieval are not standardized or complete.
- The frontend project data remains browser-local; backend jobs/assets are server-side.
- Deployment and end-to-end testing on the user's Codespace have not been performed.
