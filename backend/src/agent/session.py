"""
SQLiteSession wrapper for conversation context management.

This module provides a wrapper around OpenAI Agents SDK SQLiteSession.
"""

import re
from uuid import UUID
from pathlib import Path

from agents import SQLiteSession

from ..config import settings


# Session ID validation pattern
SESSION_ID_PATTERN = re.compile(r"^user_[0-9a-f-]{36}_conv_[0-9a-f-]{36}$")


def get_session_id(user_id: UUID, conversation_id: UUID) -> str:
    """
    Generate session ID for agent conversation context.

    Format: user_{user_id}_conv_{conversation_id}

    Args:
        user_id: User UUID
        conversation_id: Conversation UUID

    Returns:
        Session ID string
    """
    return f"user_{user_id}_conv_{conversation_id}"


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not SESSION_ID_PATTERN.match(session_id):
        return False

    # Extract and validate UUIDs
    parts = session_id.split("_")
    try:
        UUID(parts[1])  # user_id
        UUID(parts[3])  # conversation_id
        return True
    except (ValueError, IndexError):
        return False


def get_agent_session(user_id: UUID, conversation_id: UUID) -> SQLiteSession:
    """
    Get or create an agent session for conversation context.

    Args:
        user_id: User UUID
        conversation_id: Conversation UUID

    Returns:
        SQLiteSession instance for maintaining conversation context
    """
    # Ensure data directory exists
    session_db_path = Path(settings.agent_session_db_path)
    session_db_path.parent.mkdir(parents=True, exist_ok=True)

    session_id = get_session_id(user_id, conversation_id)

    # Use file-based storage instead of in-memory
    return SQLiteSession(session_id, db_path=str(session_db_path))

