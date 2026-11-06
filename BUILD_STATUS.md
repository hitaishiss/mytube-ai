# MyTube AI — Consolidated Studio v2

This package updates the deployed studio with a unified cinematic visual system and forces browsers to refresh the app cache.

## Included and currently functional
- Project creation, project list, deletion, local autosave on explicit save actions
- Script editor, Creative Director revision prompt, and backend text-job submission/polling
- Character and pet library, Story Bible, scene planner and ordering
- Voice direction profiles, original song briefs and lyrics, Shorts planning
- Export preset/size estimate, watermark settings
- AI backend URL storage and health check
- JSON backup and restore
- Dark/light theme, responsive layout, installable PWA shell

## Important integration status
- Text generation requires the backend plus a running Ollama model reachable by that backend.
- Image, video, voice, music generation, actual MP4 rendering/muxing/compression, and bilingual audio rendering are NOT yet implemented as working engines in this package. The UI must not be treated as proof those engines exist.
- The app does not provide unlimited free compute. Codespaces has usage limits and is not a production render farm.
- Browser-local project storage is tied to that browser/device. Export backups regularly.

## Deploy
Copy the contents of this folder over the repository root, commit, and let GitHub Pages deploy. Keep `backend/` on the Codespace/backend side; GitHub Pages does not run Python.
