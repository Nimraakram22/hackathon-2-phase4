# Research: Local Kubernetes Deployment

**Feature**: 004-local-k8s-deployment
**Date**: 2026-02-08 (updated from 2026-02-01 research)
**Research Method**: Context7 MCP Server queries to official documentation + specification clarifications

## Overview

This document captures technical research findings for containerizing and deploying the Todo Chatbot application to a local Kubernetes cluster. All decisions are based on official documentation from Docker, Kubernetes, and Helm projects via Context7 MCP server.

## Research Questions

1. How to containerize React frontend with optimal production configuration?
2. How to containerize Python FastAPI backend with security best practices?
3. How to structure Helm charts for multi-service web applications?
4. How to configure Kubernetes deployments with health probes and resource limits?
5. How to manage configuration and secrets in Kubernetes?

---

## Decision 1: Frontend Containerization Strategy

**Question**: How to containerize React frontend for production deployment?

**Research Source**: Context7 MCP Server - /docker/docs
- https://github.com/docker/docs/blob/main/content/guides/reactjs/containerize.md
- https://github.com/docker/docs/blob/main/content/get-started/workshop/09_image_best.md

**Options Considered**:

1. **Single-stage build with Node.js runtime** (rejected)
   - Pros: Simple Dockerfile
   - Cons: Large image size (>1GB), includes unnecessary build tools in production, security risk

2. **Multi-stage build with nginx runtime** (selected)
   - Pros: Minimal production image (<100MB), nginx optimized for static files, no Node.js in production
   - Cons: Requires nginx configuration for SPA routing

**Decision**: Multi-stage Dockerfile with Node.js 24.11.1-alpine (builder) + nginx-unprivileged:alpine3.22 (runtime)

**Rationale**:
- **Size optimization**: Multi-stage build eliminates build dependencies from final image (Node.js, npm, build tools)
- **Security**: nginx-unprivileged runs as non-root user (nginx:nginx), meeting constitution requirement
- **Performance**: nginx is production-grade web server optimized for serving static files
- **Caching**: Layer ordering (dependencies before source) maximizes Docker cache hits

**Implementation Pattern** (from Context7 research):

```dockerfile
ARG NODE_VERSION=24.11.1-alpine
ARG NGINX_VERSION=alpine3.22

# Build stage
FROM node:${NODE_VERSION} AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

# Runtime stage
FROM nginxinc/nginx-unprivileged:${NGINX_VERSION} AS runner
USER nginx
COPY nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx --from=builder /app/dist /usr/share/nginx/html
EXPOSE 8080
ENTRYPOINT ["nginx", "-c", "/etc/nginx/nginx.conf"]
CMD ["-g", "daemon off;"]
```

**Key Features**:
- Pinned versions for reproducibility
- Build cache mount for faster rebuilds
- Non-root user (nginx)
- Proper file ownership (--chown)
- Port 8080 (unprivileged port)

---

## Decision 2: Backend Containerization Strategy

**Question**: How to containerize Python FastAPI backend with security best practices?

**Research Source**: Context7 MCP Server - /docker/docs
- https://github.com/docker/docs/blob/main/content/manuals/dhi/how-to/use.md
- https://github.com/docker/docs/blob/main/content/guides/nodejs/containerize.md (pattern reference)

**Options Considered**:

1. **Single-stage with full Python image** (rejected)
   - Pros: Simple, includes all build tools
   - Cons: Large image (>500MB), includes unnecessary packages

2. **Multi-stage with Alpine base** (selected)
   - Pros: Minimal size (<200MB), security hardened, fast builds
   - Cons: Requires careful dependency management

3. **Distroless base image** (considered for future)
   - Pros: Absolute minimal attack surface
   - Cons: More complex debugging, no shell access

**Decision**: Multi-stage Dockerfile with Python 3.11-alpine (builder + runtime) using virtual environment

**Rationale**:
- **Size optimization**: Alpine base is minimal (~50MB vs ~900MB for full Python)
- **Security**: Alpine has smaller attack surface, fewer packages
- **Virtual environment**: Isolates dependencies, enables clean multi-stage copy
- **Non-root user**: Runs as app user (UID 1001), meeting constitution requirement

**Implementation Pattern** (from Context7 research):

