# API Contracts: Chat History and Session Management

**Feature**: 002-chat-history | **Date**: 2026-01-31 | **Phase**: 1 (Design)

## Overview

This feature does not introduce new API endpoints or modify existing API contracts. Session management is handled internally by the backend and is transparent to the frontend.

## Existing API Endpoints (No Changes)

### POST /chatkit/threads
**Purpose**: Create a new conversation thread

**Request**:
```json
{
  "title": "Optional thread title"
}
```

**Response** (201 Created):
```json
{
  "thread_id": "uuid",
  "title": "string or null",
  "created_at": "ISO-8601 timestamp"
}
```

**Session Impact**: None - session created lazily on first message

---

### POST /chatkit/threads/{thread_id}/messages
**Purpose**: Send a message to a thread and receive AI response

**Request**:
```json
{
  "text": "User message (1-2000 chars)"
}
```

**Response** (200 OK - Server-Sent Events):
```
data: {"content": "Agent response chunk"}

data: {"content": "More response"}

data: {"error": "Error message if failed"}
```

**Session Impact**:
- ✅ Now uses persistent SQLiteSession (previously in-memory)
- ✅ Maintains conversation context across messages
- ✅ Automatically prunes messages at 200 limit
- ✅ Survives service restarts

**Behavior Changes**:
- **Before**: Agent had no memory of previous messages after restart
- **After**: Agent remembers full conversation history (up to 200 messages)

---

### GET /chatkit/threads/{thread_id}
**Purpose**: Retrieve thread details with message history

**Query Parameters**:
- `limit`: Maximum messages to return (default: 50, max: 50)

**Response** (200 OK):
```json
{
  "thread_id": "uuid",
  "title": "string or null",
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "messages": [
    {
      "message_id": "uuid",
      "role": "user" | "assistant",
      "content": "message text",
      "created_at": "ISO-8601 timestamp"
    }
  ]
}
```

**Session Impact**: None - reads from PostgreSQL, not agent session

---

## Internal Session Management (Not Exposed to API)

### Session Lifecycle

**Session Creation**:
- Triggered automatically on first message to a thread
- Session ID format: `user_{user_id}_conv_{conversation_id}`
- Stored in SQLite at `./data/agent_sessions.db`

**Session Retrieval**:
- Happens transparently in `send_message` endpoint
- No API changes required
- Frontend unaware of session management

**Session Cleanup**:
- Background job runs daily at 2 AM UTC
- Deletes sessions inactive for > 7 days
- No API endpoint for manual cleanup

### Error Handling

**Database Unavailable**:
```json
{
  "content": "Agent response",
  "warning": "Context unavailable - conversation history may be incomplete"
}
```

**Corrupted Session**:
- Session automatically cleared and recreated
- User sees fresh conversation start
- No error exposed to frontend

## Frontend Integration

### No Changes Required

The frontend continues to use the same API endpoints with identical request/response formats. Session management is completely transparent.

**Example Frontend Code** (unchanged):
```typescript
// Create thread
const response = await fetch('/chatkit/threads', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ title: 'My Tasks' }),
});
const { thread_id } = await response.json();

// Send message
const eventSource = new EventSource(
  `/chatkit/threads/${thread_id}/messages`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: 'Create a task' }),
  }
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content); // Agent response
};
```

## Configuration Changes

### Environment Variables (Backend Only)

New configuration options in `.env`:

```bash
# Agent Session Configuration
AGENT_SESSION_DB_PATH=./data/agent_sessions.db
AGENT_SESSION_MAX_MESSAGES=200
AGENT_SESSION_RETENTION_DAYS=7
AGENT_SESSION_CLEANUP_HOUR=2
```

**Impact**: Backend only - no frontend configuration changes

## Backward Compatibility

### ✅ Fully Backward Compatible

- All existing API endpoints unchanged
- Request/response formats identical
- Frontend code requires no modifications
- Existing conversations continue to work

### Migration Path

**For Existing Conversations**:
1. First message after deployment creates persistent session
2. Previous in-memory context is lost (expected - was ephemeral)
3. New messages build persistent context going forward

**No Breaking Changes**: This is a pure enhancement

## Testing Contracts

### Contract Tests (No Changes to API)

Existing contract tests continue to pass without modification:

```python
def test_create_thread(client, auth_headers):
    """Test thread creation endpoint."""
    response = client.post(
        "/chatkit/threads",
        json={"title": "Test Thread"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert "thread_id" in response.json()

def test_send_message(client, auth_headers, thread_id):
    """Test message sending endpoint."""
    response = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": "Test message"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
```

### New Session Behavior Tests

Additional tests verify session persistence (internal behavior):

```python
@pytest.mark.asyncio
async def test_session_persistence_across_messages(client, auth_headers, thread_id):
    """Test agent remembers context across messages."""
    # First message
    response1 = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": "Create a task to buy groceries"},
        headers=auth_headers,
    )
    assert response1.status_code == 200

    # Second message - agent should remember "that task"
    response2 = client.post(
        f"/chatkit/threads/{thread_id}/messages",
        json={"text": "Add milk to that task"},
        headers=auth_headers,
    )
    assert response2.status_code == 200
    # Verify agent understood context (implementation-specific assertion)
```

## Summary

**API Contract Changes**: None

**Behavior Enhancements**:
- ✅ Persistent conversation context
- ✅ Survives service restarts
- ✅ Automatic message limit enforcement
- ✅ Automatic session cleanup

**Frontend Impact**: Zero - completely transparent

**Backend Impact**: Internal session management improvements

## References

- [Feature Specification](./spec.md)
- [Data Model](./data-model.md)
- [Quick Start Guide](./quickstart.md)
- [Research Document](./research.md)
