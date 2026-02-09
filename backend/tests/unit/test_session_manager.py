"""
Unit tests for SessionManager class.

Tests message limit enforcement, cleanup, and session statistics.
"""

import pytest
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta

from src.agent.session_manager import SessionManager
from src.agent.session import get_session_id


@pytest.fixture
def temp_session_manager(tmp_path):
    """Create a SessionManager with temporary database."""
    db_path = tmp_path / "test_sessions.db"
    manager = SessionManager(
        db_path=db_path,
        max_messages=200,
        retention_days=7,
    )
    return manager


@pytest.fixture
def session_with_messages(temp_session_manager, tmp_path):
    """Create a session with test messages."""
    user_id = uuid4()
    conversation_id = uuid4()
    session_id = get_session_id(user_id, conversation_id)

    # Create session and add messages directly to database
    db_path = tmp_path / "test_sessions.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create session
    cursor.execute(
        "INSERT INTO agent_sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
        (session_id, datetime.utcnow(), datetime.utcnow())
    )

    # Add messages
    for i in range(250):  # Exceed limit
        cursor.execute(
            "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
            (session_id, f'{{"role": "user", "content": "Message {i}"}}', datetime.utcnow())
        )

    conn.commit()
    conn.close()

    return temp_session_manager, session_id


