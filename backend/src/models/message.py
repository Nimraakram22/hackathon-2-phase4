"""
Message model for conversation messages.

This module defines the Message entity with SQLModel for type-safe ORM operations.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, Index, Column
from sqlalchemy import Enum as SAEnum

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Message role enum for user and assistant messages."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Message entity representing a single message in a conversation.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Parent conversation (foreign key to conversations.id)
        role: Message role (user or assistant)
        content: Message content (1-2000 characters)
        created_at: Message timestamp
    """

    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True, sa_column_kwargs={"nullable": False})
    role: MessageRole = Field(sa_column=Column(SAEnum(MessageRole), nullable=False))
    content: str = Field(min_length=1, max_length=2000, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True, sa_column_kwargs={"nullable": False})

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
