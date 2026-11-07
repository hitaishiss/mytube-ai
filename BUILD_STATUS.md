# MyTube AI consolidated build v0.4

## Implemented in this package
- Same-origin FastAPI + static studio; frontend uses the current origin automatically.
- Local Ollama text/script job queue with SQLite job records.
- Persistent server-side media asset uploads with file-type and size validation.
- FFmpeg MP4 renderer API: normalizes and concatenates uploaded clips, optionally muxes an audio track, applies a text watermark, and exports 720p/1080p/4K MP4 presets.
- Render status and download endpoints.
- Capability reporting distinguishes installed/available engines from merely configured endpoint placeholders.
- Browser-side project storage and backup/restore remain in place.

## Not implemented / not falsely claimed
- No image, video-generation, voice-generation, or music-generation model is bundled or connected. The optional endpoint variables are placeholders, not functioning adapters.
- No automatic bilingual speech translation or voice cloning is bundled.
- The renderer combines media the user has already generated; it does not create cinematic footage.
- The browser UI does not yet provide a complete end-user upload-and-render workflow; the renderer is available through the backend API.
- Codespaces can stop/sleep and are not always-on hosting.

## Requirements
- Python packages in requirements.txt.
- Ollama + qwen2.5:3b for local text generation.
- FFmpeg installed on the host for actual MP4 rendering.
