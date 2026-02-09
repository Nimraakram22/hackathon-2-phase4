# ✅ Solution: Fix "Failed to Fetch" Error

## Problem
Your frontend at `http://localhost:8080` cannot connect to the backend API at `http://localhost:8000`.

## Root Cause
The backend port-forward needs to be running for the frontend to communicate with the backend API.

---

## ✅ Solution: Start Backend Port-Forward

### Step 1: Open a NEW Terminal/Command Prompt

**Important**: You need to keep this terminal open while using the application.

### Step 2: Run This Command

```bash
kubectl port-forward service/todo-chatbot-backend 8000:8000
```

**Expected Output**:
```
Forwarding from 127.0.0.1:8000 -> 8000
Forwarding from [::1]:8000 -> 8000
```

### Step 3: Keep This Terminal Open

**Do NOT close this terminal** - it needs to stay running for the frontend to work.

### Step 4: Test Your Application

1. Go back to your browser at `http://localhost:8080`
2. Try to signup again
3. It should work now!

---

## ✅ Verification

Test if the backend is accessible:

```bash
# In another terminal, run:
curl http://localhost:8000/health
```

**Expected output**:
```json
{"status":"healthy","timestamp":"...","version":"2.1"}
```

---

## 📋 Summary: What You Need Running

For the application to work, you need **TWO port-forwards** running:

### Terminal 1: Frontend Port-Forward
```bash
kubectl port-forward service/todo-chatbot-frontend 8080:80
```
**Access**: http://localhost:8080

### Terminal 2: Backend Port-Forward
```bash
kubectl port-forward service/todo-chatbot-backend 8000:8000
```
**Access**: http://localhost:8000 (used by frontend)

---

## 🎯 Quick Start Script

To make this easier, you can run both port-forwards in the background:

**Windows PowerShell**:
```powershell
# Start frontend port-forward
Start-Process powershell -ArgumentList "kubectl port-forward service/todo-chatbot-frontend 8080:80"

# Start backend port-forward
Start-Process powershell -ArgumentList "kubectl port-forward service/todo-chatbot-backend 8000:8000"
```

**Git Bash / Linux / Mac**:
```bash
# Start both in background
kubectl port-forward service/todo-chatbot-frontend 8080:80 &
kubectl port-forward service/todo-chatbot-backend 8000:8000 &
```

---

## 🔧 Troubleshooting

### If signup still fails:

1. **Check both port-forwards are running**:
   ```bash
   netstat -an | findstr "8080 8000"
   ```
   You should see both ports LISTENING.

2. **Check backend logs**:
   ```bash
   kubectl logs -l app.kubernetes.io/component=backend --tail=20
   ```

3. **Test backend directly**:
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test123!","username":"testuser"}'
   ```

4. **Check browser console** (F12):
   - Look for error messages
   - Check if requests are being made to `http://localhost:8000`

---

## 🎉 Once Fixed

After starting the backend port-forward:

1. ✅ Frontend accessible at: http://localhost:8080
2. ✅ Backend accessible at: http://localhost:8000
3. ✅ Signup should work
4. ✅ Login should work
5. ✅ Todo creation should work
6. ✅ Chat should work

---

## 💡 Alternative: Use NodePort (No Port-Forward Needed)

If you don't want to keep terminals open, you can expose the backend as NodePort:

```bash
# Change backend service to NodePort
kubectl patch service todo-chatbot-backend -p '{"spec":{"type":"NodePort"}}'

# Get the NodePort
kubectl get svc todo-chatbot-backend

# Update frontend to use the NodePort
# Then rebuild the frontend image
```

**Note**: This requires rebuilding the frontend with the new backend URL.

---

## 📞 Need Help?

If the issue persists:
1. Check both port-forwards are running
2. Check browser console for errors (F12)
3. Check backend logs: `kubectl logs -l app.kubernetes.io/component=backend`
4. Verify pods are healthy: `kubectl get pods`

---

**Start the backend port-forward now and try signup again!** 🚀
