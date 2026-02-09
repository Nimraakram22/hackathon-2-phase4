# 🔧 Fix Chat 405 Error - Solution

## Problem Identified

The chat is failing with:
- **405 Method Not Allowed** error
- **URL shows "undefined"** in the request

## Root Cause

The frontend is making a request with an undefined API URL. This happens because:
1. The environment variable `VITE_API_URL` is not available at runtime in the container
2. Vite environment variables are embedded at **build time**, not runtime

## ✅ Quick Fix: Rebuild Frontend with Correct API URL

### Step 1: Verify Backend is Accessible

```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy",...}`

### Step 2: Check Current Frontend Environment

The frontend was built with `VITE_API_URL=http://localhost:8000`, but the container might not have this set correctly.

### Step 3: Rebuild Frontend Container

```bash
# Navigate to project root
cd /c/Users/user/hackathon-2/phase-4-local-kubernetees-deployment

# Configure Docker for Minikube
export PATH="/c/Program Files/Kubernetes/Minikube:$PATH"
eval $(minikube docker-env)

# Rebuild frontend with correct environment
cd frontend
docker build -t todo-chatbot-frontend:1.0.0 .

# Restart frontend pod
cd ..
kubectl rollout restart deployment/todo-chatbot-frontend

# Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend --timeout=120s
```

### Step 4: Hard Refresh Browser

After the pod restarts:
1. Go to http://localhost:8080
2. Press `Ctrl + Shift + Delete` to clear cache
3. Or press `Ctrl + F5` to hard refresh
4. Try the chat again

---

## Alternative: Quick Test Without Rebuild

To verify the backend chat endpoint works:

```bash
# Create a thread
curl -X POST http://localhost:8000/chatkit/threads \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Thread"}'

# Send a message (replace THREAD_ID with the ID from above)
curl -X POST http://localhost:8000/chatkit/threads/THREAD_ID/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, create a task to test the chat"}'
```

If these work, the backend is fine and the issue is in the frontend build.

---

## Why This Happened

Vite (the frontend build tool) embeds environment variables at **build time**:
- `import.meta.env.VITE_API_URL` is replaced with the actual value during build
- If the `.env` file wasn't present or correct during the Docker build, it defaults to undefined
- The container image needs to be rebuilt with the correct environment variables

---

## Expected Behavior After Fix

1. ✅ Chat interface loads
2. ✅ You can type a message
3. ✅ Message sends successfully
4. ✅ AI agent responds with streaming text
5. ✅ You can create tasks via chat (e.g., "Add a task to buy groceries")

---

## 🎯 Quick Commands

```bash
# Rebuild and restart (all in one)
cd /c/Users/user/hackathon-2/phase-4-local-kubernetees-deployment
eval $(minikube docker-env)
docker build -t todo-chatbot-frontend:1.0.0 frontend/
kubectl rollout restart deployment/todo-chatbot-frontend
kubectl get pods -w
```

Wait for the new pod to show `Running` and `1/1` ready, then refresh your browser!

---

**Try rebuilding the frontend container and the chat should work!** 🚀
