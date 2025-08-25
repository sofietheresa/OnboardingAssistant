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

# System libs für psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libc6-dev && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Frontend Build in Image kopieren
COPY --from=frontend-build /app/frontend/build /app/frontend/build

# Backend Source (inkl. allen app/ und ingest/ Modulen)
COPY backend/ /app/

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
