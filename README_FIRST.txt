MYTUBE AI — CONSOLIDATED ENGINE BUILD v0.4

This package consolidates the studio and its backend on one Codespace port. It adds persistent media uploads and a real FFmpeg MP4 render API, in addition to the existing local Ollama script engine.

SETUP
1. Extract/replace the package in the root of the existing Codespace repository.
2. Run: bash start.sh
3. Open port 8000. The studio and API share that address; no backend URL is entered in the app.

RESTART
After Codespace stops or restarts, run bash start.sh again. A free Codespace is not always-on.

IMPORTANT CAPABILITY STATUS
Text/script generation uses Ollama qwen2.5:3b. MP4 assembly/rendering is available when FFmpeg exists. Image, video, voice and music GENERATION models are not included or connected in this build; the dashboard will say so. External endpoint variables in .env.example are configuration placeholders, not working integrations. No unlimited free generation is promised.

Server-side uploads/exports are stored under mytube_data/. Back up that folder if you need to preserve uploaded media and rendered MP4s. Browser projects remain in localStorage; use the in-app backup for those.
