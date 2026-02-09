# Implementation Plan: Chat History and Session Management

**Branch**: `002-chat-history` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-chat-history/spec.md`

## Summary

Implement persistent chat history using OpenAI Agents SDK's SQLiteSession to maintain conversation context across multiple messages and service restarts. The current implementation uses in-memory sessions that are lost on restart. This plan upgrades to file-based SQLite storage with session cleanup, message limits, and proper error handling.

**Key Changes**:
- Fix `get_agent_session()` to use persistent file-based SQLite storage
- Implement 200-message limit per session with automatic pruning
- Add session cleanup job for 7-day inactive session retention
- Enhance error handling for database failures
- Add comprehensive tests for session persistence and isolation

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- OpenAI Agents SDK (openai-agents-python) with SQLiteSession
- FastAPI 0.100+
- SQLModel 0.0.14+ (for PostgreSQL models)
- SQLite 3.35+ (for agent session storage)
- Pydantic 2.0+ (for validation)

**Storage**:
- PostgreSQL (Neon Serverless) for user-facing data (Conversations, Messages, Tasks, Users)
- SQLite for agent session context (OpenAI Agents SDK internal state)

**Testing**: pytest with pytest-asyncio, pytest-cov
**Target Platform**: Linux server (FastAPI backend)
**Project Type**: Web application (backend + frontend)

**Performance Goals**:
- Response time <3 seconds for conversations up to 50 messages
- Support 100+ concurrent active conversations
- Session retrieval <100ms

**Constraints**:
- 200 messages maximum per session
- 7-day retention for inactive sessions
- Zero session data leakage between users/threads
- 100% data retention through service restarts

**Scale/Scope**:
- Multi-user environment with isolated sessions
- Estimated 1000+ conversations per month
- Average 20-30 messages per conversation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Test-Driven Development (NON-NEGOTIABLE)
- **Status**: PASS
- **Plan**: Tests will be written first for session persistence, isolation, cleanup, and message limits before implementation

### ✅ Documentation-First via MCP Context7
- **Status**: PASS
- **Evidence**: OpenAI Agents SDK documentation queried via Context7 for SQLiteSession implementation details, schema structure, and best practices

### ✅ Type Safety First
- **Status**: PASS
- **Plan**: All session management functions will use type hints; SQLModel for database models; Pydantic for validation

### ✅ Git Versioning on Milestones
- **Status**: PASS
- **Plan**: Version bump to MINOR (0.X.0) upon completion as this adds new session persistence capability

### ✅ Simplicity First (YAGNI)
- **Status**: PASS
- **Justification**: Using built-in SQLiteSession from OpenAI Agents SDK rather than custom implementation. No premature abstractions.

### ✅ Architecture Plan First
- **Status**: PASS
- **Evidence**: This plan document with research, data models, and contracts

### ✅ MCP Server for Tools
- **Status**: PASS
- **Note**: Session management is internal to agent; existing MCP tools remain stateless

## Project Structure

### Documentation (this feature)

```text
specs/002-chat-history/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - SQLiteSession deep dive
├── data-model.md        # Phase 1 output - Session schema and relationships
├── quickstart.md        # Phase 1 output - Developer guide for sessions
├── contracts/           # Phase 1 output - API contracts (no changes needed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agent/
│   │   ├── session.py           # MODIFY: Fix persistent storage
│   │   ├── session_manager.py   # NEW: Session cleanup and limits
│   │   └── todo_agent.py        # NO CHANGE: Already uses sessions
│   ├── models/
│   │   ├── conversation.py      # NO CHANGE: PostgreSQL model
│   │   └── message.py           # NO CHANGE: PostgreSQL model
│   ├── api/
│   │   └── routes/
│   │       └── chatkit.py       # MINOR: Enhanced error handling
│   ├── database/
│   │   └── cleanup.py           # NEW: Background cleanup job
│   └── config.py                # MODIFY: Add session config
└── tests/
    ├── unit/
    │   ├── test_session.py      # NEW: Session unit tests
    │   └── test_session_manager.py  # NEW: Manager unit tests
    ├── integration/
    │   ├── test_session_persistence.py  # NEW: Persistence tests
    │   └── test_session_isolation.py    # NEW: Isolation tests
    └── contract/
        └── test_chatkit_api.py  # MODIFY: Add session tests

frontend/
└── src/
    └── components/
        └── ChatInterface.tsx    # NO CHANGE: Already handles threads

data/
└── agent_sessions.db            # NEW: SQLite database for sessions
```

**Structure Decision**: Web application structure with backend/frontend separation. Agent session storage is isolated in SQLite database separate from PostgreSQL for user data. This follows the existing architecture where PostgreSQL stores user-facing data (conversations, messages, tasks) while SQLite handles agent internal state (conversation context for OpenAI Agents SDK).

## Complexity Tracking

> **No violations - all Constitution Check items passed**

No complexity violations to justify. The implementation uses existing OpenAI Agents SDK capabilities without custom abstractions or unnecessary complexity.

