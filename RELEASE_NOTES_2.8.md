# MyTube AI — Release 2.8

## Persistent scene-image generation
- Scene image generation now creates a durable backend image job instead of submitting directly to ComfyUI from the browser.
- The scene stores its backend job ID and status in the project, so navigation or a page reload does not lose the job reference.
- Scene image jobs use the existing job refresh and import-output endpoints.
- Completed ComfyUI outputs are imported into the managed asset library and linked to the scene.
- Added a per-scene refresh action for unfinished image jobs.

## Validation and limitations
- Python and JavaScript syntax checks passed in the build environment.
- Backend lifecycle was tested using mocked ComfyUI responses; this does not prove a live ComfyUI model is installed or reachable.
- Actual image generation still requires a configured ComfyUI server, installed models, and a valid API workflow.
- No live Codespace deployment was performed.
