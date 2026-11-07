# MyTube AI Final One-Address Build

- Frontend and FastAPI backend served from the same port 8000.
- Frontend API base defaults to `window.location.origin`; no endpoint entry required.
- `start.sh` starts Ollama, checks/pulls `qwen2.5:3b` only if missing, installs Python requirements, and launches Uvicorn.
- SQLite job records persist in the Codespace workspace.
- User projects persist in browser localStorage; backups can be exported.
- Text generation is implemented through Ollama. Image/video/voice/music generation and final MP4 rendering are not implemented.
- Codespaces can sleep/stop and require restart; this is not always-on hosting.
