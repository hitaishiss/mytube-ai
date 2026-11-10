# MyTube AI Release 2.9

## Reliability: bounded background execution
- Replaced unbounded per-request daemon threads with a shared ThreadPoolExecutor.
- Script, production, provider, full-render, and individual-Short jobs share a bounded worker pool.
- Default concurrency is 3 workers; configure MYTUBE_MAX_WORKERS from 1 to 8 according to available CPU/RAM.
- Backend and health version are aligned at 2.9.0.

## Why this matters
Large scene batches previously spawned one OS thread per task and could overwhelm a small Codespace. The bounded executor limits simultaneous work and queues remaining tasks.

## Limitations
The pending executor queue is in-process, not durable across restarts. Jobs interrupted by restart are marked failed by startup recovery and can be retried. This release does not install image/video/voice/music models; those still require configured providers and compute.
\n## Additional recovery hardening\n- Startup recovery now marks queued media tasks failed/retryable instead of leaving them queued forever.\n- Processing media tasks without a remote provider job identifier are marked failed; tasks with provider identifiers remain available for remote refresh.\n- Invalid MYTUBE_MAX_WORKERS values fall back safely to 3 workers.\n\n# Release 2.10\nBackend recovery hardening and safe worker configuration.\n