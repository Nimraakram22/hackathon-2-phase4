# Development Workflow Guide

This guide explains how to develop the Todo Chatbot application with hot reload and automatic deployment to local Kubernetes.

## Prerequisites

1. **Minikube** - Local Kubernetes cluster
   ```bash
   # macOS
   brew install minikube

   # Linux
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```

2. **Skaffold** - Kubernetes development tool
   ```bash
   # macOS
   brew install skaffold

   # Linux
   curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
   chmod +x skaffold
   sudo mv skaffold /usr/local/bin
   ```

3. **kubectl** - Kubernetes CLI (usually installed with Minikube)

4. **Docker** - Container runtime (usually installed with Minikube)

## Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from example
cp .env.example .env

# Generate JWT secret
./deployment/generate-jwt-secret.sh

# Edit .env and add your credentials
nano .env
```

**Required variables:**
- `GEMINI_API_KEY` - Your Google Gemini API key (get from https://aistudio.google.com/app/apikey)
- `DATABASE_URL` - PostgreSQL connection string (Neon or local)
- `JWT_SECRET_KEY` - Generate with `./deployment/generate-jwt-secret.sh`

**Optional variables:**
- `NEON_API_KEY` - Neon API key for database management
- `SENDGRID_API_KEY` - SendGrid API key for email notifications
- `HIBP_API_KEY` - Have I Been Pwned API key for password security

### 2. Start Development Environment

```bash
# Start Minikube and deploy with hot reload
./deployment/dev-start.sh
```

This will:
- ✅ Start Minikube (if not running)
- ✅ Configure Docker to use Minikube's daemon
- ✅ Create Kubernetes secrets from `.env`
- ✅ Build development containers with hot reload
- ✅ Deploy to Kubernetes with Skaffold
- ✅ Set up file watching for automatic rebuilds
- ✅ Forward ports to localhost

**Access URLs:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 3. Make Changes

The development environment watches for file changes and automatically:

**Backend (Python):**
- Syncs `.py` files to container
- Restarts uvicorn server (via `--reload` flag)
- Changes reflect in ~2-3 seconds

**Frontend (React/Vite):**
- Syncs source files to container
- Vite HMR updates browser instantly
- Changes reflect in <1 second

### 4. Stop Development Environment

Press `Ctrl+C` in the terminal running `dev-start.sh`

Skaffold will automatically:
- Stop port forwarding
- Clean up Kubernetes resources (optional)
- Restore Docker environment

## Development Workflow

### Making Code Changes

1. **Edit files** in your IDE (VS Code, PyCharm, etc.)
2. **Save the file** - changes sync automatically
3. **Check the terminal** - Skaffold shows rebuild/sync status
4. **Refresh browser** (or wait for HMR) - see changes

### Viewing Logs

Skaffold streams logs from all pods:

```bash
# Logs are shown automatically in dev-start.sh terminal

# Or view specific pod logs
kubectl logs -f deployment/todo-chatbot-backend
kubectl logs -f deployment/todo-chatbot-frontend
```

### Debugging

**Backend debugging:**
```bash
# Add breakpoints in your IDE
# Or add print statements / logging
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
```

**Frontend debugging:**
- Use browser DevTools (F12)
- React DevTools extension
- Console logs: `console.log("Debug:", data)`

### Database Access

**PostgreSQL (Neon):**
```bash
# Connect via psql
psql $DATABASE_URL

# Or use GUI tool (DBeaver, pgAdmin, etc.)
```

**SQLite (Agent Sessions):**
```bash
# Access SQLite database in pod
kubectl exec -it deployment/todo-chatbot-backend -- sqlite3 /app/data/agent_sessions.db