```dockerfile
# Build stage
FROM python:3.11-alpine AS builder
ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app
RUN python -m venv /app/venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-alpine
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

# Create non-root user
RUN addgroup -g 1001 -S app && \
    adduser -S app -u 1001 -G app && \
    chown -R app:app /app

COPY --from=builder --chown=app:app /app/venv /app/venv
COPY --chown=app:app src ./src

USER app
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Features**:
- Virtual environment for clean dependency isolation
- No pip cache in final image (--no-cache-dir)
- Non-root user (app:app, UID 1001)
- Proper file ownership
- Environment variables for Python optimization

---

## Decision 3: Kubernetes Deployment Configuration

**Question**: How to configure Kubernetes deployments for web applications with health probes and resource limits?

**Research Source**: Context7 MCP Server - /websites/kubernetes_io
- https://kubernetes.io/docs/tasks/access-application-cluster/connecting-frontend-backend
- https://kubernetes.io/docs/tutorials/stateful-application/mysql-wordpress-persistent-volume

**Pattern**: Frontend and backend as separate Deployments with Services

**Frontend Deployment Configuration**:
- **Replicas**: 1 (local development), scalable to 3+ in production
- **Resource Requests**: 512Mi memory, 250m CPU
- **Resource Limits**: 1Gi memory, 500m CPU
- **Liveness Probe**: HTTP GET /health, initialDelaySeconds: 30, periodSeconds: 10, failureThreshold: 3
- **Readiness Probe**: HTTP GET /health, initialDelaySeconds: 30, periodSeconds: 10, failureThreshold: 3
- **Rolling Update**: maxSurge: 1, maxUnavailable: 1

**Backend Deployment Configuration**:
- **Replicas**: 1 (local development), scalable to 3+ in production
- **Resource Requests**: 1Gi memory, 500m CPU
- **Resource Limits**: 2Gi memory, 1000m CPU
- **Liveness Probe**: HTTP GET /health, initialDelaySeconds: 30, periodSeconds: 10, failureThreshold: 3
- **Readiness Probe**: HTTP GET /health, initialDelaySeconds: 30, periodSeconds: 10, failureThreshold: 3
- **Rolling Update**: maxSurge: 1, maxUnavailable: 1
- **Environment Variables**: From ConfigMap (API_URL) and Secret (DATABASE_URL)

**Service Configuration**:
- **Frontend Service**: Type NodePort, port 3000 → 3000, accessed via kubectl port-forward
- **Backend Service**: Type NodePort, port 8000 → 8000, accessed via kubectl port-forward

**Rationale**:
- **Resource limits**: Conservative allocation for local development (Frontend: 512Mi/1Gi RAM, 250m/500m CPU; Backend: 1Gi/2Gi RAM, 500m/1000m CPU) prevents resource exhaustion while fitting within 8GB RAM / 4 CPU minimum system requirements
- **Health probes**: 30s initial delay allows proper startup, 10s period balances responsiveness with overhead, 3 failures prevents flapping
- **Rolling updates**: Ensure availability during updates (maxSurge: 1 allows one extra pod, maxUnavailable: 1 ensures at least one pod always running)
- **Service types**: Both services use NodePort with kubectl port-forward for simple, reliable local access

---

## Decision 4: Configuration Management Strategy

**Question**: How to manage configuration and secrets in Kubernetes?

**Research Source**: Context7 MCP Server - /websites/kubernetes_io
- https://kubernetes.io/docs/tutorials/stateful-application/mysql-wordpress-persistent-volume

**Pattern**: ConfigMaps for non-sensitive data, Secrets for credentials

**ConfigMap Usage**:
- API URLs (BACKEND_API_URL, FRONTEND_URL)
- Feature flags (ENABLE_ANALYTICS, DEBUG_MODE)
- Non-sensitive application settings

**Secret Usage**:
- Database credentials (DATABASE_URL with username/password)
- API keys (OPENAI_API_KEY, NEON_API_KEY)
- Encryption keys

**Implementation**:
```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-chatbot-config
data:
  BACKEND_API_URL: "http://backend:8000"
  FRONTEND_URL: "http://localhost:8080"

# Secret (base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: todo-chatbot-secret
type: Opaque
data:
  DATABASE_URL: <base64-encoded-value>
