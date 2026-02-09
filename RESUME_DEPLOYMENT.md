# Resume Phase 4 Deployment

**Quick Start Guide for Continuing Implementation**

## Current Situation

Implementation stopped at **Task T049** (Start Minikube cluster) because Minikube is not installed.

All preparation work is complete:
- ✅ Dockerfiles created and tested
- ✅ Helm charts created and validated
- ✅ Deployment scripts ready
- ✅ Documentation complete

## Prerequisites Check

Before continuing, verify:

```bash
# Check Docker Desktop is running
docker version

# Check kubectl is available
kubectl version --client

# Check Helm is available
helm version

# Check Minikube is installed (THIS IS MISSING)
minikube version
```

## Install Minikube (Required)

### Windows Installation Options

**Option 1: Chocolatey (Fastest)**
```bash
choco install minikube
```

**Option 2: winget**
```bash
winget install Kubernetes.minikube
```

**Option 3: Manual Download**
1. Visit: https://minikube.sigs.k8s.io/docs/start/
2. Download Windows installer
3. Run installer
4. Restart terminal

**Verify Installation**:
```bash
minikube version
# Expected: minikube version: v1.32.0 or higher
```

## Resume Deployment (Step-by-Step)

### Step 1: Navigate to Project
```bash
cd /c/Users/user/hackathon-2/phase-4-local-kubernetees-deployment
```

### Step 2: Start Minikube (T049)
```bash
./deployment/minikube-setup.sh
```

This script will:
- Verify all tools are installed
- Start Minikube with Docker driver
- Configure 2 CPUs and 2GB RAM
- Enable metrics-server and storage-provisioner addons
- Verify cluster is ready

**Expected Output**:
```
✓ Minikube is installed
✓ kubectl is installed
✓ Helm is installed
Starting Minikube cluster...
✓ Minikube cluster started successfully
```

### Step 3: Configure Docker for Minikube (T050)
```bash
eval $(minikube docker-env)
```

This configures your Docker CLI to use Minikube's Docker daemon.

**Verify**:
```bash
docker info | grep -i minikube
# Should show minikube context
```

### Step 4: Build Images in Minikube (T051)
```bash
./deployment/build-images.sh
```

This rebuilds images inside Minikube's Docker daemon so they're available to Kubernetes.

**Expected Output**:
```
✓ Frontend image built successfully
  Image size: 76.4MB
✓ Backend image built successfully
  Image size: 359MB
✓ Images verified successfully
```

### Step 5: Verify .env File (T052 Prerequisite)
```bash
cat .env
```

Ensure these keys are present:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `JWT_SECRET_KEY` - JWT signing key
- Other configuration values

### Step 6: Deploy to Minikube (T052-T053)
```bash
./deployment/deploy.sh
```

This script will:
- Verify Minikube is running
- Create Kubernetes Secret from .env
- Install Helm chart
- Wait for pods to be ready
- Display deployment status

**Expected Output**:
```
✓ Minikube is running
✓ .env file found
✓ Secret created/updated
✓ Deployment successful
✓ All pods ready
```

### Step 7: Verify Deployment (T054-T069)

**Check Pods (T054)**:
```bash
kubectl get pods
```
Expected: All pods in `Running` state with `READY 1/1`

**Check PVC (T055)**:
```bash
kubectl get pvc
```
Expected: `backend-data` PVC in `Bound` state

**Check Liveness Probes (T056-T057)**:
```bash
kubectl describe pod -l component=frontend | grep -A 5 "Liveness"
kubectl describe pod -l component=backend | grep -A 5 "Liveness"
```
Expected: Probes passing with no failures

**Check Readiness Probes (T058-T059)**:
```bash
kubectl describe pod -l component=frontend | grep -A 5 "Readiness"
kubectl describe pod -l component=backend | grep -A 5 "Readiness"
```
Expected: Probes passing with no failures

**Get Frontend URL (T060-T061)**:
```bash
minikube service todo-chatbot-frontend --url
```
Expected: URL like `http://192.168.49.2:30080`

**Test Frontend (T061)**:
```bash
curl $(minikube service todo-chatbot-frontend --url)
```
Expected: HTML response with application content

