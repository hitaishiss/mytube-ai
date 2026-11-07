# MyTube AI 1.4

## Implemented
- Backend job runner now dispatches image jobs to ComfyUI using a supplied API-format workflow.
- Backend job runner now dispatches video, speech and music jobs to configured provider `/generate` adapters.
- Media job results and failures are persisted in the existing SQLite job history.
- Added `/api/subtitles` to generate validated SRT or WebVTT files from supplied timed cues.
- Backend version reports 1.4.0.

## Still requires external components
- Image jobs require a reachable ComfyUI instance, installed model(s), and a valid API-format workflow.
- Video, speech and music jobs require compatible private provider endpoints and credentials.
- Subtitle timing must come from supplied timestamps; this endpoint does not perform speech recognition or forced alignment.
- The frontend does not yet provide full scene-by-scene media job controls. A configured endpoint alone is not proof that a model is installed or generation will succeed.
