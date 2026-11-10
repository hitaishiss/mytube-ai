# MyTube AI Release 2.12

## Provider media recovery and scene association
- Refreshing saved media jobs now also attempts to import completed video, voice, and music outputs into the local asset library.
- Imported provider assets are associated with the matching numbered scene in the saved production pack (`videoAssetId`, `voiceAssetId`, or `musicAssetId`).
- The association is persisted with the project, so the scene-to-asset mapping survives a browser refresh.
- Updated the service worker cache namespace and backend version to 2.12.0.

## Important boundaries
- This does not install or configure image, video, voice, or music generation models/providers.
- Media import requires the configured provider to implement the documented asynchronous job/output contract.
- Scene association records the asset IDs; it does not automatically assemble a complete film or guarantee that the provider output is a playable, correctly synchronized video.
