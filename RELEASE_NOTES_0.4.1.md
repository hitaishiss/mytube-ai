# MyTube AI — consolidated repair 0.4.1

## Fixed from the uploaded project
- The root `app.py` is the production backend used by `start.sh`.
- The static-file catch-all mount is now registered last. Previously it was registered before the voice endpoint, so `/api/voice/generate` was swallowed by the static mount and returned HTTP 405.
- Removed five duplicate voice endpoint definitions and kept one validated implementation.
- Fixed the studio static directory to point at the project root.
- Startup now detects an already responding backend on port 8000 and avoids launching a duplicate Uvicorn process.
- Startup still reuses local Ollama and the existing `qwen2.5:3b` model.

## Actual capabilities / limits
- Text generation: local Ollama, if Ollama is running and the model is installed.
- Voice: local eSpeak NG speech synthesis plus FFmpeg MP3 encoding, if both executables are installed.
- Video rendering: FFmpeg-based assembly of uploaded/licensed media.
- Image/video/music generation models are NOT bundled or configured by this package. No external API keys or paid services were added.
- The separate `backend/app.py` is an older v0.2 backend and is not the startup target.
- Codespaces can sleep/stop; this is not always-on hosting.

## Apply
Replace the project files with this package, then start using `bash start.sh`.
