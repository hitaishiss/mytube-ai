# MyTube AI Release 2.0

## Production reliability updates
- Fixed the production queue result-scope bug that could break the final job summary.
- Media job IDs and latest states are saved into the browser project record while polling.
- Production Workflow displays the last saved media-job states.
- Added a backend retry endpoint that creates a fresh attempt from a failed job's original input without altering the failed record.
- Backend health reports version 2.0.0.

## Important limitations
- Image generation still needs ComfyUI, a compatible workflow and model.
- Video, voice and music require configured providers implementing the documented API contract.
- Browser project data is local to that browser; backend job records and media files remain on Codespace disk.
- This release has not been deployed to the user's Codespace.
