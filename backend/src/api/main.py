"""
FastAPI application initialization.

This module initializes the FastAPI app with CORS middleware, security headers,
and API routes for the AI-powered todo chatbot.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.config import settings
from src.api.routes import auth, chatkit, contact
from src.database.cleanup import session_cleanup_job

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.

    Manages the session cleanup job lifecycle:
    - Startup: Start background cleanup job for inactive sessions
    - Shutdown: Stop cleanup job gracefully
    """
    # Startup
    logger.info("Application startup: initializing session cleanup job")
    await session_cleanup_job.start()

    yield

    # Shutdown
    logger.info("Application shutdown: stopping session cleanup job")
    await session_cleanup_job.stop()


# Initialize FastAPI app
app = FastAPI(
    title="Todo Chatbot API",
    description="AI-powered todo chatbot backend with FastAPI, FastMCP, and OpenAI Agents SDK",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next: callable) -> Response:
    """
    Add security headers to all responses.

    Headers added:
    - X-Content-Type-Options: nosniff (prevent MIME type sniffing)
    - X-Frame-Options: DENY (prevent clickjacking)
    - X-XSS-Protection: 1; mode=block (enable XSS protection)
    - Strict-Transport-Security: max-age=31536000 (HSTS for HTTPS)
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Add HSTS header in production
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# Include routers
app.include_router(auth.router)
app.include_router(chatkit.router)
app.include_router(contact.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring and load balancers.

    Checks the application health and database connectivity. This endpoint can be used
    by monitoring systems, load balancers, and orchestration platforms to verify the
    service is operational.

    Returns:
        dict: Health status information containing:
            - status: "healthy" if application is running
            - database: "connected" or "disconnected" based on database connectivity
            - version: Application version string

    Example:
        ```bash
        curl http://localhost:8001/health
        ```

    Response:
        ```json
        {
            "status": "healthy",
            "database": "connected",
            "version": "0.1.0"
        }
        ```

    Note:
        - This endpoint does not require authentication
        - Database check performs a simple SELECT 1 query
        - Returns 200 OK even if database is disconnected (check "database" field)
    """
    from ..database.connection import get_session_context

    # Check database connection
    db_status = "connected"
    try:
        with get_session_context() as session:
            session.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "version": "0.1.0",
    }
