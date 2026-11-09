# Build status — Release 2.2

Implemented and verified:
- Local text/production jobs.
- Scene-level video/voice/music provider submission, polling and output-import contract.
- ComfyUI image submission/status/output routes.
- Subtitle generation endpoint and production-pack subtitle drafts.
- FFmpeg 16:9/9:16 full-video rendering, configurable watermark and multiple audio-track mixing.
- Project-local media-job tracking, saved status refresh and failed-job retry.
- Individual Shorts trim/render: upload a source clip, select start/end seconds, render a 9:16 H.264/AAC MP4, apply project watermark, check render status and open the output.
- Release 2.2: per-Short status refresh restores saved render state and download links after leaving/reopening the planner.

Verification performed in build environment:
- Python syntax compilation passed.
- JavaScript syntax check passed.
- FastAPI app imported and routes registered.
- Actual FFmpeg short render tested using a generated sample clip; output verified at 720x1280 with audio and watermark.

External dependencies remain:
- ComfyUI + model + workflow for image generation.
- Compatible configured video/TTS/music providers for those generation types.
- FFmpeg on the backend for rendering.
- No model weights or provider credentials are bundled.

Deployment has not been performed from this build environment.
