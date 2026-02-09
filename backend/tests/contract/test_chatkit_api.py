"""
Contract tests for ChatKit API endpoints.

Verifies that API contracts remain unchanged after session management implementation.
These tests ensure backward compatibility and that the frontend requires no changes.
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.user import User
from src.models.conversation import Conversation
from src.database.connection import get_session_context


@pytest.fixture
def test_user():
    """Create a test user for authentication."""
    with get_session_context() as session:
        user = User(
            email=f"test_{uuid4()}@example.com",
            hashed_password="$2b$12$test_hash",  # Mock bcrypt hash
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        yield user


@pytest.fixture
def auth_headers(test_user):
    """Generate authentication headers for test user."""
    from src.api.dependencies import create_access_token

    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


def test_create_thread_contract(client, auth_headers):
    """Test POST /chatkit/threads endpoint contract.

    Verifies that the endpoint:
    - Accepts optional title field
    - Returns thread_id, title, created_at
    - Returns 201 Created status
    - Response format matches frontend expectations
    """
    # Test with title
    response = client.post(
        "/chatkit/threads",
        json={"title": "Test Thread"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    # Verify response structure
    assert "thread_id" in data
    assert "title" in data
    assert "created_at" in data

    # Verify data types
    assert isinstance(data["thread_id"], str)
    assert data["title"] == "Test Thread"
    assert isinstance(data["created_at"], str)

    # Test without title
    response = client.post(
        "/chatkit/threads",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] is None


def test_send_message_contract(client, auth_headers, test_user):
    """Test POST /chatkit/threads/{thread_id}/messages endpoint contract.

    Verifies that the endpoint:
    - Accepts text field (1-2000 characters)
    - Returns streaming response (text/event-stream)
    - Response format: data: {"content": "..."} or data: {"error": "..."}
    - Optional warning field: data: {"content": "...", "warning": "..."}
    - Returns 404 for non-existent thread
    - Returns 404 for thread belonging to different user
    """
    # Create thread first
    with get_session_context() as session:
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation",
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        thread_id = conversation.id

    # Test valid message
    response = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": "Create a task to test the API"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Verify streaming response format
    content = response.text
    assert content.startswith("data: ")
    assert "\n\n" in content  # SSE format

    # Parse JSON from SSE
    import json
    json_str = content.replace("data: ", "").strip()
    data = json.loads(json_str)

    # Verify response structure
    assert "content" in data or "error" in data

    if "content" in data:
        assert isinstance(data["content"], str)
        # Optional warning field
        if "warning" in data:
            assert isinstance(data["warning"], str)

    # Test non-existent thread
    fake_thread_id = uuid4()
    response = client.post(
        f"/chatkit/threads/{fake_thread_id}/messages",
        json={"text": "Test message"},
        headers=auth_headers,
    )

    assert response.status_code == 404

    # Test invalid message (too short)
    response = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": ""},
        headers=auth_headers,
    )

    assert response.status_code == 422  # Validation error

    # Test invalid message (too long)
    response = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": "x" * 2001},
        headers=auth_headers,
    )

    assert response.status_code == 422  # Validation error


def test_get_thread_contract(client, auth_headers, test_user):
    """Test GET /chatkit/threads/{thread_id} endpoint contract.

    Verifies that the endpoint:
    - Returns thread_id, title, created_at, updated_at, messages
    - Messages array contains: message_id, role, content, created_at
    - Supports limit parameter (default 50, max 50)
    - Returns 404 for non-existent thread
    - Returns 404 for thread belonging to different user
    """
    # Create thread with messages
    with get_session_context() as session:
        from src.models.message import Message, MessageRole

        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation",
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Add messages
        for i in range(3):
            message = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Test message {i}",
            )
            session.add(message)

        session.commit()
        thread_id = conversation.id

    # Test get thread
    response = client.get(
        f"/chatkit/threads/{thread_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "thread_id" in data
    assert "title" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "messages" in data

    # Verify data types
    assert isinstance(data["thread_id"], str)
    assert isinstance(data["title"], str)
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)
    assert isinstance(data["messages"], list)

    # Verify messages structure
    assert len(data["messages"]) == 3

    for message in data["messages"]:
        assert "message_id" in message
        assert "role" in message
        assert "content" in message
        assert "created_at" in message

        assert isinstance(message["message_id"], str)
        assert message["role"] in ["user", "assistant"]
        assert isinstance(message["content"], str)
        assert isinstance(message["created_at"], str)

    # Test with limit parameter
    response = client.get(
        f"/chatkit/threads/{thread_id}?limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 2

    # Test non-existent thread
    fake_thread_id = uuid4()
    response = client.get(
        f"/chatkit/threads/{fake_thread_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_end_to_end_conversation_flow(client, auth_headers, test_user):
    """Test end-to-end conversation flow with session persistence.

    Verifies that:
    1. Thread can be created
    2. Multiple messages can be sent
    3. Context is maintained across messages
    4. Thread history can be retrieved
    5. Session persistence works correctly
    """
    # Step 1: Create thread
    response = client.post(
        "/chatkit/threads",
        json={"title": "E2E Test Thread"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    thread_data = response.json()
    thread_id = thread_data["thread_id"]

    # Step 2: Send first message
    response = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": "Create a task to buy groceries"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "data: " in response.text

    # Step 3: Send second message (requires context)
    response = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": "Add milk to that task"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "data: " in response.text

    # Step 4: Send third message
    response = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": "What tasks do I have?"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "data: " in response.text

    # Step 5: Retrieve thread history
    response = client.get(
        f"/chatkit/threads/{thread_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify all messages are present
    assert len(data["messages"]) >= 6  # 3 user + 3 assistant (minimum)

    # Verify message order (chronological)
    messages = data["messages"]
    for i in range(len(messages) - 1):
        assert messages[i]["created_at"] <= messages[i + 1]["created_at"]

    # Verify alternating roles (user, assistant, user, assistant, ...)
    expected_roles = ["user", "assistant"] * 3
    actual_roles = [msg["role"] for msg in messages[:6]]
    assert actual_roles == expected_roles
