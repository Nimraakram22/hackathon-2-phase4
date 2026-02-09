# Data Model: AI-Powered Todo Chatbot

**Date**: 2026-01-29
**Feature**: 001-todo-chatbot
**Status**: Complete

## Overview

This document defines all database entities, relationships, validation rules, and state transitions for the AI-powered todo chatbot. All entities use SQLModel for type-safe ORM with Pydantic validation.

## Entity Definitions

### User

Represents an authenticated user who can manage tasks and have conversations.

**Fields**:
- `id` (UUID, primary key): Unique user identifier
- `email` (str, unique, indexed): User email address for authentication
- `hashed_password` (str): Bcrypt-hashed password
- `created_at` (datetime): Account creation timestamp
- `updated_at` (datetime): Last update timestamp
- `is_active` (bool, default=True): Account active status

**Validation Rules**:
- `email`: Valid email format, max 255 characters
- `hashed_password`: Non-empty string
- `created_at`, `updated_at`: Auto-generated timestamps

**Relationships**:
- One-to-many with Task (user can have multiple tasks)
- One-to-many with Conversation (user can have multiple conversations)

**Indexes**:
- Primary key on `id`
- Unique index on `email`
- Index on `is_active` for filtering active users

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, index=True)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")
    conversations: list["Conversation"] = Relationship(back_populates="user")
```

---

### Task

Represents a todo item with title, optional description, and completion status.

**Fields**:
- `id` (UUID, primary key): Unique task identifier
- `user_id` (UUID, foreign key): Owner of the task
- `title` (str): Task title (1-100 characters)
- `description` (str, optional): Task description (max 1000 characters)
- `is_completed` (bool, default=False): Completion status
- `created_at` (datetime): Task creation timestamp
- `updated_at` (datetime): Last update timestamp
- `completed_at` (datetime, optional): Completion timestamp

**Validation Rules**:
- `title`: Required, 1-100 characters, non-empty after stripping whitespace
- `description`: Optional, max 1000 characters
- `is_completed`: Boolean, defaults to False
- `completed_at`: Set automatically when `is_completed` changes to True

**Relationships**:
- Many-to-one with User (task belongs to one user)

**Indexes**:
- Primary key on `id`
- Foreign key index on `user_id`
- Composite index on `(user_id, is_completed)` for filtering user's pending/completed tasks
- Index on `created_at` for sorting by creation date

**State Transitions**:
```
[Created] → is_completed=False, completed_at=None
    ↓
[Completed] → is_completed=True, completed_at=<timestamp>
    ↓
[Uncompleted] → is_completed=False, completed_at=None (optional: allow uncompleting)
    ↓
[Deleted] → Hard delete (permanent removal per spec clarification)
```

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="tasks")

    # Composite index for efficient queries
    __table_args__ = (
        Index("ix_tasks_user_completed", "user_id", "is_completed"),
    )
```

---

### Conversation

Represents a chat session between a user and the AI agent with 30-day retention.

**Fields**:
- `id` (UUID, primary key): Unique conversation identifier
- `user_id` (UUID, foreign key): Owner of the conversation
- `title` (str, optional): Conversation title (auto-generated from first message)
- `created_at` (datetime): Conversation start timestamp
- `updated_at` (datetime): Last message timestamp
- `is_deleted` (bool, default=False): Soft delete flag for retention policy
- `deleted_at` (datetime, optional): Deletion timestamp

**Validation Rules**:
- `title`: Optional, max 200 characters, auto-generated from first user message
- `is_deleted`: Boolean, defaults to False
- `deleted_at`: Set automatically when conversation is marked deleted (30-day retention)

**Relationships**:
- Many-to-one with User (conversation belongs to one user)
- One-to-many with Message (conversation contains multiple messages)

**Indexes**:
- Primary key on `id`
- Foreign key index on `user_id`
- Composite index on `(user_id, is_deleted)` for filtering active conversations
- Index on `updated_at` for sorting by recent activity
- Index on `deleted_at` for cleanup job

**State Transitions**:
```
[Active] → is_deleted=False, deleted_at=None
    ↓
[Marked for Deletion] → is_deleted=True, deleted_at=<timestamp>
    ↓ (after 30 days)
[Purged] → Hard delete (permanent removal)
```

**Retention Policy**:
- Conversations older than 30 days (based on `updated_at`) are marked `is_deleted=True`
- Scheduled job runs daily to purge conversations where `deleted_at < now() - 30 days`

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Index
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")

    # Composite index for efficient queries
    __table_args__ = (
        Index("ix_conversations_user_deleted", "user_id", "is_deleted"),
    )
