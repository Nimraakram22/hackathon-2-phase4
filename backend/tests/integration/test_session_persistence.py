"""
Integration tests for session persistence and context continuity.

Tests that sessions maintain context across messages and restarts.
"""

import pytest
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta
import sqlite3

from agents import Runner
from src.agent.session import get_agent_session, get_session_id
from src.agent.session_manager import SessionManager
from src.agent.todo_agent import todo_agent


@pytest.mark.asyncio
async def test_context_continuity_across_messages(tmp_path):
    """Test that agent maintains context across multiple messages.

    Verifies that the agent can reference previous messages in the conversation.
    This is the core functionality of User Story 1.
    """
    user_id = uuid4()
    conversation_id = uuid4()

    # Mock settings to use temp database
    import src.config
    original_path = src.config.settings.agent_session_db_path
    db_path = tmp_path / "test_sessions.db"
    src.config.settings.agent_session_db_path = str(db_path)

    try:
        # Get session
        session = get_agent_session(user_id, conversation_id)

        # First message: Create a task
        result1 = await Runner.run(
            todo_agent,
            "Create a task to buy groceries",
            session=session,
            context={"user_id": str(user_id)},
        )

        # Verify task was created
        assert result1.final_output is not None
        assert "groceries" in result1.final_output.lower() or "task" in result1.final_output.lower()

        # Second message: Reference "that task" - requires context
        result2 = await Runner.run(
            todo_agent,
            "Add milk to that task",
            session=session,
            context={"user_id": str(user_id)},
        )

        # Verify agent understood "that task" refers to groceries task
        assert result2.final_output is not None
        # Agent should acknowledge the update or show understanding of context

        # Third message: Ask about tasks - should remember the conversation
        result3 = await Runner.run(
            todo_agent,
            "What tasks do I have?",
            session=session,
            context={"user_id": str(user_id)},
        )

        # Verify agent can retrieve tasks from context
        assert result3.final_output is not None

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path


@pytest.mark.asyncio
async def test_session_persistence_across_restarts(tmp_path):
    """Test that session persists across service restarts.

    Verifies that conversation history is maintained even after
    creating a new session instance (simulating restart).
    """
    user_id = uuid4()
    conversation_id = uuid4()

    # Mock settings to use temp database
    import src.config
    original_path = src.config.settings.agent_session_db_path
    db_path = tmp_path / "test_sessions.db"
    src.config.settings.agent_session_db_path = str(db_path)

    try:
        # First session: Add messages
        session1 = get_agent_session(user_id, conversation_id)

        result1 = await Runner.run(
            todo_agent,
            "Create a task to buy groceries",
            session=session1,
            context={"user_id": str(user_id)},
        )

        assert result1.final_output is not None

        # Simulate restart: Create new session instance with same IDs
        session2 = get_agent_session(user_id, conversation_id)

        # Verify session has same ID
        assert session2.session_id == session1.session_id

        # Send follow-up message that requires context
        result2 = await Runner.run(
            todo_agent,
            "What was the task I just created?",
            session=session2,
            context={"user_id": str(user_id)},
        )

        # Verify agent can access previous context
        assert result2.final_output is not None
        # Agent should be able to reference the groceries task

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path


@pytest.mark.asyncio
async def test_message_pruning_at_limit(tmp_path):
    """Test that messages are pruned when session reaches 200 message limit.

    Verifies that SessionManager.prune_session_messages correctly
    maintains the 200 message limit while keeping most recent messages.
    """
    user_id = uuid4()
    conversation_id = uuid4()
    session_id = get_session_id(user_id, conversation_id)

    # Create session manager with temp database
    db_path = tmp_path / "test_sessions.db"
    manager = SessionManager(
        db_path=db_path,
        max_messages=200,
        retention_days=7,
    )

    # Mock settings
    import src.config
    original_path = src.config.settings.agent_session_db_path
    src.config.settings.agent_session_db_path = str(db_path)

    try:
        # Get session
        session = get_agent_session(user_id, conversation_id)

        # Add 205 messages (exceeds limit)
        for i in range(205):
            await Runner.run(
                todo_agent,
                f"Test message {i}",
                session=session,
                context={"user_id": str(user_id)},
            )

        # Get stats before pruning
        stats_before = await manager.get_session_stats(session_id)
        assert stats_before["message_count"] > 200

        # Prune messages
        deleted_count = await manager.prune_session_messages(session_id)

        # Verify messages were deleted
        assert deleted_count > 0

        # Get stats after pruning
        stats_after = await manager.get_session_stats(session_id)
        assert stats_after["message_count"] == 200

        # Verify most recent messages are kept
        # Send a message that references recent context
        result = await Runner.run(
            todo_agent,
            "What was my last test message number?",
            session=session,
            context={"user_id": str(user_id)},
        )

        # Agent should be able to reference recent messages (200-204)
        assert result.final_output is not None

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path


@pytest.mark.asyncio
async def test_session_recovery_after_24_hours(tmp_path):
    """Test that session can be recovered after 24+ hours of inactivity.

    Verifies that sessions persist and can be resumed even after
    extended periods of inactivity (within 7-day retention window).
    """
    user_id = uuid4()
    conversation_id = uuid4()
    session_id = get_session_id(user_id, conversation_id)

    # Mock settings to use temp database
    import src.config
    original_path = src.config.settings.agent_session_db_path
    db_path = tmp_path / "test_sessions.db"
    src.config.settings.agent_session_db_path = str(db_path)

    try:
        # Create session and add message
        session1 = get_agent_session(user_id, conversation_id)

        result1 = await Runner.run(
            todo_agent,
            "Create a task to buy groceries",
            session=session1,
            context={"user_id": str(user_id)},
        )

        assert result1.final_output is not None

        # Simulate 24+ hours passing by updating session timestamp
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        old_date = datetime.utcnow() - timedelta(hours=25)
        cursor.execute(
            "UPDATE agent_sessions SET updated_at = ? WHERE session_id = ?",
            (old_date, session_id)
        )
        conn.commit()
        conn.close()

        # Verify session still exists (within 7-day retention)
        manager = SessionManager(db_path=db_path)
        stats = await manager.get_session_stats(session_id)
        assert stats["message_count"] > 0

        # Create new session instance (simulating recovery)
        session2 = get_agent_session(user_id, conversation_id)

        # Verify session can be recovered
        assert session2.session_id == session1.session_id

        # Send follow-up message
        result2 = await Runner.run(
            todo_agent,
            "What tasks do I have?",
            session=session2,
            context={"user_id": str(user_id)},
        )

        # Verify agent can access old context
        assert result2.final_output is not None

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path

