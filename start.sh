#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Install the optional local speech engine when this host supports apt and
# the startup process has root privileges. Otherwise continue without voice.
if ! command -v espeak-ng >/dev/null 2>&1 && ! command -v espeak >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1 && [ "$(id -u)" -eq 0 ]; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends espeak-ng
  else
    echo "Voice preview disabled: install espeak-ng on this backend host to enable it."
  fi
fi

# Start Ollama automatically if it is not already running.
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

# Ensure the local text model exists; download only if missing.
if ! curl -fsS http://127.0.0.1:11434/api/tags | grep -q 'qwen2.5:3b'; then
  ollama pull qwen2.5:3b
fi

python -m pip install -r requirements.txt
exec python -m uvicorn app:app --host 0.0.0.0 --port 8000
