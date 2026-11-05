MYTUBE AI ENGINE BRIDGE

This package adds a secure-backend connection screen and a health check.

Expected backend:
GET /health
Response: {"status":"ok"}

Future job API contract:
POST /api/jobs with JSON {projectId, kind, input, output}
GET /api/jobs/{jobId} for queued/running/complete/failed status.
The backend must store provider credentials as environment variables, authenticate requests, restrict CORS to your GitHub Pages origin, and implement provider-specific adapters.

This package DOES NOT generate AI media yet. It does not submit jobs or render files. A real backend and model adapters are still required. Do not put API keys in this public repository or in browser storage.

No third-party quota can be guaranteed away unless models run on hardware you control. Local compute still has speed, memory, storage and electricity limits. A phone is not suitable for unlimited long-form cinematic video generation.
