# Quick Reference: Development with Hot Reload

## Start Development Environment

```bash
# One command to start everything
./deployment/dev-start.sh
```

**What it does**:
- ✅ Starts Minikube (if not running)
- ✅ Configures Docker for Minikube
- ✅ Creates Kubernetes secrets from `.env`
- ✅ Builds development containers
- ✅ Deploys to Kubernetes with Skaffold
- ✅ Enables hot reload for backend and frontend
- ✅ Forwards ports to localhost
- ✅ Streams logs from all pods

**Access URLs**:
- Frontend: http://localhost:8080
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Prerequisites

```bash
# Install Skaffold
brew install skaffold  # macOS
# Or: https://skaffold.dev/docs/install/

# Install Minikube (if not installed)
brew install minikube  # macOS
# Or: https://minikube.sigs.k8s.io/docs/start/

# Create .env file
cp .env.example .env

# Generate JWT secret
./deployment/generate-jwt-secret.sh

# Edit .env and add:
# - GEMINI_API_KEY (get from https://aistudio.google.com/app/apikey)
# - DATABASE_URL (PostgreSQL connection string)
# - JWT_SECRET_KEY (from generate-jwt-secret.sh)
nano .env
```

## Development Workflow

### 1. Make Changes

**Backend** (Python):
```bash
# Edit any file in backend/src/
nano backend/src/agent/todo_agent.py
```

**Frontend** (React):
```bash
# Edit any file in frontend/src/
nano frontend/src/components/ChatInterface.tsx
```

### 2. See Changes Automatically

**Backend**:
- Skaffold syncs `.py` files to container
- uvicorn restarts automatically (~2-3 seconds)
- Changes reflect at http://localhost:8000

**Frontend**:
- Skaffold syncs source files to container
- Vite HMR updates browser instantly (<1 second)
- Changes reflect at http://localhost:8080

### 3. View Logs

Logs are streamed automatically in the terminal running `dev-start.sh`.

Or view specific pod logs:
```bash
# Backend logs
kubectl logs -f deployment/todo-chatbot-backend

# Frontend logs
kubectl logs -f deployment/todo-chatbot-frontend
```

### 4. Stop Development

Press `Ctrl+C` in the terminal running `dev-start.sh`.

## Common Commands

### Restart Pods
```bash
# Restart backend
kubectl rollout restart deployment/todo-chatbot-backend

# Restart frontend
kubectl rollout restart deployment/todo-chatbot-frontend
```

### View Pod Status
```bash
kubectl get pods
kubectl describe pod <pod-name>
```

### Access Pod Shell
```bash
# Backend
kubectl exec -it deployment/todo-chatbot-backend -- /bin/sh

# Frontend
kubectl exec -it deployment/todo-chatbot-frontend -- /bin/sh
```

### Update Secret
```bash
# After editing .env
kubectl delete secret todo-chatbot-secret
kubectl create secret generic todo-chatbot-secret --from-env-file=.env
kubectl rollout restart deployment/todo-chatbot-backend
```

### View Database
```bash
# PostgreSQL (Neon)
psql $DATABASE_URL

# SQLite (Agent Sessions)
kubectl exec -it deployment/todo-chatbot-backend -- sqlite3 /app/data/agent_sessions.db
```

## Troubleshooting

### Changes not reflecting?

**Backend**:
```bash
# Check if --reload is enabled
kubectl logs deployment/todo-chatbot-backend | grep reload

# Should see: "Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)"
# Should see: "Started reloader process"
```

**Frontend**:
```bash
# Check if Vite dev server is running
kubectl logs deployment/todo-chatbot-frontend | grep VITE

# Should see: "VITE v5.x.x ready in xxx ms"
# Should see: "Local: http://localhost:5173/"
```

### Port already in use?
```bash
lsof -i :8080  # Find process
kill -9 <PID>  # Kill process
```

### Minikube not running?
```bash
./deployment/minikube-setup.sh
```

### Skaffold not found?
```bash
brew install skaffold  # macOS
# Or: https://skaffold.dev/docs/install/
```

### GEMINI_API_KEY not working?
```bash
# Verify in .env
cat .env | grep GEMINI_API_KEY

# Verify in secret
kubectl get secret todo-chatbot-secret -o jsonpath='{.data.GEMINI_API_KEY}' | base64 -d

# Verify in pod
kubectl exec deployment/todo-chatbot-backend -- env | grep GEMINI_API_KEY

# Check logs for errors
kubectl logs deployment/todo-chatbot-backend
```

## Production Deployment

```bash
# Build production images
./deployment/build-images.sh

# Deploy to Kubernetes
./deployment/deploy.sh

# Or upgrade existing deployment
./deployment/deploy.sh --upgrade
```

## File Structure

```
.
├── backend/
│   ├── Dockerfile          # Production image
│   ├── Dockerfile.dev      # Development image (hot reload)
│   └── src/                # Python source code
├── frontend/
│   ├── Dockerfile          # Production image
│   ├── Dockerfile.dev      # Development image (Vite HMR)
│   └── src/                # React source code
├── helm/todo-chatbot/
│   ├── values.yaml         # Production values
│   └── values-dev.yaml     # Development values
├── deployment/
│   ├── dev-start.sh        # Start development environment
│   ├── minikube-setup.sh   # Initialize Minikube
│   ├── build-images.sh     # Build Docker images
│   └── deploy.sh           # Deploy to Kubernetes
├── skaffold.yaml           # Skaffold configuration
├── .env.example            # Environment template
└── .env                    # Your credentials (git-ignored)
```

## Environment Variables

### Required
```bash
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=postgresql://user:password@host:5432/database
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32
```

### Optional
```bash
NEON_API_KEY=your-neon-api-key-here
SENDGRID_API_KEY=your-sendgrid-api-key-here
HIBP_API_KEY=optional-api-key-here
```

## Testing Agent

1. Open http://localhost:8080
2. Register a new user
3. Start chatting:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Mark task 1 as done"
   - "Delete the groceries task"

## Documentation

- [DEVELOPMENT.md](DEVELOPMENT.md) - Comprehensive development guide
- [CONFIGURATION_SUMMARY.md](CONFIGURATION_SUMMARY.md) - Configuration details
- [deployment/README.md](deployment/README.md) - Deployment guide
- [deployment/TROUBLESHOOTING.md](deployment/TROUBLESHOOTING.md) - Troubleshooting

## Support

For issues:
1. Check logs: `kubectl logs deployment/todo-chatbot-backend`
2. Check pod status: `kubectl get pods`
3. Check documentation: [DEVELOPMENT.md](DEVELOPMENT.md)
4. Check troubleshooting: [deployment/TROUBLESHOOTING.md](deployment/TROUBLESHOOTING.md)
