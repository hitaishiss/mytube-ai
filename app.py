import os, sqlite3, threading, uuid, json, time, shutil, subprocess, tempfile
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse, JSONResponse
from fastapi import UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = os.getenv("MYTUBE_DB_PATH", "mytube_jobs.sqlite3")
DATA_DIR = os.path.abspath(os.getenv("MYTUBE_DATA_DIR", "mytube_data"))
ASSET_DIR = os.path.join(DATA_DIR, "assets")
EXPORT_DIR = os.path.join(DATA_DIR, "exports")
os.makedirs(ASSET_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
MAX_UPLOAD_MB = int(os.getenv("MYTUBE_MAX_UPLOAD_MB", "500"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
TEXT_MODEL = os.getenv("MYTUBE_TEXT_MODEL", "qwen2.5:3b")
ALLOWED_ORIGINS = [x.strip() for x in os.getenv(
    "MYTUBE_ALLOWED_ORIGINS", "https://hitaishiss.github.io"
).split(",") if x.strip()]
APP_TOKEN = os.getenv("MYTUBE_API_TOKEN", "")

STUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app = FastAPI(title="MyTube AI private backend", version="2.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
db_lock = threading.Lock()
worker_lock = threading.Lock()

def now():
    return datetime.now(timezone.utc).isoformat()

def connect():
    c = sqlite3.connect(DB_PATH, timeout=30)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, kind TEXT NOT NULL,
            status TEXT NOT NULL, progress INTEGER NOT NULL, message TEXT NOT NULL,
            input_json TEXT NOT NULL, output_json TEXT, error TEXT,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )""")
init_db()

class JobIn(BaseModel):
    projectId: str = Field(min_length=1, max_length=120)
    kind: str = Field(pattern="^(text|production|image|video|voice|music)$")
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)

class ProductionQueueIn(BaseModel):
    projectId: str = Field(min_length=1, max_length=120)
    scenes: list[dict[str, Any]] = Field(min_length=1, max_length=100)
    characters: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    musicPrompt: str = Field(default="", max_length=8000)
    includeVoice: bool = True
    includeVideo: bool = True
    includeMusic: bool = True


def check_auth(authorization: str | None):
    if APP_TOKEN and authorization != f"Bearer {APP_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid backend token")

def ollama_status():
    try:
        req = Request(OLLAMA_URL.rstrip("/") + "/api/tags", headers={"Accept":"application/json"})
        with urlopen(req, timeout=2) as r:
            data=json.loads(r.read().decode("utf-8"))
        models=[m.get("name","") for m in data.get("models",[])]
        return {"available": True, "model": TEXT_MODEL, "installed": any(m == TEXT_MODEL or m.startswith(TEXT_MODEL + ":") for m in models)}
    except Exception:
        return {"available": False, "model": TEXT_MODEL, "installed": False}

def ollama_generate(prompt: str, system: str = "", progress_callback=None):
    payload = {
        "model": TEXT_MODEL, "prompt": prompt, "system": system,
        "stream": True, "keep_alive": "10m",
        "options": {"num_predict": 900, "num_ctx": 4096, "temperature": 0.7}
    }
    req = Request(OLLAMA_URL.rstrip("/") + "/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    parts = []
    try:
        with urlopen(req, timeout=900) as response:
            for line in response:
                if not line.strip():
                    continue
                item = json.loads(line.decode("utf-8"))
                if item.get("error"):
                    raise RuntimeError(item["error"])
                piece = item.get("response", "")
                if piece:
                    parts.append(piece)
                    if progress_callback:
                        progress_callback("".join(parts))
                if item.get("done"):
                    break
        result = "".join(parts).strip()
        if not result:
            raise RuntimeError("The local model returned an empty response.")
        return result
    except HTTPError as e:
        raise RuntimeError(f"Local model error ({e.code}): " + e.read().decode("utf-8", "replace")[:500])
    except URLError as e:
        raise RuntimeError("Cannot reach Ollama at " + OLLAMA_URL + ": " + str(e))

def update_job(job_id, **values):
    values["updated_at"]=now()
    cols=", ".join(f"{k}=?" for k in values)
    with connect() as c:
        c.execute(f"UPDATE jobs SET {cols} WHERE job_id=?", [*values.values(),job_id])

def run_job(job_id, kind, inp):
    try:
        update_job(job_id, status="processing", progress=5, message="Preparing generation…")
        prompt = str(inp.get("prompt") or inp.get("idea") or "").strip()
        if not prompt:
            raise RuntimeError("Add a prompt or story idea before generating.")
        if kind in ("image", "video", "voice", "music"):
            update_job(job_id, progress=15, message=f"Submitting {kind} request to configured engine…")
            if kind == "image":
                from backend.media_engines import comfyui_submit
                result = comfyui_submit(prompt, inp.get("workflow"))
            else:
                from backend.media_engines import configured_provider_submit
                env = {"video":"MYTUBE_VIDEO_API_URL", "voice":"MYTUBE_TTS_API_URL", "music":"MYTUBE_MUSIC_API_URL"}[kind]
                label = {"video":"Video", "voice":"Speech", "music":"Music"}[kind]
                result = configured_provider_submit(env, label, {"projectId": inp.get("projectId"), "prompt": prompt, "input": inp})
            update_job(job_id, status="submitted", progress=25,
                       message=f"{kind.title()} request accepted. Provider-side completion and asset retrieval are not yet standardized.",
                       output_json=json.dumps(result, ensure_ascii=False), error=None)
            return
        if kind not in ("text", "production"):
            raise RuntimeError(f"Unsupported job kind: {kind}")
        system = str(inp.get("system") or
            "You are MyTube AI's original drama-writing assistant. Write compelling "
            "scenes with clear motivations, natural dialogue and continuity.")
        update_job(job_id, progress=10, message="Connecting to local model…")
        # Throttle SQLite writes: Ollama can stream hundreds of small chunks.
        # Updating the jobs table for every chunk creates needless lock/IO pressure
        # and can interrupt long generations in constrained Codespaces.
        last_progress = {"chars": 0, "time": time.monotonic()}
        def on_piece(text):
            now_mono = time.monotonic()
            chars = len(text)
            if chars - last_progress["chars"] >= 600 or now_mono - last_progress["time"] >= 3:
                progress = min(95, 10 + chars // 100)
                update_job(job_id, progress=progress,
                           message=f"Generating script · {chars} characters received…")
                last_progress["chars"] = chars
                last_progress["time"] = now_mono
        result = ollama_generate(prompt, system, on_piece)
        # Persist final progress and output together only after Ollama completes.
        if kind == "production":
            try:
                structured = json.loads(result)
            except Exception:
                structured = {"production_notes": result, "format_warning": "Model did not return strict JSON."}
            output = {"production": structured, "text": result}
            message = "Production pack generated. Review before production."
        else:
            output = {"text": result}
            message = "Script generation completed."
        update_job(job_id, status="completed", progress=100,
                   message=message, output_json=json.dumps(output, ensure_ascii=False), error=None)
    except Exception as e:
        update_job(job_id, status="failed", progress=0,
                   message="Generation failed.", error=str(e))

def job_dict(row):
    d=dict(row)
    d["input"]=json.loads(d.pop("input_json"))
    d["output"]=json.loads(d.pop("output_json")) if d.get("output_json") else None
    d["jobId"]=d.pop("job_id"); d["projectId"]=d.pop("project_id")
    d["createdAt"]=d.pop("created_at"); d["updatedAt"]=d.pop("updated_at")
    return d

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(STUDIO_DIR, "index.html"))

@app.get("/health")
def health():
    from backend.media_engines import comfyui_status, provider_status
    local=ollama_status()
    ffmpeg=shutil.which("ffmpeg")
    image_status=comfyui_status()
    video_status=provider_status("MYTUBE_VIDEO_API_URL","Configured video provider")
    voice_status=provider_status("MYTUBE_TTS_API_URL","Configured speech provider")
    music_status=provider_status("MYTUBE_MUSIC_API_URL","Configured music provider")
    return {"status":"ok","engine":"MyTube AI","version":"2.0.0",
        "adapters":{
            "text":{"available":local["available"],"installed":local["installed"],"model":local["model"],"provider":"ollama"},
            "image":image_status,
            "video":video_status,
            "voice":voice_status,
            "music":music_status,
            "render":{"available":bool(ffmpeg),"provider":"ffmpeg" if ffmpeg else None}
        },"storage":{"assets":ASSET_DIR,"exports":EXPORT_DIR,"maxUploadMB":MAX_UPLOAD_MB}}

@app.post("/api/jobs", status_code=202)
def create_job(body: JobIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    job_id=str(uuid.uuid4()); stamp=now()
    with connect() as c:
        c.execute("""INSERT INTO jobs(job_id,project_id,kind,status,progress,message,input_json,
            output_json,error,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (job_id,body.projectId,body.kind,"queued",0,"Queued.",json.dumps(body.input),
             None,None,stamp,stamp))
    # One background thread per submitted job; SQLite persists job state across restarts.
    threading.Thread(target=run_job,args=(job_id,body.kind,body.input),daemon=True).start()
    with connect() as c:
        row=c.execute("SELECT * FROM jobs WHERE job_id=?",(job_id,)).fetchone()
    return job_dict(row)

@app.post("/api/production/queue", status_code=202)
def queue_production(body: ProductionQueueIn, authorization: str | None = Header(default=None)):
    """Queue scene-level media tasks; real generation requires configured providers."""
    check_auth(authorization)
    tasks=[]
    cast=json.dumps(body.characters,ensure_ascii=False)
    for index, scene in enumerate(body.scenes,1):
        label=str(scene.get("slugline") or scene.get("title") or f"Scene {index}")[:180]
        visual=str(scene.get("visual_prompt") or scene.get("action") or scene.get("description") or "").strip()
        dialogue=str(scene.get("dialogue_summary") or scene.get("dialogue") or "").strip()
        if body.includeVideo and visual:
            tasks.append(("video",{"prompt":f"Cinematic scene: {label}. Visual direction: {visual}. Camera: {scene.get('camera','cinematic')}. Lighting: {scene.get('lighting','story-appropriate')}. Cast continuity: {cast}","sceneNumber":index}))
        if body.includeVoice and dialogue:
            tasks.append(("voice",{"prompt":f"Generate dialogue audio for {label}. Dialogue: {dialogue}. Voice directions: {cast}","sceneNumber":index}))
    if body.includeMusic and body.musicPrompt.strip():
        tasks.append(("music",{"prompt":body.musicPrompt.strip(),"scope":"project soundtrack"}))
    if not tasks:
        raise HTTPException(status_code=422,detail="No usable scene visual prompts, dialogue, or music brief were found.")
    stamp=now(); jobs=[]
    with connect() as c:
        for kind,payload in tasks:
            jid=str(uuid.uuid4()); inp={**payload,"projectId":body.projectId}
            c.execute("INSERT INTO jobs(job_id,project_id,kind,status,progress,message,input_json,output_json,error,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (jid,body.projectId,kind,"queued",0,"Queued by production orchestrator.",json.dumps(inp,ensure_ascii=False),None,None,stamp,stamp))
            jobs.append({"jobId":jid,"kind":kind,"sceneNumber":payload.get("sceneNumber")})
    for job in jobs:
        with connect() as c: row=c.execute("SELECT input_json FROM jobs WHERE job_id=?",(job["jobId"],)).fetchone()
        threading.Thread(target=run_job,args=(job["jobId"],job["kind"],json.loads(row["input_json"])),daemon=True).start()
    return {"projectId":body.projectId,"queued":len(jobs),"jobs":jobs,"message":"Queued jobs. Provider acceptance is not the same as completed media; inspect each job status."}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    with connect() as c:
        row=c.execute("SELECT * FROM jobs WHERE job_id=?",(job_id,)).fetchone()
    if not row: raise HTTPException(status_code=404,detail="Job not found")
    return job_dict(row)


@app.post("/api/jobs/{job_id}/retry", status_code=202)
def retry_job(job_id: str, authorization: str | None = Header(default=None)):
    """Create a fresh attempt from a failed job's original input."""
    check_auth(authorization)
    with connect() as c:
        old = c.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    if not old:
        raise HTTPException(status_code=404, detail="Job not found")
    if old["status"] != "failed":
        raise HTTPException(status_code=409, detail="Only failed jobs can be retried")
    new_id = str(uuid.uuid4())
    stamp = now()
    with connect() as c:
        c.execute("""INSERT INTO jobs(job_id,project_id,kind,status,progress,message,input_json,
            output_json,error,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (new_id, old["project_id"], old["kind"], "queued", 0,
             "Retry queued from failed job.", old["input_json"], None, None, stamp, stamp))
        row = c.execute("SELECT * FROM jobs WHERE job_id=?", (new_id,)).fetchone()
    inp = json.loads(old["input_json"] or "{}")
    threading.Thread(target=run_job, args=(new_id, old["kind"], inp), daemon=True).start()
    return job_dict(row)


@app.post("/api/jobs/{job_id}/refresh")
def refresh_job(job_id: str, authorization: str | None = Header(default=None)):
    """Refresh submitted video, speech or music jobs using GET /jobs/{id}."""
    check_auth(authorization)
    with connect() as c:
        row = c.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    current = job_dict(row)
    if current["status"] not in ("submitted", "processing", "queued"):
        return current
    kind = current["kind"]
    env_name = {"video":"MYTUBE_VIDEO_API_URL", "voice":"MYTUBE_TTS_API_URL",
                "music":"MYTUBE_MUSIC_API_URL"}.get(kind)
    if not env_name:
        return current
    provider_result = (current.get("output") or {}).get("result") or {}
    provider_id = provider_result.get("jobId") or provider_result.get("job_id") or provider_result.get("id")
    if not provider_id:
        return current
    try:
        from backend.media_engines import configured_provider_poll
        polled = configured_provider_poll(env_name, kind.title(), provider_id)
        state = polled["status"]
        progress = 100 if state == "completed" else (0 if state == "queued" else 75)
        message = {"queued":"Provider job is queued.", "processing":"Provider job is running.",
                   "completed":"Provider job completed.", "failed":"Provider job failed."}[state]
        refreshed_output = {**(current.get("output") or {}),
                            "providerStatus": state, "providerResult": polled.get("result", {})}
        with connect() as c:
            c.execute("UPDATE jobs SET status=?,progress=?,message=?,output_json=?,error=?,updated_at=? WHERE job_id=?",
                      (state, progress, message, json.dumps(refreshed_output, ensure_ascii=False),
                       str(polled["result"].get("error", "")) if state == "failed" else None, now(), job_id))
            fresh = c.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        return job_dict(fresh)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Provider status check failed: {str(e)[:240]}")


@app.post("/api/jobs/{job_id}/import-output")
def import_provider_output(job_id: str, authorization: str | None = Header(default=None)):
    """Import a completed provider media file into MyTube's managed asset store."""
    check_auth(authorization)
    with connect() as c:
        row = c.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    current = job_dict(row)
    if current["status"] != "completed":
        raise HTTPException(status_code=409, detail="Provider job is not completed")
    if (current.get("output") or {}).get("assetId"):
        return {"assetId": current["output"]["assetId"], "status": "imported"}
    kind = current["kind"]
    env_name = {"video":"MYTUBE_VIDEO_API_URL", "voice":"MYTUBE_TTS_API_URL", "music":"MYTUBE_MUSIC_API_URL"}.get(kind)
    if not env_name:
        raise HTTPException(status_code=400, detail="This job kind does not use a downloadable media provider")
    result = (current.get("output") or {}).get("result") or {}
    provider_id = result.get("jobId") or result.get("job_id") or result.get("id")
    if not provider_id:
        raise HTTPException(status_code=502, detail="Provider job ID is missing; cannot retrieve its output")
    try:
        from backend.media_engines import configured_provider_fetch_output
        data, content_type, ext = configured_provider_fetch_output(env_name, kind.title(), provider_id)
        name = uuid.uuid4().hex + ext
        with open(os.path.join(ASSET_DIR, name), "wb") as out:
            out.write(data)
        output = {**(current.get("output") or {}), "assetId": name, "assetContentType": content_type, "assetSize": len(data)}
        update_job(job_id, output_json=json.dumps(output, ensure_ascii=False), message="Provider media imported into project assets.")
        return {"assetId": name, "contentType": content_type, "size": len(data), "status": "imported"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not import provider output: {str(e)[:240]}")


@app.get("/api/jobs")
def list_jobs(projectId: str | None = None, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    with connect() as c:
        if projectId:
            rows=c.execute("SELECT * FROM jobs WHERE project_id=? ORDER BY created_at DESC LIMIT 100",(projectId,)).fetchall()
        else:
            rows=c.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100").fetchall()
    return [job_dict(r) for r in rows]


class SubtitleCue(BaseModel):
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    text: str = Field(min_length=1, max_length=2000)

class SubtitleIn(BaseModel):
    cues: list[SubtitleCue] = Field(min_length=1, max_length=2000)
    format: str = Field(default="srt", pattern="^(srt|vtt)$")

@app.post("/api/subtitles")
def create_subtitles(body: SubtitleIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    def stamp(seconds, comma=True):
        ms = max(0, int(round(seconds * 1000)))
        h, rem = divmod(ms, 3600000); m, rem = divmod(rem, 60000); sec, milli = divmod(rem, 1000)
        sep = "," if comma else "."
        return f"{h:02d}:{m:02d}:{sec:02d}{sep}{milli:03d}"
    rows = []
    if body.format == "vtt": rows.append("WEBVTT\n")
    for i, cue in enumerate(body.cues, 1):
        if cue.end <= cue.start: raise HTTPException(status_code=422, detail=f"Cue {i} end must be after start.")
        rows.extend(([str(i)] if body.format == "srt" else []) +
                    [f"{stamp(cue.start, body.format == 'srt')} --> {stamp(cue.end, body.format == 'srt')}", cue.text.strip(), ""])
    return {"format": body.format, "content": "\n".join(rows), "cueCount": len(body.cues)}


class RenderIn(BaseModel):
    projectId: str = Field(min_length=1, max_length=120)
    clips: list[str] = Field(min_length=1, max_length=500)
    audioTracks: list[str] = Field(default_factory=list, max_length=8)
    resolution: str = Field(default="1080p", pattern="^(720p|1080p|4K)$")
    fps: int = Field(default=30, ge=24, le=60)
    preset: str = Field(default="Balanced", pattern="^(High Quality|Balanced|Smaller File)$")
    watermark: str = Field(default="", max_length=100)
    watermarkPosition: str = Field(default="Bottom right", pattern="^(Bottom right|Bottom left|Top right|Top left|Center)$")
    aspectRatio: str = Field(default="16:9", pattern="^(16:9|9:16)$")


def safe_asset(name: str) -> str:
    # API accepts only filenames returned by /api/assets, never arbitrary paths.
    if not name or os.path.basename(name) != name or name.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid asset name")
    path=os.path.realpath(os.path.join(ASSET_DIR,name))
    if os.path.commonpath([path,os.path.realpath(ASSET_DIR)]) != os.path.realpath(ASSET_DIR) or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Asset not found")
    return path


@app.post("/api/assets", status_code=201)
async def upload_asset(projectId: str = Form(...), file: UploadFile = File(...), authorization: str | None = Header(default=None)):
    check_auth(authorization)
    if len(projectId) > 120 or not projectId.strip(): raise HTTPException(status_code=400, detail="Invalid project ID")
    original=os.path.basename(file.filename or "upload.bin")
    ext=os.path.splitext(original)[1].lower()
    allowed={".mp4", ".mov", ".mkv", ".webm", ".mp3", ".wav", ".m4a", ".aac", ".png", ".jpg", ".jpeg", ".webp", ".srt", ".vtt"}
    if ext not in allowed: raise HTTPException(status_code=415, detail="Unsupported media type")
    name=f"{uuid.uuid4().hex}{ext}"; dest=os.path.join(ASSET_DIR,name); total=0
    try:
        with open(dest,"wb") as out:
            while chunk:=await file.read(1024*1024):
                total+=len(chunk)
                if total > MAX_UPLOAD_MB*1024*1024: raise HTTPException(status_code=413, detail=f"Upload exceeds {MAX_UPLOAD_MB} MB")
                out.write(chunk)
    except Exception:
        if os.path.exists(dest): os.remove(dest)
        raise
    return {"assetId":name,"filename":original,"size":total,"projectId":projectId}


@app.get("/api/assets/{name}")
def download_asset(name: str, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    return FileResponse(safe_asset(name), filename=name)


@app.post("/api/render", status_code=202)
def render_video(body: RenderIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    if not shutil.which("ffmpeg"): raise HTTPException(status_code=503, detail="FFmpeg is not installed on this host")
    clips=[safe_asset(x) for x in body.clips]
    audios=[safe_asset(x) for x in body.audioTracks]
    render_id=uuid.uuid4().hex
    output=os.path.join(EXPORT_DIR, f"{render_id}.mp4")
    threading.Thread(target=_render_worker,args=(clips,audios,body,output),daemon=True).start()
    return {"renderId":render_id,"status":"processing","message":"Render started"}


def _render_worker(clips, audios, body, output):
    # Normalize and concatenate clips; mix all selected audio tracks.
    work=tempfile.mkdtemp(prefix="mytube-render-")
    try:
        dimensions = {"720p":(1280,720),"1080p":(1920,1080),"4K":(3840,2160)} if body.aspectRatio == "16:9" else {"720p":(720,1280),"1080p":(1080,1920),"4K":(2160,3840)}
        w,h=dimensions[body.resolution]
        normalized=[]
        for i,clip in enumerate(clips):
            target=os.path.join(work,f"clip-{i:04d}.mp4")
            vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2" if body.aspectRatio == "16:9" else f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}") + f",setsar=1,fps={body.fps}"
            cmd=["ffmpeg","-y","-i",clip,"-vf",vf,"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-an",target]
            subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=7200)
            normalized.append(target)
        concat=os.path.join(work,"concat.txt")
        with open(concat,"w") as f:
            for item in normalized: f.write("file '"+item.replace("'","'\''")+"'\n")
        merged=os.path.join(work,"merged.mp4")
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c","copy",merged],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=7200)
        cmd=["ffmpeg","-y","-i",merged]
        for audio in audios:
            cmd += ["-i",audio]
        if body.watermark:
            # Escape drawtext metacharacters; never interpret user text as a filter expression.
            txt=body.watermark.replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%")
            positions = {"Bottom right": ("w-tw-24", "h-th-24"), "Bottom left": ("24", "h-th-24"), "Top right": ("w-tw-24", "24"), "Top left": ("24", "24"), "Center": ("(w-tw)/2", "(h-th)/2")}
            wx, wy = positions[body.watermarkPosition]
            cmd += ["-vf",f"drawtext=text='{txt}':x={wx}:y={wy}:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.45"]
        cmd += ["-c:v","libx264","-preset","medium" if body.preset=="High Quality" else "veryfast","-crf","18" if body.preset=="High Quality" else "23" if body.preset=="Balanced" else "28"]
        if audios:
            audio_inputs="".join(f"[{i+1}:a:0]" for i in range(len(audios)))
            filter_complex=audio_inputs+f"amix=inputs={len(audios)}:duration=longest:dropout_transition=2[aout]"
            cmd += ["-filter_complex",filter_complex,"-map","0:v:0","-map","[aout]","-c:a","aac","-b:a","192k"]
        else:
            cmd += ["-an"]
        cmd += ["-movflags","+faststart",output]
        subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=7200)
    except Exception as exc:
        with open(output+".error","w") as f: f.write(str(exc)[:2000])
    finally:
        shutil.rmtree(work,ignore_errors=True)


@app.get("/api/render/{render_id}")
def render_status(render_id: str, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    if not render_id.isalnum(): raise HTTPException(status_code=400,detail="Invalid render ID")
    path=os.path.join(EXPORT_DIR,render_id+".mp4")
    err=path+".error"
    if os.path.isfile(path): return {"renderId":render_id,"status":"completed","downloadUrl":f"/api/render/{render_id}/download"}
    if os.path.isfile(err): return {"renderId":render_id,"status":"failed","error":open(err).read()}
    return {"renderId":render_id,"status":"processing"}


@app.get("/api/render/{render_id}/download")
def render_download(render_id: str, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    if not render_id.isalnum(): raise HTTPException(status_code=400,detail="Invalid render ID")
    path=os.path.join(EXPORT_DIR,render_id+".mp4")
    if not os.path.isfile(path): raise HTTPException(status_code=404,detail="Render is not ready")
    return FileResponse(path,media_type="video/mp4",filename="mytube-export.mp4")


class ShortRenderIn(BaseModel):
    projectId: str = Field(min_length=1, max_length=120)
    assetId: str = Field(min_length=1, max_length=180)
    startSeconds: float = Field(default=0, ge=0)
    endSeconds: float = Field(gt=0)
    resolution: str = Field(default="1080p", pattern="^(720p|1080p)$")
    watermark: str = Field(default="", max_length=100)


@app.post("/api/shorts/render", status_code=202)
def render_short(body: ShortRenderIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    if not shutil.which("ffmpeg"):
        raise HTTPException(status_code=503, detail="FFmpeg is not installed on this host")
    if body.endSeconds <= body.startSeconds:
        raise HTTPException(status_code=422, detail="End time must be greater than start time")
    source = safe_asset(body.assetId)
    render_id = uuid.uuid4().hex
    output = os.path.join(EXPORT_DIR, render_id + ".mp4")
    threading.Thread(target=_short_render_worker, args=(source, body, output), daemon=True).start()
    return {"renderId": render_id, "status": "processing", "format": "9:16"}


def _short_render_worker(source, body, output):
    try:
        w, h = (720, 1280) if body.resolution == "720p" else (1080, 1920)
        duration = body.endSeconds - body.startSeconds
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"
        cmd = ["ffmpeg", "-y", "-ss", str(body.startSeconds), "-i", source,
               "-t", str(duration), "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
               "-movflags", "+faststart"]
        if body.watermark:
            txt = body.watermark.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")
            cmd += ["-vf", vf + f",drawtext=text='{txt}':x=w-tw-24:y=h-th-24:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.45"]
        cmd.append(output)
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=7200)
    except Exception as exc:
        with open(output + ".error", "w", encoding="utf-8") as f:
            f.write(str(exc)[:1000])


class ImageIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    workflow: dict[str, Any] = Field(default_factory=dict)

class ProviderIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    projectId: str = Field(min_length=1, max_length=120)
    options: dict[str, Any] = Field(default_factory=dict)

@app.post("/api/engines/image")
def generate_image(body: ImageIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    from backend.media_engines import comfyui_submit
    try: return comfyui_submit(body.prompt, body.workflow)
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))

@app.get("/api/engines/image/{prompt_id}")
def image_job_status(prompt_id: str, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    from backend.media_engines import comfyui_history
    try:
        history = comfyui_history(prompt_id)
        item = history.get(prompt_id)
        if not item:
            return {"promptId":prompt_id,"status":"processing","outputs":[]}
        outputs=[]
        for node_id, node in (item.get("outputs") or {}).items():
            for image_item in node.get("images",[]):
                outputs.append({"nodeId":node_id,"filename":image_item.get("filename"),
                    "subfolder":image_item.get("subfolder",""),"type":image_item.get("type","output")})
        status = item.get("status",{})
        completed = bool(status.get("completed")) or bool(outputs)
        return {"promptId":prompt_id,"status":"completed" if completed else "processing",
                "outputs":outputs,"messages":status.get("messages",[])}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/api/engines/image/{prompt_id}/output/{index}")
def image_job_output(prompt_id: str, index: int, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    from backend.media_engines import comfyui_history, comfyui_fetch_image
    from fastapi.responses import Response
    try:
        history = comfyui_history(prompt_id)
        item = history.get(prompt_id)
        if not item: raise HTTPException(status_code=404, detail="Image job is not complete.")
        outputs=[]
        for node_id, node in (item.get("outputs") or {}).items():
            for image_item in node.get("images",[]):
                outputs.append(image_item)
        if index < 0 or index >= len(outputs): raise HTTPException(status_code=404, detail="Image output not found.")
        image_item=outputs[index]
        content, content_type = comfyui_fetch_image(image_item.get("filename",""),
            image_item.get("subfolder",""), image_item.get("type","output"))
        return Response(content=content, media_type=content_type,
            headers={"Content-Disposition":'inline; filename="mytube-generated-image"'})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/api/engines/video")
def generate_video(body: ProviderIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    from backend.media_engines import configured_provider_submit
    try: return configured_provider_submit("MYTUBE_VIDEO_API_URL","Video",body.model_dump())
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))

@app.post("/api/engines/voice")
def generate_voice(body: ProviderIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    from backend.media_engines import configured_provider_submit
    try: return configured_provider_submit("MYTUBE_TTS_API_URL","Speech",body.model_dump())
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))

@app.post("/api/engines/music")
def generate_music(body: ProviderIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    from backend.media_engines import configured_provider_submit
    try: return configured_provider_submit("MYTUBE_MUSIC_API_URL","Music",body.model_dump())
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))

# Serve CSS, JS, icons and manifest after explicit API routes.
app.mount("/", StaticFiles(directory=STUDIO_DIR, html=True), name="studio")
