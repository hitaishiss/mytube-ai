MYTUBE AI — FINAL ONE-ADDRESS PACKAGE

This build serves the studio AND its private AI backend from the SAME Codespace port. The app calls /health and /api/jobs on its own address. There is no backend URL box and no URL to paste into the app.

ONE FINAL SETUP
1. Upload this ZIP into the root of your existing Codespace repository and extract it there, replacing existing files.
2. In the Codespace terminal, run: bash start.sh
3. In the Ports tab, make port 8000 Public, then open its forwarded address. Use that one address for the studio.

After a Codespace restart, run `bash start.sh` again. Codespaces may stop when idle; no package can keep a free Codespace permanently awake. Your existing browser projects remain in that browser's local storage; export a backup before changing browsers/devices.

WHAT IS ACTUALLY CONNECTED
- Working local text/script generation through Ollama qwen2.5:3b, when the Codespace has enough resources.
- Project planning, script editing, cast/pets, Story Bible, scenes, voice directions, song briefs, Shorts planning, export settings, watermark settings, backup/restore.

NOT YET IMPLEMENTED AS GENERATION ENGINES
- Image, video, voice, music generation; actual video rendering, MP4 muxing/compression, bilingual audio rendering. Those require separate model runtimes and substantial compute/storage. This package does not pretend those buttons are working engines.
- Codespaces is not always-on production hosting and has usage limits. No paid service is enabled by this package.
