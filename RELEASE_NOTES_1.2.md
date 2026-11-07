# MyTube AI Release 1.2

## Completed in this pass
- Wired Smart Export to the backend: select and upload multiple video clips in playback order, optionally upload one audio track, submit an FFmpeg render, poll render status, and expose the MP4 download link.
- Added downloadable English and Chinese subtitle-draft text exports from the generated production pack.
- Corrected the overview copy so it no longer says all generation buttons are disconnected.
- Updated backend version reporting to 1.2.0.

## Verification performed
- Python compilation: passed.
- JavaScript syntax check: passed.
- Backend `/health`: HTTP 200.
- Media upload endpoint: HTTP 201.
- Render submission: HTTP 202.
- FFmpeg render: completed successfully using a generated sample clip.
- MP4 download: HTTP 200; output inspected with ffprobe (1.0 second duration).
- ZIP integrity: checked.

## Not available without additional engines
- AI image generation requires a running ComfyUI instance, model weights, and an API workflow.
- AI video generation requires a compatible video-generation model/provider and compute.
- Voice and music generation require compatible services/models.
- Subtitle exports are draft text files, not time-coded SRT/VTT captions; timing requires speech recognition/alignment against final audio.
- The backend does not yet automatically turn generated production-pack scene prompts into rendered shots. It can assemble clips that are supplied to Smart Export.

No external paid service is enabled and no API keys are bundled.
