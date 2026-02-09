# Quickstart: Local Kubernetes Deployment

**Feature**: 004-local-k8s-deployment
**Date**: 2026-02-01
**Purpose**: Step-by-step guide for deploying Todo Chatbot to local Kubernetes cluster

## Overview

This guide walks through deploying the Todo Chatbot application (frontend and backend) to a local Kubernetes cluster using Docker, Minikube, and Helm.

**Estimated Time**: 30-45 minutes (first time), 10-15 minutes (subsequent deployments)

---

## Prerequisites

### Required Tools

1. **Docker Desktop 4.53+**
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version`
   - Enable Kubernetes in Docker Desktop settings (optional, we'll use Minikube)

2. **Minikube**
   - Install: `brew install minikube` (macOS) or see https://minikube.sigs.k8s.io/docs/start/
   - Verify: `minikube version`

3. **kubectl**
   - Install: `brew install kubectl` (macOS) or see https://kubernetes.io/docs/tasks/tools/
   - Verify: `kubectl version --client`

4. **Helm 3.x**
   - Install: `brew install helm` (macOS) or see https://helm.sh/docs/intro/install/
   - Verify: `helm version`

5. **hadolint** (optional, for Dockerfile linting)
   - Install: `brew install hadolint` (macOS)
   - Verify: `hadolint --version`

### System Requirements

- **RAM**: 8GB minimum (4GB for Minikube, 4GB for host)
- **CPU**: 4 cores minimum (2 for Minikube, 2 for host)
- **Disk**: 20GB free space
- **OS**: Linux, macOS, or Windows with WSL2

---

## Step 1: Start Minikube Cluster

### 1.1 Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=2 --memory=4096 --driver=docker

# Verify cluster is running
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

### 1.2 Enable Minikube Addons (Optional)

```bash
# Enable metrics server for resource monitoring
minikube addons enable metrics-server

# Enable dashboard for web UI
minikube addons enable dashboard

# View dashboard (opens in browser)
minikube dashboard
```

### 1.3 Configure Docker to Use Minikube Registry

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify Docker is using Minikube
docker ps | grep kube

# To revert to local Docker daemon later:
# eval $(minikube docker-env -u)
```

**Why**: Building images directly in Minikube's Docker daemon avoids pushing to external registry.

---

## Step 2: Build Container Images

### 2.1 Build Frontend Image

```bash
# Navigate to frontend directory
cd frontend

# Lint Dockerfile (optional)
hadolint Dockerfile

# Build multi-stage image
docker build -t todo-chatbot-frontend:1.0.0 .

# Verify image
docker images | grep todo-chatbot-frontend

# Expected output:
# todo-chatbot-frontend   1.0.0   <image-id>   <time>   <size>
```

**Expected Build Time**: 3-5 minutes (first build), 30-60 seconds (incremental)

**Expected Image Size**: <100MB

### 2.2 Build Backend Image

```bash
# Navigate to backend directory
cd ../backend

# Lint Dockerfile (optional)
hadolint Dockerfile

# Build multi-stage image
docker build -t todo-chatbot-backend:1.0.0 .

# Verify image
docker images | grep todo-chatbot-backend

# Expected output:
# todo-chatbot-backend   1.0.0   <image-id>   <time>   <size>
```

**Expected Build Time**: 2-4 minutes (first build), 30-60 seconds (incremental)

**Expected Image Size**: <200MB

### 2.3 Verify Images

```bash
# List all todo-chatbot images
docker images | grep todo-chatbot

# Check image details
docker inspect todo-chatbot-frontend:1.0.0 | grep -A 5 "Config"
docker inspect todo-chatbot-backend:1.0.0 | grep -A 5 "Config"

# Verify non-root user
docker inspect todo-chatbot-frontend:1.0.0 | grep User
docker inspect todo-chatbot-backend:1.0.0 | grep User
```

---

## Step 3: Create Kubernetes Secrets

### 3.1 Create .env File

