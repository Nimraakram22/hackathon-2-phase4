# Todo Chatbot Backend

AI-powered todo chatbot backend built with FastAPI, FastMCP, and OpenAI Agents SDK.

## Features

- **Natural Language Task Management**: Create, view, update, delete, and complete tasks through conversational AI
- **AI Agent with Guardrails**: Google Gemini 2.0 Flash with input validation
- **MCP Tools**: Task management operations exposed as MCP tools
- **JWT Authentication**: Secure user authentication with bcrypt password hashing
- **PostgreSQL Database**: Neon serverless PostgreSQL for data persistence
- **Conversation Context**: SQLite-based session management for multi-turn conversations
- **Type Safety**: Strict type checking with Mypy and Pydantic validation

## Tech Stack

- **Framework**: FastAPI
- **MCP Server**: FastMCP v3.0.0b1
- **AI Agent**: OpenAI Agents SDK v0.7.0
- **LLM**: Google Gemini 2.0 Flash (via OpenAI-compatible API)
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL (production), SQLite (agent sessions)
- **Migrations**: Alembic
- **Testing**: Pytest with coverage
- **Type Checking**: Mypy (strict mode)

## Setup

### Prerequisites

- Python 3.11+
- Poetry (recommended) or pip
- PostgreSQL database (or Neon account)
- Google Gemini API key

### Installation

1. **Install dependencies**:

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

2. **Configure environment variables**:

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection URL
- `GEMINI_API_KEY`: Google Gemini API key
- `JWT_SECRET_KEY`: Secret key for JWT signing (generate with `openssl rand -hex 32`)

3. **Run database migrations**:

```bash
poetry run alembic upgrade head
```

4. **Start the server**:

```bash
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at `http://localhost:8001`.

API documentation: `http://localhost:8001/docs`

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with email and password
- `GET /auth/me` - Get current user profile

### ChatKit Integration

- `POST /chatkit/threads` - Create new conversation thread
- `POST /chatkit/threads/{thread_id}/messages` - Send message and stream AI response
- `GET /chatkit/threads/{thread_id}` - Get thread with message history

### Health Check

- `GET /health` - Server health status

## MCP Tools

The following MCP tools are available for the AI agent:

- `create_task(user_id, title, description)` - Create a new task
- `list_tasks(user_id, status_filter, limit, offset)` - List user's tasks
- `get_task(user_id, task_id)` - Get task by ID
- `complete_task(user_id, task_id)` - Mark task as completed
- `update_task(user_id, task_id, title, description)` - Update task details
- `delete_task(user_id, task_id)` - Delete task permanently

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_task_tools.py
```

### Type Checking

```bash
poetry run mypy src --strict
```

### Code Formatting

```bash
poetry run black src tests
poetry run ruff check src tests --fix
```

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel entities
│   ├── mcp/             # FastMCP server and tools
│   ├── agent/           # AI agent and guardrails
│   ├── api/             # FastAPI routes and dependencies
│   ├── database/        # Database connection and migrations
│   └── config.py        # Configuration management
├── tests/               # Test suite
├── pyproject.toml       # Poetry dependencies
└── alembic.ini          # Alembic configuration
```

## License

MIT
