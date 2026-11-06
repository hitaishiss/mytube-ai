#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python -m pip install -r requirements.txt
if command -v ollama >/dev/null 2>&1; then
  if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    nohup ollama serve >/tmp/mytube-ollama.log 2>&1 &
    for i in $(seq 1 30); do
      curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
      sleep 1
    done
  fi
else
  echo "Ollama is not installed; the studio will open, but local script generation needs Ollama."
fi
exec python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
