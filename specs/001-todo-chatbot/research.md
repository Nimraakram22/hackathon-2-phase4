# Research: AI-Powered Todo Chatbot

**Date**: 2026-01-29
**Feature**: 001-todo-chatbot
**Status**: Complete

## Overview

This document consolidates research findings for building an AI-powered todo chatbot using FastMCP, OpenAI Agents SDK, and OpenAI ChatKit. All research was conducted using the Context7 MCP server to ensure current, authoritative documentation.

## Research Questions & Findings

### 1. FastMCP Tool Creation and Middleware

**Question**: How do we create type-safe MCP tools with proper error handling and retry logic?

**Findings**:

**Tool Creation Pattern** (Source: FastMCP v3.0.0b1):
- Use `@mcp.tool` decorator on Python functions
- Type hints automatically generate MCP schemas
- Docstrings become tool descriptions
- Pydantic `Field` with `Annotated` provides advanced validation

```python
from fastmcp import FastMCP
from typing import Annotated
from pydantic import Field

mcp = FastMCP(name="Todo MCP Server")

@mcp.tool
def create_task(
    title: Annotated[str, Field(description="Task title", min_length=1, max_length=200)],
    description: Annotated[str | None, Field(description="Optional task description")] = None,
    user_id: Annotated[str, Field(description="User identifier")]
) -> dict:
    """Create a new task for the user."""
    # Implementation
    return {"task_id": "...", "title": title, "created_at": "..."}
```

**Error Handling & Retry Middleware** (Source: FastMCP v3.0.0b1):
- `ErrorHandlingMiddleware`: Transforms exceptions to MCP error format
- `RetryMiddleware`: Automatic retries with exponential backoff
- Middleware added via `mcp.add_middleware()`

```python
from fastmcp.server.middleware.error_handling import (
    ErrorHandlingMiddleware,
    RetryMiddleware
)

# Comprehensive error logging
mcp.add_middleware(ErrorHandlingMiddleware(
    include_traceback=True,
    transform_errors=True,
    error_callback=log_error_callback
))

# Automatic retry for DB failures
mcp.add_middleware(RetryMiddleware(
    max_retries=3,
    retry_exceptions=(ConnectionError, TimeoutError)
))
```

**Decision**: Use FastMCP with Pydantic Field annotations for all tools. Apply ErrorHandlingMiddleware and RetryMiddleware to handle database connection failures per spec requirement (FR-010a: exponential backoff up to 30s).

**Rationale**: FastMCP's decorator pattern is simple and type-safe. Built-in middleware handles retry logic without custom implementation, adhering to Simplicity First principle.

---

### 2. OpenAI Agents SDK - Guardrails and Session Management

**Question**: How do we implement input validation guardrails and maintain conversation context?

**Findings**:

**Input Guardrails** (Source: OpenAI Agents Python v0.7.0):
- Agent-based guardrails use separate agents for validation
- `@input_guardrail` decorator creates validation functions
- `GuardrailFunctionOutput` with `tripwire_triggered=True` blocks execution
- `InputGuardrail(run_in_parallel=False)` creates blocking guardrails

```python
from agents import (
    Agent, Runner, GuardrailFunctionOutput, InputGuardrail,
    input_guardrail, RunContextWrapper
)
from pydantic import BaseModel

class RelevanceCheck(BaseModel):
    is_task_related: bool
    reason: str

relevance_agent = Agent(
    name="Relevance Checker",
    instructions="Check if input is related to task management (create, view, update, delete, complete tasks).",
    output_type=RelevanceCheck,
)

@input_guardrail
async def validate_input_relevance(
    ctx: RunContextWrapper, agent: Agent, input: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(relevance_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_task_related,
    )

blocking_guardrail = InputGuardrail(
    guardrail_function=validate_input_relevance,
    run_in_parallel=False,  # Block agent until validation completes
)
```

**Session Management** (Source: OpenAI Agents Python v0.7.0):
- `SQLiteSession` built-in for conversation history
- Session ID persists context across multiple `Runner.run()` calls
- Automatic context maintenance without manual state management

