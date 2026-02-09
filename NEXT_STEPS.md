# Next Steps: AI-Powered Todo Chatbot

This document provides clear next steps for getting the application running and preparing it for production.

## Immediate: Get It Running (30 minutes)

### Step 1: Install Dependencies

**Backend**:
```bash
cd backend

# Option A: Using Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -
poetry install

# Option B: Using pip
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn[standard] fastmcp openai agents sqlmodel alembic psycopg2-binary pydantic[email] pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart httpx
```

**Frontend**:
```bash
cd frontend
npm install
```

### Step 2: Get API Keys

1. **Google Gemini API Key** (Free):
   - Go to https://ai.google.dev/
   - Sign in with Google account
   - Create API key
   - Copy the key

2. **Neon Database** (Free):
   - Go to https://neon.tech/
   - Sign up for free account
   - Create a new project
   - Copy the connection string

### Step 3: Configure Environment

**Backend** (`backend/.env`):
```bash
cd backend
cp .env.example .env

# Edit .env and set:
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/todo_chatbot
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

**Frontend** (`frontend/.env`):
```bash
cd frontend
cp .env.example .env

# Edit .env and set:
VITE_API_URL=http://localhost:8001
VITE_CHATKIT_URL=http://localhost:8001/chatkit
VITE_CHATKIT_DOMAIN_KEY=local-dev
```

### Step 4: Initialize Database

```bash
cd backend
poetry run alembic upgrade head
# Or with pip: alembic upgrade head
```

### Step 5: Start Services

**Terminal 1 - Backend**:
```bash
cd backend
poetry run uvicorn src.api.main:app --reload --port 8001
# Or with pip: uvicorn src.api.main:app --reload --port 8001
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Step 6: Test It!

1. Open http://localhost:5173
2. Click "Register" and create an account
3. Start chatting:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Mark task 1 as complete"
   - "Delete the groceries task"

---

## Short Term: Polish for Production (2-4 hours)

### Task 1: Add API Documentation
```bash
cd backend/src/api/routes

# Add docstrings to all endpoints in:
# - auth.py
# - chatkit.py
```

### Task 2: Run Type Checking
```bash
cd backend
poetry run mypy src --strict

# Fix any type errors found
```

### Task 3: Add Security Headers
```python
# In backend/src/api/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Add security headers
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Add custom headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### Task 4: Add Rate Limiting
```bash
# Install slowapi
poetry add slowapi

# In backend/src/api/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In backend/src/api/routes/chatkit.py
from slowapi import Limiter

@router.post("/threads/{thread_id}/messages")
@limiter.limit("10/minute")  # 10 messages per minute
async def send_message(...):
    ...
```

### Task 5: Set Up Conversation Cleanup Job
```bash
# Create a cron job or scheduled task

# Option A: Cron (Linux/Mac)
crontab -e
# Add: 0 2 * * * cd /path/to/backend && poetry run python -c "from src.database.cleanup import mark_old_conversations_for_deletion, purge_deleted_conversations; mark_old_conversations_for_deletion(); purge_deleted_conversations()"

# Option B: systemd timer (Linux)
# Create /etc/systemd/system/todo-cleanup.service
# Create /etc/systemd/system/todo-cleanup.timer

# Option C: Python script with schedule library
poetry add schedule
# Create backend/cleanup_job.py
```

---

## Medium Term: Production Deployment (1 day)

### Backend Deployment (Render/Railway/Fly.io)

1. **Prepare for Production**:
```bash
cd backend

# Add gunicorn
poetry add gunicorn

# Create Procfile
echo "web: gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:\$PORT" > Procfile
```

2. **Set Environment Variables** (in hosting platform):
```
DATABASE_URL=<neon-production-url>
GEMINI_API_KEY=<your-key>
JWT_SECRET_KEY=<generate-new-one>
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend-domain.com
```

3. **Deploy**:
- Push to GitHub
- Connect repository to hosting platform
- Deploy

### Frontend Deployment (Vercel/Netlify)

1. **Build for Production**:
```bash
cd frontend
npm run build
```

2. **Set Environment Variables** (in hosting platform):
```
VITE_API_URL=https://your-backend-domain.com
VITE_CHATKIT_URL=https://your-backend-domain.com/chatkit
VITE_CHATKIT_DOMAIN_KEY=production
```

3. **Deploy**:
- Push to GitHub
- Connect repository to Vercel/Netlify
- Deploy

### Database Setup

1. **Production Database** (Neon):
- Create production project
- Enable connection pooling
- Set up backups
- Configure retention policies

2. **Run Migrations**:
```bash
# On production
alembic upgrade head
```

---

## Long Term: Monitoring & Scaling (Ongoing)

### Monitoring

1. **Application Monitoring**:
- Set up Sentry for error tracking
- Add logging with structured logs
- Monitor API response times

2. **Database Monitoring**:
- Monitor query performance
- Set up alerts for slow queries
- Track connection pool usage

3. **Infrastructure Monitoring**:
- Monitor server resources (CPU, memory)
- Set up uptime monitoring
- Track API rate limits

### Scaling

1. **Backend Scaling**:
- Add more Uvicorn workers
- Implement caching (Redis)
- Add database read replicas

2. **Frontend Scaling**:
- CDN for static assets
- Image optimization
- Code splitting

3. **Database Scaling**:
- Optimize indexes
- Partition large tables
- Archive old data

---

## Optional Enhancements

### Features
- [ ] Task priorities (P1, P2, P3)
- [ ] Task due dates and reminders
- [ ] Task categories/tags
- [ ] Task sharing and collaboration
- [ ] Search functionality
- [ ] Export tasks (CSV, JSON)
- [ ] Dark mode
- [ ] Mobile app (React Native)

### Technical
- [ ] Add unit tests (Pytest)
- [ ] Add integration tests
- [ ] Add E2E tests (Playwright)
- [ ] Set up CI/CD pipeline
- [ ] Add code coverage reporting
- [ ] Implement WebSocket for real-time updates
- [ ] Add Redis for caching
- [ ] Implement full-text search (PostgreSQL)

---

## Troubleshooting

### Common Issues

**"poetry: command not found"**:
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

**"Module not found" errors**:
```bash
cd backend
poetry install --no-cache
```

**Database connection errors**:
- Check DATABASE_URL is correct
- Verify Neon database is running
- Check firewall/network settings

**Gemini API errors**:
- Verify API key is valid
- Check API quota/limits
- Ensure API is enabled in Google Cloud Console

**Frontend can't connect to backend**:
- Verify backend is running on port 8001
- Check VITE_API_URL in frontend/.env
- Check CORS_ORIGINS in backend/.env

---

## Getting Help

- **Documentation**: Check `specs/001-todo-chatbot/quickstart.md`
- **Validation Report**: See `QUICKSTART_VALIDATION.md`
- **API Docs**: http://localhost:8001/docs (when backend is running)
- **Architecture**: See `specs/001-todo-chatbot/plan.md`

---

**Last Updated**: 2026-01-29