# Or copy to local machine
kubectl cp todo-chatbot-backend-xxx:/app/data/agent_sessions.db ./sessions.db
sqlite3 sessions.db
```

## Architecture

### Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Dockerfile | `Dockerfile.dev` | `Dockerfile` |
| Hot Reload | ✅ Enabled | ❌ Disabled |
| File Sync | ✅ Skaffold sync | ❌ N/A |
| Image Build | On change | On deploy |
| Resources | Low (128Mi/100m) | High (512Mi/500m) |
| Replicas | 1 | 3+ |
| Port Forward | ✅ Automatic | ❌ Use Ingress |

### Container Images

**Backend (Development):**
- Base: `python:3.11-alpine`
- Command: `uvicorn src.api.main:app --reload --reload-dir /app/src`
- Port: 8000
- Hot reload: ✅ Enabled

**Frontend (Development):**
- Base: `node:20.11.1-alpine`
- Command: `npm run dev -- --host 0.0.0.0 --port 5173`
- Port: 5173 (Vite dev server)
- HMR: ✅ Enabled

### Kubernetes Resources

**Deployments:**
- `todo-chatbot-backend` - FastAPI backend (1 replica)
- `todo-chatbot-frontend` - Vite dev server (1 replica)

**Services:**
- `todo-chatbot-backend` - ClusterIP on port 8000
- `todo-chatbot-frontend` - NodePort on port 80 → 5173

**Secrets:**
- `todo-chatbot-secret` - Created from `.env` file

**PersistentVolumeClaim:**
- `todo-chatbot-backend-data` - 1Gi for SQLite sessions

## Troubleshooting

### Skaffold not found
```bash
# Install Skaffold
brew install skaffold  # macOS
# Or see: https://skaffold.dev/docs/install/
```

### Minikube not running
```bash
# Start Minikube
./deployment/minikube-setup.sh

# Or manually
minikube start --cpus=2 --memory=4096
```

### Docker not configured for Minikube
```bash
# Configure Docker
eval $(minikube docker-env)

# Verify
docker info | grep minikube
```

### Changes not reflecting

**Backend:**
```bash
# Check if uvicorn --reload is running
kubectl logs deployment/todo-chatbot-backend | grep reload

# Restart pod
kubectl rollout restart deployment/todo-chatbot-backend
```

**Frontend:**
```bash
# Check if Vite dev server is running
kubectl logs deployment/todo-chatbot-frontend | grep VITE

# Restart pod
kubectl rollout restart deployment/todo-chatbot-frontend
```

### Port already in use
```bash
# Find process using port
lsof -i :8080
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in skaffold.yaml
```

### Secret not found
```bash
# Recreate secret from .env
kubectl delete secret todo-chatbot-secret
kubectl create secret generic todo-chatbot-secret --from-env-file=.env
```

### Pod not starting
```bash
# Check pod status
kubectl get pods

# View pod events
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>

# Common issues:
# - Missing environment variables in .env
# - Invalid GEMINI_API_KEY
# - Database connection failed
```

## CI/CD Pipeline

### GitHub Actions

The project includes a CI/CD pipeline (`.github/workflows/ci-cd.yml`) that:

1. **On Pull Request:**
   - Runs backend tests (pytest)
   - Runs frontend tests (vitest)
   - Runs type checking (mypy, tsc)
   - Builds Docker images (no push)

2. **On Push to main:**
   - Runs all tests
   - Builds and pushes images to GitHub Container Registry
   - Tags images with branch name and commit SHA

3. **On Push to main (deploy job):**
   - Deploys to Kubernetes cluster (requires configuration)

### Setting Up Auto-Deployment

To enable auto-deployment on push:

1. **Configure Kubernetes cluster access:**
   ```bash
   # Add kubeconfig to GitHub Secrets
   cat ~/.kube/config | base64
   # Add as KUBE_CONFIG secret in GitHub
   ```

2. **Update deploy job in `.github/workflows/ci-cd.yml`:**
   ```yaml
   deploy:
     needs: [backend, frontend]
     runs-on: ubuntu-latest
     steps:
       - name: Set up kubectl
         uses: azure/setup-kubectl@v3

       - name: Configure kubectl
         run: |
           echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > ~/.kube/config

       - name: Deploy with Helm
         run: |
           helm upgrade --install todo-chatbot ./helm/todo-chatbot \
             --set backend.image=${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}:${{ github.sha }} \
             --set frontend.image=${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}:${{ github.sha }}
   ```

3. **Add secrets to GitHub:**
   - `KUBE_CONFIG` - Base64-encoded kubeconfig
   - `DATABASE_URL` - PostgreSQL connection string
   - `GEMINI_API_KEY` - Google Gemini API key
   - `JWT_SECRET_KEY` - JWT secret key

## Production Deployment

For production deployment without hot reload:

```bash
# Build production images
./deployment/build-images.sh

# Deploy to Kubernetes
./deployment/deploy.sh

# Or upgrade existing deployment
./deployment/deploy.sh --upgrade
```

Production uses:
- `Dockerfile` (not `Dockerfile.dev`)
- No `--reload` flag for uvicorn
- nginx for frontend (not Vite dev server)
- Higher resource limits
- Multiple replicas for high availability

## Additional Resources

- [Skaffold Documentation](https://skaffold.dev/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Google Gemini API](https://ai.google.dev/docs)
