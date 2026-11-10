# MyTube AI Release 2.13

## Full portable backup
- Added a backend full-backup endpoint that packages browser project data, a consistent SQLite jobs snapshot, uploaded/generated assets, and rendered exports into one ZIP.
- Added a **Full backup + media** action beside the existing lightweight project JSON export.
- Kept the existing JSON export/restore workflow intact.
- Uses SQLite's online backup API and excludes backup archives and temporary SQLite snapshots from the media payload to prevent recursive backups.

## Verification
- Python syntax compilation passed.
- JavaScript syntax check passed.
- Backend module import and route registration passed.
- Full-backup endpoint smoke test passed with a temporary database, project payload, asset and rendered-export fixture.
- ZIP integrity and expected archive contents passed.

## Limitations
- Full backup requires the private backend to be running and reachable from the studio.
- This creates a portable backup archive; it does not yet provide an in-app full-media restore workflow.
- AI media providers still require separately configured models/services.
