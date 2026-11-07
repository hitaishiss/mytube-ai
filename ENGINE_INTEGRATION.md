# MyTube AI — Engine integration contract

This release consolidates the existing studio, Ollama text jobs, persistent media
uploads, FFmpeg MP4 rendering, and optional generation-engine adapters.

## What works in this package
- Local Ollama script generation with throttled progress persistence.
- SQLite job history and persistent asset/export directories.
- Upload/download of video, audio, image, and subtitle assets.
- FFmpeg video concatenation, audio muxing, watermarking, and MP4 export.
- Engine health reporting that distinguishes a reachable engine from a configured URL.
- ComfyUI image workflow submission when a ComfyUI server and API workflow are supplied.
- Video, speech, and music provider adapters using the contract below.

## Provider contract (video, speech, music)
Set the matching private environment variable on the backend:
`MYTUBE_VIDEO_API_URL`, `MYTUBE_TTS_API_URL`, or `MYTUBE_MUSIC_API_URL`.
Optional bearer tokens use the corresponding `_TOKEN` variable.

The service must implement:
- `GET /health` returning JSON with `{"status":"ok"}` (or `ready`, `healthy`, or `available:true`)
- `POST /generate` accepting `{"prompt":"...","projectId":"...","options":{...}}`
  and returning JSON describing the generated result.

The adapter intentionally does not guess vendor-specific API formats. It will not
claim generation works just because a URL is present.

## Image generation
Set `COMFYUI_URL` to a reachable ComfyUI server. POST `/api/engines/image` with
a ComfyUI API-format workflow JSON object. The workflow must reference models and
nodes installed on that ComfyUI server. This package does not bundle image models.

## Important limits
- Codespaces is not guaranteed to be always-on; its public forwarded URL can change.
- The free Codespace CPU/RAM/storage may be insufficient for image/video diffusion.
- Actual generative video and music require a compatible model/provider and compute.
- FFmpeg rendering is editing/encoding, not AI video generation.
- Do not put provider secrets in the GitHub Pages frontend or commit them to Git.
- No paid provider is enabled by default. No billing is initiated by this package.
