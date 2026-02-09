---
description: "Task list for AI-Powered Todo Chatbot implementation"
---

# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/001-todo-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are NOT included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure with src/, tests/, and configuration files
- [X] T002 Initialize Poetry project in backend/ with Python 3.11+ and core dependencies (FastAPI, FastMCP, OpenAI Agents SDK, SQLModel, Alembic)
- [X] T003 [P] Create frontend directory structure with src/, tests/, and configuration files
- [X] T004 [P] Initialize npm project in frontend/ with Vite, React, TypeScript, and OpenAI ChatKit dependencies
- [X] T005 [P] Configure Mypy strict mode in backend/mypy.ini
- [X] T006 [P] Configure Pytest in backend/pytest.ini with coverage settings
- [X] T007 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [X] T008 [P] Create backend/.env.example with all required environment variables (DATABASE_URL, GEMINI_API_KEY, JWT_SECRET_KEY, etc.)
- [X] T009 [P] Create frontend/.env.example with frontend environment variables (VITE_API_URL, VITE_CHATKIT_URL, etc.)
- [X] T010 [P] Create backend/src/config.py for environment configuration management using Pydantic Settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 [P] Create User model in backend/src/models/user.py with SQLModel (id, email, hashed_password, created_at, updated_at, is_active)
- [X] T012 [P] Create Task model in backend/src/models/task.py with SQLModel (id, user_id, title, description, is_completed, created_at, updated_at, completed_at)
- [X] T013 [P] Create Conversation model in backend/src/models/conversation.py with SQLModel (id, user_id, title, created_at, updated_at, is_deleted, deleted_at)
- [X] T014 [P] Create Message model in backend/src/models/message.py with SQLModel and MessageRole enum (id, conversation_id, role, content, created_at)
- [X] T015 Create database connection module in backend/src/database/connection.py with Neon PostgreSQL connection and session management
- [X] T016 Initialize Alembic in backend/src/database/migrations/ and create initial migration for all models
- [X] T017 [P] Create JWT authentication utilities in backend/src/api/auth_utils.py (hash_password, verify_password, create_access_token, verify_token)
- [X] T018 [P] Create authentication dependency in backend/src/api/dependencies.py (get_current_user) for FastAPI dependency injection
- [X] T019 Create FastMCP server initialization in backend/src/mcp/server.py with ErrorHandlingMiddleware and RetryMiddleware (5 retries, exponential backoff)
- [X] T020 Create Google Gemini client configuration in backend/src/agent/gemini_client.py with AsyncOpenAI client pointing to Gemini API
- [X] T021 Create main todo agent in backend/src/agent/todo_agent.py with OpenAIChatCompletionsModel using Gemini 2.0 Flash
- [X] T022 Create relevance guardrail agent in backend/src/agent/guardrails.py with input validation for task-related messages
- [X] T023 Create SQLiteSession wrapper in backend/src/agent/session.py for conversation context management
- [X] T024 Create FastAPI app initialization in backend/src/api/main.py with CORS middleware and health check endpoint
- [X] T025 [P] Create authentication routes in backend/src/api/routes/auth.py (register, login, get_current_user endpoints)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks to their todo list by describing them in natural language through a conversational interface.

**Independent Test**: Send natural language messages like "I need to buy groceries" or "Remind me to call mom" and verify tasks are created and stored in the database.

### Implementation for User Story 1

