# Build status — Release 1.8

Implemented: local Ollama text/script generation, production-pack generation, scene-level media job queue, generic provider submission/status polling, automatic completed media import for providers implementing the documented output endpoint, asset upload/download, subtitle formatting endpoint, FFmpeg 16:9/9:16 MP4 rendering, multiple audio mixing, watermark placement, and browser-local project backup/restore.

Verified in this build environment: Python compilation, JavaScript syntax, FastAPI route registration, provider output content-type/extension tests, job import route smoke tests, and ZIP integrity.

Not included: bundled or hosted image/video/TTS/music models, provider accounts/credentials, default ComfyUI model workflow, persistent always-on compute, or deployment to the user's Codespace. External engines and compatible provider implementations are required for generated media.
