MYTUBE AI — CONSOLIDATED RELEASE 1.0

This package supersedes the v0.5 files. It includes the existing studio UI and
backend plus the optional image/video/speech/music engine adapter routes.

IMPORTANT: This is an integration-ready release, not a bundle of AI models.
Text generation and FFmpeg rendering can run locally when their dependencies are
installed. Image generation requires a configured ComfyUI server and workflow.
Video, speech, and music require compatible private provider endpoints.

See ENGINE_INTEGRATION.md before configuring optional engines.
Keep API tokens in Codespaces secrets/environment variables, never in frontend files.
