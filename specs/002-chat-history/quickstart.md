# Quick Start: Chat History and Session Management

**Feature**: 002-chat-history | **Date**: 2026-01-31 | **Phase**: 1 (Design)

## Overview

This guide helps developers understand and work with the chat history and session management system. The implementation uses OpenAI Agents SDK's SQLiteSession for persistent conversation context.

## Architecture at a Glance

```
User Message → FastAPI → PostgreSQL (save message)
                    ↓
              Get SQLiteSession
                    ↓
         Runner.run(agent, message, session)
                    ↓
         Agent processes with context
                    ↓
         PostgreSQL (save response) → User
```

## Key Concepts

### Dual Database Strategy

**PostgreSQL (Neon)**: User-facing data
- Conversations (threads)
- Messages (user + assistant)
- Tasks
- Users

**SQLite (Local File)**: Agent internal state
- Session context (managed by OpenAI Agents SDK)
- Conversation history for agent memory
- Automatically managed by SQLiteSession

### Session Lifecycle

1. **Creation**: First message in a conversation creates session
2. **Usage**: Each message retrieves session and passes to Runner
3. **Maintenance**: Messages pruned at 200 limit
4. **Cleanup**: Inactive sessions deleted after 7 days

## Getting Started

### Prerequisites

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Ensure data directory exists
mkdir -p data
```

### Configuration

Add to `.env`:

```bash
# Agent Session Configuration
AGENT_SESSION_DB_PATH=./data/agent_sessions.db
AGENT_SESSION_MAX_MESSAGES=200
AGENT_SESSION_RETENTION_DAYS=7
AGENT_SESSION_CLEANUP_HOUR=2
```

### Basic Usage

#### 1. Get a Session

```python
from uuid import UUID
from src.agent.session import get_agent_session

# Get or create session for a conversation
user_id = UUID("...")
conversation_id = UUID("...")

session = get_agent_session(user_id, conversation_id)
```

#### 2. Run Agent with Session

```python
from agents import Runner
from src.agent.todo_agent import todo_agent

# Run agent with conversation context
result = await Runner.run(
    todo_agent,
    "What tasks do I have?",
    session=session,
    context={"user_id": str(user_id)},
)

print(result.final_output)
```

#### 3. Session Automatically Maintains Context

```python
# First message
result1 = await Runner.run(
    todo_agent,
    "Create a task to buy groceries",
    session=session,
    context={"user_id": str(user_id)},
)
# Agent creates task

# Second message - agent remembers context
result2 = await Runner.run(
    todo_agent,
    "Add milk to that task",  # "that task" refers to groceries
    session=session,
    context={"user_id": str(user_id)},
)
# Agent updates the groceries task
```

## Common Tasks

### Check Session Message Count

```python
from src.agent.session_manager import SessionManager
from src.config import settings

manager = SessionManager(
    db_path=settings.agent_session_db_path,
    max_messages=settings.agent_session_max_messages,
    retention_days=settings.agent_session_retention_days,
)

stats = await manager.get_session_stats(session_id)
print(f"Messages: {stats['message_count']}")
print(f"Last activity: {stats['last_activity']}")
```

### Manually Prune Session

```python
# Prune messages if over limit
deleted_count = await manager.prune_session_messages(session_id)
print(f"Pruned {deleted_count} old messages")
```

### Clear Session (Emergency Recovery)

```python
# Clear all messages for a session
await manager.clear_session(session_id)
print("Session cleared - fresh start")
```

### Run Cleanup Job Manually

```python
# Clean up inactive sessions
deleted_count = await manager.cleanup_inactive_sessions()
print(f"Cleaned up {deleted_count} inactive sessions")
```

## API Integration

### ChatKit Endpoint Example

```python
@router.post("/threads/{thread_id}/messages")
async def send_message(
    thread_id: UUID,
    request: SendMessageRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> StreamingResponse:
    # Verify thread ownership
    conversation = session.query(Conversation).filter(
        Conversation.id == thread_id,
        Conversation.user_id == current_user.id,
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Save user message to PostgreSQL
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.text,
    )
    session.add(user_message)
    session.commit()

    # Get agent session for context
    agent_session = get_agent_session(current_user.id, conversation.id)

    # Run agent with session
    result = await Runner.run(
        todo_agent,
        request.text,
        session=agent_session,
        context={"user_id": str(current_user.id)},
    )

    # Save assistant response to PostgreSQL
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=result.final_output,
    )
    session.add(assistant_message)
    session.commit()

    # Prune session if needed
    await manager.prune_session_messages(
        get_session_id(current_user.id, conversation.id)
    )

    return StreamingResponse(...)
```

## Testing

### Unit Test Example

```python
import pytest
from uuid import uuid4
from src.agent.session import get_agent_session, get_session_id

def test_session_id_format():
    """Test session ID generation format."""
    user_id = uuid4()
    conv_id = uuid4()

    session_id = get_session_id(user_id, conv_id)

    assert session_id.startswith("user_")
    assert "_conv_" in session_id
    assert str(user_id) in session_id
    assert str(conv_id) in session_id

