# Data Model: Chat History and Session Management

**Feature**: 002-chat-history | **Date**: 2026-01-31 | **Phase**: 1 (Design)

## Overview

This document defines the data models and schema for chat history and session management. The system uses a dual-database approach:
- **PostgreSQL (Neon)**: User-facing data (conversations, messages, tasks, users)
- **SQLite**: Agent session context (OpenAI Agents SDK internal state)

## Database Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  (FastAPI + OpenAI Agents SDK)                              │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             │                                │
    ┌────────▼────────┐              ┌───────▼────────┐
    │   PostgreSQL    │              │     SQLite     │
    │  (Neon Server)  │              │  (Local File)  │
    │                 │              │                │
    │  - Users        │              │  - Sessions    │
    │  - Conversations│              │  - Messages    │
    │  - Messages     │              │  (Agent State) │
    │  - Tasks        │              │                │
    └─────────────────┘              └────────────────┘
         (User Data)                  (Agent Context)
```

## PostgreSQL Models (Existing - No Changes)

### Conversation Entity

**Purpose**: Represents a user's conversation thread (user-facing)

**Schema** (SQLModel):
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    __table_args__ = (
        Index("ix_conversations_user_deleted", "user_id", "is_deleted"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")
```

**Key Attributes**:
- `id`: Unique conversation identifier (UUID)
- `user_id`: Owner of the conversation (foreign key)
- `title`: Auto-generated from first message
- `updated_at`: Updated on each new message
- `is_deleted`: Soft delete flag for 7-day retention

**Indexes**:
- Primary: `id`
- Composite: `(user_id, is_deleted)` - for user's active conversations
- Single: `updated_at` - for cleanup queries

### Message Entity

**Purpose**: Stores user and assistant messages (user-facing)

**Schema** (SQLModel):
```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column=Column(Enum(MessageRole)))
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

**Key Attributes**:
- `id`: Unique message identifier (UUID)
- `conversation_id`: Parent conversation (foreign key)
- `role`: USER or ASSISTANT
- `content`: Message text (max 10,000 chars)
- `created_at`: Message timestamp

**Indexes**:
- Primary: `id`
- Composite: `(conversation_id, created_at)` - for chronological retrieval

## SQLite Models (Agent Session Context)

### Agent Session Entity

**Purpose**: Tracks agent conversation sessions (internal to OpenAI Agents SDK)

**Schema** (SQLite - managed by SQLiteSession):
```sql
CREATE TABLE IF NOT EXISTS agent_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_agent_sessions_updated
ON agent_sessions(updated_at);
```

**Key Attributes**:
- `session_id`: Format `user_{user_id}_conv_{conversation_id}`
- `created_at`: Session creation timestamp
- `updated_at`: Last message timestamp (for cleanup)

**Indexes**:
- Primary: `session_id`
- Single: `updated_at` - for cleanup queries (ADDED by us)

### Agent Message Entity

**Purpose**: Stores agent conversation context (internal to OpenAI Agents SDK)

**Schema** (SQLite - managed by SQLiteSession):
```sql
CREATE TABLE IF NOT EXISTS agent_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    message_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id)
);

CREATE INDEX IF NOT EXISTS ix_agent_messages_session
ON agent_messages(session_id);

CREATE INDEX IF NOT EXISTS ix_agent_messages_session_created
ON agent_messages(session_id, created_at);
```

**Key Attributes**:
- `id`: Auto-increment integer ID
- `session_id`: Foreign key to agent_sessions
- `message_data`: JSON-serialized message object
- `created_at`: Message timestamp

**Message Data Format** (JSON):
```json
{
  "role": "user" | "assistant",
  "content": "message text",
  "metadata": {
    "user_id": "uuid",
    "conversation_id": "uuid",
    "timestamp": "ISO-8601"
  }
}
```

**Indexes**:
- Primary: `id`
- Single: `session_id` - for session lookups
- Composite: `(session_id, created_at)` - for chronological retrieval (ADDED by us)

## Session Management Models (New)

### SessionManager Class

**Purpose**: Manages session lifecycle, limits, and cleanup

**Interface**:
```python
from typing import Optional
from uuid import UUID
from pathlib import Path
from agents import SQLiteSession

class SessionManager:
    """Manages agent session lifecycle and maintenance."""

    def __init__(
        self,
        db_path: Path,
        max_messages: int = 200,
        retention_days: int = 7,
    ):
        self.db_path = db_path
        self.max_messages = max_messages
        self.retention_days = retention_days

    def get_session(
        self,
        user_id: UUID,
        conversation_id: UUID,
    ) -> SQLiteSession:
        """Get or create agent session with persistent storage."""
        ...

    async def prune_session_messages(
        self,
        session_id: str,
    ) -> int:
        """Remove oldest messages if session exceeds max_messages limit."""
        ...

    async def cleanup_inactive_sessions(self) -> int:
        """Delete sessions inactive for more than retention_days."""
        ...

    async def get_session_stats(
        self,
        session_id: str,
    ) -> dict:
        """Get session statistics (message count, age, last activity)."""
        ...

    async def clear_session(
        self,
        session_id: str,
    ) -> None:
        """Clear all messages for a session (emergency recovery)."""
        ...
