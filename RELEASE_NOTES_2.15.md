# MyTube AI Release 2.15

## Private backend connection setup
- Added a saved backend URL and optional backend access-token field in the AI Engine tab.
- The URL is persisted locally on the current browser/device and reused by script, production, media, upload, backup, restore and render requests.
- GitHub Pages no longer silently targets its own `github.io` origin when no Codespace URL has been saved; the connection panel explains what is missing.
- Optional bearer tokens are attached only to requests targeting the configured backend origin. Tokens are stored in this browser's local storage; use only on a trusted personal device.
- Image previews and media downloads now fetch through the authenticated backend connection, so optional token protection does not break protected media links.
- Added authenticated `/api/session` probe so the UI can distinguish an online backend from a missing/incorrect access token.
- Remote backends require HTTPS; HTTP is permitted only for localhost.

## Verification
- Python syntax compilation, JavaScript syntax check, backend import and route inspection.
- Authenticated session route tested with token disabled and enabled; invalid/missing token rejected when enabled.
- Frontend config persistence and URL validation inspected with automated JS checks.
- ZIP integrity checked.

## Remaining external requirements
- The Codespace's actual forwarded port 8000 address must be entered once in AI Engine because GitHub Pages cannot discover a private Codespace URL automatically.
- Actual image/video/voice/music engines still require compatible models/providers and compute.
