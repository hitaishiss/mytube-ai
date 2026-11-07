MYTUBE AI — CONSOLIDATED RELEASE 1.2

This is a complete replacement package for the previous MyTube AI release files.
It retains the studio, local Ollama text jobs, project/production-pack features,
media storage and FFmpeg backend, and now wires Smart Export to media upload,
render submission, status polling and MP4 download. English/Chinese subtitle drafts
can be downloaded as text files from the production pack.

Deployment: extract the ZIP into the existing repository root, replacing matching
application files. Preserve your existing mytube_data directory, SQLite database,
.env/secrets, and any user project backups. Do not commit API tokens.

Start from the extracted repository root with: bash start.sh

AI image/video/voice/music engines still require separate compatible models or
services. See ENGINE_INTEGRATION.md and RELEASE_NOTES_1.2.md. This package does not
claim those engines are active unless the backend health check confirms them.
