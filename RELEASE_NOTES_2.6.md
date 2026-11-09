# Release 2.6

## Reliability improvement
- On backend startup, interrupted local text/production jobs left in `queued` or `processing` are now marked `failed` with a clear retry message.
- Provider-side jobs (`submitted`/`processing`) are not forcibly marked failed by this recovery step; their remote status can still be refreshed.
- Backend and health endpoint version updated to 2.6.0.

## Why this matters
Codespaces and other containers can stop or restart. Python background threads do not survive those restarts. Previously, local jobs could remain stuck in `processing` indefinitely. The startup recovery now makes the interruption visible and retryable rather than showing a false active state.

## Validation
- Python syntax compilation.
- JavaScript syntax check.
- Startup-recovery behavior tested against a temporary SQLite database.
- FastAPI route registration and archive integrity checked.

## Limitations
This does not make Codespaces always-on and does not resume a generation midway through an Ollama response. It marks interrupted local work honestly so it can be retried. Actual model availability and live deployment remain environment-dependent.
