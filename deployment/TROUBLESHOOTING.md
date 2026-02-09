# Troubleshooting Guide: Local Kubernetes Deployment

This guide covers common issues encountered during local Kubernetes deployment and their solutions.

## Table of Contents

1. [Minikube Issues](#minikube-issues)
2. [Container Image Issues](#container-image-issues)
3. [Pod Issues](#pod-issues)
4. [Service Issues](#service-issues)
5. [Storage Issues](#storage-issues)
6. [Network Issues](#network-issues)
7. [Secret Issues](#secret-issues)
8. [Performance Issues](#performance-issues)

---

## Minikube Issues

### Issue: Minikube fails to start

**Symptoms**:
```
❌ Exiting due to PROVIDER_DOCKER_NOT_RUNNING: "docker version --format -" exit status 1
```

**Solutions**:
1. Verify Docker Desktop is running:
   ```bash
   docker ps
   ```

2. Restart Docker Desktop

3. Try different driver:
   ```bash
   minikube start --driver=virtualbox
   # or
   minikube start --driver=hyperkit  # macOS only
   ```

### Issue: Insufficient resources

**Symptoms**:
```
❌ Exiting due to RSRC_INSUFFICIENT_CORES: Requested cpu count 2 is greater than available cpus: 1
```

**Solutions**:
1. Reduce resource allocation:
   ```bash
   minikube start --cpus=1 --memory=2048
   ```

2. Close other applications to free resources

3. Increase Docker Desktop resource limits:
   - Docker Desktop → Settings → Resources
   - Increase CPUs and Memory

### Issue: Minikube cluster not responding

**Symptoms**:
```bash
kubectl get nodes
# Error: connection refused
```

**Solutions**:
1. Check Minikube status:
   ```bash
   minikube status
   ```

2. Restart Minikube:
   ```bash
   minikube stop
   minikube start
   ```

3. Delete and recreate cluster:
   ```bash
   minikube delete
   ./deployment/minikube-setup.sh
   ```

---

## Container Image Issues

### Issue: ImagePullBackOff

**Symptoms**:
```bash
kubectl get pods
# NAME                        READY   STATUS             RESTARTS   AGE
# backend-xxxxx               0/1     ImagePullBackOff   0          2m
```

**Root Cause**: Image not found in Minikube's Docker registry

**Solutions**:
1. Verify Docker is configured for Minikube:
   ```bash
   docker info | grep -i minikube
   ```

2. Configure Docker for Minikube:
   ```bash
   eval $(minikube docker-env)
   ```

3. Rebuild images in Minikube context:
   ```bash
   ./deployment/build-images.sh
   ```

4. Verify images exist:
   ```bash
   docker images | grep todo-chatbot
   ```

### Issue: Image build fails

**Symptoms**:
```
ERROR: failed to solve: process "/bin/sh -c npm run build" did not complete successfully
```

**Solutions**:
1. Check Dockerfile syntax:
   ```bash
   docker build --no-cache -t test-image .
   ```

2. Verify all files exist:
   ```bash
   ls -la frontend/  # Check package.json, src/, etc.
   ```

3. Check .dockerignore isn't excluding required files

4. Build with verbose output:
   ```bash
   docker build --progress=plain -t test-image .
   ```

### Issue: Container crashes on startup

**Symptoms**:
```bash
kubectl get pods
# NAME                        READY   STATUS             RESTARTS   AGE
# backend-xxxxx               0/1     CrashLoopBackOff   5          5m
```

**Solutions**:
1. Check container logs:
   ```bash
   kubectl logs <pod-name>
   kubectl logs <pod-name> --previous  # Previous container
   ```

2. Check for missing environment variables:
   ```bash
   kubectl describe pod <pod-name> | grep -A 10 "Environment"
   ```

3. Test container locally:
   ```bash
   docker run -it todo-chatbot-backend:1.0.0 sh
   # Inside container: check if app starts
   ```

---

## Pod Issues

### Issue: Pods stuck in Pending

**Symptoms**:
```bash
kubectl get pods
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxxxx               0/1     Pending   0          5m
```

**Solutions**:
1. Check pod events:
   ```bash
   kubectl describe pod <pod-name>
   # Look for: "FailedScheduling" or "Insufficient cpu/memory"
   ```

2. Check node resources:
   ```bash
   kubectl top nodes
   kubectl describe nodes
   ```

3. Reduce resource requests in values.yaml:
   ```yaml
   backend:
     resources:
       requests:
         memory: "128Mi"  # Reduced from 256Mi
         cpu: "100m"      # Reduced from 250m
   ```

4. Restart Minikube with more resources:
   ```bash
   minikube delete
   minikube start --cpus=4 --memory=8192
   ```

### Issue: Pods not ready

**Symptoms**:
```bash
kubectl get pods
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxxxx               0/1     Running   0          5m
```

**Solutions**:
1. Check readiness probe:
   ```bash
   kubectl describe pod <pod-name> | grep -A 5 "Readiness"
   ```

2. Test health endpoint manually:
   ```bash
   kubectl port-forward <pod-name> 8000:8000
   curl http://localhost:8000/health
   ```

3. Check application logs:
   ```bash
   kubectl logs <pod-name>
   ```

4. Increase initialDelaySeconds in values.yaml:
   ```yaml
   backend:
     readinessProbe:
       initialDelaySeconds: 30  # Increased from 10
   ```

### Issue: High restart count

**Symptoms**:
```bash
kubectl get pods
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxxxx               1/1     Running   15         10m
```

**Solutions**:
1. Check liveness probe configuration:
   ```bash
   kubectl describe pod <pod-name> | grep -A 5 "Liveness"
   ```

2. Increase failure threshold:
   ```yaml
   backend:
     livenessProbe:
       failureThreshold: 5  # Increased from 3
       periodSeconds: 20    # Increased from 10
   ```

3. Check for memory leaks:
   ```bash
   kubectl top pod <pod-name>
   ```

---

## Service Issues

### Issue: Service not accessible

**Symptoms**:
```bash
minikube service todo-chatbot-frontend --url
# Waiting for service to be available...
```

**Solutions**:
1. Check service exists:
   ```bash
   kubectl get services
   ```

2. Check service endpoints:
   ```bash
   kubectl get endpoints
   # Should show pod IPs
   ```

3. Verify pod labels match service selector:
   ```bash
   kubectl get pods --show-labels
   kubectl describe service todo-chatbot-frontend | grep Selector
   ```

4. Use port-forward as alternative:
   ```bash
   kubectl port-forward service/todo-chatbot-frontend 8080:80
   ```

### Issue: LoadBalancer stuck in Pending

**Symptoms**:
```bash
kubectl get services
# NAME                       TYPE           EXTERNAL-IP   PORT(S)
# todo-chatbot-frontend      LoadBalancer   <pending>     80:30080/TCP
```

**Root Cause**: Minikube doesn't support LoadBalancer by default

**Solutions**:
1. Use minikube tunnel (requires sudo):
   ```bash
   minikube tunnel
   # In another terminal: kubectl get services
   ```

2. Use NodePort instead:
   ```yaml
   frontend:
     service:
       type: NodePort
   ```

3. Use minikube service command:
   ```bash
   minikube service todo-chatbot-frontend --url
   ```

---

## Storage Issues

### Issue: PVC stuck in Pending

**Symptoms**:
```bash
kubectl get pvc
# NAME                           STATUS    VOLUME   CAPACITY   ACCESS MODES
# todo-chatbot-backend-data      Pending
```

**Solutions**:
1. Check PVC events:
   ```bash
   kubectl describe pvc todo-chatbot-backend-data
   ```

2. Verify storage class exists:
   ```bash
   kubectl get storageclass
   ```

3. Enable storage provisioner:
   ```bash
   minikube addons enable storage-provisioner
   ```

4. Create PersistentVolume manually (if needed):
   ```yaml
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: backend-pv
   spec:
     capacity:
       storage: 5Gi
     accessModes:
       - ReadWriteOnce
     hostPath:
       path: /data/backend
   ```

### Issue: SQLite database not persisting

**Symptoms**: Data lost after pod restart

**Solutions**:
1. Verify PVC is bound:
   ```bash
   kubectl get pvc
   # STATUS should be "Bound"
   ```

2. Check volume mount in pod:
   ```bash
   kubectl describe pod <backend-pod> | grep -A 5 "Mounts"
   ```

3. Verify SQLite file location:
   ```bash
   kubectl exec -it <backend-pod> -- ls -la /app/data
   ```

4. Check SQLITE_DB_PATH environment variable:
   ```bash
   kubectl exec -it <backend-pod> -- env | grep SQLITE
   ```

---

## Network Issues

### Issue: Frontend cannot reach backend

**Symptoms**: Frontend shows connection errors

**Solutions**:
1. Verify backend service exists:
   ```bash
   kubectl get service todo-chatbot-backend
   ```

2. Test backend from frontend pod:
   ```bash
   kubectl exec -it <frontend-pod> -- wget -O- http://todo-chatbot-backend:8000/health
   ```

3. Check BACKEND_API_URL in ConfigMap:
   ```bash
   kubectl get configmap todo-chatbot-config -o yaml
   ```

4. Verify DNS resolution:
   ```bash
   kubectl exec -it <frontend-pod> -- nslookup todo-chatbot-backend
   ```

### Issue: Cannot access application from host

**Symptoms**: Browser shows "connection refused"

**Solutions**:
1. Use minikube service:
   ```bash
   minikube service todo-chatbot-frontend --url
   ```

2. Use port-forward:
   ```bash
   kubectl port-forward service/todo-chatbot-frontend 8080:80
   # Access: http://localhost:8080
   ```

3. Check firewall settings

4. Verify Minikube IP:
   ```bash
   minikube ip
   # Access: http://<minikube-ip>:<nodeport>
   ```

---

## Secret Issues

### Issue: Secret not found

**Symptoms**:
```
Error: secret "todo-chatbot-secret" not found
```

**Solutions**:
1. Create secret from .env file:
   ```bash
   kubectl create secret generic todo-chatbot-secret --from-env-file=.env
   ```

2. Verify secret exists:
   ```bash
   kubectl get secrets
   ```

3. Check secret data:
   ```bash
   kubectl get secret todo-chatbot-secret -o yaml
   ```

### Issue: Invalid credentials

**Symptoms**: Backend logs show authentication errors

**Solutions**:
1. Verify .env file format:
   ```bash
   cat .env
   # Should be: KEY=value (no spaces around =)
   ```

2. Check secret values are base64 encoded:
   ```bash
   kubectl get secret todo-chatbot-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d
   ```

3. Update secret:
   ```bash
   kubectl delete secret todo-chatbot-secret
   kubectl create secret generic todo-chatbot-secret --from-env-file=.env
   kubectl rollout restart deployment/todo-chatbot-backend
   ```

---

## Performance Issues

### Issue: Slow application response

**Symptoms**: Application takes >5 seconds to respond

**Solutions**:
1. Check resource usage:
   ```bash
   kubectl top pods
   ```

2. Increase resource limits:
   ```yaml
   backend:
     resources:
       limits:
         memory: "1Gi"    # Increased from 512Mi
         cpu: "1000m"     # Increased from 500m
   ```

3. Check for CPU throttling:
   ```bash
   kubectl describe pod <pod-name> | grep -i throttl
   ```

4. Scale replicas:
   ```bash
   kubectl scale deployment/todo-chatbot-backend --replicas=2
   ```

### Issue: Out of memory errors

**Symptoms**:
```
OOMKilled
```

**Solutions**:
1. Increase memory limits:
   ```yaml
   backend:
     resources:
       limits:
         memory: "1Gi"  # Increased from 512Mi
   ```

2. Check for memory leaks in application logs

3. Restart pod:
   ```bash
   kubectl delete pod <pod-name>
   ```

---

## Diagnostic Commands

### Quick Health Check
```bash
# Check all resources
kubectl get all -l app.kubernetes.io/instance=todo-chatbot

# Check pod status
kubectl get pods -o wide

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check logs
kubectl logs -l app.kubernetes.io/component=backend --tail=50
```

### Deep Dive
```bash
# Describe pod
kubectl describe pod <pod-name>

# Get pod YAML
kubectl get pod <pod-name> -o yaml

# Check resource usage
kubectl top pods
kubectl top nodes

# Check storage
kubectl get pv,pvc

# Check network
kubectl get services,endpoints
```

### Debug Container
```bash
# Run debug container
kubectl run -it --rm debug --image=alpine --restart=Never -- sh

# Inside debug container:
apk add curl
curl http://todo-chatbot-backend:8000/health
```

---

## Getting Help

If issues persist:

1. **Check logs**: `kubectl logs <pod-name>`
2. **Check events**: `kubectl describe pod <pod-name>`
3. **Review documentation**: [Kubernetes Docs](https://kubernetes.io/docs/)
4. **Check GitHub issues**: Search for similar problems
5. **Ask for help**: Provide logs and describe steps taken

## Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| ImagePullBackOff | Image not found | Rebuild in Minikube context |
| CrashLoopBackOff | Container keeps crashing | Check logs for errors |
| Pending | Cannot schedule pod | Check resources |
| ErrImagePull | Cannot pull image | Check image name/tag |
| OOMKilled | Out of memory | Increase memory limits |
| Error: connection refused | Service not accessible | Check service/endpoints |
| FailedScheduling | No nodes available | Check node resources |
