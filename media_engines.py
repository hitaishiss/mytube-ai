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
