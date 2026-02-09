"""
User model for authentication and user management.

This module defines the User entity with SQLModel for type-safe ORM operations.
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation


class User(SQLModel, table=True):
    """
    User entity representing an authenticated user.

    Attributes:
        id: Unique user identifier (UUID)
        email: User email address (unique, indexed)
        hashed_password: Bcrypt-hashed password
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        is_active: Account active status
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, sa_column_kwargs={"nullable": False})
    hashed_password: str = Field(min_length=1, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    is_active: bool = Field(default=True, index=True, sa_column_kwargs={"nullable": False})

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    conversations: list["Conversation"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
