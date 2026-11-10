# MyTube AI — Release 2.7

## Engine health reporting correction
- AI Engine dashboard now distinguishes a provider URL being configured from the provider actually responding to its health check.
- Ollama status distinguishes an unreachable Ollama service from an online service where the selected model is not installed.
- Image, video, voice and music statuses no longer imply that an adapter is verified merely because a URL exists.
- Backend version is 2.7.0.

## Scope and limitations
- This release improves diagnostics; it does not bundle image/video/TTS/music models or create provider accounts.
- A provider marked connected has passed its `/health` check, not necessarily a full generation-and-output test.