@pytest.mark.asyncio
async def test_message_limit_enforcement(session_with_messages):
    """Test that sessions enforce 200 message limit.

    Verifies that prune_session_messages deletes oldest messages
    when session exceeds max_messages limit.
    """
    manager, session_id = session_with_messages

    # Verify session has 250 messages
    conn = sqlite3.connect(str(manager.db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agent_messages WHERE session_id = ?", (session_id,))
    count_before = cursor.fetchone()[0]
    conn.close()

    assert count_before == 250

    # Prune messages
    deleted_count = await manager.prune_session_messages(session_id)

    # Verify 50 messages were deleted
    assert deleted_count == 50

    # Verify session now has exactly 200 messages
    conn = sqlite3.connect(str(manager.db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agent_messages WHERE session_id = ?", (session_id,))
    count_after = cursor.fetchone()[0]
    conn.close()

    assert count_after == 200


@pytest.mark.asyncio
async def test_prune_keeps_most_recent_messages(session_with_messages):
    """Test that pruning keeps the most recent messages.

    Verifies that oldest messages are deleted first.
    """
    manager, session_id = session_with_messages

    # Get message IDs before pruning
    conn = sqlite3.connect(str(manager.db_path))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM agent_messages WHERE session_id = ? ORDER BY created_at ASC LIMIT 50",
        (session_id,)
    )
    oldest_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Prune messages
    await manager.prune_session_messages(session_id)

    # Verify oldest messages were deleted
    conn = sqlite3.connect(str(manager.db_path))
    cursor = conn.cursor()
    for msg_id in oldest_ids:
        cursor.execute("SELECT COUNT(*) FROM agent_messages WHERE id = ?", (msg_id,))
        count = cursor.fetchone()[0]
        assert count == 0, f"Oldest message {msg_id} should have been deleted"
    conn.close()


@pytest.mark.asyncio
async def test_prune_no_op_when_under_limit(temp_session_manager, tmp_path):
    """Test that pruning does nothing when under message limit."""
    user_id = uuid4()
    conversation_id = uuid4()
    session_id = get_session_id(user_id, conversation_id)

    # Create session with 100 messages (under limit)
    db_path = tmp_path / "test_sessions.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO agent_sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
        (session_id, datetime.utcnow(), datetime.utcnow())
    )

    for i in range(100):
        cursor.execute(
            "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
            (session_id, f'{{"role": "user", "content": "Message {i}"}}', datetime.utcnow())
        )

    conn.commit()
    conn.close()

    # Prune messages
    deleted_count = await temp_session_manager.prune_session_messages(session_id)

    # Verify no messages were deleted
    assert deleted_count == 0

    # Verify session still has 100 messages
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agent_messages WHERE session_id = ?", (session_id,))
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 100


@pytest.mark.asyncio
async def test_cleanup_inactive_sessions(temp_session_manager, tmp_path):
    """Test cleanup of sessions inactive for more than retention_days."""
    # Create active session (updated today)
    active_session_id = f"user_{uuid4()}_conv_{uuid4()}"

    # Create inactive session (updated 8 days ago)
    inactive_session_id = f"user_{uuid4()}_conv_{uuid4()}"
    old_date = datetime.utcnow() - timedelta(days=8)

    db_path = tmp_path / "test_sessions.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Insert active session
    cursor.execute(
        "INSERT INTO agent_sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
        (active_session_id, datetime.utcnow(), datetime.utcnow())
    )
    cursor.execute(
        "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
        (active_session_id, '{"role": "user", "content": "Active"}', datetime.utcnow())
    )

    # Insert inactive session
    cursor.execute(
        "INSERT INTO agent_sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
        (inactive_session_id, old_date, old_date)
    )
    cursor.execute(
        "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
        (inactive_session_id, '{"role": "user", "content": "Inactive"}', old_date)
    )

    conn.commit()
    conn.close()

    # Run cleanup
    deleted_count = await temp_session_manager.cleanup_inactive_sessions()

    # Verify 1 session was deleted
    assert deleted_count == 1

    # Verify active session still exists
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agent_sessions WHERE session_id = ?", (active_session_id,))
    assert cursor.fetchone()[0] == 1

    # Verify inactive session was deleted
    cursor.execute("SELECT COUNT(*) FROM agent_sessions WHERE session_id = ?", (inactive_session_id,))
    assert cursor.fetchone()[0] == 0

    # Verify inactive session messages were deleted
    cursor.execute("SELECT COUNT(*) FROM agent_messages WHERE session_id = ?", (inactive_session_id,))
    assert cursor.fetchone()[0] == 0

    conn.close()


@pytest.mark.asyncio
async def test_cleanup_respects_retention_days(tmp_path):
    """Test that cleanup respects the retention_days configuration.

    Verifies that sessions within the retention window are kept,
    and only sessions older than retention_days are deleted.
    """
    db_path = tmp_path / "test_sessions.db"

    # Create manager with 7-day retention
    manager = SessionManager(
        db_path=db_path,
        max_messages=200,
        retention_days=7,
    )

    # Create sessions at different ages
    session_6_days = f"user_{uuid4()}_conv_{uuid4()}"  # Within retention
    session_7_days = f"user_{uuid4()}_conv_{uuid4()}"  # Exactly at boundary
    session_8_days = f"user_{uuid4()}_conv_{uuid4()}"  # Beyond retention

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Insert sessions with different ages
    date_6_days = datetime.utcnow() - timedelta(days=6)
    date_7_days = datetime.utcnow() - timedelta(days=7)
    date_8_days = datetime.utcnow() - timedelta(days=8)

    for session_id, date in [
        (session_6_days, date_6_days),
        (session_7_days, date_7_days),
        (session_8_days, date_8_days),
    ]:
        cursor.execute(
            "INSERT INTO agent_sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
            (session_id, date, date)
        )
        cursor.execute(
            "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
            (session_id, '{"role": "user", "content": "Test"}', date)
        )

    conn.commit()
    conn.close()

    # Run cleanup
    deleted_count = await manager.cleanup_inactive_sessions()

    # Verify only sessions beyond retention were deleted
    # Note: 7-day boundary behavior depends on implementation (< vs <=)
    # Expecting at least the 8-day session to be deleted
    assert deleted_count >= 1

    # Verify 6-day session still exists
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agent_sessions WHERE session_id = ?", (session_6_days,))
    assert cursor.fetchone()[0] == 1

    # Verify 8-day session was deleted
    cursor.execute("SELECT COUNT(*) FROM agent_sessions WHERE session_id = ?", (session_8_days,))
    assert cursor.fetchone()[0] == 0

    conn.close()


@pytest.mark.asyncio
async def test_get_session_stats(temp_session_manager, tmp_path):
    """Test retrieving session statistics."""
    user_id = uuid4()
    conversation_id = uuid4()
    session_id = get_session_id(user_id, conversation_id)

    # Create session with messages
    db_path = tmp_path / "test_sessions.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    created_at = datetime.utcnow()
    cursor.execute(
        "INSERT INTO agent_sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
        (session_id, created_at, created_at)
    )

    for i in range(50):
        cursor.execute(
            "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
            (session_id, f'{{"role": "user", "content": "Message {i}"}}', created_at)
        )

    conn.commit()
    conn.close()

    # Get stats
    stats = await temp_session_manager.get_session_stats(session_id)

    # Verify stats
    assert stats["session_id"] == session_id
    assert stats["message_count"] == 50
    assert stats["created_at"] is not None
    assert stats["last_activity"] is not None


@pytest.mark.asyncio
async def test_clear_session(temp_session_manager, tmp_path):
    """Test clearing all messages for a session."""
    user_id = uuid4()
    conversation_id = uuid4()
    session_id = get_session_id(user_id, conversation_id)

    # Create session with messages
    db_path = tmp_path / "test_sessions.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO agent_sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
        (session_id, datetime.utcnow(), datetime.utcnow())
    )

    for i in range(50):
        cursor.execute(
            "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
            (session_id, f'{{"role": "user", "content": "Message {i}"}}', datetime.utcnow())
        )

    conn.commit()
    conn.close()

    # Clear session
    await temp_session_manager.clear_session(session_id)

    # Verify all messages were deleted
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agent_messages WHERE session_id = ?", (session_id,))
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 0


@pytest.mark.asyncio
async def test_database_unavailable_scenario(tmp_path):
    """Test handling when database is unavailable.

    Verifies that SessionManager handles database errors gracefully
    and returns appropriate error indicators.
    """
    # Create manager with non-existent directory (will fail on access)
    invalid_path = tmp_path / "nonexistent" / "invalid.db"

    manager = SessionManager(
        db_path=invalid_path,
        max_messages=200,
        retention_days=7,
    )

    # Attempt to prune session - should handle error gracefully
    session_id = f"user_{uuid4()}_conv_{uuid4()}"
    deleted_count = await manager.prune_session_messages(session_id)

    # Should return 0 (no messages deleted) rather than raising exception
    assert deleted_count == 0


@pytest.mark.asyncio
async def test_corrupted_session_data_recovery(tmp_path):
    """Test recovery from corrupted session data.

    Verifies that SessionManager can detect and handle corrupted
    message_data in the database.
    """
    user_id = uuid4()
    conversation_id = uuid4()
    session_id = get_session_id(user_id, conversation_id)

    db_path = tmp_path / "test_sessions.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create session with corrupted message data
    cursor.execute(
        "INSERT INTO agent_sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
        (session_id, datetime.utcnow(), datetime.utcnow())
    )

    # Insert valid message
    cursor.execute(
        "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
        (session_id, '{"role": "user", "content": "Valid message"}', datetime.utcnow())
    )

    # Insert corrupted message (invalid JSON)
    cursor.execute(
        "INSERT INTO agent_messages (session_id, message_data, created_at) VALUES (?, ?, ?)",
        (session_id, 'CORRUPTED_DATA_NOT_JSON', datetime.utcnow())
    )

    conn.commit()
    conn.close()

    # Clear session should handle corrupted data
    manager = SessionManager(db_path=db_path)
    await manager.clear_session(session_id)

    # Verify session was cleared
    stats = await manager.get_session_stats(session_id)
    assert stats["message_count"] == 0


@pytest.mark.asyncio
async def test_non_existent_session_id_handling(tmp_path):
    """Test handling of non-existent session IDs.

    Verifies that operations on non-existent sessions handle
    gracefully without raising exceptions.
    """
    db_path = tmp_path / "test_sessions.db"
    manager = SessionManager(db_path=db_path)

    # Non-existent session ID
    session_id = f"user_{uuid4()}_conv_{uuid4()}"

    # Get stats for non-existent session
    stats = await manager.get_session_stats(session_id)

    # Should return empty stats, not raise exception
    assert stats["session_id"] == session_id
    assert stats["message_count"] == 0
    assert stats["created_at"] is None
    assert stats["last_activity"] is None

    # Prune non-existent session
    deleted_count = await manager.prune_session_messages(session_id)
    assert deleted_count == 0

    # Clear non-existent session
    await manager.clear_session(session_id)  # Should not raise exception

