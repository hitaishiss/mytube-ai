# MyTube AI Consolidated Release 1.3

## Changes
- Completed the ComfyUI image job lifecycle: submit workflow, poll job status,
  enumerate generated outputs, and securely proxy generated image bytes through
  the private MyTube backend.
- Renderer now mixes all supplied audio tracks instead of silently using only
  the first audio track.
- Image output proxy validates prompt IDs, filenames and subfolders.

## Image API
1. `POST /api/engines/image` with `{"prompt":"...","workflow":{...}}`
2. Poll `GET /api/engines/image/{prompt_id}`
3. Fetch image `GET /api/engines/image/{prompt_id}/output/{index}`

A ComfyUI server and installed model/workflow are still required. The workflow
must be in ComfyUI API format and include the nodes/models required to save images.

## Verification
Python compilation, JavaScript syntax, ZIP integrity, API route smoke tests,
and an FFmpeg test combining two audio inputs were run in the build environment.

## Not bundled
No image/video diffusion weights, TTS models, music models, or third-party API
credentials are bundled. Video, speech and music endpoints still require a
compatible provider implementing the documented private `/health` and `/generate`
contract. This release does not claim those models are installed.