@pytest.mark.asyncio
async def test_session_persistence(tmp_path):
    """Test session persists across restarts."""
    db_path = tmp_path / "test_sessions.db"
    user_id = uuid4()
    conv_id = uuid4()

    # Create session and add message
    session1 = get_agent_session(user_id, conv_id, db_path=str(db_path))
    await Runner.run(todo_agent, "Test message", session=session1)

    # Simulate restart - create new session instance
    session2 = get_agent_session(user_id, conv_id, db_path=str(db_path))
    items = await session2.get_items()

    assert len(items) == 1  # Message persisted
    assert items[0]["content"] == "Test message"
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_session_isolation():
    """Test sessions are isolated between users."""
    user1_id = uuid4()
    user2_id = uuid4()
    conv_id = uuid4()

    # User 1 sends message
    session1 = get_agent_session(user1_id, conv_id)
    await Runner.run(todo_agent, "User 1 message", session=session1)

    # User 2 with different session
    session2 = get_agent_session(user2_id, conv_id)
    items = await session2.get_items()

    assert len(items) == 0  # User 2 doesn't see User 1's messages
```

## Troubleshooting

### Session Database Locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Cause**: High concurrent writes to SQLite

**Solution**:
```python
# Add retry logic
import time
from sqlite3 import OperationalError

max_retries = 3
for attempt in range(max_retries):
    try:
        result = await Runner.run(agent, message, session=session)
        break
    except OperationalError as e:
        if attempt < max_retries - 1:
            time.sleep(0.1 * (attempt + 1))  # Exponential backoff
        else:
            # Fallback: run without session
            result = await Runner.run(agent, message)
```

### Corrupted Session Data

**Symptom**: `json.JSONDecodeError` when retrieving session

**Cause**: Corrupted message_data in SQLite

**Solution**:
```python
try:
    result = await Runner.run(agent, message, session=session)
except json.JSONDecodeError:
    # Clear corrupted session
    await session.clear_session()
    # Retry with fresh session
    result = await Runner.run(agent, message, session=session)
```

### Session Not Persisting

**Symptom**: Context lost after restart

**Cause**: Using in-memory database (`:memory:`)

**Solution**:
```python
# Check configuration
print(settings.agent_session_db_path)
# Should be: ./data/agent_sessions.db
# NOT: :memory:

# Verify file exists after messages
import os
assert os.path.exists(settings.agent_session_db_path)
```

### Messages Not Being Pruned

**Symptom**: Session exceeds 200 messages

**Cause**: Pruning not called after message add

**Solution**:
```python
# Always prune after adding messages
result = await Runner.run(agent, message, session=session)

# Prune immediately
await manager.prune_session_messages(session_id)
```

## Performance Tips

### 1. Use Connection Pooling

```python
# For high-concurrency scenarios
from sqlalchemy.pool import StaticPool

# Configure SQLite with connection pool
# (Note: SQLiteSession handles this internally)
```

### 2. Batch Cleanup Operations

```python
# Run cleanup during low-traffic hours
# Configure in settings: AGENT_SESSION_CLEANUP_HOUR=2
```

### 3. Monitor Database Size

```bash
# Check database size
ls -lh data/agent_sessions.db

# If > 500MB, investigate retention policy
```

### 4. Index Optimization

```sql
-- Ensure indexes exist (auto-created by SessionManager)
CREATE INDEX IF NOT EXISTS ix_agent_sessions_updated
ON agent_sessions(updated_at);

CREATE INDEX IF NOT EXISTS ix_agent_messages_session_created
ON agent_messages(session_id, created_at);
```

## Best Practices

### ✅ DO

- Always use file-based storage in production
- Prune sessions after each message
- Run cleanup job daily
- Handle database errors gracefully
- Monitor session database size
- Test session isolation thoroughly

### ❌ DON'T

- Don't use in-memory sessions in production
- Don't skip pruning (causes performance degradation)
- Don't expose session IDs to frontend
- Don't share sessions between users
- Don't store sensitive data in session context
- Don't manually modify SQLite database

## Monitoring

### Key Metrics to Track

```python
# Session metrics
active_sessions = await manager.get_active_session_count()
avg_messages = await manager.get_average_messages_per_session()

# Performance metrics
session_retrieval_time = measure_latency(get_agent_session)
message_add_time = measure_latency(Runner.run)

# Health metrics
db_size = os.path.getsize(settings.agent_session_db_path)
cleanup_success_rate = cleanup_successes / cleanup_attempts
```

### Alerting Thresholds

- Database size > 500 MB → Investigate retention
- Session retrieval p95 > 100ms → Performance issue
- Cleanup job failure → Manual intervention needed
- Active sessions > 10,000 → Capacity planning

## Migration Guide

### From In-Memory to Persistent Sessions

**Current Code**:
```python
# Old: In-memory (lost on restart)
session = SQLiteSession(session_id)  # defaults to :memory:
```

**New Code**:
```python
# New: Persistent file-based storage
from pathlib import Path
from src.config import settings

db_path = Path(settings.agent_session_db_path)
db_path.parent.mkdir(parents=True, exist_ok=True)

session = SQLiteSession(session_id, db_path=str(db_path))
```

**No Data Migration Needed**: In-memory sessions were ephemeral

## References

- [Feature Specification](./spec.md)
- [Research Document](./research.md)
- [Data Model](./data-model.md)
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/sessions)
- [SQLite WAL Mode](https://www.sqlite.org/wal.html)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test examples in `tests/` directory
3. Consult OpenAI Agents SDK documentation
4. File issue in project repository

## Next Steps

After reading this guide:
1. Review [data-model.md](./data-model.md) for schema details
2. Run tests: `pytest tests/unit/test_session.py`
3. Implement session management in your feature
4. Add monitoring for session metrics
