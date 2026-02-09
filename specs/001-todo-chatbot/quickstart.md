# Quickstart Guide: AI-Powered Todo Chatbot

**Date**: 2026-01-29
**Feature**: 001-todo-chatbot
**Status**: Complete

## Overview

This guide provides step-by-step instructions for setting up and running the AI-powered todo chatbot locally. The system consists of a Python backend (FastAPI + FastMCP + OpenAI Agents SDK) and a React frontend (Vite + OpenAI ChatKit).

## Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **PostgreSQL**: 15.x or higher (or Neon account)
- **Git**: Latest version

### Required API Keys
- **Google Gemini API Key**: Free tier from [Google AI Studio](https://ai.google.dev/)
- **Neon Database URL**: Free tier from [Neon](https://neon.tech/)

## Project Structure

```
agentic-todo/
├── backend/          # Python FastAPI backend
│   ├── src/          # Source code
│   ├── tests/        # Tests
│   └── pyproject.toml
├── frontend/         # React frontend
│   ├── src/          # Source code
│   ├── tests/        # Tests
│   └── package.json
└── specs/            # Feature specifications
```

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Install Python Dependencies

Using Poetry (recommended):
```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

Using pip:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/todo_chatbot
# Or use Neon: postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/todo_chatbot

# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# JWT Configuration
JWT_SECRET_KEY=your_secret_key_here_generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# MCP Server Configuration
MCP_SERVER_NAME=Todo MCP Server
MCP_SERVER_VERSION=0.1.0

# Agent Configuration
AGENT_SESSION_DB_PATH=./data/agent_sessions.db
CONVERSATION_RETENTION_DAYS=30
```

### 4. Generate Secret Key

```bash
# Generate JWT secret key
openssl rand -hex 32
# Copy output to JWT_SECRET_KEY in .env
```

### 5. Initialize Database

```bash
# Run database migrations
poetry run alembic upgrade head

# Or with pip:
alembic upgrade head
```

### 6. Run Backend Server

```bash
# With Poetry
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001

# Or with pip
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001
```

Backend will be available at: `http://localhost:8001`

API documentation: `http://localhost:8001/docs`

### 7. Verify Backend Health

```bash
curl http://localhost:8001/health
# Expected response: {"status": "healthy", "database": "connected", "version": "0.1.0"}
```

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create `.env` file in `frontend/` directory:

```bash
# Backend API Configuration
VITE_API_URL=http://localhost:8001
VITE_CHATKIT_URL=http://localhost:8001/chatkit
VITE_CHATKIT_DOMAIN_KEY=local-dev

# Application Configuration
VITE_APP_NAME=Todo Chatbot
VITE_APP_VERSION=0.1.0
```

### 4. Run Frontend Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 5. Build for Production

```bash
npm run build
# Output in dist/ directory
```

## Testing the Application

### 1. Register a New User

**Using cURL**:
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

**Expected Response**:
```json
{
  "user_id": "uuid-here",
  "email": "test@example.com",
  "access_token": "jwt-token-here"
}
```

### 2. Login

**Using cURL**:
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

Save the `access_token` for subsequent requests.

### 3. Test Chat Interface

1. Open browser to `http://localhost:5173`
2. Login with your credentials
3. Start chatting with the AI assistant
4. Try natural language commands:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Mark the first task as complete"
   - "Delete the groceries task"

### 4. Test MCP Tools Directly (Optional)

**Note**: MCP tools are integrated with the AI agent and are not exposed as direct HTTP endpoints. To test task operations, use the chat interface with natural language commands, or use the authentication endpoints to create tasks programmatically through the agent.

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_task_tools.py

# Run with verbose output
poetry run pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### Type Checking

**Backend (Mypy)**:
```bash
cd backend
poetry run mypy src --strict
```

**Frontend (TypeScript)**:
```bash
cd frontend
npm run type-check
```

## Development Workflow

### 1. Start Development Environment

**Terminal 1 - Backend**:
```bash
cd backend
poetry run uvicorn src.api.main:app --reload --port 8001
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Terminal 3 - Tests (optional)**:
```bash
cd backend
poetry run pytest --watch
```

### 2. Make Changes

- Backend code: `backend/src/`
- Frontend code: `frontend/src/`
- Tests: `backend/tests/` or `frontend/tests/`

### 3. Verify Changes

- Backend auto-reloads on file changes
- Frontend hot-reloads on file changes
- Run tests to verify functionality
- Check type checking passes

### 4. Commit Changes

```bash
# Stage changes
git add .

# Run pre-commit checks (if configured)
pre-commit run --all-files

# Commit with descriptive message
git commit -m "feat: add task completion feature"
```

## Troubleshooting

### Backend Issues

**Database Connection Error**:
```
Error: could not connect to server
```
**Solution**: Verify DATABASE_URL in `.env` and ensure PostgreSQL is running.

**Gemini API Error**:
```
Error: 401 Unauthorized
```
**Solution**: Verify GEMINI_API_KEY in `.env` is valid.

**Import Errors**:
```
ModuleNotFoundError: No module named 'fastmcp'
```
**Solution**: Reinstall dependencies with `poetry install` or `pip install -r requirements.txt`.

### Frontend Issues

**API Connection Error**:
```
Network Error: Failed to fetch
```
**Solution**: Verify backend is running at `http://localhost:8001` and VITE_API_URL is correct.

**ChatKit Not Rendering**:
```
Error: ChatKit component not found
```
**Solution**: Reinstall dependencies with `npm install`.

### Common Issues

**Port Already in Use**:
```
Error: Address already in use
```
**Solution**: Kill process using the port or use a different port:
```bash
# Find process using port 8001
lsof -i :8001
# Kill process
kill -9 <PID>
```

**CORS Errors**:
```
Access to fetch blocked by CORS policy
```
**Solution**: Add frontend URL to CORS_ORIGINS in backend `.env`.

## Database Management

### Create Migration

```bash
cd backend
poetry run alembic revision --autogenerate -m "Add new field to tasks"
```

### Apply Migrations

```bash
poetry run alembic upgrade head
```

### Rollback Migration

```bash
poetry run alembic downgrade -1
```

### Reset Database

```bash
# Drop all tables
poetry run alembic downgrade base

# Recreate tables
poetry run alembic upgrade head
```

## Production Deployment

### Backend Deployment

1. Set environment variables in production environment
2. Use production database URL (Neon or managed PostgreSQL)
3. Set `ENVIRONMENT=production` in `.env`
4. Run migrations: `alembic upgrade head`
5. Start server with production ASGI server:
   ```bash
   gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
   ```

### Frontend Deployment

1. Build production bundle:
   ```bash
   npm run build
   ```
2. Deploy `dist/` directory to static hosting (Vercel, Netlify, etc.)
3. Configure environment variables in hosting platform
4. Set VITE_API_URL to production backend URL

## Monitoring and Logging

### Backend Logs

Logs are written to stdout/stderr. Configure log level in `.env`:
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Database Monitoring

Monitor database performance:
```bash
# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Check slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

### Agent Session Monitoring

Check agent session database:
```bash
sqlite3 ./data/agent_sessions.db
.tables
SELECT count(*) FROM sessions;
```

## Next Steps

After completing setup:
1. Review [data-model.md](./data-model.md) for database schema
2. Review [contracts/](./contracts/) for API specifications
3. Run `/sp.tasks` to generate implementation tasks
4. Run `/sp.implement` to execute tasks with TDD workflow

## Support

For issues or questions:
- Check [plan.md](./plan.md) for architecture decisions
- Check [research.md](./research.md) for technical details
- Review API documentation at `http://localhost:8001/docs`

---

**Quickstart Status**: ✅ COMPLETE - Ready for development
