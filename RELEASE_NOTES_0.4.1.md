# MyTube AI 0.4.1 — API routing repair

- Fixed a routing-order bug: the root StaticFiles mount previously appeared before the voice POST endpoint and could intercept `/api/voice/generate`, returning 405.
- Consolidated duplicate voice handlers into one validated local eSpeak NG + FFmpeg endpoint.
- Health now reports local voice availability only when both required executables exist.
- Frontend voice capability text reflects actual local-engine availability.

## Still not connected
Image generation requires a configured ComfyUI server and workflow/model. AI video and music generation require real provider services and credentials or locally hosted models. FFmpeg provides editing/rendering, not AI video generation. This release does not claim those engines are connected.
