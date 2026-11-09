"""Optional media engine adapters for MyTube AI.

ComfyUI image generation is supported through its HTTP API when configured.
Video/voice/music providers use explicit HTTP endpoint contracts; they are never
reported as working merely because a URL exists.
"""
import json, os, time, uuid
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def _json_request(url, payload=None, timeout=30, headers=None):
    data = None if payload is None else json.dumps(payload).encode()
    h = {"Accept":"application/json"}
    if data is not None: h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = Request(url, data=data, headers=h)
    with urlopen(req, timeout=timeout) as r:
        raw = r.read()
    try: return json.loads(raw.decode())
    except Exception: return {"raw": raw.decode("utf-8","replace")}

def comfyui_status():
    url = os.getenv("COMFYUI_URL","").rstrip("/")
    if not url: return {"available":False,"configured":False,"provider":None}
    try:
        _json_request(url + "/system_stats", timeout=3)
        return {"available":True,"configured":True,"provider":"ComfyUI"}
    except Exception as e:
        return {"available":False,"configured":True,"provider":"ComfyUI","error":str(e)[:180]}

def comfyui_submit(prompt, workflow=None):
    """Submit a caller-supplied ComfyUI API workflow; prompt is available as metadata.
    A valid ComfyUI API-format workflow JSON object is required in workflow.
    """
    url = os.getenv("COMFYUI_URL","").rstrip("/")
    if not url: raise RuntimeError("Set COMFYUI_URL to enable ComfyUI image generation.")
    if not isinstance(workflow, dict) or not workflow:
        raise RuntimeError("A ComfyUI API-format workflow JSON is required. No default model/workflow is bundled.")
    client_id = str(uuid.uuid4())
    result = _json_request(url + "/prompt", {"prompt":workflow,"client_id":client_id}, timeout=45)
    pid = result.get("prompt_id")
    if not pid: raise RuntimeError("ComfyUI did not return a prompt_id: " + str(result)[:300])
    return {"provider":"ComfyUI","promptId":pid,"clientId":client_id,"prompt":prompt}

def provider_status(env_name, label):
    url = os.getenv(env_name,"").rstrip("/")
    if not url: return {"available":False,"configured":False,"provider":None}
    try:
        data = _json_request(url + "/health", timeout=3)
        ok = data.get("status") in ("ok","ready","healthy") or data.get("available") is True
        return {"available":bool(ok),"configured":True,"provider":label}
    except Exception as e:
        return {"available":False,"configured":True,"provider":label,"error":str(e)[:180]}

def configured_provider_submit(env_name, label, payload):
    url = os.getenv(env_name,"").rstrip("/")
    if not url: raise RuntimeError(f"{label} engine is not configured. Set {env_name} on the private backend.")
    token_env = env_name.replace("_URL","_TOKEN")
    token = os.getenv(token_env,"")
    headers = {"Authorization":"Bearer "+token} if token else {}
    result = _json_request(url + "/generate", payload, timeout=120, headers=headers)
    return {"provider":label,"result":result}


def comfyui_history(prompt_id):
    url = os.getenv("COMFYUI_URL","").rstrip("/")
    if not url: raise RuntimeError("Set COMFYUI_URL to enable ComfyUI.")
    if not prompt_id or not all(c in "0123456789abcdef-" for c in prompt_id.lower()):
        raise ValueError("Invalid ComfyUI prompt ID.")
    return _json_request(url + "/history/" + prompt_id, timeout=15)

def comfyui_fetch_image(filename, subfolder="", image_type="output"):
    """Fetch a ComfyUI image through the private backend; blocks path traversal."""
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    url = os.getenv("COMFYUI_URL","").rstrip("/")
    if not url: raise RuntimeError("Set COMFYUI_URL to enable ComfyUI.")
    if not filename or "/" in filename or "\\\\" in filename or filename in (".",".."):
        raise ValueError("Invalid image filename.")
    if subfolder and (subfolder.startswith("/") or ".." in subfolder.split("/") or "\\\\" in subfolder):
        raise ValueError("Invalid image subfolder.")
    query = urlencode({"filename":filename,"subfolder":subfolder,"type":image_type})
    req = Request(url + "/view?" + query, headers={"Accept":"image/*"})
    with urlopen(req, timeout=60) as response:
        content_type = response.headers.get("Content-Type","application/octet-stream")
        if not content_type.startswith("image/"):
            raise RuntimeError("ComfyUI returned a non-image output.")
        return response.read(), content_type


def configured_provider_poll(env_name, label, provider_job_id):
    """Poll the provider's GET /jobs/{id} endpoint."""
    from urllib.parse import quote
    url = os.getenv(env_name, "").rstrip("/")
    if not url:
        raise RuntimeError(f"{label} engine is not configured.")
    token = os.getenv(env_name.replace("_URL", "_TOKEN"), "")
    headers = {"Authorization": "Bearer " + token} if token else {}
    result = _json_request(url + "/jobs/" + quote(str(provider_job_id), safe=""), timeout=12, headers=headers)
    status = str(result.get("status", "processing")).lower()
    if status in ("succeeded", "success", "done"):
        status = "completed"
    elif status in ("error", "cancelled", "canceled"):
        status = "failed"
    if status not in ("queued", "processing", "completed", "failed"):
        status = "processing"
    return {"provider": label, "status": status, "result": result}


def configured_provider_fetch_output(env_name, label, provider_job_id, max_bytes=1024*1024*1024):
    """Fetch completed media from the provider's documented GET /jobs/{id}/output endpoint.

    The URL is built from the private configured base URL; provider-supplied arbitrary
    URLs are deliberately not followed (avoids SSRF).
    """
    from urllib.parse import quote
    from urllib.request import Request, urlopen
    url = os.getenv(env_name, "").rstrip("/")
    if not url:
        raise RuntimeError(f"{label} engine is not configured.")
    token = os.getenv(env_name.replace("_URL", "_TOKEN"), "")
    headers = {"Accept": "video/*, audio/*, application/octet-stream"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request(url + "/jobs/" + quote(str(provider_job_id), safe="") + "/output", headers=headers)
    with urlopen(req, timeout=180) as response:
        content_type = response.headers.get("Content-Type", "application/octet-stream").split(";", 1)[0].lower()
        allowed = {
            "video/mp4": ".mp4", "video/webm": ".webm", "video/quicktime": ".mov",
            "audio/mpeg": ".mp3", "audio/mp3": ".mp3", "audio/wav": ".wav",
            "audio/x-wav": ".wav", "audio/ogg": ".ogg", "audio/mp4": ".m4a",
            "application/octet-stream": {"video": ".mp4", "voice": ".mp3", "music": ".mp3"}.get(label.lower(), ".bin"),
        }
        if content_type not in allowed:
            raise RuntimeError(f"Provider output has unsupported Content-Type: {content_type}")
        length = int(response.headers.get("Content-Length", "0") or 0)
        if length > max_bytes:
            raise RuntimeError("Provider output exceeds the 1 GB import limit.")
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise RuntimeError("Provider output exceeds the 1 GB import limit.")
        if not data:
            raise RuntimeError("Provider returned an empty media file.")
    return data, content_type, allowed[content_type]
