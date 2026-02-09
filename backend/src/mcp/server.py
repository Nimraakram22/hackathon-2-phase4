"""
FastMCP server initialization.

This module initializes the FastMCP server with middleware for error handling and retries.
"""

from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware, RetryMiddleware

from ..config import settings
from .tools.task_tools import (
    create_task,
    list_tasks,
    get_task,
    complete_task,
    update_task,
    delete_task,
)


# Initialize FastMCP server
mcp = FastMCP(
    name=settings.mcp_server_name,
    version=settings.mcp_server_version,
)

# Add error handling middleware
mcp.add_middleware(
    ErrorHandlingMiddleware(
        include_traceback=settings.is_development,
        transform_errors=True,
    )
)

# Add retry middleware with exponential backoff
# 5 retries: 1s, 2s, 4s, 8s, 16s = 31s total (within 30s constraint per spec)
mcp.add_middleware(
    RetryMiddleware(
        max_retries=5,
        retry_exceptions=(ConnectionError, TimeoutError),
    )
)

# Register MCP tools
mcp.tool(create_task)
mcp.tool(list_tasks)
mcp.tool(get_task)
mcp.tool(complete_task)
mcp.tool(update_task)
mcp.tool(delete_task)
