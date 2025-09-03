# ---------- Frontend Build ----------
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
COPY frontend/tsconfig.json frontend/vite.config.ts ./
COPY frontend/index.html ./index.html
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm ci --no-audit --no-fund || npm install --no-audit --no-fund
RUN npm run build

# ---------- Backend ----------
FROM python:3.11-slim AS backend
WORKDIR /app

# System-CA-Zertifikate (wichtig für Postgres TLS) und System libs für psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libc6-dev \
    ca-certificates \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*



# Python Dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Backend Source (inkl. allen app/ und ingest/ Modulen)
COPY ./ .

# Expose (Info, Code Engine nimmt $PORT)
ENV PORT=8000
CMD ["bash","-lc","uvicorn server:app --host 0.0.0.0 --port ${PORT}"]