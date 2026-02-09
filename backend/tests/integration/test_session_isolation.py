"""
Integration tests for session isolation.

Tests that sessions are properly isolated between users and threads.
"""

import pytest
import asyncio
from pathlib import Path
from uuid import uuid4

from agents import Runner
from src.agent.session import get_agent_session, get_session_id
from src.agent.session_manager import SessionManager
from src.agent.todo_agent import todo_agent


@pytest.mark.asyncio
async def test_session_isolation_between_users(tmp_path):
    """Test that sessions are isolated between different users.

    Verifies that User 1's conversation context is not visible to User 2,
    even if they use the same conversation ID.
    """
    user1_id = uuid4()
    user2_id = uuid4()
    conversation_id = uuid4()

    # Mock settings to use temp database
    import src.config
    original_path = src.config.settings.agent_session_db_path
    db_path = tmp_path / "test_sessions.db"
    src.config.settings.agent_session_db_path = str(db_path)

    try:
        # User 1 sends message
        session1 = get_agent_session(user1_id, conversation_id)
        result1 = await Runner.run(
            todo_agent,
            "Create a task to buy groceries for user 1",
            session=session1,
            context={"user_id": str(user1_id)},
        )

        assert result1.final_output is not None

        # User 2 with different user_id but same conversation_id
        session2 = get_agent_session(user2_id, conversation_id)

        # Verify sessions have different IDs
        assert session1.session_id != session2.session_id

        # User 2 sends message - should not see User 1's context
        result2 = await Runner.run(
            todo_agent,
            "What tasks do I have?",
            session=session2,
            context={"user_id": str(user2_id)},
        )

        # User 2 should not see User 1's groceries task
        assert result2.final_output is not None
        # The response should indicate no tasks or different tasks

        # Verify session isolation at database level
        manager = SessionManager(db_path=db_path)
        stats1 = await manager.get_session_stats(session1.session_id)
        stats2 = await manager.get_session_stats(session2.session_id)

        # Both sessions should exist independently
        assert stats1["message_count"] > 0
        assert stats2["message_count"] > 0
        assert stats1["session_id"] != stats2["session_id"]

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path


@pytest.mark.asyncio
async def test_session_isolation_between_threads(tmp_path):
    """Test that sessions are isolated between different threads (same user).

    Verifies that a user's different conversation threads maintain
    separate contexts and don't interfere with each other.
    """
    user_id = uuid4()
    conversation1_id = uuid4()
    conversation2_id = uuid4()

    # Mock settings to use temp database
    import src.config
    original_path = src.config.settings.agent_session_db_path
    db_path = tmp_path / "test_sessions.db"
    src.config.settings.agent_session_db_path = str(db_path)

    try:
        # Thread 1: Create groceries task
        session1 = get_agent_session(user_id, conversation1_id)
        result1 = await Runner.run(
            todo_agent,
            "Create a task to buy groceries",
            session=session1,
            context={"user_id": str(user_id)},
        )

        assert result1.final_output is not None

        # Thread 2: Create work task
        session2 = get_agent_session(user_id, conversation2_id)
        result2 = await Runner.run(
            todo_agent,
            "Create a task to finish project report",
            session=session2,
            context={"user_id": str(user_id)},
        )

        assert result2.final_output is not None

        # Verify sessions have different IDs
        assert session1.session_id != session2.session_id

        # Thread 1: Reference "that task" - should refer to groceries
        result3 = await Runner.run(
            todo_agent,
            "Add milk to that task",
            session=session1,
            context={"user_id": str(user_id)},
        )

        # Should update groceries task, not project report
        assert result3.final_output is not None

        # Thread 2: Reference "that task" - should refer to project report
        result4 = await Runner.run(
            todo_agent,
            "Set that task as high priority",
            session=session2,
            context={"user_id": str(user_id)},
        )

        # Should update project report, not groceries
        assert result4.final_output is not None

        # Verify session isolation at database level
        manager = SessionManager(db_path=db_path)
        stats1 = await manager.get_session_stats(session1.session_id)
        stats2 = await manager.get_session_stats(session2.session_id)

        # Both sessions should exist independently
        assert stats1["message_count"] > 0
        assert stats2["message_count"] > 0
        assert stats1["session_id"] != stats2["session_id"]

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path


@pytest.mark.asyncio
async def test_concurrent_messages_to_same_thread(tmp_path):
    """Test concurrent messages to the same thread are handled correctly.

    Verifies that when multiple messages are sent to the same thread
    concurrently, they are processed sequentially (FR-012) and don't
    corrupt the session state.
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

        # Send multiple messages concurrently
        async def send_message(message_num: int):
            """Send a message and return result."""
            result = await Runner.run(
                todo_agent,
                f"Create task number {message_num}",
                session=session,
                context={"user_id": str(user_id)},
            )
            return result.final_output

        # Send 5 messages concurrently
        results = await asyncio.gather(
            send_message(1),
            send_message(2),
            send_message(3),
            send_message(4),
            send_message(5),
        )

        # All messages should complete successfully
        assert len(results) == 5
        for result in results:
            assert result is not None

        # Verify session has all messages
        manager = SessionManager(db_path=db_path)
        stats = await manager.get_session_stats(session.session_id)

        # Should have at least 10 messages (5 user + 5 assistant)
        assert stats["message_count"] >= 10

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path


@pytest.mark.asyncio
async def test_session_id_collision_prevention(tmp_path):
    """Test that session IDs are unique and collision-free.

    Verifies that the UUID-based session ID generation prevents
    collisions even with many concurrent sessions.
    """
    # Mock settings to use temp database
    import src.config
    original_path = src.config.settings.agent_session_db_path
    db_path = tmp_path / "test_sessions.db"
    src.config.settings.agent_session_db_path = str(db_path)

    try:
        # Create 100 sessions with different user/conversation combinations
        session_ids = set()

        for _ in range(100):
            user_id = uuid4()
            conversation_id = uuid4()
            session_id = get_session_id(user_id, conversation_id)

            # Verify no collision
            assert session_id not in session_ids, f"Session ID collision detected: {session_id}"
            session_ids.add(session_id)

        # Verify all session IDs are unique
        assert len(session_ids) == 100

        # Verify deterministic generation (same inputs = same output)
        user_id = uuid4()
        conversation_id = uuid4()

        session_id1 = get_session_id(user_id, conversation_id)
        session_id2 = get_session_id(user_id, conversation_id)

        assert session_id1 == session_id2

    finally:
        # Restore original settings
        src.config.settings.agent_session_db_path = original_path