- [X] T026 [P] [US1] Create create_task MCP tool in backend/src/mcp/tools/task_tools.py with Pydantic validation (user_id, title, description)
- [X] T027 [P] [US1] Register create_task tool with FastMCP server in backend/src/mcp/server.py
- [X] T028 [US1] Integrate create_task tool with todo agent in backend/src/agent/todo_agent.py (add tool to agent's available tools)
- [X] T029 [US1] Implement input guardrail validation in backend/src/agent/guardrails.py using blocking InputGuardrail with relevance_agent
- [X] T030 [US1] Create ChatKit thread creation endpoint in backend/src/api/routes/chatkit.py (POST /chatkit/threads)
- [X] T031 [US1] Create ChatKit message sending endpoint in backend/src/api/routes/chatkit.py (POST /chatkit/threads/{thread_id}/messages) with SSE streaming
- [X] T032 [US1] Implement agent runner integration in backend/src/api/routes/chatkit.py to process user messages and stream responses
- [X] T033 [US1] Add conversation and message persistence logic in backend/src/api/routes/chatkit.py (save user messages and agent responses to database)
- [X] T034 [US1] Add error handling for ambiguous task creation requests (agent asks clarifying questions)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language and see confirmation responses

---

## Phase 4: User Story 2 - View and List Tasks (Priority: P2)

**Goal**: Users can view their tasks by asking the chatbot to show all tasks, pending tasks, or completed tasks.

**Independent Test**: Create several tasks (some completed, some pending) and ask "Show me my tasks", "What's pending?", or "What have I completed?" and verify correct task lists are returned.

### Implementation for User Story 2

- [X] T035 [P] [US2] Create list_tasks MCP tool in backend/src/mcp/tools/task_tools.py with filtering (user_id, status_filter, limit, offset)
- [X] T036 [P] [US2] Create get_task MCP tool in backend/src/mcp/tools/task_tools.py (user_id, task_id)
- [X] T037 [US2] Register list_tasks and get_task tools with FastMCP server in backend/src/mcp/server.py
- [X] T038 [US2] Integrate list_tasks and get_task tools with todo agent in backend/src/agent/todo_agent.py
- [X] T039 [US2] Update agent instructions in backend/src/agent/todo_agent.py to handle task listing queries with natural language understanding
- [X] T040 [US2] Add response formatting logic for task lists (readable format with task IDs for reference)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create and view tasks

---

## Phase 5: User Story 3 - Complete Tasks (Priority: P3)

**Goal**: Users can mark tasks as complete by telling the chatbot which task they've finished.

**Independent Test**: Create tasks, then say "Mark task 3 as done" or "I finished buying groceries" and verify the task status changes to completed.

### Implementation for User Story 3

- [X] T041 [P] [US3] Create complete_task MCP tool in backend/src/mcp/tools/task_tools.py (user_id, task_id) with completion timestamp logic
- [X] T042 [US3] Register complete_task tool with FastMCP server in backend/src/mcp/server.py
- [X] T043 [US3] Integrate complete_task tool with todo agent in backend/src/agent/todo_agent.py
- [X] T044 [US3] Update agent instructions in backend/src/agent/todo_agent.py to handle task completion by ID or by title matching
- [X] T045 [US3] Add error handling for non-existent tasks and already-completed tasks

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently - full task lifecycle (create, view, complete)

---

## Phase 6: User Story 4 - Modify and Delete Tasks (Priority: P4)

**Goal**: Users can update task details or remove tasks they no longer need through natural language commands.

**Independent Test**: Create a task, then say "Change task 1 to 'Buy groceries and fruits'" or "Delete the meeting task" and verify the changes are applied.

### Implementation for User Story 4

- [X] T046 [P] [US4] Create update_task MCP tool in backend/src/mcp/tools/task_tools.py (user_id, task_id, title, description) with partial update support
- [X] T047 [P] [US4] Create delete_task MCP tool in backend/src/mcp/tools/task_tools.py (user_id, task_id) with hard delete logic
- [X] T048 [US4] Register update_task and delete_task tools with FastMCP server in backend/src/mcp/server.py
- [X] T049 [US4] Integrate update_task and delete_task tools with todo agent in backend/src/agent/todo_agent.py
- [X] T050 [US4] Update agent instructions in backend/src/agent/todo_agent.py to handle task modification and deletion with confirmation prompts
- [X] T051 [US4] Add error handling for non-existent tasks and bulk deletion confirmation

**Checkpoint**: All core task management operations (CRUD + complete) should now be functional

---

## Phase 7: User Story 5 - Maintain Conversation Context (Priority: P5)

**Goal**: Users can have multi-turn conversations where the chatbot remembers previous context within the session.

**Independent Test**: Have a conversation like "Add a task to buy milk" followed by "Actually, make that buy milk and eggs" and verify the system understands the reference.

### Implementation for User Story 5

- [X] T052 [US5] Implement SQLiteSession integration in backend/src/agent/session.py with session ID format: user_{user_id}_conv_{conversation_id}
- [X] T053 [US5] Update agent runner in backend/src/api/routes/chatkit.py to use SQLiteSession for maintaining conversation context
- [X] T054 [US5] Implement conversation history loading in backend/src/api/routes/chatkit.py (GET /chatkit/threads/{thread_id}) with pagination
- [X] T055 [US5] Add conversation title auto-generation from first user message in backend/src/api/routes/chatkit.py
- [X] T056 [US5] Implement 30-day conversation retention policy with scheduled cleanup job (mark conversations as deleted after 30 days of inactivity)
- [X] T057 [US5] Add context window management (limit session history to last 50 messages to prevent performance degradation)

**Checkpoint**: All user stories should now be independently functional with full conversation context support

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Frontend UI, documentation, and final improvements

- [X] T058 [P] Create ChatKit integration component in frontend/src/components/ChatInterface.tsx with useChatKit hook
- [X] T059 [P] Create authentication provider in frontend/src/components/AuthProvider.tsx with JWT token management
- [X] T060 [P] Create API client service in frontend/src/services/api.ts for authentication endpoints
- [X] T061 [P] Create login/register UI components in frontend/src/components/Auth.tsx
- [X] T062 Create main App component in frontend/src/App.tsx integrating AuthProvider and ChatInterface
- [X] T063 [P] Add input validation and error handling in frontend components
- [X] T064 [P] Add loading states and error messages for better UX
- [X] T065 [P] Update backend/README.md with setup instructions
- [X] T066 [P] Update frontend/README.md with setup instructions
- [X] T067 Run quickstart.md validation (follow all setup steps and verify application works end-to-end)
- [X] T068 [P] Add API documentation comments to all FastAPI endpoints
- [X] T069 [P] Add type hints and docstrings to all Python functions
- [ ] T070 Run Mypy strict mode check on backend code and fix any type errors
- [X] T071 [P] Add security headers to FastAPI app (CORS, CSP, etc.)
- [ ] T072 [P] Implement rate limiting for ChatKit endpoints to prevent abuse

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 but integrates with same agent
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2 but uses same task models
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3 but uses same task models
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Enhances all previous stories with context

### Within Each User Story

- MCP tools before agent integration
- Agent integration before ChatKit endpoints
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005, T006, T007, T008, T009, T010)
- All Foundational model tasks can run in parallel (T011, T012, T013, T014)
- All Foundational utility tasks can run in parallel (T017, T018, T020, T022, T025)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- MCP tools within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch MCP tool creation and guardrail setup together:
Task T026: "Create create_task MCP tool in backend/src/mcp/tools/task_tools.py"
Task T027: "Register create_task tool with FastMCP server"

