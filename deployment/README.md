# Deployment Guide

This directory contains scripts and documentation for deploying the Todo Chatbot application to a local Kubernetes cluster using Minikube.

---

## 📋 DEPLOYMENT TODO LIST

### Option A: Development Mode (Hot Reload) - RECOMMENDED

Use this for active development with automatic file sync and hot reload.

- [ ] **Step 1**: Create `.env` file
  ```bash
  cp .env.example .env
  ```

- [ ] **Step 2**: Generate JWT secret
  ```bash
  ./deployment/generate-jwt-secret.sh
  ```

- [ ] **Step 3**: Edit `.env` and add your credentials
  ```bash
  nano .env
  # Required:
  #   GEMINI_API_KEY=your-gemini-api-key-here
  #   DATABASE_URL=postgresql://user:pass@host/db
  #   JWT_SECRET_KEY=<from-step-2>
  ```

- [ ] **Step 4**: Verify configuration
  ```bash
  ./deployment/verify-config.sh
  ```

- [ ] **Step 5**: Start development environment
  ```bash
  ./deployment/dev-start.sh
  ```

- [ ] **Step 6**: Access the application
  - Frontend: http://localhost:8080
  - Backend: http://localhost:8000
  - API Docs: http://localhost:8000/docs

**Features**: Hot reload for backend (~2-3s), instant HMR for frontend (<1s), automatic file sync, no rebuild needed.

---

### Option B: Production Mode (Standard Deployment)

Use this for production-like deployment without hot reload.

- [ ] **Step 1**: Setup Minikube cluster
  ```bash
  ./deployment/minikube-setup.sh
  ```

- [ ] **Step 2**: Configure Docker for Minikube
  ```bash
  eval $(minikube docker-env)
  ```

- [ ] **Step 3**: Build container images
  ```bash
  ./deployment/build-images.sh
  ```

- [ ] **Step 4**: Create `.env` file with your credentials
  ```bash
  cp .env.example .env
  # Edit .env with your actual credentials
  nano .env
  ```

- [ ] **Step 5**: Deploy to Minikube
  ```bash
  ./deployment/deploy.sh
  ```

- [ ] **Step 6**: Access the application
  ```bash
  minikube service todo-chatbot-frontend --url
  ```

**Features**: Production-ready deployment, no hot reload, requires rebuild for changes.

---

## 🔄 Common Operations

### Update Deployment
```bash
# After making code changes
./deployment/build-images.sh
./deployment/deploy.sh --upgrade
```

### Restart Pods
```bash
kubectl rollout restart deployment/todo-chatbot-backend
kubectl rollout restart deployment/todo-chatbot-frontend
```

### View Logs
```bash
kubectl logs -f deployment/todo-chatbot-backend
kubectl logs -f deployment/todo-chatbot-frontend
```

### Clean Up
```bash
./deployment/cleanup.sh              # Remove deployment
./deployment/cleanup.sh --delete-cluster  # Remove deployment + cluster
```

---

## Prerequisites

- **Docker Desktop 4.53+**: Container runtime
- **Minikube v1.38+**: Local Kubernetes cluster
- **kubectl v1.34+**: Kubernetes CLI
- **Helm v3.20+**: Kubernetes package manager
- **System Resources**: 8GB RAM, 4 CPU cores minimum

## Scripts

### minikube-setup.sh

Initializes a local Kubernetes cluster with Minikube.

```bash
./deployment/minikube-setup.sh
```

**What it does:**
- Verifies all prerequisites are installed
- Starts Minikube with 2 CPUs and 4GB RAM
- Enables metrics-server and storage-provisioner addons
- Provides instructions for configuring Docker

**Options:**
- Interactive: Prompts to delete existing cluster if found

### build-images.sh

Builds frontend and backend container images.

```bash
./deployment/build-images.sh [--push]
```

**What it does:**
- Builds multi-stage Docker images for frontend and backend
- Tags images with version 1.0.0 and latest
- Verifies images run as non-root users
- Displays image sizes

**Options:**
- `--push`: Push images to container registry (optional)

**Expected Output:**
- Frontend image: ~76MB
- Backend image: ~359MB

### deploy.sh

Deploys the application to Minikube using Helm.

```bash
./deployment/deploy.sh [--upgrade]
```

**What it does:**
- Verifies Minikube is running
- Checks for container images in Minikube registry
- Creates Kubernetes Secret from .env file
- Installs Helm chart
- Waits for pods to be ready
- Displays deployment status and access URLs

