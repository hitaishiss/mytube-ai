#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Reuse the existing Ollama daemon if available; otherwise start it.
if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  nohup ollama serve >/tmp/mytube-ollama.log 2>&1 </dev/null &
  for i in $(seq 1 60); do
    curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
    sleep 1
  done
fi
if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "Ollama did not start. Check /tmp/mytube-ollama.log"
  exit 1
fi

# Pull the configured text model only if it is missing.
if ! curl -fsS http://127.0.0.1:11434/api/tags | grep -q 'qwen2.5:3b'; then
  ollama pull qwen2.5:3b
fi

python -m pip install -r requirements.txt
if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
  echo "MyTube backend is already responding on port 8000; not starting a duplicate."
  exit 0
fi
exec python -m uvicorn app:app --host 0.0.0.0 --port 8000
