# MyTube AI

MyTube AI is a browser-based drama production studio with a FastAPI backend and a local Ollama text-generation service.

## Current status

The backend currently supports health and capability reporting, local text/script generation through Ollama, local speech preview through eSpeak NG / eSpeak, and SQLite job status persistence.

AI image generation, AI video generation, music generation, and final video rendering/export are not implemented as production generation adapters yet. UI planning/settings for these features do not mean the corresponding media pipeline is operational.

## Run with Docker Compose

Requirements: Docker Engine with the Compose plugin, plus enough memory and disk for the Ollama model. The first start downloads qwen2.5:3b and can take a while.

1. Clone this repository.
2. In the repository directory, run:

   docker compose up --build

3. Open http://localhost:8000.

To stop the stack, press Ctrl+C and run docker compose down. Persistent Ollama model, job database, and generated audio data are stored in Docker volumes.

The compose stack is intended for local testing or a host you control. It is not a free always-on public hosting service. Do not expose port 8000 publicly without suitable authentication, HTTPS, rate limits, and monitoring.

## Run the backend without Docker

Requirements: Python 3.11+, Ollama, and (optional for voice preview) eSpeak NG.

1. Install dependencies: python -m pip install -r requirements.txt
2. Install and start Ollama, then pull the configured model: ollama pull qwen2.5:3b
3. Install eSpeak NG if voice previews are needed.
4. Start the API: uvicorn app:app --host 127.0.0.1 --port 8000

The API health endpoint is /health. It reports which capabilities are available on the current host.

## Configuration

- OLLAMA_URL: Ollama base URL (default http://127.0.0.1:11434)
- MYTUBE_TEXT_MODEL: Ollama model name (default qwen2.5:3b)
- MYTUBE_DB_PATH: SQLite database path (default mytube_jobs.sqlite3)
- MYTUBE_ALLOWED_ORIGINS: comma-separated browser origins allowed by CORS
- MYTUBE_API_TOKEN: optional bearer token required by protected job and voice-generation endpoints

If MYTUBE_API_TOKEN is enabled, the browser client must be configured to send that token securely. Do not put a private server token in public frontend JavaScript or commit it to this repository. The current static client does not provide a secure token-management flow; leave this unset only for trusted local testing, not an exposed public service.

## Deployment notes

GitHub Pages can host static frontend files, but it cannot run this FastAPI/Ollama backend. A separately hosted backend is required for online generation. Ollama also needs compute, memory, and persistent storage; a free host may not provide enough resources or remain online. No public backend deployment is configured by this repository change.

## Verification

GitHub Actions checks Python compilation/import, JavaScript syntax, Docker Compose configuration, and Docker image build. These are build/syntax checks; they do not prove that Ollama, voice generation, or a deployed public service works end-to-end.