**Options:**
- `--upgrade`: Upgrade existing deployment instead of fresh install

**Requirements:**
- Minikube must be running
- Docker must be configured for Minikube: `eval $(minikube docker-env)`
- .env file must exist with credentials

### cleanup.sh

Removes the application from Minikube.

```bash
./deployment/cleanup.sh [--delete-cluster]
```

**What it does:**
- Uninstalls Helm release
- Deletes Kubernetes Secret
- Verifies cleanup
- Optionally deletes Minikube cluster

**Options:**
- `--delete-cluster`: Delete the entire Minikube cluster (optional)

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root with your credentials:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@your-neon-host.neon.tech:5432/your-database

# OpenAI API Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# Neon API Configuration
NEON_API_KEY=your-neon-api-key-here

# SQLite Configuration (for local session storage)
SQLITE_DB_PATH=/app/data/sessions.db

# Application Configuration
LOG_LEVEL=info
BACKEND_API_URL=http://backend:8000
FRONTEND_URL=http://localhost:8080
```

**⚠️ IMPORTANT**: Never commit `.env` to version control. It's already in `.gitignore`.

### Helm Values

Default configuration is in `helm/todo-chatbot/values.yaml`. You can override values during deployment:

```bash
# Override frontend replicas
helm install todo-chatbot ./helm/todo-chatbot --set frontend.replicas=2

# Override image tags
helm install todo-chatbot ./helm/todo-chatbot \
  --set frontend.tag=1.1.0 \
  --set backend.tag=1.1.0

# Use custom values file
helm install todo-chatbot ./helm/todo-chatbot -f custom-values.yaml
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                        │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Frontend Pod    │         │  Backend Pod     │         │
│  │  ┌────────────┐  │         │  ┌────────────┐  │         │
│  │  │   nginx    │  │         │  │  FastAPI   │  │         │
│  │  │  (React)   │  │         │  │  (Python)  │  │         │
│  │  └────────────┘  │         │  └────────────┘  │         │
│  │  Port: 8080      │         │  Port: 8000      │         │
│  │  User: nginx     │         │  User: app       │         │
│  └──────────────────┘         └──────────────────┘         │
│           │                            │                     │
│           │                            │                     │
│  ┌────────▼────────┐         ┌────────▼────────┐           │
│  │ Frontend Service│         │ Backend Service │           │
│  │  LoadBalancer   │         │   ClusterIP     │           │
│  │  Port: 80       │         │   Port: 8000    │           │
│  └─────────────────┘         └─────────────────┘           │
│                                       │                      │
│                              ┌────────▼────────┐            │
│                              │  ConfigMap      │            │
│                              │  (Config Data)  │            │
│                              └─────────────────┘            │
│                                       │                      │
│                              ┌────────▼────────┐            │
│                              │  Secret         │            │
│                              │  (Credentials)  │            │
│                              └─────────────────┘            │
│                                       │                      │
│                              ┌────────▼────────┐            │
│                              │  PVC (5Gi)      │            │
│                              │  SQLite DB      │            │
│                              └─────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Verification Steps

After deployment, verify everything is working:

### 1. Check Pod Status

```bash
kubectl get pods -l app.kubernetes.io/instance=todo-chatbot
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
todo-chatbot-backend-xxxxx              1/1     Running   0          2m
todo-chatbot-frontend-xxxxx             1/1     Running   0          2m
```

### 2. Check Services

```bash
kubectl get services -l app.kubernetes.io/instance=todo-chatbot
```

Expected output:
```
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
todo-chatbot-backend       ClusterIP      10.96.xxx.xxx   <none>        8000/TCP       2m
todo-chatbot-frontend      LoadBalancer   10.96.xxx.xxx   <pending>     80:xxxxx/TCP   2m
```

### 3. Check Persistent Volume

```bash
kubectl get pvc -l app.kubernetes.io/instance=todo-chatbot
```

Expected output:
```
NAME                           STATUS   VOLUME                                     CAPACITY   ACCESS MODES   AGE
todo-chatbot-backend-data      Bound    pvc-xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx     5Gi        RWO            2m
```

### 4. Test Health Endpoints

```bash
# Frontend health check
kubectl port-forward service/todo-chatbot-frontend 8080:80
curl http://localhost:8080/health.html
# Expected: "healthy"

# Backend health check
kubectl port-forward service/todo-chatbot-backend 8000:8000
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected","version":"0.1.0"}
```

