# --- Build ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
COPY tsconfig.json vite.config.ts ./
COPY index.html ./index.html
COPY src ./src
COPY public ./public
RUN npm ci --no-audit --no-fund
# API-URL zur Buildzeit setzen
#ARG VITE_BACKEND_URL
#ENV VITE_BACKEND_URL=$VITE_BACKEND_URL
RUN npm run build

# --- Runtime (static server) ---
FROM node:20-alpine
WORKDIR /app
RUN npm i -g serve
ENV PORT=8080
COPY --from=build /app/build ./build
# Wichtig: Shell-Form, damit $PORT expandiert
CMD ["sh","-lc","serve -s build -l tcp://0.0.0.0:${PORT:-8080}"]
