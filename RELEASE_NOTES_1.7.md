# MyTube AI Release 1.7

- Added asynchronous provider status polling for configured video, voice and music adapters.
- Added `POST /api/jobs/{job_id}/refresh` to update MyTube job state from provider status.
- Normalized common provider status aliases into queued/processing/completed/failed.
- Added provider contract documentation. Provider-specific asset download/ingest is still not standardized.

This does not bundle or configure media models/providers. A provider must implement the documented `/generate` and `/jobs/{id}` contract.