### 5. View Logs

```bash
# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -f

# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -f
```

### 6. Test Self-Healing

```bash
# Delete backend pod
kubectl delete pod -l app.kubernetes.io/component=backend

# Watch pod recreate (should be <30 seconds)
kubectl get pods -w
```

### 7. Test SQLite Persistence

```bash
# Create a session in the application
# Then restart the backend pod
kubectl rollout restart deployment/todo-chatbot-backend

# Verify session data persists after restart
```

## Troubleshooting

### Pods Not Starting

**Symptom**: Pods stuck in `Pending` or `ImagePullBackOff`

**Solution**:
```bash
# Check pod events
kubectl describe pod <pod-name>

# If ImagePullBackOff, rebuild images in Minikube context
eval $(minikube docker-env)
./deployment/build-images.sh
```

### Service Not Accessible

**Symptom**: Cannot access frontend URL

**Solution**:
```bash
# Check if pods are ready
kubectl get pods

# Check service endpoints
kubectl get endpoints

# Use port-forward as alternative
kubectl port-forward service/todo-chatbot-frontend 8080:80
```

### Database Connection Issues

**Symptom**: Backend pod crashes or health check fails

**Solution**:
```bash
# Check if secret exists
kubectl get secret todo-chatbot-secret

# Verify secret values
kubectl get secret todo-chatbot-secret -o yaml

# Check backend logs
kubectl logs -l app.kubernetes.io/component=backend
```

### PVC Not Binding

**Symptom**: PVC stuck in `Pending` state

**Solution**:
```bash
# Check PVC status
kubectl describe pvc todo-chatbot-backend-data

# Verify storage class exists
kubectl get storageclass

# Check if storage provisioner is enabled
minikube addons list | grep storage-provisioner
```

## Updating the Deployment

### Update Application Code

```bash
# 1. Make code changes
# 2. Rebuild images with new tag
docker build -t todo-chatbot-frontend:1.1.0 frontend/
docker build -t todo-chatbot-backend:1.1.0 backend/

# 3. Upgrade Helm release
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --set frontend.tag=1.1.0 \
  --set backend.tag=1.1.0
```

### Update Configuration

```bash
# 1. Edit values.yaml or create custom values file
# 2. Upgrade Helm release
helm upgrade todo-chatbot ./helm/todo-chatbot -f custom-values.yaml
```

### Rolling Update

```bash
# Trigger rolling update without changing images
kubectl rollout restart deployment/todo-chatbot-frontend
kubectl rollout restart deployment/todo-chatbot-backend

# Watch rolling update progress
kubectl rollout status deployment/todo-chatbot-backend
```

## Performance Tuning

### Resource Limits

Adjust resource limits in `values.yaml`:

```yaml
backend:
  resources:
    requests:
      memory: "512Mi"  # Increase for better performance
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

### Scaling

```bash
# Scale frontend to 2 replicas
kubectl scale deployment/todo-chatbot-frontend --replicas=2

# Or use Helm
helm upgrade todo-chatbot ./helm/todo-chatbot --set frontend.replicas=2
```

### Storage

Increase PVC size if needed:

```yaml
backend:
  persistence:
    size: 10Gi  # Increase from 5Gi
```

**Note**: PVC size can only be increased, not decreased.

## Security Considerations

1. **Secrets Management**: Never commit `.env` to version control
2. **Non-Root Users**: All containers run as non-root users (nginx, app)
3. **Resource Limits**: Prevent resource exhaustion attacks
4. **Network Policies**: Backend is ClusterIP (internal only)
5. **Image Scanning**: Run `docker scout cves` before deployment

## Next Steps

After successful deployment:

1. **Monitoring**: Set up Prometheus and Grafana
2. **Ingress**: Configure Ingress controller for external access
3. **TLS**: Add TLS certificates for HTTPS
4. **CI/CD**: Automate builds and deployments
5. **Production**: Deploy to cloud Kubernetes (EKS, GKE, AKS)

## Support

For issues or questions:
- Check logs: `kubectl logs <pod-name>`
- Check events: `kubectl describe pod <pod-name>`
- Review troubleshooting section above
- Consult [Kubernetes Docs](https://kubernetes.io/docs/)
- Consult [Helm Docs](https://helm.sh/docs/)
