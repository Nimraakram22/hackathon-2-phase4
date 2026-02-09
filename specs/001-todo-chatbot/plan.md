# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `001-todo-chatbot` | **Date**: 2026-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-chatbot/spec.md`

## Summary

Build an AI-powered chatbot interface for managing todos through natural language using MCP server architecture and OpenAI Agents SDK. The system will expose task management operations (create, read, update, delete, complete) as MCP tools, use an AI agent with guardrails for natural language understanding, and provide a conversational web interface using OpenAI ChatKit. The agent will use Google Gemini 2.0 Flash (free tier) for cost-effective operation while maintaining conversation context through SQLite-based session management.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, FastMCP, OpenAI Agents SDK, OpenAI ChatKit (React), SQLModel, Neon PostgreSQL
**Storage**: Neon Serverless PostgreSQL for tasks/users/conversations, SQLite for agent session management
**Testing**: Pytest with coverage reporting, type checking with Mypy (strict mode)
**Target Platform**: Web application (Linux server backend + React frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <3s response time for 95% of requests, support 100 concurrent users
**Constraints**: <200ms p95 database query latency, 30-day conversation retention, exponential backoff up to 30s for DB failures
**Scale/Scope**: 10-100 active tasks per user, 10-50 messages per conversation, English language only (initial version)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS** - Plan includes comprehensive test strategy:
- Unit tests for MCP tools, agent logic, and database operations
- Integration tests for agent-to-MCP-tool workflows
- Contract tests for API endpoints
- Tests will be written FIRST for each user story before implementation
- TDD workflow enforced: Red (write failing tests) → Green (minimal implementation) → Refactor

### II. Documentation-First via MCP Context7
✅ **PASS** - All technical decisions reference current documentation:
- FastMCP v3.0.0b1 documentation consulted for tool creation and middleware
- OpenAI Agents Python v0.7.0 documentation for agent configuration, guardrails, and sessions
- OpenAI ChatKit documentation for frontend integration
- All implementation will verify API contracts against latest docs
- ADRs will include documentation references with timestamps

### III. Type Safety First
✅ **PASS** - Strong typing enforced throughout:
- Pydantic models for all MCP tool schemas (input/output validation)
- SQLModel for type-safe ORM with database entities
- Type hints for all Python function signatures
- TypeScript for React frontend components
- Mypy strict mode required to pass before PR approval
- No `Any` types unless justified in code comments

### IV. Git Versioning on Milestones
✅ **PASS** - Semantic versioning planned:
- v0.1.0: User Story 1 (Create Tasks) - MINOR bump for first feature
- v0.2.0: User Story 2 (View/List Tasks) - MINOR bump for new feature
- v0.3.0: User Story 3 (Complete Tasks) - MINOR bump for new feature
- v0.4.0: User Story 4 (Modify/Delete Tasks) - MINOR bump for new feature
- v0.5.0: User Story 5 (Conversation Context) - MINOR bump for new feature
- CHANGELOG.md maintained with each version
- Git tags applied at each user story completion

### V. Simplicity First (YAGNI)
✅ **PASS** - Minimal viable implementation:
- Start with stateless MCP tools (no premature caching)
- Use SQLiteSession (built-in) instead of custom session management
- Direct database access via SQLModel (no repository pattern initially)
- Single agent with guardrails (no multi-agent orchestration)
- No task scheduling, priorities, tags, or sharing in initial version
- Refactor only when requirements demand complexity

### VI. Architecture Plan First
✅ **PASS** - Comprehensive planning workflow:
- This plan.md created before implementation
- Phase 0: research.md will resolve all technical unknowns
- Phase 1: data-model.md, contracts/, quickstart.md before coding
- Constitution Check completed and passing
- ADRs will document significant decisions (agent model selection, session storage)
- Implementation blocked until plan approved

### VII. MCP Server for Tools
✅ **PASS** - Tool-based architecture:
- All task operations exposed as stateless MCP tools via FastMCP
- Tools use Pydantic models for input/output schemas
- Agent interacts with system exclusively through MCP tools
- Tools independently testable with clear contracts
- State persisted to PostgreSQL (tools remain stateless)
- Error handling via FastMCP middleware (RetryMiddleware, ErrorHandlingMiddleware)

**Constitution Check Result**: ✅ ALL GATES PASSED - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── mcp-tools.yaml   # MCP tool schemas (OpenAPI format)
│   └── api-endpoints.yaml # ChatKit backend API contract
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLModel entities (Task, User, Conversation, Message)
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── mcp/             # FastMCP server and tools
│   │   ├── __init__.py
│   │   ├── server.py    # FastMCP server initialization
│   │   ├── tools/       # MCP tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── task_tools.py     # create_task, list_tasks, etc.
│   │   │   └── conversation_tools.py
│   │   └── middleware.py # Error handling and retry middleware
│   ├── agent/           # OpenAI Agents SDK integration
│   │   ├── __init__.py
│   │   ├── todo_agent.py # Main agent with guardrails
│   │   ├── guardrails.py # Input validation guardrails
│   │   └── session.py    # Session management wrapper
│   ├── api/             # FastAPI endpoints for ChatKit
│   │   ├── __init__.py
│   │   ├── main.py      # FastAPI app initialization
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chatkit.py # ChatKit protocol endpoints
│   │   │   └── auth.py    # Authentication endpoints
│   │   └── dependencies.py # Dependency injection
│   ├── database/        # Database connection and migrations
│   │   ├── __init__.py
│   │   ├── connection.py # Neon PostgreSQL connection
│   │   └── migrations/   # Alembic migrations
│   └── config.py        # Environment configuration
├── tests/
│   ├── contract/        # MCP tool contract tests
│   ├── integration/     # Agent + MCP + DB integration tests
│   └── unit/            # Unit tests for models, tools, agent logic
├── pyproject.toml       # Poetry dependencies
├── pytest.ini           # Pytest configuration
└── mypy.ini             # Mypy strict mode configuration

frontend/
├── src/
│   ├── components/      # React components
│   │   ├── ChatInterface.tsx # Main ChatKit wrapper
│   │   └── AuthProvider.tsx  # Authentication context
│   ├── hooks/           # Custom React hooks
│   │   └── useChatKit.ts
│   ├── services/        # API client services
│   │   └── api.ts
│   ├── App.tsx          # Root component
│   └── main.tsx         # Entry point
├── tests/               # Frontend tests (Vitest)
├── package.json         # npm dependencies
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite build configuration
```

**Structure Decision**: Web application structure selected because the feature requires both a backend API (FastAPI + MCP server + AI agent) and a frontend chat interface (React + ChatKit). The backend handles all business logic, database operations, and AI agent orchestration, while the frontend provides the conversational UI. This separation enables independent scaling, testing, and deployment of frontend and backend components.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied by the proposed architecture.

## Phase 0: Research & Technical Decisions

See [research.md](./research.md) for detailed research findings on:
- FastMCP tool creation patterns and middleware configuration
- OpenAI Agents SDK guardrails and session management
- Google Gemini model configuration (Agent Level)
- ChatKit backend integration protocol
- Database schema design for tasks and conversations
- Error handling and retry strategies

## Phase 1: Design Artifacts

### Data Model
See [data-model.md](./data-model.md) for complete entity definitions, relationships, and validation rules.

### API Contracts
See [contracts/](./contracts/) for:
- `mcp-tools.yaml`: MCP tool schemas (input/output for all task operations)
- `api-endpoints.yaml`: ChatKit backend API contract (message streaming, thread management)

### Quickstart Guide
See [quickstart.md](./quickstart.md) for:
- Local development setup
- Environment configuration
- Running backend and frontend
- Testing the chatbot interface

## Phase 2: Task Breakdown

Task breakdown will be generated by `/sp.tasks` command after this plan is approved. Tasks will be organized by user story priority (P1-P5) with dependency ordering and TDD workflow.

## Key Architectural Decisions

### ADR-001: Agent Model Selection (Google Gemini 2.0 Flash)
**Decision**: Use Google Gemini 2.0 Flash via Agent Level configuration
**Rationale**: Constitution mandates cost-effective LLM providers. Gemini 2.0 Flash provides sufficient capability for task management at zero cost. Agent Level configuration allows per-agent model optimization.
**Alternatives Considered**: OpenAI GPT-4 (rejected: cost), Global Level configuration (rejected: less flexible)
**Reference**: Constitution v1.1.0, Section VIII (AI Agent Configuration)

### ADR-002: Session Storage (SQLite for Agent, PostgreSQL for Application)
**Decision**: Use SQLiteSession for agent conversation context, PostgreSQL for application data
**Rationale**: SQLiteSession is built-in to OpenAI Agents SDK and handles conversation history efficiently. PostgreSQL stores persistent application data (tasks, users). Separation of concerns: agent memory vs. application state.
**Alternatives Considered**: Single PostgreSQL for all data (rejected: unnecessary coupling), Redis for sessions (rejected: over-engineering)
**Reference**: OpenAI Agents SDK Sessions documentation

### ADR-003: Guardrails Strategy (Agent-Based Input Validation)
**Decision**: Use agent-based input guardrails with blocking execution
**Rationale**: Spec requires blocking unrelated messages before processing. Agent-based guardrails provide semantic understanding of input relevance, superior to regex/keyword filtering.
**Alternatives Considered**: Keyword filtering (rejected: brittle), No guardrails (rejected: violates spec FR-008a)
**Reference**: OpenAI Agents SDK Guardrails documentation

## Risk Analysis

### Top 3 Risks

1. **Risk**: Google Gemini API rate limits or availability issues
   **Mitigation**: Implement exponential backoff, fallback to Gemini 1.5 Flash, monitor API health
   **Blast Radius**: All chat interactions blocked
   **Kill Switch**: Feature flag to disable chatbot, fallback to form-based task entry

2. **Risk**: Conversation context grows unbounded, degrading performance
   **Mitigation**: 30-day retention policy (spec), limit session history to last 50 messages, implement pagination
   **Blast Radius**: Slow responses for users with long conversations
   **Kill Switch**: Clear old sessions, reduce history limit to 20 messages

3. **Risk**: Agent misinterprets natural language, creates incorrect tasks
   **Mitigation**: Confirmation prompts for ambiguous commands, structured output validation, user feedback loop
   **Blast Radius**: User frustration, incorrect task data
   **Kill Switch**: Disable natural language parsing, require explicit commands

## Next Steps

1. ✅ Phase 0: Generate research.md (resolve technical unknowns)
2. ✅ Phase 1: Generate data-model.md (entity definitions)
3. ✅ Phase 1: Generate contracts/ (API schemas)
4. ✅ Phase 1: Generate quickstart.md (setup guide)
5. ⏸️ Phase 2: Run `/sp.tasks` to generate tasks.md (NOT part of /sp.plan)
6. ⏸ Implementation: Run `/sp.implement` to execute tasks (NOT part of /sp.plan)

---

**Plan Status**: ✅ COMPLETE - Ready for user approval and Phase 2 task generation