```

## Data Relationships

### Conversation ↔ Agent Session Mapping

```
PostgreSQL Conversation (id: UUID)
         ↓
    1:1 mapping
         ↓
SQLite Agent Session (session_id: "user_{user_id}_conv_{conversation_id}")
```

**Relationship Rules**:
1. Each PostgreSQL Conversation has exactly one SQLite Agent Session
2. Session ID is deterministically generated from user_id + conversation_id
3. Sessions are created lazily on first message
4. Deleting a Conversation does NOT automatically delete Agent Session (cleanup job handles this)

### Message Duplication Strategy

**PostgreSQL Messages**: User-facing, permanent record
- Stored for audit trail and UI display
- Never automatically deleted
- Soft-deleted with conversation

**SQLite Agent Messages**: Agent context, temporary
- Stored for agent conversation memory
- Automatically pruned at 200 messages
- Automatically deleted after 7 days inactivity
- Can be cleared for recovery

**Why Both?**:
- PostgreSQL: Source of truth for user data, supports complex queries, relational integrity
- SQLite: Optimized for agent SDK, fast local access, automatic serialization

## Data Flow

### Message Send Flow

```
1. User sends message via ChatKit API
   ↓
2. Save to PostgreSQL messages table
   ↓
3. Get/create SQLite agent session
   ↓
4. Runner.run() with session (auto-saves to SQLite)
   ↓
5. Agent processes with full conversation context
   ↓
6. Save agent response to PostgreSQL messages table
   ↓
7. Prune SQLite session if > 200 messages
   ↓
8. Return response to user
```

### Session Cleanup Flow

```
1. Daily cleanup job runs at 2 AM UTC
   ↓
2. Query agent_sessions WHERE updated_at < (now - 7 days)
   ↓
3. For each inactive session:
   - DELETE FROM agent_messages WHERE session_id = ?
   - DELETE FROM agent_sessions WHERE session_id = ?
   ↓
4. Log cleanup statistics
   ↓
5. Update monitoring metrics
```

## Schema Migrations

### Required Migrations

**SQLite Schema Enhancement**:
```sql
-- Add index for cleanup queries (if not exists)
CREATE INDEX IF NOT EXISTS ix_agent_sessions_updated
ON agent_sessions(updated_at);

-- Add composite index for message retrieval
CREATE INDEX IF NOT EXISTS ix_agent_messages_session_created
ON agent_messages(session_id, created_at);
```

**PostgreSQL**: No schema changes required

### Migration Strategy

1. SQLite indexes are created automatically by SessionManager on first run
2. No data migration needed (no existing persistent sessions)
3. Backward compatible (in-memory sessions were ephemeral)

## Data Validation Rules

### Session ID Validation

```python
import re
from uuid import UUID

SESSION_ID_PATTERN = re.compile(r"^user_[0-9a-f-]{36}_conv_[0-9a-f-]{36}$")

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format."""
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
```

### Message Limit Validation

```python
def validate_message_count(session_id: str, max_messages: int = 200) -> bool:
    """Check if session is within message limit."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM agent_messages WHERE session_id = ?",
        (session_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count <= max_messages
```

## Performance Characteristics

### Query Performance

| Operation | Expected Latency | Notes |
|-----------|------------------|-------|
| Get session | <10ms | SQLite local file access |
| Add message | <50ms | Includes serialization |
| Retrieve history (50 msgs) | <20ms | Indexed query |
| Prune messages | <100ms | DELETE with LIMIT |
| Cleanup inactive sessions | <5s | Batch operation, daily |

### Storage Estimates

| Entity | Size per Record | Growth Rate |
|--------|----------------|-------------|
| Agent Session | ~100 bytes | 1000/month |
| Agent Message | ~500 bytes | 20,000/month |
| Database Size (1 year) | ~120 MB | Linear growth |

**Cleanup Impact**: 7-day retention reduces storage by ~75%

## Monitoring and Observability

### Key Metrics

1. **Session Metrics**:
   - Active sessions count
   - Average messages per session
   - Session creation rate

2. **Performance Metrics**:
   - Session retrieval latency (p50, p95, p99)
   - Message add latency
   - Cleanup job duration

3. **Health Metrics**:
   - Database file size
   - Cleanup success rate
   - Pruning operations per day

### Alerting Thresholds

- Database size > 500 MB (investigate retention policy)
- Session retrieval p95 > 100ms (performance degradation)
- Cleanup job failure (manual intervention needed)
- Active sessions > 10,000 (capacity planning)

## Security Considerations

### Data Isolation

- Session IDs include user_id - prevents cross-user access
- No shared sessions between users
- SQLite file permissions: 600 (owner read/write only)

### Data Retention

- Agent messages deleted after 7 days (FR-011)
- PostgreSQL messages retained indefinitely (audit trail)
- Soft-deleted conversations retained for 30 days (configurable)

### Sensitive Data

- Session database contains conversation history
- Must be included in backup procedures
- Consider encryption at rest for production
- Exclude from logs and error messages

## References

- OpenAI Agents SDK SQLiteSession: https://openai.github.io/openai-agents-python/ref/memory/sqlite_session
- SQLite WAL Mode: https://www.sqlite.org/wal.html
- Feature Specification: [spec.md](./spec.md)
- Research Document: [research.md](./research.md)
