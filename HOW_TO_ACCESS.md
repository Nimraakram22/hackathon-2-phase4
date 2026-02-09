# How to Access Your Deployed Application

## Your Application is Running! ✅

**Pods Status**: Both frontend and backend are healthy
**Minikube IP**: 192.168.49.2
**Frontend NodePort**: 31346

---

## Method 1: Direct NodePort Access (Recommended)

**Frontend URL**: http://192.168.49.2:31346

Simply open this URL in your browser. This works because:
- Frontend service is exposed as NodePort
- Minikube IP is 192.168.49.2
- NodePort is 31346

---

## Method 2: Localhost Port-Forward (Alternative)

If the NodePort doesn't work, use port-forwarding:

```bash
# Open a new terminal and run:
kubectl port-forward service/todo-chatbot-frontend 8080:80

# Then access: http://localhost:8080
```

**Note**: Keep this terminal open while using the app.

---

## Method 3: Minikube Service Tunnel (Alternative)

```bash
# Open a new terminal and run:
minikube service todo-chatbot-frontend --url

# This will output a URL like: http://127.0.0.1:XXXXX
# Open that URL in your browser
```

**Note**: Keep this terminal open while using the app.

---

## Access Backend API

To access the backend API documentation:

```bash
# Open a new terminal and run:
kubectl port-forward service/todo-chatbot-backend 8000:8000

# Then access: http://localhost:8000/docs
```

---

## Troubleshooting

### If NodePort doesn't work:
1. Check if Minikube is running: `minikube status`
2. Try Method 2 (port-forward) instead

### If nothing works:
```bash
# Check pod logs
kubectl logs -l app.kubernetes.io/component=frontend
kubectl logs -l app.kubernetes.io/component=backend

# Check pod status
kubectl get pods -l app.kubernetes.io/instance=todo-chatbot
```

---

## Quick Test

Try this command to test frontend health:
```bash
curl http://192.168.49.2:31346/health.html
```

Expected output: `healthy`
