# Multi-stage Dockerfile for Python FastAPI backend
#
# This Dockerfile uses a multi-stage build strategy to create a minimal production image:
# - Stage 1 (builder): Compiles Python dependencies with build tools
# - Stage 2 (runtime): Runs application with only runtime dependencies
#
# Benefits:
# - Smaller image size: ~359MB vs ~500MB+ with build tools included
# - Better security: No compilers or build tools in production image
# - Faster deployments: Smaller images transfer and start faster
# - Clean separation: Build dependencies isolated from runtime
#
# Virtual Environment Strategy:
# We use a Python virtual environment to isolate dependencies, which allows us to:
# - Copy only the venv directory to the runtime stage (clean dependency isolation)
# - Avoid polluting the system Python installation
# - Ensure consistent dependency versions across environments

# Build argument for Python version pinning (ensures reproducible builds)
ARG PYTHON_VERSION=3.11

# ============================================================================
# Stage 1: Builder - Compile Python dependencies
# ============================================================================
FROM python:${PYTHON_VERSION}-alpine AS builder

# Set environment variables for Python optimization
# LANG=C.UTF-8: Use UTF-8 encoding for all text operations
# PYTHONDONTWRITEBYTECODE=1: Don't create .pyc files (not needed in containers)
# PYTHONUNBUFFERED=1: Force stdout/stderr to be unbuffered (better logging in containers)
# PATH: Add virtual environment to PATH so pip installs to venv
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/venv/bin:$PATH"

WORKDIR /app

# Install build dependencies required for compiling Python packages
# gcc, musl-dev: C compiler and standard library (needed for packages with C extensions)
# libffi-dev: Foreign function interface library (needed for cryptography packages)
# postgresql-dev: PostgreSQL client library headers (needed for psycopg2)
# Note: These are only needed during build, not in runtime image
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

# Create Python virtual environment
# This isolates our dependencies from the system Python installation
RUN python -m venv /app/venv

# Copy requirements file first (separate layer for better caching)
# If requirements.txt doesn't change, this layer is cached and pip install is skipped
COPY requirements.txt .

# Install Python dependencies into virtual environment
# --no-cache-dir: Don't cache pip packages (reduces image size)
# --upgrade pip: Ensure we have the latest pip version
# -r requirements.txt: Install all packages from requirements file
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Run FastAPI application
# ============================================================================
FROM python:${PYTHON_VERSION}-alpine

# Set environment variables for Python optimization
# PYTHONUNBUFFERED=1: Force stdout/stderr to be unbuffered (better logging)
# PATH: Add virtual environment to PATH so Python finds installed packages
# SQLITE_DB_PATH: Default path for SQLite session database (can be overridden)
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/venv/bin:$PATH" \
    SQLITE_DB_PATH="/app/data/sessions.db"

WORKDIR /app

# Install runtime dependencies only (no build tools)
# libpq: PostgreSQL client library (needed for psycopg2 at runtime)
# Note: This is much smaller than postgresql-dev (only runtime library, no headers)
RUN apk add --no-cache libpq

# Create non-root user for security
# addgroup -g 1001 -S app: Create system group with GID 1001
# adduser -S app -u 1001 -G app: Create system user with UID 1001 in app group
# mkdir -p /app/data: Create directory for SQLite database (will be mounted from PVC)
# chown -R app:app /app: Give app user ownership of /app directory
# Running as non-root prevents privilege escalation attacks
RUN addgroup -g 1001 -S app && \
    adduser -S app -u 1001 -G app && \
    mkdir -p /app/data && \
    chown -R app:app /app

# Copy virtual environment from builder stage
# --from=builder: Copy from previous stage (only venv, no build tools)
# --chown=app:app: Ensure files are owned by app user
# This gives us all installed packages without any build dependencies
COPY --from=builder --chown=app:app /app/venv /app/venv

# Copy application source code
# --chown=app:app: Ensure files are owned by app user
# Only copy src/ directory (no tests, docs, or other non-runtime files)
COPY --chown=app:app src ./src

# Switch to non-root user for security
# All subsequent commands and the application will run as this user
USER app

# Expose port 8000 (FastAPI default port)
# This is informational only; actual port binding happens at runtime
EXPOSE 8000

# Health check for Docker (also used by Kubernetes)
# Kubernetes will use this to determine if container is healthy
# --interval=30s: Check every 30 seconds
# --timeout=3s: Fail if check takes longer than 3 seconds
# --start-period=10s: Wait 10 seconds before first check (allows FastAPI to start)
# --retries=3: Mark unhealthy after 3 consecutive failures
# /health endpoint checks both application health and database connectivity
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Start FastAPI application with uvicorn
# uvicorn: ASGI server for FastAPI
# src.api.main:app: Import path to FastAPI app instance
# --host 0.0.0.0: Listen on all network interfaces (required for Docker)
# --port 8000: Listen on port 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
