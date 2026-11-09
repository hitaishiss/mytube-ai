# MyTube AI Release 2.1

## Individual Shorts rendering
- Each planned Short now accepts its own source video, start/end time range and 720p/1080p choice.
- The backend trims the selected range, center-crops to a vertical 9:16 frame, encodes H.264/AAC and adds the project's saved watermark.
- Each Short has its own render status and downloadable MP4 link.
- Uses FFmpeg and user-supplied/licensed footage; it does not create new AI-generated video.

## Requirements and limitations
- FFmpeg must be installed on the private backend.
- Upload a video clip for each Short and set the desired time range.
- Automatic scene generation still requires configured image/video providers and models.
- This release has not been deployed to the user's Codespace.
