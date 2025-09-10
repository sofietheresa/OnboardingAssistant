# --- Build Stage ---
FROM node:20-alpine AS build
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json vite.config.ts ./

# Install dependencies
RUN npm ci --no-audit --no-fund

# Copy source code
COPY index.html ./
COPY src ./src
COPY public ./public

# Build arguments for environment variables
ARG VITE_BACKEND_URL
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

# Build the application
RUN npm run build

# --- Production Stage ---
FROM nginx:alpine AS production
WORKDIR /usr/share/nginx/html

# Install curl for health check
RUN apk add --no-cache curl

# Copy built files from build stage
COPY --from=build /app/build .

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
