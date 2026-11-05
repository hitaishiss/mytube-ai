MYTUBE AI — FOUNDATION BUILD 1

WHAT THIS VERSION DOES
- Mobile-first, installable web app foundation.
- Create drama projects from a title or a free-form idea.
- Save projects locally in the browser using IndexedDB.
- Rename, archive, restore, move to trash, and permanently delete projects.
- Recently deleted projects can be restored (the interface describes a 30-day recovery period; automatic expiry cleanup is not yet implemented in this first build).
- Export and import JSON backups.
- Dark theme by default, with optional light theme.
- Basic offline app shell after first successful load.

IMPORTANT LIMITATIONS
- This is the first foundation build, not the complete AI drama generator.
- AI text, image, voice and video generation are not connected yet.
- YouTube URL analysis and video upload analysis are not implemented yet.
- The project data is stored in this browser on this device. Clearing browser/site data or uninstalling may erase it. Export backups regularly.
- The app must be served from HTTPS or localhost for PWA installation and service workers. Opening index.html directly as a file may not enable install/offline features.
- Google Fonts are optional styling; the app itself does not depend on them for its core layout.
- Full video generation requires external generation services and may have quotas/costs.

ANDROID SETUP
1. Extract this ZIP on a computer or use a hosting service that can publish a static website.
2. Publish the contents of this folder to an HTTPS static host.
3. Open the resulting HTTPS address in Chrome on Android.
4. In Chrome, open the menu (⋮) and choose "Install app" or "Add to Home screen" if offered.
5. Open MyTube AI from the new home-screen icon.
6. Create a test project, then use Backup & restore → Export backup.

Do not share private backup files publicly.
