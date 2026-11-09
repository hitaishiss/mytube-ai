# Release 1.8

- Provider job refresh preserves provider job IDs and result payloads.
- Completed video, voice and music jobs can be imported into managed project assets.
- Production queue refreshes provider status and attempts media import after completion.
- Provider output contract: `GET /jobs/{id}/output` returns raw media with a supported audio/video Content-Type. The URL is derived from the private configured provider base; arbitrary provider-supplied URLs are not followed.

This does not bundle or configure media-generation models/providers. Providers must implement `/health`, `POST /generate`, `GET /jobs/{id}`, and `GET /jobs/{id}/output`.
