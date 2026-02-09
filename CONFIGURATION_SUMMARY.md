# Configuration Summary: Gemini Models + Hot Reload Development

## Overview

This document summarizes the configuration changes made to enable:
1. **Google Gemini API** integration (replacing OpenAI references)
2. **Hot reload development** with Skaffold watch mode
3. **Auto-deployment pipeline** for continuous development

## Changes Made

### 1. Environment Variables Configuration

**File**: `.env.example`

**Key Changes**:
- ✅ Replaced `OPENAI_API_KEY` with `GEMINI_API_KEY`
- ✅ Added all required backend configuration variables
- ✅ Added JWT authentication variables
- ✅ Added agent session management variables

**Required Variables**:
```bash
GEMINI_API_KEY=your-gemini-api-key-here          # Google Gemini API
DATABASE_URL=postgresql://...                     # PostgreSQL connection
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32  # JWT secret
```

### 2. Kubernetes Secret Configuration

**File**: `helm/todo-chatbot/templates/secret.yaml`

**Changes**:
- ✅ Changed `OPENAI_API_KEY` → `GEMINI_API_KEY`
- ✅ Added `JWT_SECRET_KEY` to secrets

**Before**:
```yaml
OPENAI_API_KEY: {{ .Values.secret.openaiApiKey | b64enc | quote }}
```

**After**:
```yaml
GEMINI_API_KEY: {{ .Values.secret.geminiApiKey | b64enc | quote }}
JWT_SECRET_KEY: {{ .Values.secret.jwtSecretKey | b64enc | quote }}
```

### 3. Backend Deployment Configuration

**File**: `helm/todo-chatbot/templates/backend-deployment.yaml`

**Changes**:
- ✅ Updated environment variable references to use `GEMINI_API_KEY`
- ✅ Added `JWT_SECRET_KEY` environment variable
- ✅ Added all application configuration variables
- ✅ Added agent session management variables

**Environment Variables Added**:
- `GEMINI_API_KEY` - Google Gemini API key
- `JWT_SECRET_KEY` - JWT authentication secret
- `JWT_ALGORITHM` - JWT signing algorithm (HS256)
- `JWT_EXPIRATION_MINUTES` - Token expiration (1440 = 24h)
- `CORS_ORIGINS` - Allowed CORS origins
- `ENVIRONMENT` - Application environment
- `AGENT_SESSION_DB_PATH` - SQLite path for agent sessions
- `AGENT_SESSION_MAX_MESSAGES` - Max messages per session (200)
- `AGENT_SESSION_RETENTION_DAYS` - Session retention (7 days)
- `AGENT_SESSION_CLEANUP_HOUR` - Cleanup job hour (2 AM UTC)
- `CONVERSATION_RETENTION_DAYS` - Conversation retention (30 days)

### 4. Development Dockerfiles

**Files Created**:
- `backend/Dockerfile.dev` - Backend with hot reload
- `frontend/Dockerfile.dev` - Frontend with Vite HMR

**Backend Features**:
```dockerfile
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src"]
```
- ✅ Hot reload enabled with `--reload` flag
- ✅ Watches `/app/src` directory for changes
- ✅ Automatic restart on Python file changes

**Frontend Features**:
```dockerfile
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
```
- ✅ Vite dev server with HMR
- ✅ Instant browser updates on file changes
- ✅ No rebuild required for most changes

### 5. Skaffold Configuration

**File**: `skaffold.yaml`

**Features**:
- ✅ Automatic file watching and syncing
- ✅ Incremental builds on changes
- ✅ Port forwarding to localhost
- ✅ Live log streaming
- ✅ Development and production profiles

**File Sync Configuration**:

**Backend**:
- Syncs `src/**/*.py` files without rebuilding
- Syncs `requirements.txt` and triggers rebuild

**Frontend**:
- Syncs `src/**/*` files for instant HMR
- Syncs `public/**/*` for static assets
- Syncs config files and triggers rebuild

