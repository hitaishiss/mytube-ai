MyTube AI Consolidated Release 1.1

Implemented:
- Local Ollama text generation and saved jobs
- Production Workflow tab: script-to-production-pack generation
- Story/cast continuity notes, scene breakdowns, visual prompts, audio cues, five Shorts concepts, bilingual subtitle draft fields
- Persistent media upload/download
- FFmpeg MP4 assembly, audio muxing, watermark and export status
- Engine capability reporting and optional ComfyUI/provider adapters
- Browser project backup/restore

Verified here:
- Python and JavaScript syntax
- FastAPI health
- Upload -> FFmpeg render -> status -> MP4 download
- Production job API acceptance
- ZIP integrity

Not bundled/claimed active:
- Image/video/TTS/music model weights or services
- External provider credentials
- Live Codespace deployment verification
- Fully automated generated-media pipeline
