# MyTube AI Release 2.3

## Fixes
- Corrected AI Engine health checks to use the configured backend base URL, matching the other frontend API calls. This matters when the frontend and private backend are hosted on different origins.
- Fixed the individual Shorts FFmpeg filter chain so the vertical scale/crop filter and watermark are applied together. Previously, a watermark could override the crop filter because FFmpeg received two `-vf` options.
- Updated the landing-page capability notice to accurately describe the included local text integration, optional media adapters and FFmpeg renderer without claiming unconfigured media models are available.
- Updated service-worker cache key to force clients to load the 2.3 frontend assets.
- Updated backend version reporting to 2.3.0.

## Verification
- Python syntax compilation: passed.
- JavaScript syntax check: passed.
- Standalone Shorts render with audio and watermark: passed; output verified as 720x1280.

## Remaining external dependencies
- Image generation requires ComfyUI, a model and a valid API workflow.
- Video, speech and music generation require compatible provider services and credentials.
- The private backend must be running and reachable from the frontend. This build environment cannot deploy to the user's GitHub/Codespace.
