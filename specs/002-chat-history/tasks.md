# Tasks: Chat History and Session Management

**Input**: Design documents from `/specs/002-chat-history/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Following TDD approach per constitution - tests written FIRST before implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `backend/tests/`, `frontend/src/`
- Paths follow plan.md structure with backend/frontend separation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration for session management

- [x] T001 Create data directory structure for SQLite session database at `data/`
- [x] T002 [P] Add session configuration fields to `backend/src/config.py` (agent_session_db_path, agent_session_max_messages, agent_session_retention_days, agent_session_cleanup_hour)
- [x] T003 [P] Update `.env.example` with session configuration variables

**Checkpoint**: Configuration ready for session implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core session infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create SessionManager class skeleton in `backend/src/agent/session_manager.py` with type hints and method signatures
- [x] T005 Update `backend/src/agent/session.py` to use file-based SQLite storage instead of in-memory (modify get_agent_session function)
- [x] T006 [P] Add session ID validation function in `backend/src/agent/session.py` (validate UUID format)
- [x] T007 [P] Add SQLite index creation for cleanup queries in SessionManager.__init__

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Contextual Conversation Continuity (Priority: P1) 🎯 MVP

**Goal**: Enable chatbot to remember conversation context across multiple messages within the same thread

**Independent Test**: Send sequence of related messages ("Create task", "Add to that task", "What tasks?") and verify context is maintained

### Tests for User Story 1 (TDD - Write FIRST, Ensure FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Unit test for session creation with file-based storage in `backend/tests/unit/test_session.py`
- [x] T009 [P] [US1] Unit test for session ID generation format in `backend/tests/unit/test_session.py`
- [x] T010 [P] [US1] Unit test for message limit enforcement (200 messages) in `backend/tests/unit/test_session_manager.py`
- [x] T011 [P] [US1] Integration test for context continuity across messages in `backend/tests/integration/test_session_persistence.py`
- [x] T012 [P] [US1] Integration test for message pruning at 200 limit in `backend/tests/integration/test_session_persistence.py`

### Implementation for User Story 1

- [x] T013 [US1] Implement SessionManager.get_session() method in `backend/src/agent/session_manager.py` (creates/retrieves SQLiteSession with file-based storage)
- [x] T014 [US1] Implement SessionManager.prune_session_messages() method in `backend/src/agent/session_manager.py` (deletes oldest messages beyond 200 limit)
- [x] T015 [US1] Implement SessionManager.get_session_stats() method in `backend/src/agent/session_manager.py` (returns message count, age, last activity)
- [x] T016 [US1] Update `backend/src/api/routes/chatkit.py` send_message endpoint to call prune_session_messages after Runner.run
- [x] T017 [US1] Add logging for session operations (creation, pruning, stats) in SessionManager

**Checkpoint**: At this point, User Story 1 should be fully functional - chatbot maintains context across messages with automatic pruning

---

## Phase 4: User Story 2 - Session Isolation and Management (Priority: P2)

**Goal**: Ensure conversations from different users/threads don't interfere with each other

**Independent Test**: Create two separate threads, send different messages to each, verify no context bleeding

### Tests for User Story 2 (TDD - Write FIRST, Ensure FAIL)

- [x] T018 [P] [US2] Integration test for session isolation between different users in `backend/tests/integration/test_session_isolation.py`
- [x] T019 [P] [US2] Integration test for session isolation between different threads (same user) in `backend/tests/integration/test_session_isolation.py`
- [x] T020 [P] [US2] Unit test for concurrent request handling (sequential processing) in `backend/tests/unit/test_session_manager.py`
- [x] T021 [P] [US2] Integration test for concurrent messages to same thread in `backend/tests/integration/test_session_isolation.py`

### Implementation for User Story 2

- [x] T022 [US2] Add request queueing mechanism for same conversation thread in `backend/src/api/routes/chatkit.py` (FR-012: sequential processing)
- [x] T023 [US2] Add session ID collision prevention validation in `backend/src/agent/session.py` (verify UUID-based format prevents collisions)
- [x] T024 [US2] Add logging for session isolation events (different users, different threads) in SessionManager

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - context maintained AND isolated per thread

---

## Phase 5: User Story 3 - Conversation Persistence (Priority: P3)

**Goal**: Conversation history persists across chatbot restarts and deployments

**Independent Test**: Have conversation, restart service, send follow-up message referencing previous context

### Tests for User Story 3 (TDD - Write FIRST, Ensure FAIL)

- [x] T025 [P] [US3] Integration test for persistence across service restart in `backend/tests/integration/test_session_persistence.py`
- [x] T026 [P] [US3] Integration test for session recovery after 24+ hours in `backend/tests/integration/test_session_persistence.py`
- [x] T027 [P] [US3] Unit test for cleanup of inactive sessions (7 days) in `backend/tests/unit/test_session_manager.py`

### Implementation for User Story 3

- [x] T028 [US3] Implement SessionManager.cleanup_inactive_sessions() method in `backend/src/agent/session_manager.py` (deletes sessions inactive > 7 days)
- [x] T029 [US3] Create background cleanup job in `backend/src/database/cleanup.py` using FastAPI lifespan events
- [x] T030 [US3] Schedule cleanup job to run daily at configured hour (default 2 AM UTC) in `backend/src/database/cleanup.py`
- [x] T031 [US3] Add cleanup job logging and metrics in `backend/src/database/cleanup.py`

**Checkpoint**: All user stories should now be independently functional - context, isolation, AND persistence

---

## Phase 6: Error Handling & Edge Cases

**Purpose**: Implement robust error handling per clarifications (FR-007, FR-013, FR-014)

### Tests for Error Handling (TDD - Write FIRST, Ensure FAIL)

- [x] T032 [P] Unit test for database unavailable scenario in `backend/tests/unit/test_session_manager.py`
- [x] T033 [P] Unit test for corrupted session data recovery in `backend/tests/unit/test_session_manager.py`
- [x] T034 [P] Unit test for non-existent session ID handling in `backend/tests/unit/test_session_manager.py`
- [x] T035 [P] Integration test for graceful degradation (continue without context) in `backend/tests/integration/test_session_persistence.py`

### Implementation for Error Handling

- [x] T036 [P] Implement database unavailable handling in `backend/src/api/routes/chatkit.py` (FR-007: continue without context, warn user)
- [x] T037 [P] Implement SessionManager.clear_session() method in `backend/src/agent/session_manager.py` (FR-013: clear corrupted session)
- [x] T038 [P] Add corrupted session data detection and recovery in `backend/src/agent/session.py` (catch JSONDecodeError, call clear_session)
- [x] T039 [P] Add non-existent session ID handling in SessionManager.get_session() (FR-014: create new session with that ID)
- [x] T040 Add error response format with warning field in `backend/src/api/routes/chatkit.py` (e.g., {"content": "...", "warning": "Context unavailable"})

**Checkpoint**: System handles all edge cases gracefully without blocking users

---

## Phase 7: Contract Tests & API Validation

**Purpose**: Verify API contracts remain unchanged (transparent enhancement)

**Note**: Integration tests T011 (context continuity), T021 (concurrent messages), and T044 (end-to-end flow) implicitly validate performance criteria SC-004 (response time) and SC-007 (concurrent conversations). Explicit performance benchmarks can be added if needed.

- [x] T041 [P] Contract test for POST /chatkit/threads endpoint in `backend/tests/contract/test_chatkit_api.py` (verify no changes)
- [x] T042 [P] Contract test for POST /chatkit/threads/{thread_id}/messages endpoint in `backend/tests/contract/test_chatkit_api.py` (verify response format unchanged)
- [x] T043 [P] Contract test for GET /chatkit/threads/{thread_id} endpoint in `backend/tests/contract/test_chatkit_api.py` (verify no changes)
- [x] T044 Integration test for end-to-end conversation flow with session persistence in `backend/tests/integration/test_chatkit_api.py`

**Checkpoint**: API contracts validated - frontend requires no changes

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T045 [P] Add comprehensive docstrings to SessionManager class in `backend/src/agent/session_manager.py`
- [x] T046 [P] Add type hints validation (mypy strict mode) for all session management code - verify/update mypy.ini or pyproject.toml configuration in backend/
- [x] T047 [P] Update quickstart.md with session management examples and troubleshooting
- [x] T048 [P] Add monitoring metrics for session operations (creation rate, cleanup count, database size)
- [x] T049 [P] Set SQLite file permissions to 600 (owner read/write only) in SessionManager.__init__
- [x] T050 Code review and refactoring for simplicity (YAGNI principle)
- [x] T051 Run full test suite and verify 90%+ coverage for session management code
- [x] T052 Validate quickstart.md examples work correctly

**Checkpoint**: Production-ready implementation with documentation and monitoring

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Error Handling (Phase 6)**: Can start after Foundational, parallel with user stories
- **Contract Tests (Phase 7)**: Depends on user story implementations being complete
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- SessionManager methods before API integration
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Error handling tasks marked [P] can run in parallel
- Contract tests marked [P] can run in parallel
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task T008: "Unit test for session creation with file-based storage"
Task T009: "Unit test for session ID generation format"
Task T010: "Unit test for message limit enforcement"
Task T011: "Integration test for context continuity"
Task T012: "Integration test for message pruning"

# After tests fail, implement in sequence:
Task T013: "Implement SessionManager.get_session()"
Task T014: "Implement SessionManager.prune_session_messages()"
Task T015: "Implement SessionManager.get_session_stats()"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007) - CRITICAL
3. Complete Phase 3: User Story 1 (T008-T017)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - chatbot now remembers context!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - Context continuity)
3. Add User Story 2 → Test independently → Deploy/Demo (+ Session isolation)
4. Add User Story 3 → Test independently → Deploy/Demo (+ Restart persistence)
5. Add Error Handling → Test independently → Deploy/Demo (+ Robust error handling)
6. Each increment adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T007)
2. Once Foundational is done:
   - Developer A: User Story 1 (T008-T017)
   - Developer B: User Story 2 (T018-T024)
   - Developer C: User Story 3 (T025-T031)
   - Developer D: Error Handling (T032-T040)
3. Stories complete and integrate independently
4. Team completes Contract Tests + Polish together (T041-T052)

---

## Task Summary

**Total Tasks**: 52
- Setup: 3 tasks
- Foundational: 4 tasks (BLOCKING)
- User Story 1 (P1): 10 tasks (5 tests + 5 implementation)
- User Story 2 (P2): 7 tasks (4 tests + 3 implementation)
- User Story 3 (P3): 7 tasks (3 tests + 4 implementation)
- Error Handling: 9 tasks (4 tests + 5 implementation)
- Contract Tests: 4 tasks
- Polish: 8 tasks

**Parallel Opportunities**: 28 tasks marked [P] can run in parallel within their phase

**Test Coverage**: 20 test tasks (38% of total) following TDD approach

**MVP Scope**: Phases 1-3 (17 tasks) delivers User Story 1 - chatbot remembers context

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD MANDATORY**: Verify tests fail before implementing (constitution requirement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- File paths follow backend/frontend separation per plan.md
- SQLite database at `data/agent_sessions.db` (file-based, not in-memory)
- No PostgreSQL schema changes required
- Frontend requires no changes (transparent enhancement)
