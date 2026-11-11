MYTUBE AI — FINAL CONSOLIDATED PACKAGE 3.0

This archive contains the complete current MyTube AI application source in the archive root.
It is designed to be extracted into the ROOT of the existing GitHub/Codespace repository,
replacing matching application files. It deliberately does NOT include the live SQLite jobs
database or mytube_data media directory, so extracting it will not overwrite those runtime
data stores.

STARTUP
1. Open the existing Codespace repository folder (the folder containing index.html).
2. Extract/replace the contents of this archive into that repository root.
3. Run: bash start.sh
4. In MyTube AI → AI Engine, enter the HTTPS forwarded URL for Codespaces port 8000
   and select “Save connection & test”. If MYTUBE_API_TOKEN is enabled on the backend,
   enter the same token in the optional token field.

Do not create a new repository or Codespace. Keep the existing mytube_data directory and
mytube_jobs.sqlite3 file if present. GitHub Pages hosts the frontend; the Codespace runs
the backend. Its forwarded URL may change after a Codespace restart.

WHAT IS INCLUDED
- Project workspace, script/production drafting via local Ollama, characters, Story Bible,
  scene planning, voice/song briefs, Shorts planning, watermark and Smart Export UI.
- SQLite-backed job tracking and restart recovery.
- Upload/asset library, ComfyUI image workflow adapter, generic video/TTS/music provider
  adapters, provider polling/import, subtitles, FFmpeg MP4 and Short rendering.
- Browser project backup, full ZIP backup and full restore.
- Saved private-backend URL and optional bearer-token connection support.

IMPORTANT LIMITATIONS — NOT CLAIMED AS COMPLETE
- Ollama provides text generation only; it is not an image, video, voice or music generator.
- ComfyUI requires a separately running server, installed models and a compatible API workflow.
- Video, TTS and music adapters require compatible provider services configured privately.
  A configured URL is not proof that a provider works.
- FFmpeg edits/encodes uploaded or generated assets; it does not generate cinematic footage.
- GitHub Pages/Codespaces deployment and real provider operation must be verified in the user's
  account. This package was not deployed to that account by the build process.
- Codespaces may stop when idle; a free always-on backend is not guaranteed.
- No paid service or billing is enabled by default.

SECURITY
- Never commit provider API keys or backend tokens to the public frontend or repository.
- Use HTTPS for remote backend URLs. The optional backend token is stored in this browser's
  local storage; use it only on a trusted personal device.
- Keep backups of the existing mytube_jobs.sqlite3 and mytube_data directory.

See FINAL_STATUS.md and ENGINE_INTEGRATION.md for the precise handover.
