# MyTube AI Release 1.6

- Added a single production-queue endpoint that creates per-scene video jobs, per-scene dialogue voice jobs, and an optional project music job.
- Added a Production Workflow control to submit those jobs and watch their backend statuses.
- Production-pack Shorts are now copied into the project's Shorts planner for editing.
- Provider acceptance is now reported as `submitted`, not `completed`. This avoids falsely claiming a generated media file exists when a provider only acknowledges a request.

## Important
The generic provider contract still needs a compatible provider implementation and private backend configuration. This release does not bundle video, TTS, or music models, and does not standardize provider-specific result polling/download. A `submitted` job means accepted for processing, not that the final asset is ready.