```bash
# Navigate to project root
cd ..

# Create .env file with actual credentials
cat > .env <<EOF
DATABASE_URL=postgresql://user:password@neon-host:5432/database
OPENAI_API_KEY=sk-your-actual-key
NEON_API_KEY=your-neon-key
EOF

# Secure the file
chmod 600 .env
```

**⚠️ IMPORTANT**: Never commit .env to version control. Add to .gitignore.

### 3.2 Create Kubernetes Secret

```bash
# Create secret from .env file
kubectl create secret generic todo-chatbot-secret --from-env-file=.env

# Verify secret created
kubectl get secrets

# View secret (base64 encoded)
kubectl describe secret todo-chatbot-secret
```

---

## Step 4: Deploy with Helm

### 4.1 Install Helm Chart

```bash
# Navigate to helm chart directory
cd helm/todo-chatbot

# Lint chart
helm lint .

# Expected output:
# ==> Linting .
# [INFO] Chart.yaml: icon is recommended
# 1 chart(s) linted, 0 chart(s) failed

# Dry-run to validate templates
helm install todo-chatbot . --dry-run --debug

# Install chart
helm install todo-chatbot .

# Expected output:
# NAME: todo-chatbot
# LAST DEPLOYED: <timestamp>
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
```

### 4.2 Verify Deployment

```bash
# Watch pods starting
kubectl get pods -w

# Expected output (after 1-2 minutes):
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-<hash>              1/1     Running   0          1m
# frontend-<hash>             1/1     Running   0          1m

# Check deployment status
kubectl get deployments

# Check services
kubectl get services

# Check all resources
kubectl get all
```

---

## Step 5: Access Application

### 5.1 Get Frontend URL

```bash
# For LoadBalancer service (Minikube)
minikube service frontend --url

# Expected output:
# http://192.168.49.2:30080

# Open in browser
open $(minikube service frontend --url)
```

### 5.2 Test Backend API

```bash
# Get backend service URL (internal)
kubectl get service backend

# Port-forward to access backend locally
kubectl port-forward service/backend 8000:8000

# In another terminal, test health endpoint
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","database":"connected"}
```

### 5.3 Test Application Functionality

1. Open frontend URL in browser
2. Create a new todo item
3. Verify item appears in list
4. Mark item as complete
5. Delete item
6. Verify all operations work correctly

---

## Step 6: Verify Deployment Health

### 6.1 Check Pod Health

```bash
# Check pod status
kubectl get pods

# Check pod logs
kubectl logs -l app=todo-chatbot,component=frontend
kubectl logs -l app=todo-chatbot,component=backend

# Check pod events
kubectl describe pod -l app=todo-chatbot
```

### 6.2 Check Resource Usage

```bash
# View resource usage (requires metrics-server)
kubectl top pods

# Expected output:
# NAME                        CPU(cores)   MEMORY(bytes)
# backend-<hash>              50m          200Mi
# frontend-<hash>             10m          50Mi
```

### 6.3 Test Health Probes

```bash
# Check liveness probe
kubectl exec -it <frontend-pod> -- wget -O- http://localhost:8080/health

# Check readiness probe
kubectl exec -it <backend-pod> -- wget -O- http://localhost:8000/health
```

---

## Step 7: Update Deployment

### 7.1 Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap todo-chatbot-config

# Update values (e.g., LOG_LEVEL: "debug")
# Save and exit

# Restart pods to pick up changes
kubectl rollout restart deployment/frontend
kubectl rollout restart deployment/backend

# Watch rolling update
kubectl rollout status deployment/frontend
kubectl rollout status deployment/backend
```

### 7.2 Update Application Version

```bash
# Build new image version
cd frontend
docker build -t todo-chatbot-frontend:1.1.0 .

# Update Helm values
cd ../../helm/todo-chatbot
helm upgrade todo-chatbot . --set frontendTag=1.1.0

# Watch rolling update
kubectl rollout status deployment/frontend
```

---

## Step 8: Troubleshooting

### 8.1 Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Check pod events
kubectl describe pod <pod-name>

# Common issues:
# - ImagePullBackOff: Image not found in Minikube registry
#   Solution: Rebuild image with eval $(minikube docker-env)
# - CrashLoopBackOff: Container crashing on startup
#   Solution: Check logs with kubectl logs <pod-name>
# - Pending: Insufficient resources
#   Solution: Increase Minikube resources or reduce pod requests
```

