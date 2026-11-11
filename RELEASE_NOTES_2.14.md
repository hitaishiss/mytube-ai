# MyTube AI Release 2.14

## Full backup restore
- Added an in-app full ZIP backup restore workflow.
- Restores browser projects and adds missing uploaded/generated assets and rendered exports.
- Preserves existing media files and the current jobs database; it does not overwrite active backend job history.
- Validates the MyTube AI manifest, ZIP paths, duplicate entries, symbolic links, file count, compressed upload size and expanded size before importing.
- Retains the existing JSON-only project restore.

## Verification
- Python syntax compilation and backend import passed.
- JavaScript syntax check passed.
- Restore endpoint tested with a fixture archive containing projects, assets, exports and a jobs snapshot.
- Path traversal, duplicate entry and invalid archive rejection tested.
- ZIP integrity passed.

## Limitations
- Full restore requires the private backend to be running and reachable.
- Existing same-named media files are preserved rather than overwritten.
- Jobs database snapshots are retained in the backup for safekeeping but are not installed over the active database.
- Actual media generation still requires configured providers/models.
