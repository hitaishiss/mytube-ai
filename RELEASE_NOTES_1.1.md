# MyTube AI Consolidated Release 1.1

## Added in this release
- New **Production Workflow** tab.
- A production-pack job that uses the existing local Ollama text model to turn a saved script and Story Bible into structured JSON containing a logline, cast continuity notes, scene breakdowns, visual prompts, camera/lighting direction, audio cues, five Shorts concepts, and English/Chinese subtitle draft fields.
- Production packs are saved with the browser project after successful generation.
- Updated Smart Export copy to correctly describe the backend FFmpeg renderer rather than claiming it is absent.
- Backend job validation now accepts `production` jobs.

## Verified in this build environment
- Python syntax compilation.
- JavaScript syntax check.
- FastAPI health endpoint.
- Media upload endpoint.
- Real FFmpeg render of a sample clip.
- Render status polling.
- MP4 download endpoint.
- Production job submission/validation.
- ZIP integrity.

## Still requires external engines/resources
- AI image generation requires a configured ComfyUI server, installed model and workflow.
- AI video generation requires a compatible video model/provider.
- Speech and music generation require compatible services/models.
- The production pack creates plans/prompts/subtitle drafts; it does not itself create image/video/audio files or translate subtitle drafts with guaranteed accuracy.
- Full live deployment and Ollama generation cannot be verified from this build environment.

No paid service is enabled by default. Provider credentials belong only in private backend environment variables.
