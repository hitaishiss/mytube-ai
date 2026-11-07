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
app = FastAPI(title="MyTube AI private backend", version="0.3.0")
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
    kind: str = Field(pattern="^(text|image|video|voice|music)$")
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)

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
        if kind != "text":
            raise RuntimeError(f"The {kind} adapter is not installed in this build.")
        prompt = str(inp.get("prompt") or inp.get("idea") or "").strip()
        if not prompt:
            raise RuntimeError("Add a prompt or story idea before generating.")
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
        update_job(job_id, status="completed", progress=100,
                   message="Script generation completed.",
                   output_json=json.dumps({"text": result}, ensure_ascii=False), error=None)
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
    local=ollama_status()
    ffmpeg=shutil.which("ffmpeg")
    return {"status":"ok","engine":"MyTube AI","version":"0.4.0",
        "adapters":{
            "text":{"available":local["available"],"installed":local["installed"],"model":local["model"],"provider":"ollama"},
            "image":{"available":False,"configured":bool(os.getenv("COMFYUI_URL")),"provider":"comfyui" if os.getenv("COMFYUI_URL") else None},
            "video":{"available":False,"configured":bool(os.getenv("MYTUBE_VIDEO_API_URL")),"provider":"configured-http" if os.getenv("MYTUBE_VIDEO_API_URL") else None},
            "voice":{"available":False,"configured":bool(os.getenv("MYTUBE_TTS_API_URL")),"provider":"configured-http" if os.getenv("MYTUBE_TTS_API_URL") else None},
            "music":{"available":False,"configured":bool(os.getenv("MYTUBE_MUSIC_API_URL")),"provider":"configured-http" if os.getenv("MYTUBE_MUSIC_API_URL") else None},
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

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    with connect() as c:
        row=c.execute("SELECT * FROM jobs WHERE job_id=?",(job_id,)).fetchone()
    if not row: raise HTTPException(status_code=404,detail="Job not found")
    return job_dict(row)

@app.get("/api/jobs")
def list_jobs(projectId: str | None = None, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    with connect() as c:
        if projectId:
            rows=c.execute("SELECT * FROM jobs WHERE project_id=? ORDER BY created_at DESC LIMIT 100",(projectId,)).fetchall()
        else:
            rows=c.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100").fetchall()
    return [job_dict(r) for r in rows]


class RenderIn(BaseModel):
    projectId: str = Field(min_length=1, max_length=120)
    clips: list[str] = Field(min_length=1, max_length=500)
    audioTracks: list[str] = Field(default_factory=list, max_length=8)
    resolution: str = Field(default="1080p", pattern="^(720p|1080p|4K)$")
    fps: int = Field(default=30, ge=24, le=60)
    preset: str = Field(default="Balanced", pattern="^(High Quality|Balanced|Smaller File)$")
    watermark: str = Field(default="", max_length=100)


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
    # Normalize and concatenate clips; mux the first selected audio track.
    work=tempfile.mkdtemp(prefix="mytube-render-")
    try:
        w,h={"720p":(1280,720),"1080p":(1920,1080),"4K":(3840,2160)}[body.resolution]
        normalized=[]
        for i,clip in enumerate(clips):
            target=os.path.join(work,f"clip-{i:04d}.mp4")
            vf=f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={body.fps}"
            cmd=["ffmpeg","-y","-i",clip,"-vf",vf,"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-an",target]
            subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=7200)
            normalized.append(target)
        concat=os.path.join(work,"concat.txt")
        with open(concat,"w") as f:
            for item in normalized: f.write("file '"+item.replace("'","'\''")+"'\n")
        merged=os.path.join(work,"merged.mp4")
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c","copy",merged],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=7200)
        cmd=["ffmpeg","-y","-i",merged]
        if audios: cmd += ["-i",audios[0]]
        if body.watermark:
            # Escape drawtext metacharacters; never interpret user text as a filter expression.
            txt=body.watermark.replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%")
            cmd += ["-vf",f"drawtext=text='{txt}':x=w-tw-24:y=h-th-24:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.45"]
        cmd += ["-c:v","libx264","-preset","medium" if body.preset=="High Quality" else "veryfast","-crf","18" if body.preset=="High Quality" else "23" if body.preset=="Balanced" else "28"]
        if audios: cmd += ["-map","0:v:0","-map","1:a:0","-c:a","aac","-b:a","192k","-shortest"]
        else: cmd += ["-an"]
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

# Serve CSS, JS, icons and manifest after explicit API routes.
app.mount("/", StaticFiles(directory=STUDIO_DIR, html=True), name="studio")