# Then proceed with integration tasks sequentially
```

---

## Parallel Example: Foundational Phase

```bash
# Launch all model creation tasks together:
Task T011: "Create User model in backend/src/models/user.py"
Task T012: "Create Task model in backend/src/models/task.py"
Task T013: "Create Conversation model in backend/src/models/conversation.py"
Task T014: "Create Message model in backend/src/models/message.py"

# Launch all utility tasks together:
Task T017: "Create JWT authentication utilities"
Task T018: "Create authentication dependency"
Task T020: "Create Google Gemini client configuration"
Task T022: "Create relevance guardrail agent"
Task T025: "Create authentication routes"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T025) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T026-T034)
4. **STOP and VALIDATE**: Test User Story 1 independently (create tasks via natural language)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add Polish (Phase 8) → Final release
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T026-T034)
   - Developer B: User Story 2 (T035-T040)
   - Developer C: User Story 3 (T041-T045)
3. Stories complete and integrate independently

---

## Summary

- **Total Tasks**: 72 tasks
- **Task Count by Phase**:
  - Phase 1 (Setup): 10 tasks
  - Phase 2 (Foundational): 15 tasks
  - Phase 3 (US1 - Create Tasks): 9 tasks
  - Phase 4 (US2 - View Tasks): 6 tasks
  - Phase 5 (US3 - Complete Tasks): 5 tasks
  - Phase 6 (US4 - Modify/Delete Tasks): 6 tasks
  - Phase 7 (US5 - Conversation Context): 6 tasks
  - Phase 8 (Polish): 15 tasks
- **Parallel Opportunities**: 28 tasks marked [P] can run in parallel within their phases
- **Independent Test Criteria**: Each user story has clear acceptance criteria from spec.md
- **Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 34 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not explicitly requested in the specification
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
