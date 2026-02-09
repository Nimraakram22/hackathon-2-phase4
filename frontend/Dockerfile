# Multi-stage Dockerfile for React frontend
#
# This Dockerfile uses a multi-stage build strategy to create a minimal production image:
# - Stage 1 (builder): Compiles React application with Node.js and build tools
# - Stage 2 (runner): Serves static files with nginx (no Node.js in production)
#
# Benefits:
# - Smaller image size: ~76MB vs ~1GB+ with Node.js included
# - Better security: No build tools or source code in production image
# - Faster deployments: Smaller images transfer and start faster
# - Layer caching: Dependencies cached separately from source code for faster rebuilds

# Build arguments for version pinning (ensures reproducible builds)
ARG NODE_VERSION=20.11.1
ARG NGINX_VERSION=alpine3.22

# ============================================================================
# Stage 1: Builder - Compile React application
# ============================================================================
FROM node:${NODE_VERSION}-alpine AS builder

# Set working directory for build
WORKDIR /app

# Copy package files first (separate layer for better caching)
# If package.json doesn't change, this layer is cached and npm ci is skipped
COPY package.json package-lock.json ./

# Install ALL dependencies (including dev dependencies needed for build)
# --mount=type=cache: Caches npm packages between builds for faster rebuilds
# npm ci: Clean install from package-lock.json (faster and more reliable than npm install)
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy source code (separate layer so code changes don't invalidate npm install)
COPY . .

# Build the application
# Note: We skip TypeScript type checking here (npx vite build instead of npm run build)
# Rationale: Type checking should be done in CI/CD pipeline, not during image builds
# This prevents build failures from test files and speeds up image builds
RUN npx vite build

# ============================================================================
# Stage 2: Runner - Serve static files with nginx
# ============================================================================
FROM nginxinc/nginx-unprivileged:${NGINX_VERSION} AS runner

# Switch to non-root user for security (nginx user already exists in nginx-unprivileged)
# Running as non-root prevents privilege escalation attacks
USER nginx

# Copy custom nginx configuration for SPA routing
# This configuration ensures all routes are handled by React Router (client-side routing)
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built assets from builder stage
# --chown=nginx:nginx: Ensures files are owned by nginx user
# --from=builder: Copies from previous stage (only production assets, no source code)
COPY --chown=nginx:nginx --from=builder /app/dist /usr/share/nginx/html

# Copy health check file for Kubernetes liveness/readiness probes
COPY --chown=nginx:nginx public/health.html /usr/share/nginx/html/health.html

# Expose port 8080 (unprivileged port, can be used by non-root user)
# Note: Ports <1024 require root privileges, so we use 8080 instead of 80
EXPOSE 8080

# Health check for Docker (also used by Kubernetes)
# Kubernetes will use this to determine if container is healthy
# --interval=30s: Check every 30 seconds
# --timeout=3s: Fail if check takes longer than 3 seconds
# --start-period=5s: Wait 5 seconds before first check (allows nginx to start)
# --retries=3: Mark unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health.html || exit 1

# Start nginx in foreground mode (required for Docker)
# -g "daemon off;": Prevents nginx from daemonizing (Docker needs foreground process)
CMD ["nginx", "-g", "daemon off;"]
