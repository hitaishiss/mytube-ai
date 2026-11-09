# MyTube AI Release 2.4

## Reliability and security hardening
- Hardened ComfyUI output retrieval against POSIX and Windows path traversal, null-byte metadata, and unsupported image types.
- Added a 100 MB cap and empty-response check when retrieving generated images, preventing unbounded image responses from exhausting backend memory.
- Made render failure-status reads explicit UTF-8 with a bounded response size.
- Updated backend version reporting to 2.4.0.

## Verification
- Python syntax compilation and JavaScript syntax checks.
- Security validation for malicious ComfyUI filename/subfolder metadata.
- FastAPI route registration and package integrity.

## Limits
- No image/video/TTS/music models or paid provider credentials are bundled.
- Actual model execution and live Codespace deployment require the user's configured backend environment and have not been verified here.