**Test Backend via Port-Forward (T062)**:
```bash
# In one terminal:
kubectl port-forward service/todo-chatbot-backend 8000:8000

# In another terminal:
curl http://localhost:8000/health
```
Expected: `{"status":"healthy","timestamp":"...","version":"2.1"}`

**Test Application Functionality (T063)**:
1. Open frontend URL in browser
2. Create a new todo item
3. Verify it appears in the list
4. Update the todo item
5. Delete the todo item

**Test Self-Healing (T064-T065)**:
```bash
# Delete backend pod
kubectl delete pod -l component=backend

# Watch recreation (should be <30 seconds)
kubectl get pods -w
```
Expected: New pod created automatically and reaches `Running` state

**Test SQLite Persistence (T066)**:
```bash
# Create a chat session via frontend
# Note the session ID

# Restart backend pod
kubectl rollout restart deployment/todo-chatbot-backend

# Wait for new pod
kubectl wait --for=condition=ready pod -l component=backend --timeout=60s

# Verify session data persists (check via frontend)
```
Expected: Session data still available after restart

**Test Rolling Update (T067-T068)**:
```bash
# Trigger rolling update
kubectl rollout restart deployment/todo-chatbot-backend

# Watch rollout status
kubectl rollout status deployment/todo-chatbot-backend
```
Expected: `deployment "todo-chatbot-backend" successfully rolled out`

**Check Resource Limits (T069)**:
```bash
kubectl top pods
```
Expected: Pods within configured limits (Frontend: <1Gi RAM, Backend: <2Gi RAM)

## Verification Checklist

After completing all steps, verify:

- [ ] Minikube cluster is running
- [ ] Docker configured for Minikube
- [ ] Images built in Minikube context
- [ ] Kubernetes Secret created
- [ ] Helm chart installed
- [ ] All pods in Running state
- [ ] PVC bound successfully
- [ ] Liveness probes passing
- [ ] Readiness probes passing
- [ ] Frontend accessible via URL
- [ ] Backend accessible via port-forward
- [ ] Application functionality works
- [ ] Self-healing verified
- [ ] Persistence verified
- [ ] Rolling updates work

## Troubleshooting

### Minikube Won't Start
```bash
# Check Docker Desktop is running
docker version

# Delete and recreate cluster
minikube delete
minikube start --cpus=2 --memory=2048 --driver=docker
```

### Pods Not Starting
```bash
# Check pod logs
kubectl logs -l component=backend
kubectl logs -l component=frontend

# Check pod events
kubectl describe pod -l component=backend
```

### Images Not Found
```bash
# Verify Docker context
docker info | grep -i minikube

# Rebuild images
eval $(minikube docker-env)
./deployment/build-images.sh
```

### Secret Issues
```bash
# Recreate secret
kubectl delete secret todo-chatbot-secret
kubectl create secret generic todo-chatbot-secret --from-env-file=.env
```

### More Help
See `deployment/TROUBLESHOOTING.md` for detailed troubleshooting guide.

## Cleanup (When Done Testing)

```bash
# Remove deployment
./deployment/cleanup.sh

# Or manually:
helm uninstall todo-chatbot
kubectl delete secret todo-chatbot-secret
kubectl delete pvc backend-data

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Next Steps After Deployment

Once deployment is verified:

1. **Complete T090**: Run end-to-end validation from `quickstart.md`
2. **Document Results**: Update `DEPLOYMENT_STATUS.md` with results
3. **Create PHR**: Document this implementation session
4. **Consider Phase 5**: Plan for cloud deployment (AWS EKS, GCP GKE, or Azure AKS)

## Estimated Time

- Minikube installation: 2-5 minutes
- Cluster setup: 2-3 minutes
- Image building: 3-5 minutes
- Deployment: 2-3 minutes
- Verification: 10-15 minutes

**Total**: 20-30 minutes

## Questions?

- Check `deployment/README.md` for detailed documentation
- Check `deployment/TROUBLESHOOTING.md` for common issues
- Check `specs/004-local-k8s-deployment/tasks.md` for task details
- Check `DEPLOYMENT_STATUS.md` for current status
