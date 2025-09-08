# --- Build ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
COPY tsconfig.json vite.config.ts ./
COPY index.html ./index.html
COPY src ./src
COPY public ./public
RUN npm ci --no-audit --no-fund
# Optional: API-URL zur Buildzeit setzen (siehe Hinweis unten)
# ARG VITE_API_BASE_URL
# ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# --- Runtime (static server) ---
FROM node:20-alpine
WORKDIR /app
RUN npm i -g serve
ENV PORT=8080
COPY --from=build /app/dist ./dist
# Wichtig: Shell-Form, damit $PORT expandiert
CMD ["sh","-lc","serve -s dist -l ${PORT:-8080}"]
