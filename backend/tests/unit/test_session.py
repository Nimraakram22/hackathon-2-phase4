"""
Unit tests for agent session management.

Tests session creation, ID generation, and validation.
"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.agent.session import (
    get_agent_session,
    get_session_id,
    validate_session_id,
)


def test_session_id_generation_format():
    """Test session ID generation follows expected format.

    Format: user_{user_uuid}_conv_{conversation_uuid}
    """
    user_id = uuid4()
    conversation_id = uuid4()

    session_id = get_session_id(user_id, conversation_id)

    # Verify format
    assert session_id.startswith("user_")
    assert "_conv_" in session_id
    assert str(user_id) in session_id
    assert str(conversation_id) in session_id

    # Verify structure
    parts = session_id.split("_")
    assert len(parts) == 4
    assert parts[0] == "user"
    assert parts[2] == "conv"


def test_session_id_validation_valid():
    """Test session ID validation accepts valid IDs."""
    user_id = uuid4()
    conversation_id = uuid4()

    session_id = get_session_id(user_id, conversation_id)

    assert validate_session_id(session_id) is True


def test_session_id_validation_invalid_format():
    """Test session ID validation rejects invalid formats."""
    invalid_ids = [
        "invalid",
        "user_123_conv_456",  # Not UUIDs
        "user_conv_",
        "",
        "random_string",
        f"user_{uuid4()}_wrong_{uuid4()}",  # Wrong separator
    ]

    for invalid_id in invalid_ids:
        assert validate_session_id(invalid_id) is False


def test_session_creation_with_file_storage(tmp_path):
    """Test session creation uses file-based storage.

    Verifies that sessions are created with persistent storage
    and database file is created.
    """
    user_id = uuid4()
    conversation_id = uuid4()

    # Create session with temporary database
    db_path = tmp_path / "test_sessions.db"

    # Mock settings to use temp path
    import src.config
    original_path = src.config.settings.agent_session_db_path
    src.config.settings.agent_session_db_path = str(db_path)

    try:
        session = get_agent_session(user_id, conversation_id)

        # Verify session was created
        assert session is not None
        assert session.session_id == get_session_id(user_id, conversation_id)

        # Verify database file was created
        assert db_path.exists()
        assert db_path.is_file()

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path


def test_session_id_uniqueness():
    """Test session IDs are unique per user and conversation."""
    user1_id = uuid4()
    user2_id = uuid4()
    conv1_id = uuid4()
    conv2_id = uuid4()

    # Same user, different conversations
    session1 = get_session_id(user1_id, conv1_id)
    session2 = get_session_id(user1_id, conv2_id)
    assert session1 != session2

    # Different users, same conversation
    session3 = get_session_id(user1_id, conv1_id)
    session4 = get_session_id(user2_id, conv1_id)
    assert session3 != session4

    # Same user and conversation (deterministic)
    session5 = get_session_id(user1_id, conv1_id)
    session6 = get_session_id(user1_id, conv1_id)
    assert session5 == session6
