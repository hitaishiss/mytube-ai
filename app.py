import os, sqlite3, threading, uuid, json, time, shutil, subprocess
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = os.getenv("MYTUBE_DB_PATH", "mytube_jobs.sqlite3")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
TEXT_MODEL = os.getenv("MYTUBE_TEXT_MODEL", "qwen2.5:3b")
ALLOWED_ORIGINS = [x.strip() for x in os.getenv(
    "MYTUBE_ALLOWED_ORIGINS", "https://hitaishiss.github.io"
).split(",") if x.strip()]
APP_TOKEN = os.getenv("MYTUBE_API_TOKEN", "")

app = FastAPI(title="MyTube AI private backend", version="0.2.0")
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
        "model": TEXT_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": True,
        "keep_alive": "10m",
        "options": {
            "num_predict": 900,
            "num_ctx": 4096,
            "temperature": 0.7
        }
    }
    req = Request(
        OLLAMA_URL.rstrip("/") + "/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    parts = []
    try:
        with urlopen(req, timeout=600) as response:
            while True:
                line = response.readline()
                if not line:
                    break
                item = json.loads(line.decode("utf-8"))
                piece = item.get("response", "")
                if piece:
                    parts.append(piece)
                    if progress_callback:
                        progress_callback("".join(parts))
                if item.get("error"):
                    raise RuntimeError(item["error"])
                if item.get("done"):
                    break
        result = "".join(parts).strip()
        if not result:
            raise RuntimeError("Ollama returned an empty response.")
        return result
    except HTTPError as e:
        raise RuntimeError("Ollama HTTP error: " + e.read().decode("utf-8", "replace")[:500])
    except URLError as e:
        raise RuntimeError("Cannot reach Ollama at " + OLLAMA_URL + ": " + str(e))
def update_job(job_id, **values):
    values["updated_at"]=now()
    cols=", ".join(f"{k}=?" for k in values)
    with connect() as c:
        c.execute(f"UPDATE jobs SET {cols} WHERE job_id=?", [*values.values(),job_id])


def run_job(job_id, kind, inp):
    try:
        update_job(job_id, status="processing", progress=10,
                   message="Preparing generation…")
        if kind != "text":
            raise RuntimeError(
                f"The {kind} adapter is not installed yet."
            )
        prompt = str(inp.get("prompt") or inp.get("idea") or "").strip()
        if not prompt:
            raise RuntimeError("Add a prompt or story idea before generating.")

        system = str(inp.get("system") or
            "You are MyTube AI's original drama-writing assistant. "
            "Write compelling scenes with clear character motivations, "
            "natural dialogue and consistent story facts.")

        update_job(job_id, progress=35, message="Loading local model…")

        def report_progress(text):
            # Real progress based on streamed output, not a fixed percentage.
            progress = min(94, 40 + len(text) // 180)
            update_job(job_id, progress=progress,
                       message=f"Writing script… {len(text)} characters received")

        result = ollama_generate(prompt, system, report_progress)
        update_job(
            job_id, status="completed", progress=100,
            message="Script generation completed.",
            output_json=json.dumps({"text": result}, ensure_ascii=False),
            error=None
        )
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

@app.get("/")
def root():
    return FileResponse("index.html")

@app.get("/health")
def health():
    local=ollama_status()
    return {"status":"ok","engine":"MyTube AI","adapters":{
        "text":{"available":local["available"],"installed":local["installed"],"model":local["model"]},
        "image":{"available":False},"video":{"available":False},
        "voice":{"available":bool(shutil.which("espeak-ng") or shutil.which("espeak"))},"music":{"available":False},"render":{"available":False,"ffmpeg_installed":bool(shutil.which("ffmpeg"))}
    }}

class VoiceIn(BaseModel):
    projectId: str = Field(min_length=1, max_length=120)
    text: str = Field(min_length=1, max_length=3000)
    style: str = Field(default="Warm", max_length=40)
    delivery: str = Field(default="Conversational", max_length=40)

VOICE_STYLES = {
    "Warm": (165, 48), "Calm": (145, 42), "Bright": (190, 58),
    "Deep": (135, 30), "Gentle": (150, 38), "Playful": (190, 62),
    "Mysterious": (130, 35), "Narrator": (155, 42), "Custom": (165, 50)
}

@app.get("/api/voice/health")
def voice_health():
    engine = shutil.which("espeak-ng") or shutil.which("espeak")
    return {"available": bool(engine), "engine": os.path.basename(engine) if engine else None,
            "message": "Local speech engine ready." if engine else
            "Install espeak-ng (or espeak) on the backend host to enable voice previews."}

@app.post("/api/voice/generate", status_code=201)
def generate_voice(body: VoiceIn, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    engine = shutil.which("espeak-ng") or shutil.which("espeak")
    if not engine:
        raise HTTPException(status_code=503, detail="No local speech engine is installed. Install espeak-ng on the backend host.")
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Enter dialogue before generating.")
    speed, pitch = VOICE_STYLES.get(body.style, VOICE_STYLES["Warm"])
    if body.delivery == "Whispered":
        speed, pitch = max(115, speed - 15), max(25, pitch - 8)
    elif body.delivery == "Dramatic":
        speed, pitch = max(120, speed - 10), min(75, pitch + 4)
    elif body.delivery == "Confident":
        speed, pitch = speed + 8, min(75, pitch + 3)
    elif body.delivery == "Emotional":
        speed = max(120, speed - 8)
    out_dir = Path("generated_audio")
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.wav"
    output = out_dir / filename
    try:
        subprocess.run([engine, "-s", str(speed), "-p", str(pitch), "-w", str(output), "--", text],
                       check=True, capture_output=True, timeout=45)
    except subprocess.TimeoutExpired:
        output.unlink(missing_ok=True)
        raise HTTPException(status_code=504, detail="Voice preview timed out.")
    except subprocess.CalledProcessError as exc:
        output.unlink(missing_ok=True)
        detail = exc.stderr.decode("utf-8", "replace")[:300] if exc.stderr else "Speech engine failed."
        raise HTTPException(status_code=500, detail=detail)
    return {"status": "completed", "audioUrl": f"/generated_audio/{filename}",
            "filename": filename, "engine": os.path.basename(engine)}

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

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

@app.get("/studio")
def studio():
    return FileResponse("index.html")

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory=".", html=True), name="studio")
