# MyTube AI

MyTube AI is a browser-based drama production studio with a FastAPI backend and a local Ollama text-generation service.

## Current status

The backend supports local text/script generation through Ollama, speech previews through eSpeak NG / eSpeak, SQLite job persistence, Stable Diffusion-compatible image generation, FFmpeg video assembly/export, and optional local AI video/music service adapters. The optional AI adapters require separately installed model runtimes and workflows; they are not bundled in this repository.

## Run with Docker Compose

Requirements: Docker Engine with the Compose plugin, plus enough memory and disk for the Ollama model. The first start downloads qwen2.5:3b and can take a while.

1. Clone this repository.
2. In the repository directory, run:

   docker compose up --build

3. Open http://localhost:8000.

To stop the stack, press Ctrl+C and run docker compose down. Persistent Ollama model, job database, generated audio, and generated media assets are stored in Docker volumes.

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
- MYTUBE_IMAGE_API_URL: AUTOMATIC1111-compatible Stable Diffusion API base URL
- MYTUBE_COMFYUI_URL: optional ComfyUI base URL for AI video workflows
- MYTUBE_COMFYUI_WORKFLOW_FILE: path to a ComfyUI API-format workflow JSON file (default `comfyui_workflow_api.json`)
- MYTUBE_MUSIC_API_URL: optional local AI music service base URL; the app POSTs to `/generate`

If MYTUBE_API_TOKEN is enabled, the browser client must be configured to send that token securely. Do not put a private server token in public frontend JavaScript or commit it to this repository. The current static client does not provide a secure token-management flow; leave this unset only for trusted local testing, not an exposed public service.

## Deployment notes

GitHub Pages can host static frontend files, but it cannot run this FastAPI/Ollama backend. A separately hosted backend is required for online generation. Ollama also needs compute, memory, and persistent storage; a free host may not provide enough resources or remain online. No public backend deployment is configured by this repository change.

## Verification

GitHub Actions checks Python compilation/import, JavaScript syntax, Docker Compose configuration, and Docker image build. These are build/syntax checks; they do not prove that Ollama, voice generation, or a deployed public service works end-to-end.

## Media generation adapters

The Media Lab tab connects to backend jobs for four production steps:

- **Images:** calls an AUTOMATIC1111-compatible Stable Diffusion WebUI API at `MYTUBE_IMAGE_API_URL` (default `http://127.0.0.1:7860`). Start that image service on the same backend host and enable its API before using image generation. Docker Compose points to a host-side API at `http://host.docker.internal:7860` by default; set `MYTUBE_IMAGE_API_URL` to override it. The stack does not download or start Stable Diffusion automatically; image models require substantial storage and compatible compute.
- **Video:** when `MYTUBE_COMFYUI_URL` and a compatible API workflow file are configured, the backend uploads the selected image, substitutes prompt/input placeholders, queues the workflow, waits for completion, and downloads its video output. If ComfyUI is not configured, it falls back to a 720p FFmpeg still-image sequence.
- **Music:** when `MYTUBE_MUSIC_API_URL` is configured, the backend POSTs `{ "prompt": "...", "duration": 30 }` to `/generate` and expects JSON containing base64-encoded audio in `audio_base64` (optional `format`: `wav` or `mp3`). Otherwise it uses the built-in procedural synthesizer.
- **Final export:** FFmpeg muxes the assembled video and optional generated music into a single MP4 with AAC audio.

Generated files are stored in the backend asset directory and served from `/assets/`. The project browser stores generated asset filenames/URLs locally; back up your project data and keep the backend's generated_assets directory persistent.

For ComfyUI video, export your installed image-to-video or text-to-video graph using ComfyUI’s **Save (API Format)** option, place that JSON at `comfyui_workflow_api.json` (or configure another path), and set `MYTUBE_COMFYUI_URL` to the reachable ComfyUI server. In the exported graph, use the literal placeholders `{{prompt}}`, `{{image}}`, `{{width}}`, `{{height}}`, `{{frames}}`, `{{fps}}`, and `{{seed}}` in the relevant node input values. `{{image}}` is replaced with the uploaded selected still image filename. The graph must include a video output node whose history output contains a `videos`, `gifs`, or `files` entry. Workflow graphs and required custom nodes are model-specific; this adapter cannot install missing models or guess a compatible graph.

For AI music, point `MYTUBE_MUSIC_API_URL` at a trusted local service implementing the documented `/generate` contract. Keep both services private to your machine/network. Set `MYTUBE_IMAGE_API_URL` to the reachable Stable Diffusion API URL if it uses a different address. These media endpoints are intended for a trusted, private backend. Before exposing them publicly, add authentication to all job/media routes, request limits, storage quotas, and HTTPS. The existing static browser client does not yet have a secure private-token configuration flow.


### Important free-first limitations

- A compatible image model service must be installed and running on hardware you control. The project does not bundle multi-gigabyte model weights.
- The ComfyUI adapter is real workflow plumbing, but it only produces AI video after a compatible workflow, custom nodes, model weights and sufficient compute are installed and tested on the host.
- The optional music adapter connects to a local model service; the built-in fallback remains a procedural synthesizer, not a neural music model.
- FFmpeg final export is implemented as a muxing step; it does not generate animated scenes. The complete cinematic workflow is therefore not yet available end-to-end.
- Free-first means open-source/local software without per-generation API charges. It does not remove hardware, electricity, storage, or hosting requirements.
