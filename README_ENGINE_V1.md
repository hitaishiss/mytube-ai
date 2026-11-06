# MyTube AI — Text Engine Foundation v1

This update keeps the existing Studio UI and adds a real backend job API with a local Ollama text adapter.

## What works in this build
- Persistent SQLite job records and status polling.
- `GET /health`, `POST /api/jobs`, `GET /api/jobs/{jobId}`, `GET /api/jobs`.
- CORS defaults to the verified GitHub Pages origin: `https://hitaishiss.github.io`.
- Text jobs call a local Ollama model when Ollama is installed and running.
- Image, video, voice and music jobs are explicitly marked unavailable; no fake success.
- No API keys are embedded in the public website.

## Important hardware note
This uses a model running on the same machine as the backend. GitHub Codespaces does not automatically provide a suitable GPU or a persistent always-on server. If Ollama is not reachable from the backend, text jobs will fail with a clear message. A laptop can run a small quantized text model only if it has enough RAM; video generation is much heavier.

## Run
Use Python 3.11+ in the backend folder:

```bash
pip install -r requirements.txt
```

Install Ollama separately on the same machine, start it, then pull a model:
```bash
ollama pull qwen2.5:3b
```

Set environment variables using `.env.example` as a reference, then:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Check:
- `/` should show the service message.
- `/health` should show text adapter `available` and `installed` as true only when Ollama and the model are ready.
- `/docs` documents the API.

## API example
```json
{
  "projectId": "your-project-id",
  "kind": "text",
  "input": {
    "prompt": "Write an original opening scene for a mystery drama..."
  },
  "output": {}
}
```

Poll the returned `jobId` at `/api/jobs/{jobId}` until `status` is `completed` or `failed`. Completed text is in `output.text`.

## Security
Do not expose the Codespaces port to the public internet for permanent use. Codespaces forwarded URLs are temporary. For production use, deploy behind HTTPS with authentication and network restrictions. Never put provider credentials in GitHub Pages or browser JavaScript.

## Preserved roadmap — no planned feature is intentionally dropped
The Studio's full intended scope remains: natural-language AI project manager; original/adapted/inspired/fusion story workflows; script generation and Creative Director revisions; character, pet and fantasy-creature creation; reusable appearance/wardrobe/voice libraries; Story Bible and continuity; scene planning and camera/lighting/audio direction; scene-by-scene or automatic production; image/video generation; narration and character voices; voice editing; original songs/music; 5–10 Shorts; thumbnails/titles/descriptions; 9:16 and 16:9; episodic and movie-length projects; two projects in planning concurrently; queued/resumable rendering; review and approval gates; Smart Export to one synchronized MP4; 720p/1080p/4K when source supports it; compression presets; watermark; dark/light themes; English/Chinese project language; local project storage; backup/restore; deletion; production status, retries and free-usage transparency.

Only the local text adapter is implemented in this version. Other adapters remain future work and are not represented as working.

## Frontend integration included
The Script tab now has an **AI script generator**. It submits a text job to the saved backend URL, polls its status, and inserts completed text into the script editor. The user must review/edit/approve it. The public app still contains no secret token.

## Update an existing Codespace
Your current command uses `uvicorn backend.app:app`, so replace the existing `backend/app.py` with the included `backend/app.py`. Keep the backend folder. Replace `requirements.txt` at the repository root with the included one (or confirm the two packages are already installed). Restart the server with:
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```
Then update the GitHub Pages files at the repository root (`app.js` and `sw.js` at minimum; safest is to replace the matching frontend files in the package). Keep your existing Codespaces forwarded URL in the AI Engine field, without `/health`.
