from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(title="MyTube AI Engine")
jobs = {}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hitaishiss.github.io"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Job(BaseModel):
    projectId: str
    kind: str
    input: dict = {}

@app.get("/health")
def health():
    return {"status": "ok", "engine": "MyTube AI"}

@app.post("/api/jobs")
def create_job(job: Job):
    job_id = str(uuid4())
    jobs[job_id] = {
        "jobId": job_id,
        "projectId": job.projectId,
        "kind": job.kind,
        "status": "queued",
        "message": "Waiting for AI generation adapter"
    }
    return jobs[job_id]

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    return jobs.get(job_id, {"error": "Job not found"})

@app.get("/")
def home():
    return {"message": "MyTube AI backend is running", "health": "/health", "docs": "/docs"}
