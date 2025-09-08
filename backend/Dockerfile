# ---------- Backend ----------
FROM python:3.11-slim
WORKDIR /app

# System-CA-Zertifikate & Build-Deps (psycopg2 etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libc6-dev ca-certificates \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend Source
COPY . .

# Expose (Info: CE setzt $PORT automatisch)
ENV PORT=8000
CMD ["bash","-lc","uvicorn server:app --host 0.0.0.0 --port ${PORT}"]
