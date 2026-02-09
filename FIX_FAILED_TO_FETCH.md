# Fix for "Failed to Fetch" Error

## Problem Identified

The frontend is trying to connect to the backend using `http://backend:8000`, which only works inside the Kubernetes cluster, not from your browser.

## Solution: Change Backend Service to NodePort

We need to expose the backend service so your browser can access it.

### Step 1: Update Backend Service Type

Run this command:

```bash
kubectl patch service todo-chatbot-backend -p '{"spec":{"type":"NodePort"}}'
```

### Step 2: Get the Backend NodePort

```bash
kubectl get svc todo-chatbot-backend
```

Look for the port mapping like `8000:XXXXX/TCP` - the XXXXX is your NodePort.

### Step 3: Update Frontend Environment

The frontend needs to be rebuilt with the correct backend URL.

**Option A: Quick Fix - Use Port-Forward (Temporary)**

Keep both port-forwards running:
```bash
# Terminal 1 - Frontend
kubectl port-forward service/todo-chatbot-frontend 8080:80

# Terminal 2 - Backend
kubectl port-forward service/todo-chatbot-backend 8000:8000
```

Then the frontend should work with `http://localhost:8000`

**Option B: Rebuild Frontend (Permanent)**

1. Update frontend/.env:
```bash
VITE_API_URL=http://192.168.49.2:XXXXX
```
(Replace XXXXX with the backend NodePort)

2. Rebuild and redeploy:
```bash
# Configure Docker for Minikube
eval $(minikube docker-env)

# Rebuild frontend
cd frontend
docker build -t todo-chatbot-frontend:1.0.0 .

# Restart frontend pod
kubectl rollout restart deployment/todo-chatbot-frontend
```

## Quick Test

After applying the fix, test the backend is accessible:

```bash
# If using NodePort
curl http://192.168.49.2:XXXXX/health

# If using port-forward
curl http://localhost:8000/health
```

Expected output: `{"status":"healthy",...}`