```

**Rationale**:
- **Separation of concerns**: Configuration separate from code
- **Security**: Secrets encrypted at rest in etcd
- **Environment portability**: Same image, different config per environment
- **Version control**: ConfigMaps in git, Secrets managed separately

---

## Decision 5: Helm Chart Structure

**Question**: How to structure Helm charts for multi-service web applications?

**Research Source**: Context7 MCP Server - /websites/helm_sh
- https://helm.sh/docs/chart_template_guide/getting_started
- https://helm.sh/docs/topics/charts

**Pattern**: Single chart with multiple service templates

**Chart Structure**:
```
todo-chatbot/
├── Chart.yaml              # Metadata (name, version, appVersion)
├── values.yaml             # Default values (flat structure)
├── values.schema.json      # JSON Schema validation
└── templates/
    ├── _helpers.tpl        # Template helpers (labels, names)
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── NOTES.txt           # Post-install instructions
```

**values.yaml Structure** (flat, not nested):
```yaml
# Frontend configuration
frontendImage: todo-chatbot-frontend
frontendTag: 1.0.0
frontendReplicas: 1
frontendPort: 8080

# Backend configuration
backendImage: todo-chatbot-backend
backendTag: 1.0.0
backendReplicas: 1
backendPort: 8000

# Resource limits
frontendMemoryRequest: 512Mi
frontendMemoryLimit: 1Gi
frontendCpuRequest: 250m
frontendCpuLimit: 500m
backendMemoryRequest: 1Gi
backendMemoryLimit: 2Gi
backendCpuRequest: 500m
backendCpuLimit: 1000m
```

**values.schema.json** (type validation):
```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["frontendImage", "backendImage"],
  "properties": {
    "frontendImage": {"type": "string"},
    "frontendTag": {"type": "string"},
    "frontendReplicas": {"type": "integer", "minimum": 1},
    "backendImage": {"type": "string"},
    "backendTag": {"type": "string"},
    "backendReplicas": {"type": "integer", "minimum": 1}
  }
}
```

**Rationale**:
- **Single chart**: Simpler than separate charts, services deployed together
- **Flat values**: Easier to override with --set, less nesting complexity
- **Schema validation**: Catches configuration errors before deployment
- **Template helpers**: DRY principle for labels and names

---

## Decision 6: Health Check Endpoints

**Question**: What health check endpoints should services expose?

**Decision**: Both services expose `/health` endpoint

**Frontend Health Check**:
- **Endpoint**: GET /health
- **Response**: 200 OK with nginx status
- **Implementation**: nginx stub_status module or simple static file

**Backend Health Check**:
- **Endpoint**: GET /health
- **Response**: 200 OK with JSON {"status": "healthy", "database": "connected"}
- **Implementation**: FastAPI route that checks database connectivity

**Rationale**:
- **Liveness probe**: Detects if container is alive (restart if fails)
- **Readiness probe**: Detects if container is ready to serve traffic (remove from load balancer if fails)
- **Database check**: Backend readiness includes database connectivity check

---

## Summary of Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend base image | nginx-unprivileged:alpine3.22 | Minimal size, non-root, production-grade |
| Backend base image | python:3.11-alpine | Minimal size, security hardened |
| Build strategy | Multi-stage Dockerfiles | Separate build and runtime, smaller images |
| User | Non-root (UID 1001) | Security best practice, constitution requirement |
| Health probes | HTTP GET /health | Standard pattern, enables self-healing |
| Resource limits | Defined for all containers | Prevent resource exhaustion, enable scheduling |
| Configuration | ConfigMaps + Secrets | Separate config from code, security for credentials |
| Helm structure | Single chart, flat values | Simplicity, easier to manage |
| Deployment strategy | Rolling updates | Zero-downtime deployments |

---

## References

All research conducted via Context7 MCP Server on 2026-02-01:

**Docker Documentation**:
- Multi-stage builds: https://github.com/docker/docs/blob/main/content/guides/reactjs/containerize.md
- Python containerization: https://github.com/docker/docs/blob/main/content/manuals/dhi/how-to/use.md
- Security best practices: https://github.com/docker/docs/blob/main/content/guides/nodejs/containerize.md

**Kubernetes Documentation**:
- Frontend/backend pattern: https://kubernetes.io/docs/tasks/access-application-cluster/connecting-frontend-backend
- ConfigMaps and Secrets: https://kubernetes.io/docs/tutorials/stateful-application/mysql-wordpress-persistent-volume

**Helm Documentation**:
- Chart structure: https://helm.sh/docs/chart_template_guide/getting_started
- Values schema: https://helm.sh/docs/topics/charts
- Template best practices: https://helm.sh/docs/howto/charts_tips_and_tricks