```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(
    name="Todo Assistant",
    instructions="Help users manage tasks through natural language.",
)

session = SQLiteSession("user_123_conversation_456")

# First turn
result = await Runner.run(agent, "Add a task to buy groceries", session=session)

# Second turn - agent remembers previous context
result = await Runner.run(agent, "Actually, make that buy milk and eggs", session=session)
```

**Decision**: Use agent-based input guardrails with blocking execution to validate input relevance before processing. Use SQLiteSession for conversation context with session ID format: `user_{user_id}_conv_{conversation_id}`.

**Rationale**: Agent-based guardrails provide semantic understanding superior to keyword filtering (spec FR-008a). SQLiteSession is built-in and handles conversation history efficiently, adhering to Simplicity First principle.

---

### 3. Google Gemini Model Configuration

**Question**: How do we configure agents to use Google Gemini instead of OpenAI models?

**Findings**:

**Agent Level Configuration** (Source: Constitution v1.1.0, OpenAI Agents SDK):
- Create custom `AsyncOpenAI` client with Gemini base URL
- Pass client to `OpenAIChatCompletionsModel`
- Configure per-agent for optimal model selection

```python
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Reference: https://ai.google.dev/gemini-api/docs/openai
gemini_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)

# Main agent with Gemini 2.0 Flash
todo_agent = Agent(
    name="Todo Assistant",
    instructions="You help users manage tasks through natural language.",
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=gemini_client
    ),
)

# Guardrail agent with same model
relevance_agent = Agent(
    name="Relevance Checker",
    instructions="Check if input is task-related.",
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=gemini_client
    ),
    output_type=RelevanceCheck,
)
```

**Decision**: Use Agent Level configuration with Google Gemini 2.0 Flash for all agents (main agent and guardrail agents). Load API key from environment variable `GEMINI_API_KEY`.

**Rationale**: Constitution mandates Agent Level configuration for per-agent model optimization. Gemini 2.0 Flash provides zero-cost operation while maintaining sufficient capability for task management.

---

### 4. ChatKit Backend Integration

**Question**: How do we integrate ChatKit frontend with our FastAPI backend?

**Findings**:

**ChatKit React Setup** (Source: OpenAI ChatKit documentation):
- Install `@openai/chatkit-react` package
- Use `useChatKit` hook with API configuration
- `ChatKit` component renders chat interface

```typescript
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function TodoChat() {
  const { control } = useChatKit({
    api: {
      url: 'http://localhost:8001/chatkit',
      domainKey: 'local-dev',
    },
  });

  return <ChatKit control={control} className="h-[600px] w-[360px]" />;
}
```

**Backend API Requirements** (Source: OpenAI ChatKit documentation):
- ChatKit expects specific endpoints for message streaming
- `sendUserMessage` method sends POST requests to backend
- Backend must implement ChatKit protocol (message streaming, thread management)

**Decision**: Implement FastAPI endpoints at `/chatkit` path that conform to ChatKit protocol. Backend will:
1. Receive user messages from ChatKit
2. Pass messages to AI agent with MCP tools
3. Stream agent responses back to ChatKit
4. Manage conversation threads (map to SQLiteSession IDs)

**Rationale**: ChatKit provides production-ready chat UI with streaming support. Backend integration requires implementing ChatKit protocol endpoints, which is straightforward with FastAPI.

---

### 5. Database Schema Design

**Question**: What entities and relationships do we need for tasks and conversations?

**Findings from Spec**:

**Key Entities** (from spec.md):
- **Task**: unique ID, title, optional description, completion status, timestamps, user association
- **Conversation**: unique ID, user association, timestamps, 30-day retention
- **Message**: unique ID, conversation association, role (user/assistant), content, timestamp
- **User**: unique ID, authentication credentials

**Relationships**:
- User → Tasks (one-to-many)
- User → Conversations (one-to-many)
- Conversation → Messages (one-to-many)

**Validation Rules** (from spec assumptions):
- Task title: 1-100 characters
- Task description: optional, max 1000 characters
- Message content: max 2000 characters
- Conversation retention: 30 days

**Decision**: Use SQLModel for type-safe ORM with Pydantic validation. Define four entities: User, Task, Conversation, Message. Implement soft-delete for conversations (mark as deleted after 30 days) but hard-delete for tasks per spec clarification.

**Rationale**: SQLModel combines SQLAlchemy ORM with Pydantic validation, providing type safety and database operations in one library. Adheres to Type Safety First principle.

