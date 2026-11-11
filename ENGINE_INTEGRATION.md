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


## Frontend-to-backend connection (Release 2.15)

When the frontend is hosted on GitHub Pages, open a project and select **AI Engine**.
Enter the HTTPS forwarded URL for Codespaces port 8000 and choose **Save connection & test**.
The URL is stored in this browser and reused by all backend calls. GitHub Pages cannot
automatically discover a private Codespace's changing forwarded URL.

If `MYTUBE_API_TOKEN` is configured on the backend, enter the same token in the optional
frontend field. The browser stores that token in local storage on the current device; use
this only on a trusted personal device. The frontend sends the bearer token only to the
configured backend origin. The authenticated `/api/session` check validates it.

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


## Async provider polling contract (Release 1.7)

For video, speech and music, the configured endpoint receives `POST /generate`.
The JSON response must include a provider job identifier as `jobId`, `job_id`,
or `id` for asynchronous work. MyTube AI can then call `GET /jobs/{id}` using
the same base URL and bearer token. That response should contain a `status`
of `queued`, `processing`, `completed`, or `failed` (common aliases are
normalized). A completed response should include provider output metadata.

The MyTube endpoint `POST /api/jobs/{mytube_job_id}/refresh` refreshes a
submitted job's provider status. The provider must implement the contract;
this release does not invent provider-specific APIs or download arbitrary
URLs returned by a provider.
