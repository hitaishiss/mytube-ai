import os, sqlite3, threading, uuid, json, time
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = os.getenv("MYTUBE_DB_PATH", "mytube_jobs.sqlite3")
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
        def on_piece(text):
            progress = min(95, 10 + len(text) // 100)
            update_job(job_id, progress=progress,
                       message=f"Generating script · {len(text)} characters received…")
        result = ollama_generate(prompt, system, on_piece)
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
    return {"status":"ok","engine":"MyTube AI","adapters":{
        "text":{"available":local["available"],"installed":local["installed"],"model":local["model"]},
        "image":{"available":False},"video":{"available":False},
        "voice":{"available":False},"music":{"available":False}
    }}

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

# Serve CSS, JS, icons and manifest after explicit API routes.
app.mount("/", StaticFiles(directory=STUDIO_DIR, html=True), name="studio")
