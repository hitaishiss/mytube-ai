# MyTube AI Release 1.9

## Added
- Scene Planner can submit a scene image-generation job to ComfyUI.
- Generated images are polled, fetched through the private backend, uploaded into the project asset store, and linked to the scene.
- Character descriptions and Story Bible notes are included in the scene prompt to support continuity.
- Configure one ComfyUI API-format workflow in AI Engine and identify its positive text-encoder node; the workflow is saved with the local project.

## Setup requirement
- A reachable ComfyUI server with a loaded image model is required.
- Export a workflow from ComfyUI in API format. The configured node ID must be a positive CLIP text-encoder node with `inputs.text`.
- This integration generates scene still images only. It does not turn still images into video or generate voice/music.