### 8.2 Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints

# Check if pods are ready
kubectl get pods

# Check service selector matches pod labels
kubectl describe service frontend
kubectl describe pod <frontend-pod>

# Test service from within cluster
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
# Inside pod: wget -O- http://backend:8000/health
```

### 8.3 Database Connection Issues

```bash
# Check secret exists
kubectl get secret todo-chatbot-secret

# Check secret is mounted in pod
kubectl describe pod <backend-pod> | grep -A 5 "Environment"

# Check database URL is correct
kubectl exec -it <backend-pod> -- env | grep DATABASE_URL

# Test database connection from pod
kubectl exec -it <backend-pod> -- python -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); print('Connected')"
```

### 8.4 View Logs

```bash
# View recent logs
kubectl logs <pod-name>

# Follow logs in real-time
kubectl logs -f <pod-name>

# View logs from previous container (if crashed)
kubectl logs <pod-name> --previous

# View logs from all pods with label
kubectl logs -l app=todo-chatbot --all-containers=true
```

---

## Step 9: Cleanup

### 9.1 Uninstall Helm Release

```bash
# Uninstall chart
helm uninstall todo-chatbot

# Verify resources deleted
kubectl get all
```

### 9.2 Delete Secrets and ConfigMaps

```bash
# Delete secret
kubectl delete secret todo-chatbot-secret

# Delete ConfigMap (if not managed by Helm)
kubectl delete configmap todo-chatbot-config
```

### 9.3 Stop Minikube

```bash
# Stop Minikube cluster
minikube stop

# Delete Minikube cluster (optional, removes all data)
minikube delete
```

---

## Optional: AI-Assisted DevOps Tools

### Gordon (Docker AI)

```bash
# Enable Gordon in Docker Desktop
# Settings > Beta features > Enable Docker AI

# Use Gordon for Docker operations
docker ai "build an optimized image for my React app"
docker ai "why is my container failing to start?"
docker ai "show me the best practices for Python Dockerfiles"
```

### kubectl-ai

```bash
# Install kubectl-ai
# See: https://github.com/sozercan/kubectl-ai

# Use kubectl-ai for Kubernetes operations
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "scale the backend to handle more load"
kubectl-ai "check why the pods are failing"
```

### kagent

```bash
# Install kagent
# See: https://github.com/kubeshop/botkube

# Use kagent for cluster analysis
kagent "analyze the cluster health"
kagent "optimize resource allocation"
kagent "suggest improvements for my deployment"
```

---

## Next Steps

After successful deployment:

1. **Monitor Application**: Set up monitoring with Prometheus and Grafana
2. **Add Ingress**: Configure Ingress controller for external access
3. **Enable TLS**: Add TLS certificates for HTTPS
4. **Set Up CI/CD**: Automate builds and deployments
5. **Cloud Deployment**: Deploy to production Kubernetes cluster (EKS, GKE, AKS)

---

## Reference Commands

```bash
# Minikube
minikube start --cpus=2 --memory=4096
minikube status
minikube stop
minikube delete
minikube service <service-name> --url
eval $(minikube docker-env)

# Docker
docker build -t <image>:<tag> .
docker images
docker ps
docker logs <container-id>

# kubectl
kubectl get pods
kubectl get services
kubectl get deployments
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl exec -it <pod-name> -- sh
kubectl port-forward service/<service-name> <local-port>:<service-port>
kubectl rollout status deployment/<deployment-name>
kubectl rollout restart deployment/<deployment-name>

# Helm
helm lint .
helm install <release-name> .
helm upgrade <release-name> .
helm uninstall <release-name>
helm list
helm status <release-name>
```

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review logs: `kubectl logs <pod-name>`
- Check events: `kubectl describe pod <pod-name>`
- Consult documentation: [Kubernetes Docs](https://kubernetes.io/docs/), [Helm Docs](https://helm.sh/docs/)