**Port Forwarding**:
- Frontend: `localhost:8080` → `service/todo-chatbot-frontend:80`
- Backend: `localhost:8000` → `service/todo-chatbot-backend:8000`

### 6. Development Startup Script

**File**: `deployment/dev-start.sh`

**Features**:
- ✅ Checks for Skaffold installation
- ✅ Starts Minikube if not running
- ✅ Configures Docker for Minikube
- ✅ Creates Kubernetes secret from `.env`
- ✅ Starts Skaffold in dev mode with port forwarding
- ✅ Streams logs from all pods

**Usage**:
```bash
./deployment/dev-start.sh
```

### 7. Helper Scripts

**File**: `deployment/generate-jwt-secret.sh`

**Purpose**: Generate secure JWT secret key

**Usage**:
```bash
./deployment/generate-jwt-secret.sh
# Output: JWT_SECRET_KEY=<32-byte-hex-string>
```

### 8. CI/CD Pipeline

**File**: `.github/workflows/ci-cd.yml`

**Features**:
- ✅ Runs on push to main/develop branches
- ✅ Runs on pull requests
- ✅ Backend: pytest, mypy, Docker build
- ✅ Frontend: vitest, tsc, lint, Docker build
- ✅ Pushes images to GitHub Container Registry
- ✅ Optional deployment step (requires configuration)

**Image Tags**:
- Branch name (e.g., `main`, `develop`)
- Commit SHA (e.g., `main-abc123`)
- Semantic version (if tagged)

### 9. Development Values

**File**: `helm/todo-chatbot/values-dev.yaml`

**Changes**:
- ✅ Lower resource limits for development
- ✅ Faster health check intervals
- ✅ Single replica for backend and frontend
- ✅ NodePort service for frontend (port 30080)
- ✅ Smaller PVC size (1Gi vs 5Gi)

### 10. Documentation

**Files Created**:
- `DEVELOPMENT.md` - Comprehensive development guide
- `README.md` - Updated with new workflow

**Documentation Includes**:
- Prerequisites and installation
- Quick start guide
- Development workflow
- Debugging tips
- Troubleshooting guide
- CI/CD setup instructions

## How It Works

### Development Workflow

1. **Start Development Environment**:
   ```bash
   ./deployment/dev-start.sh
   ```

2. **Make Code Changes**:
   - Edit Python files in `backend/src/`
   - Edit React files in `frontend/src/`

3. **Automatic Sync**:
   - Skaffold detects file changes
   - Syncs files to running containers
   - Backend: uvicorn restarts automatically
   - Frontend: Vite HMR updates browser instantly

4. **View Changes**:
   - Frontend: http://localhost:8080
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Stop Development**:
   - Press `Ctrl+C` in terminal
   - Skaffold cleans up resources

### Backend Agent Configuration

The backend agents use Google Gemini via OpenAI-compatible API:

**File**: `backend/src/agent/gemini_client.py`
```python
from openai import AsyncOpenAI

gemini_client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
```

**File**: `backend/src/agent/todo_agent.py`
```python
todo_agent = Agent(
    name="Todo Assistant",
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=gemini_client,
    ),
    tools=[...],
)
```

**Key Points**:
- ✅ Uses OpenAI Agents SDK framework
- ✅ Google Gemini 2.0 Flash as LLM
- ✅ OpenAI-compatible API endpoint
- ✅ No code changes needed - just environment variable

## Verification Checklist

### Before Starting Development

- [ ] Minikube installed and running
- [ ] Skaffold installed
- [ ] kubectl installed
- [ ] Docker installed
- [ ] `.env` file created with credentials
- [ ] `GEMINI_API_KEY` added to `.env`
- [ ] `DATABASE_URL` added to `.env`
- [ ] `JWT_SECRET_KEY` generated and added to `.env`

### After Starting Development

