"""
MCP tools for task management.

This module provides MCP tools for creating, reading, updating, and deleting tasks.
"""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastmcp import FastMCP
from pydantic import Field
from sqlalchemy.orm import Session

from ...database.connection import get_session_context
from ...models.task import Task


async def create_task(
    user_id: Annotated[str, Field(description="User identifier (UUID)")],
    title: Annotated[str, Field(description="Task title (1-100 characters)", min_length=1, max_length=100)],
    description: Annotated[Optional[str], Field(description="Optional task description (max 1000 characters)", max_length=1000)] = None,
) -> dict[str, str]:
    """
    Create a new task for the user.

    Args:
        user_id: User UUID string
        title: Task title (1-100 characters)
        description: Optional task description (max 1000 characters)

    Returns:
        Dictionary with task_id, title, description, is_completed, and created_at

    Raises:
        ValueError: If user_id is not a valid UUID
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError(f"Invalid user_id: {user_id}")

    with get_session_context() as session:
        task = Task(
            user_id=user_uuid,
            title=title.strip(),
            description=description.strip() if description else None,
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description or "",
            "is_completed": str(task.is_completed),
            "created_at": task.created_at.isoformat(),
        }


async def list_tasks(
    user_id: Annotated[str, Field(description="User identifier (UUID)")],
    status_filter: Annotated[str, Field(description="Filter tasks by status: all, pending, or completed")] = "all",
    limit: Annotated[int, Field(description="Maximum number of tasks to return", ge=1, le=100)] = 50,
    offset: Annotated[int, Field(description="Number of tasks to skip for pagination", ge=0)] = 0,
) -> dict[str, str | int]:
    """
    List user's tasks with optional filtering.

    Args:
        user_id: User UUID string
        status_filter: Filter by status (all, pending, completed)
        limit: Maximum number of tasks to return (1-100)
        offset: Number of tasks to skip for pagination

    Returns:
        Dictionary with tasks array and total_count

    Raises:
        ValueError: If user_id is not a valid UUID or status_filter is invalid
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError(f"Invalid user_id: {user_id}")

    if status_filter not in ["all", "pending", "completed"]:
        raise ValueError(f"Invalid status_filter: {status_filter}. Must be 'all', 'pending', or 'completed'")

    with get_session_context() as session:
        query = session.query(Task).filter(Task.user_id == user_uuid)

        if status_filter == "pending":
            query = query.filter(Task.is_completed == False)
        elif status_filter == "completed":
            query = query.filter(Task.is_completed == True)

        total_count = query.count()
        tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

        tasks_list = [
            {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description or "",
                "is_completed": str(task.is_completed),
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else "",
            }
            for task in tasks
        ]

        return {
            "tasks": str(tasks_list),
            "total_count": total_count,
        }


async def get_task(
    user_id: Annotated[str, Field(description="User identifier (UUID)")],
    task_id: Annotated[str, Field(description="Task identifier (UUID)")],
) -> dict[str, str]:
    """
    Get a single task by ID.

    Args:
        user_id: User UUID string
        task_id: Task UUID string

    Returns:
        Dictionary with task details

    Raises:
        ValueError: If user_id or task_id is not a valid UUID
        LookupError: If task not found or does not belong to user
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
    except ValueError as e:
        raise ValueError(f"Invalid UUID: {e}")

    with get_session_context() as session:
        task = session.query(Task).filter(
            Task.id == task_uuid,
            Task.user_id == user_uuid
        ).first()

        if not task:
            raise LookupError(f"Task {task_id} not found or does not belong to user")

        return {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description or "",
            "is_completed": str(task.is_completed),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else "",
        }


async def complete_task(
    user_id: Annotated[str, Field(description="User identifier (UUID)")],
    task_id: Annotated[str, Field(description="Task identifier (UUID)")],
) -> dict[str, str]:
    """
    Mark a task as completed.

    Args:
        user_id: User UUID string
        task_id: Task UUID string

    Returns:
        Dictionary with task_id, is_completed, and completed_at

    Raises:
        ValueError: If user_id or task_id is not a valid UUID
        LookupError: If task not found or does not belong to user
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
    except ValueError as e:
        raise ValueError(f"Invalid UUID: {e}")

    with get_session_context() as session:
        task = session.query(Task).filter(
            Task.id == task_uuid,
            Task.user_id == user_uuid
        ).first()

        if not task:
            raise LookupError(f"Task {task_id} not found or does not belong to user")

        task.is_completed = True
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(task)

        return {
            "task_id": str(task.id),
            "is_completed": str(task.is_completed),
            "completed_at": task.completed_at.isoformat(),
        }


async def update_task(
    user_id: Annotated[str, Field(description="User identifier (UUID)")],
    task_id: Annotated[str, Field(description="Task identifier (UUID)")],
    title: Annotated[Optional[str], Field(description="New task title (1-100 characters)", min_length=1, max_length=100)] = None,
    description: Annotated[Optional[str], Field(description="New task description (max 1000 characters)", max_length=1000)] = None,
) -> dict[str, str]:
    """
    Update task title and/or description.

    Args:
        user_id: User UUID string
        task_id: Task UUID string
        title: Optional new title
        description: Optional new description

    Returns:
        Dictionary with task_id, title, description, and updated_at

    Raises:
        ValueError: If user_id or task_id is not a valid UUID, or no fields to update
        LookupError: If task not found or does not belong to user
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
    except ValueError as e:
        raise ValueError(f"Invalid UUID: {e}")

    if title is None and description is None:
        raise ValueError("At least one field (title or description) must be provided for update")

    with get_session_context() as session:
        task = session.query(Task).filter(
            Task.id == task_uuid,
            Task.user_id == user_uuid
        ).first()

        if not task:
            raise LookupError(f"Task {task_id} not found or does not belong to user")

        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip() if description else None

        task.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(task)

        return {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description or "",
            "updated_at": task.updated_at.isoformat(),
        }


async def delete_task(
    user_id: Annotated[str, Field(description="User identifier (UUID)")],
    task_id: Annotated[str, Field(description="Task identifier (UUID)")],
) -> dict[str, str]:
    """
    Permanently delete a task (hard delete).

    Args:
        user_id: User UUID string
        task_id: Task UUID string

    Returns:
        Dictionary with task_id and deleted=True

    Raises:
        ValueError: If user_id or task_id is not a valid UUID
        LookupError: If task not found or does not belong to user
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
    except ValueError as e:
        raise ValueError(f"Invalid UUID: {e}")

    with get_session_context() as session:
        task = session.query(Task).filter(
            Task.id == task_uuid,
            Task.user_id == user_uuid
        ).first()

        if not task:
            raise LookupError(f"Task {task_id} not found or does not belong to user")

        session.delete(task)
        session.commit()

        return {
            "task_id": str(task_uuid),
            "deleted": "True",
        }
