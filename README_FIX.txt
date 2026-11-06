MYTUBE AI BACKEND FIX v2

IMPORTANT:
- This package contains ONLY backend/app.py.
- Replace the repository file backend/app.py with this file.
- DO NOT copy the repository-root app.py into backend/app.py.
- Keep port 8000 Public. Keep Ollama ports 11434 and 41997 Private.
- Restart the backend after replacing the file:
  1. Stop the existing uvicorn process with Ctrl+C in its terminal.
  2. Run: uvicorn backend.app:app --host 0.0.0.0 --port 8000

Changes:
- Adds a bounded generation length (384 tokens) and 10-minute model keep-alive.
- Allows up to 30 minutes for Ollama to respond.
- Job execution remains in a background thread and its result is saved in SQLite.
- This is a text-generation reliability patch only. It does not add image/video/voice/music generation.
