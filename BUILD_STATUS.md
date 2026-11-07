# MyTube AI Consolidated Engine v0.5 — generation stability patch

This patch addresses excessive SQLite writes during streamed Ollama generation. The prior worker updated the jobs database for every model chunk, which caused unnecessary write/lock pressure during long generations. Progress is now persisted at most once per 600 generated characters or 3 seconds, with the completed script saved at the end.

This is a targeted stability improvement, not a guarantee that Codespaces will never disconnect. Image, video, voice, and music generation engines remain unconnected in this build. FFmpeg rendering remains available when FFmpeg is installed.

## Apply
Extract this package into the repository root, replacing existing files, then restart the Codespace backend with `bash start.sh`.
