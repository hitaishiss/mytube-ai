MYTUBE AI — ONE-ADDRESS STUDIO

WHAT THIS FIXES
- The website and backend are served from the same Codespace address.
- The app automatically calls its own /health and /api/jobs endpoints.
- There is no backend URL field and no URL to paste into the app.
- Projects remain in this browser's local storage; AI jobs are stored in SQLite.

ONE-TIME START
1. In your Codespace, upload this ZIP into the repository root and extract it there, replacing the files when asked.
2. Stop the old Uvicorn server in its terminal with Ctrl+C.
3. In the Codespace terminal, run: bash start.sh
4. In the Ports tab, make port 8000 Public if it is not already. Open the port's forwarded address. Bookmark THAT address and use it as MyTube AI.

IMPORTANT HONEST LIMITS
- This combines the app and backend at one address. It removes manual backend URL entry.
- GitHub Codespaces can stop when idle and has usage limits. When it is stopped, the studio server is offline until the Codespace is resumed. This is not an always-on production host.
- The installed qwen2.5:3b Ollama model is used for script text generation. Image, video, voice and music generation are not implemented in this build.
- Actual cinematic video rendering and MP4 export are not implemented in this build.
- Project data is stored in this browser; use Export backup regularly. Job records are stored in mytube_jobs.sqlite3 in the Codespace.
- Do not put API keys or secrets in the public GitHub repository.