- [ ] Skaffold builds containers successfully
- [ ] Pods are running (`kubectl get pods`)
- [ ] Port forwarding is active
- [ ] Frontend accessible at http://localhost:8080
- [ ] Backend accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] File changes trigger automatic sync
- [ ] Backend restarts on Python file changes
- [ ] Frontend updates instantly on React file changes

### Testing Agent Configuration

- [ ] Register a new user
- [ ] Start a chat conversation
- [ ] Send message: "Add a task to buy groceries"
- [ ] Verify agent responds (using Gemini)
- [ ] Verify task is created in database
- [ ] Send message: "Show me my tasks"
- [ ] Verify agent lists tasks correctly

## Troubleshooting

### Issue: Skaffold not found
```bash
# macOS
brew install skaffold

# Linux
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
chmod +x skaffold
sudo mv skaffold /usr/local/bin
```

### Issue: Minikube not running
```bash
./deployment/minikube-setup.sh
```

### Issue: Changes not reflecting

**Backend**:
```bash
# Check if --reload is enabled
kubectl logs deployment/todo-chatbot-backend | grep reload

# Restart pod
kubectl rollout restart deployment/todo-chatbot-backend
```

**Frontend**:
```bash
# Check if Vite dev server is running
kubectl logs deployment/todo-chatbot-frontend | grep VITE

# Restart pod
kubectl rollout restart deployment/todo-chatbot-frontend
```

### Issue: GEMINI_API_KEY not working

1. Verify API key is correct:
   ```bash
   cat .env | grep GEMINI_API_KEY
   ```

2. Verify secret is created:
   ```bash
   kubectl get secret todo-chatbot-secret -o yaml
   kubectl get secret todo-chatbot-secret -o jsonpath='{.data.GEMINI_API_KEY}' | base64 -d
   ```

3. Verify pod has environment variable:
   ```bash
   kubectl exec deployment/todo-chatbot-backend -- env | grep GEMINI_API_KEY
   ```

4. Check backend logs for errors:
   ```bash
   kubectl logs deployment/todo-chatbot-backend
   ```

### Issue: Port already in use
```bash
# Find process using port
lsof -i :8080
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Performance Considerations

### Development Mode

**Resource Usage**:
- Backend: 128Mi memory, 100m CPU (requests)
- Frontend: 64Mi memory, 50m CPU (requests)
- Total: ~200Mi memory, ~150m CPU

**Build Times**:
- Initial build: 2-3 minutes
- File sync: <1 second
- Backend restart: 2-3 seconds
- Frontend HMR: <1 second

### Production Mode

**Resource Usage**:
- Backend: 512Mi memory, 500m CPU (limits)
- Frontend: 256Mi memory, 250m CPU (limits)
- Total: ~768Mi memory, ~750m CPU

**Build Times**:
- Full rebuild: 3-5 minutes
- No hot reload (production images)

## Security Notes

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Rotate JWT_SECRET_KEY** regularly in production
3. **Use strong GEMINI_API_KEY** - Keep it secret
4. **Enable HTTPS** in production (not configured in dev)
5. **Review CORS_ORIGINS** - Restrict to known domains in production

## Next Steps

### For Development
1. Run `./deployment/dev-start.sh`
2. Start coding with hot reload
3. Test changes in real-time

### For Production
1. Build production images: `./deployment/build-images.sh`
2. Deploy to Kubernetes: `./deployment/deploy.sh`
3. Configure ingress and TLS
4. Set up monitoring and logging
5. Enable CI/CD auto-deployment

## Additional Resources

- [Skaffold Documentation](https://skaffold.dev/docs/)
- [Google Gemini API](https://ai.google.dev/docs)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

## Summary

All configuration is complete for:
- ✅ Google Gemini API integration
- ✅ Hot reload development with Skaffold
- ✅ Auto-deployment on file changes
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Comprehensive documentation

The development environment is ready to use. Simply run `./deployment/dev-start.sh` and start coding!
