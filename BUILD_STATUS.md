# Build status — 1.4.0

Verified in this build:
- Python syntax compilation for backend modules.
- JavaScript syntax check.
- FastAPI health route returns version 1.4.0.
- SRT subtitle endpoint smoke test returns correctly formatted timed captions.

Not verified / external dependencies:
- Live ComfyUI generation, video generation, TTS, or music generation (no provider credentials/services are bundled).
- Full production pipeline from script through generated media.
- Deployment to the user's GitHub Pages or Codespace.

This release adds backend job dispatch for configured media providers; it does not bundle model weights or claim those providers are active.
