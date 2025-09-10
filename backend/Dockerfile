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

# System dependencies for PostgreSQL and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libc6-dev \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build from previous stage
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Backend Source (inkl. allen app/ und ingest/ Modulen)
COPY . .

# IBM Cloud Code Engine configuration
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
