MYTUBE AI — RELEASE 1.6

This is a private, self-hosted studio. Extract this package into your existing Codespace repository, replacing the matching app files, then run your existing start.sh.

The local Ollama text model powers script and production-pack drafts. The Production Workflow can queue scene video, dialogue voice and soundtrack jobs when compatible providers are configured in the backend environment. Provider acceptance is not the same as a finished media asset.

FFmpeg can assemble uploaded/authorized clips and audio into MP4, including 9:16 vertical output. This renderer does not generate video from text.

Do not put API keys in app.js or commit them. Configure secrets only in the private backend environment. No paid provider is enabled by default.

See BUILD_STATUS.md and ENGINE_INTEGRATION.md for exact capabilities and dependencies.

Release 1.8 adds automatic polling and import of completed media from configured providers. Providers must implement GET /jobs/{id}/output returning raw supported media. See RELEASE_NOTES_1.8.md.


RELEASE 1.9: To generate scene stills, start ComfyUI on a reachable host, export a workflow in API format, open MyTube AI → AI Engine, paste the JSON, enter the positive CLIPTextEncode node ID, and save. Then open Scenes and choose Generate scene image. No image model is bundled.

Release 2.0 adds media queue status persistence and failed-job retry. See RELEASE_NOTES_2.0.md and BUILD_STATUS.md.

Release 2.1 adds per-Short 9:16 MP4 trimming/rendering from uploaded video clips. See RELEASE_NOTES_2.1.md and BUILD_STATUS.md.

Release 2.4: security hardening for ComfyUI output retrieval and bounded render error reporting. See RELEASE_NOTES_2.4.md.