```

---

### Message

Represents a single message in a conversation (user or assistant).

**Fields**:
- `id` (UUID, primary key): Unique message identifier
- `conversation_id` (UUID, foreign key): Parent conversation
- `role` (str, enum): Message role ("user" or "assistant")
- `content` (str): Message content (max 2000 characters)
- `created_at` (datetime): Message timestamp

**Validation Rules**:
- `role`: Must be "user" or "assistant"
- `content`: Required, 1-2000 characters
- `created_at`: Auto-generated timestamp

**Relationships**:
- Many-to-one with Conversation (message belongs to one conversation)

**Indexes**:
- Primary key on `id`
- Foreign key index on `conversation_id`
- Composite index on `(conversation_id, created_at)` for chronological ordering

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Index
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column=Column(Enum(MessageRole)))
    content: str = Field(min_length=1, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")

    # Composite index for efficient queries
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
```

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│─────────────────│
│ id (PK)         │
│ email (unique)  │
│ hashed_password │
│ created_at      │
│ updated_at      │
│ is_active       │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────┐
    │                          │
    │                          │
┌───▼──────────┐      ┌────────▼────────┐
│     Task     │      │  Conversation   │
│──────────────│      │─────────────────│
│ id (PK)      │      │ id (PK)         │
│ user_id (FK) │      │ user_id (FK)    │
│ title        │      │ title           │
│ description  │      │ created_at      │
│ is_completed │      │ updated_at      │
│ created_at   │      │ is_deleted      │
│ updated_at   │      │ deleted_at      │
│ completed_at │      └────────┬────────┘
└──────────────┘               │
                               │ 1:N
                               │
                      ┌────────▼────────┐
                      │    Message      │
                      │─────────────────│
                      │ id (PK)         │
                      │ conversation_id │
                      │ role            │
                      │ content         │
                      │ created_at      │
                      └─────────────────┘
```

## Database Constraints

### Foreign Key Constraints
- `tasks.user_id` → `users.id` (ON DELETE CASCADE)
- `conversations.user_id` → `users.id` (ON DELETE CASCADE)
- `messages.conversation_id` → `conversations.id` (ON DELETE CASCADE)

### Unique Constraints
- `users.email` (unique)

### Check Constraints
- `tasks.title`: Length between 1 and 100 characters
- `tasks.description`: Length max 1000 characters (if not null)
- `messages.content`: Length between 1 and 2000 characters
- `messages.role`: Must be 'user' or 'assistant'

## Query Patterns

### Common Queries

**Get user's pending tasks**:
```sql
SELECT * FROM tasks
WHERE user_id = ? AND is_completed = false
ORDER BY created_at DESC;
```
Index used: `ix_tasks_user_completed`

**Get user's active conversations**:
```sql
SELECT * FROM conversations
WHERE user_id = ? AND is_deleted = false
ORDER BY updated_at DESC;
```
Index used: `ix_conversations_user_deleted`

**Get conversation messages**:
```sql
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at ASC;
```
Index used: `ix_messages_conversation_created`

**Find conversations to purge**:
```sql
SELECT * FROM conversations
WHERE is_deleted = true AND deleted_at < (NOW() - INTERVAL '30 days');
```
Index used: `deleted_at`

## Migration Strategy

### Initial Schema (v0.1.0)
1. Create `users` table
2. Create `tasks` table with foreign key to users
3. Create `conversations` table with foreign key to users
4. Create `messages` table with foreign key to conversations
5. Create all indexes

### Future Migrations
- v0.2.0: Add task priority field (if needed)
- v0.3.0: Add task tags/categories (if needed)
- v0.4.0: Add conversation sharing (if needed)

## Data Validation

### Application-Level Validation (Pydantic)
- Email format validation
- String length constraints
- Enum validation for message roles
- Timestamp validation

### Database-Level Validation (PostgreSQL)
- Foreign key constraints
- Unique constraints
- Check constraints on string lengths
- NOT NULL constraints

## Performance Considerations

### Indexes
- All foreign keys indexed for join performance
- Composite indexes on common query patterns
- Timestamp indexes for sorting and filtering

### Query Optimization
- Use `LIMIT` for pagination
- Use `SELECT` specific columns instead of `SELECT *`
- Use prepared statements to prevent SQL injection

### Scalability
- Partition `messages` table by `created_at` if volume exceeds 10M rows
- Archive old conversations to separate table after purge
- Consider read replicas for high read load

---

**Data Model Status**: ✅ COMPLETE - Ready for implementation
