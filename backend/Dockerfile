FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/tsconfig.json frontend/vite.config.ts ./
COPY frontend/index.html ./index.html
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm ci --no-audit --no-fund || npm install --no-audit --no-fund
RUN npm run build

FROM python:3.11-slim AS backend
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build from builder
COPY --from=frontend-build /app/frontend/build /app/frontend/build
COPY --from=frontend-build /app/frontend/public/boardy.png /app/frontend/build/boardy.png

# Copy backend application
COPY backend/app.py .

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]