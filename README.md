# MyTube AI

MyTube AI is a browser-based drama production studio with a FastAPI backend and a local Ollama text-generation service.

## Current status

The backend currently supports health and capability reporting, local text/script generation through Ollama, local speech preview through eSpeak NG / eSpeak, and SQLite job status persistence.

The backend also has a Stable Diffusion-compatible image adapter, procedural instrumental music, FFmpeg still-image video assembly, and MP4 audio/video muxing. These adapters are not equivalent to full AI video or AI music composition; see the media limitations below.

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

If MYTUBE_API_TOKEN is enabled, the browser client must be configured to send that token securely. Do not put a private server token in public frontend JavaScript or commit it to this repository. The current static client does not provide a secure token-management flow; leave this unset only for trusted local testing, not an exposed public service.

## Deployment notes

GitHub Pages can host static frontend files, but it cannot run this FastAPI/Ollama backend. A separately hosted backend is required for online generation. Ollama also needs compute, memory, and persistent storage; a free host may not provide enough resources or remain online. No public backend deployment is configured by this repository change.

## Verification

GitHub Actions checks Python compilation/import, JavaScript syntax, Docker Compose configuration, and Docker image build. These are build/syntax checks; they do not prove that Ollama, voice generation, or a deployed public service works end-to-end.

## Media generation adapters

The Media Lab tab connects to backend jobs for four production steps:

- **Images:** calls an AUTOMATIC1111-compatible Stable Diffusion WebUI API at `MYTUBE_IMAGE_API_URL` (default `http://127.0.0.1:7860`). Start that image service on the same backend host and enable its API before using image generation. Docker Compose points to a host-side API at `http://host.docker.internal:7860` by default; set `MYTUBE_IMAGE_API_URL` to override it. The stack does not download or start Stable Diffusion automatically; image models require substantial storage and compatible compute.
- **Video:** FFmpeg assembles selected generated still images into a simple 720p H.264 MP4 sequence. This is a slideshow-style motion pipeline, not text-to-video or character animation.
- **Music:** the backend synthesizes original mood-based instrumental audio as a WAV file. It is procedural background music, not a full AI song/vocal generator.
- **Final export:** FFmpeg muxes the assembled video and optional generated music into a single MP4 with AAC audio.

Generated files are stored in the backend asset directory and served from `/assets/`. The project browser stores generated asset filenames/URLs locally; back up your project data and keep the backend's generated_assets directory persistent.

Set `MYTUBE_IMAGE_API_URL` to the reachable Stable Diffusion API URL if it uses a different address. These media endpoints are intended for a trusted, private backend. Before exposing them publicly, add authentication to all job/media routes, request limits, storage quotas, and HTTPS. The existing static browser client does not yet have a secure private-token configuration flow.


### Important free-first limitations

- A compatible image model service must be installed and running on hardware you control. The project does not bundle multi-gigabyte model weights.
- The current video adapter is a still-image sequence assembler, not an AI video diffusion model. Real prompt-to-video or image-to-video generation requires a separate model runtime and substantial GPU memory.
- The current music adapter is a procedural synthesizer, not MusicGen or another neural music model. Full AI music generation likewise requires model weights and compute.
- FFmpeg final export is implemented as a muxing step; it does not generate animated scenes. The complete cinematic workflow is therefore not yet available end-to-end.
- Free-first means open-source/local software without per-generation API charges. It does not remove hardware, electricity, storage, or hosting requirements.