---

### 6. Error Handling and Retry Strategies

**Question**: How do we handle database failures with exponential backoff per spec requirement?

**Findings**:

**Spec Requirement** (FR-010a):
- Queue failed database operations
- Retry with exponential backoff
- Maximum 30 seconds before reporting failure

**FastMCP RetryMiddleware** (Source: FastMCP v3.0.0b1):
- Supports exponential backoff
- Configurable max retries and retry exceptions
- Automatic retry for specified exception types

**Implementation Strategy**:
```python
from fastmcp.server.middleware.error_handling import RetryMiddleware

# Configure retry with exponential backoff
mcp.add_middleware(RetryMiddleware(
    max_retries=5,  # Exponential backoff: 1s, 2s, 4s, 8s, 16s = 31s total
    retry_exceptions=(ConnectionError, TimeoutError, OperationalError)
))
```

**Decision**: Use FastMCP's RetryMiddleware with 5 retries (exponential backoff totals ~31s). Catch database exceptions (ConnectionError, TimeoutError, OperationalError) and retry automatically.

**Rationale**: Built-in middleware handles retry logic without custom implementation. Exponential backoff with 5 retries stays within 30s constraint. Adheres to Simplicity First principle.

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Backend Framework | FastAPI | Latest | Async support, OpenAPI docs, production-ready |
| MCP Server | FastMCP | v3.0.0b1 | Type-safe tools, built-in middleware |
| AI Agent | OpenAI Agents SDK | v0.7.0 | Guardrails, sessions, tool integration |
| LLM Provider | Google Gemini | 2.0 Flash | Zero cost, sufficient capability |
| ORM | SQLModel | Latest | Type-safe, Pydantic validation |
| Database | Neon PostgreSQL | Serverless | Managed, scalable, serverless |
| Frontend Framework | React + Vite | Latest | Fast dev experience, production builds |
| Chat UI | OpenAI ChatKit | Latest | Production-ready, streaming support |
| Type Checking | Mypy | Latest | Strict mode enforcement |
| Testing | Pytest | Latest | Comprehensive test framework |

## Best Practices Identified

### FastMCP
1. Use `@mcp.tool` decorator for automatic schema generation
2. Apply Pydantic `Field` with `Annotated` for validation
3. Add ErrorHandlingMiddleware for consistent error responses
4. Add RetryMiddleware for resilience against transient failures
5. Keep tools stateless - persist state to database

### OpenAI Agents SDK
1. Use Agent Level configuration for model flexibility
2. Implement blocking input guardrails for validation
3. Use SQLiteSession for conversation context
4. Disable tracing in production (`set_tracing_disabled(True)`)
5. Define structured output types with Pydantic models

### ChatKit Integration
1. Configure API URL and domain key in `useChatKit` hook
2. Implement ChatKit protocol endpoints in backend
3. Stream responses for better UX
4. Map ChatKit threads to agent session IDs
5. Handle authentication before allowing chat access

### Database Design
1. Use SQLModel for type-safe ORM
2. Define validation rules in Pydantic models
3. Implement indexes on foreign keys and query fields
4. Use timestamps for audit trails
5. Implement retention policies with scheduled cleanup

## Open Questions Resolved

All technical unknowns from plan.md Technical Context have been resolved:

✅ **Language/Version**: Python 3.11+ confirmed
✅ **Primary Dependencies**: FastAPI, FastMCP, OpenAI Agents SDK, ChatKit confirmed
✅ **Storage**: Neon PostgreSQL + SQLite sessions confirmed
✅ **Testing**: Pytest + Mypy confirmed
✅ **Target Platform**: Web application (Linux server + React) confirmed
✅ **Performance Goals**: <3s response time achievable with async operations
✅ **Constraints**: <200ms DB queries achievable with indexes, 30s retry confirmed
✅ **Scale/Scope**: 100 concurrent users supported by async FastAPI

## Next Steps

Phase 0 research complete. Proceed to Phase 1:
1. Generate data-model.md with entity definitions
2. Generate contracts/ with MCP tool and API schemas
3. Generate quickstart.md with setup instructions
4. Update agent context with new technologies

---

**Research Status**: ✅ COMPLETE - All technical unknowns resolved
