FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MYTUBE_DB_PATH=/data/mytube_jobs.sqlite3 \
    OLLAMA_URL=http://ollama:11434

RUN apt-get update \
    && apt-get install -y --no-install-recommends espeak-ng ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /data /app/generated_audio

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
