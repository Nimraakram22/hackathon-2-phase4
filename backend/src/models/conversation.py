"""
Conversation model for chat sessions.

This module defines the Conversation entity with SQLModel for type-safe ORM operations.
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel, Index

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Owner of the conversation (foreign key to users.id)
        title: Optional conversation title (auto-generated from first message)
        created_at: Conversation start timestamp
        updated_at: Last message timestamp
        is_deleted: Soft delete flag for retention policy
        deleted_at: Deletion timestamp (set when marked for deletion)
    """

    __tablename__ = "conversations"
    __table_args__ = (
        Index("ix_conversations_user_deleted", "user_id", "is_deleted"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, sa_column_kwargs={"nullable": False})
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True, sa_column_kwargs={"nullable": False})
    is_deleted: bool = Field(default=False, index=True, sa_column_kwargs={"nullable": False})
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
