# MyTube AI Release 2.5

## Fixed
- Persisted ComfyUI image jobs can now be refreshed through the standard job refresh endpoint.
- Image job refresh reads ComfyUI history, records generated output metadata, and transitions jobs to processing/completed/failed.
- Completed ComfyUI image jobs can now import their first generated image into the managed MyTube asset library using the standard import-output endpoint.
- Imported image assets are stored with a validated PNG/JPEG/WebP extension and retain content type and size metadata.
- Backend version is 2.5.0.

## Validation
- Python compilation passed.
- JavaScript syntax check passed.
- FastAPI integration test passed for persisted image job refresh and generated-image import using mocked ComfyUI responses.
- Route registration: 27 routes.

## Still requires external setup
- A reachable ComfyUI server, installed image model, and valid API workflow.
- Working external video, speech, and music provider endpoints.
- Live Codespace deployment and end-to-end testing against the user's running services.
