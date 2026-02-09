"""
Task model for todo items.

This module defines the Task entity with SQLModel for type-safe ORM operations.
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel, Index

if TYPE_CHECKING:
    from .user import User


class Task(SQLModel, table=True):
    """
    Task entity representing a todo item.

    Attributes:
        id: Unique task identifier (UUID)
        user_id: Owner of the task (foreign key to users.id)
        title: Task title (1-100 characters)
        description: Optional task description (max 1000 characters)
        is_completed: Completion status (default: False)
        created_at: Task creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp (set when is_completed becomes True)
    """

    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_user_completed", "user_id", "is_completed"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, sa_column_kwargs={"nullable": False})
    title: str = Field(min_length=1, max_length=100, sa_column_kwargs={"nullable": False})
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False, index=True, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
