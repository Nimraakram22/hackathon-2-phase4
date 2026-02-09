# Data Model: Local Kubernetes Deployment

**Feature**: 004-local-k8s-deployment
**Date**: 2026-02-01
**Purpose**: Define deployment entities and their relationships

## Overview

This document defines the entities involved in containerizing and deploying the Todo Chatbot application to Kubernetes. These are infrastructure entities, not application data models.

---

## Entity 1: Container Image

**Description**: Immutable package containing application code, runtime, dependencies, and configuration needed to run a service.

**Attributes**:
- **name**: Image name (e.g., "todo-chatbot-frontend", "todo-chatbot-backend")
- **tag**: Version identifier (e.g., "1.0.0", "latest")
- **registry**: Container registry URL (e.g., "docker.io", "localhost:5000")
- **size**: Image size in MB (target: <500MB per image)
- **baseImage**: Parent image used (e.g., "nginx:alpine3.22", "python:3.11-alpine")
- **layers**: Number of filesystem layers
- **createdAt**: Build timestamp
- **digest**: SHA256 hash for content verification

**Relationships**:
- Built FROM base image (parent-child)
- Referenced BY Deployment (one-to-many)
- Stored IN registry (many-to-one)

**Lifecycle**:
1. Built from Dockerfile
2. Tagged with version
3. Pushed to registry (optional for local)
4. Pulled by Kubernetes nodes
5. Instantiated as containers in pods

**Validation Rules**:
- Tag MUST follow semver format (X.Y.Z)
- Size MUST be <500MB for production images
- MUST run as non-root user (UID 1001)
- MUST pass vulnerability scan (no critical CVEs)

---

## Entity 2: Deployment

**Description**: Kubernetes resource that manages a set of identical pods, ensuring desired state and handling updates.

**Attributes**:
- **name**: Deployment name (e.g., "frontend", "backend")
- **namespace**: Kubernetes namespace (e.g., "default", "todo-chatbot")
- **replicas**: Desired number of pod instances (1 for local, 3+ for production)
- **selector**: Label selector to identify managed pods
- **strategy**: Update strategy (RollingUpdate with maxSurge: 1, maxUnavailable: 1)
- **revisionHistoryLimit**: Number of old ReplicaSets to retain (default: 10)

**Pod Template Attributes**:
- **image**: Container image reference
- **ports**: Exposed ports (frontend: 8080, backend: 8000)
- **env**: Environment variables (from ConfigMap and Secret)
- **resources**: CPU and memory requests/limits
- **livenessProbe**: Health check to detect if container is alive
- **readinessProbe**: Health check to detect if container is ready
- **volumeMounts**: Mounted volumes (if needed)

**Relationships**:
- Manages Pods (one-to-many)
- References Container Image (many-to-one)
- References ConfigMap (many-to-one)
- References Secret (many-to-one)
- Exposed BY Service (one-to-one or one-to-many)

**Lifecycle**:
1. Created from YAML manifest or Helm template
2. ReplicaSet created to manage pods
3. Pods scheduled on nodes
4. Containers started in pods
5. Health probes monitor pod health
6. Updates trigger rolling update
7. Old pods terminated after new pods ready

**Validation Rules**:
- Replicas MUST be >= 1
- Resources.requests MUST be defined
- Resources.limits MUST be defined
- LivenessProbe MUST be defined
- ReadinessProbe MUST be defined
- Image MUST use specific tag (not "latest")

---

## Entity 3: Service

**Description**: Kubernetes resource that provides stable network endpoint for accessing pods, with load balancing.

**Attributes**:
- **name**: Service name (e.g., "frontend", "backend")
- **namespace**: Kubernetes namespace
- **type**: Service type (LoadBalancer, NodePort, ClusterIP)
- **selector**: Label selector to identify target pods
- **ports**: Port mappings (port, targetPort, protocol)
- **clusterIP**: Internal cluster IP (auto-assigned)
- **externalIP**: External IP (for LoadBalancer type)

**Service Types**:
- **LoadBalancer**: Frontend service, exposed externally (Minikube tunnel)
- **ClusterIP**: Backend service, internal only (not exposed outside cluster)

**Relationships**:
- Routes traffic TO Pods (many-to-many via selector)
- Belongs TO Deployment (one-to-one or many-to-one)
- Referenced BY Ingress (many-to-one, if used)

**Lifecycle**:
1. Created from YAML manifest or Helm template
2. Endpoints controller watches for matching pods
3. Endpoints updated as pods come/go
4. kube-proxy configures iptables rules
5. Traffic routed to healthy pods

**Validation Rules**:
- Selector MUST match Deployment pod labels
- Port MUST be valid (1-65535)
- Type MUST be appropriate (LoadBalancer for frontend, ClusterIP for backend)

---

## Entity 4: ConfigMap

**Description**: Kubernetes resource for storing non-sensitive configuration data as key-value pairs.

**Attributes**:
- **name**: ConfigMap name (e.g., "todo-chatbot-config")
- **namespace**: Kubernetes namespace
- **data**: Key-value pairs of configuration (string values)
- **immutable**: Whether ConfigMap can be modified (false for development)

**Configuration Data**:
- **BACKEND_API_URL**: Backend service URL (e.g., "http://backend:8000")
- **FRONTEND_URL**: Frontend URL (e.g., "http://localhost:8080")
- **LOG_LEVEL**: Logging level (e.g., "info", "debug")
- **ENABLE_ANALYTICS**: Feature flag (e.g., "true", "false")

**Relationships**:
- Referenced BY Deployment (many-to-many)
- Mounted AS environment variables or volume files

**Lifecycle**:
1. Created from YAML manifest or Helm template
2. Mounted into pods as env vars or files
3. Updated independently of pods
4. Pod restart required to pick up changes (unless using volume mount with subPath)

**Validation Rules**:
- Keys MUST be valid environment variable names
- Values MUST be strings
- MUST NOT contain sensitive data (use Secret instead)

---

## Entity 5: Secret

**Description**: Kubernetes resource for storing sensitive data (credentials, keys) with base64 encoding.

**Attributes**:
- **name**: Secret name (e.g., "todo-chatbot-secret")
- **namespace**: Kubernetes namespace
- **type**: Secret type (Opaque, kubernetes.io/tls, etc.)
- **data**: Key-value pairs of sensitive data (base64 encoded)
- **stringData**: Key-value pairs in plain text (auto-encoded)

**Secret Data**:
- **DATABASE_URL**: PostgreSQL connection string with credentials
- **OPENAI_API_KEY**: OpenAI API key for AI features
- **NEON_API_KEY**: Neon database API key

**Relationships**:
- Referenced BY Deployment (many-to-many)
- Mounted AS environment variables or volume files

**Lifecycle**:
1. Created from YAML manifest (template only, actual values from .env)
2. Stored encrypted at rest in etcd
3. Mounted into pods as env vars or files
4. Accessed by application at runtime

**Validation Rules**:
- MUST NOT be committed to version control (use template with placeholders)
- Values MUST be base64 encoded in data field
- MUST use type: Opaque for generic secrets
- Access MUST be restricted via RBAC (future enhancement)

---

## Entity 6: PersistentVolumeClaim (PVC)

**Description**: Kubernetes resource for requesting persistent storage that survives pod restarts.

**Attributes**:
- **name**: PVC name (e.g., "backend-data")
- **namespace**: Kubernetes namespace
- **accessModes**: Access mode (ReadWriteOnce, ReadWriteMany)
- **storageClassName**: Storage class (standard, fast, etc.)
- **resources.requests.storage**: Requested storage size (e.g., "10Gi")
- **volumeMode**: Filesystem or Block

**Use Cases**:
- Backend application data (if not using external database)
- Uploaded files
- Cache data

**Relationships**:
- Bound TO PersistentVolume (one-to-one)
- Mounted BY Pod (one-to-many)
- Referenced BY Deployment (many-to-one)

**Lifecycle**:
1. Created from YAML manifest or Helm template
2. Kubernetes finds matching PersistentVolume
3. PVC bound to PV
4. Volume mounted into pods
5. Data persists across pod restarts
6. Released when PVC deleted (retention policy applies)

**Validation Rules**:
- Storage size MUST be sufficient for application needs
- AccessMode MUST match application requirements
- StorageClassName MUST exist in cluster

---

## Entity 7: Helm Chart

**Description**: Package of Kubernetes resource templates with parameterized values for deployment.

**Attributes**:
- **name**: Chart name (e.g., "todo-chatbot")
- **version**: Chart version (semver, e.g., "1.0.0")
- **appVersion**: Application version (e.g., "1.0.0")
- **description**: Chart description
- **dependencies**: Dependent charts (if any)

**Components**:
- **Chart.yaml**: Chart metadata
- **values.yaml**: Default configuration values
- **values.schema.json**: JSON Schema for values validation
- **templates/**: Kubernetes resource templates
- **NOTES.txt**: Post-install instructions

**Relationships**:
- Contains Templates (one-to-many)
- Generates Kubernetes Resources (one-to-many)
- Depends ON other Charts (many-to-many, if dependencies exist)

**Lifecycle**:
1. Created from template structure
2. Templates filled with values
3. Validated with `helm lint`
4. Installed to cluster with `helm install`
5. Resources created in Kubernetes
6. Updated with `helm upgrade`
7. Rolled back with `helm rollback`
8. Uninstalled with `helm uninstall`

**Validation Rules**:
- Version MUST follow semver
- Chart.yaml MUST be valid YAML
- values.schema.json MUST validate values.yaml
- Templates MUST render valid Kubernetes YAML
- MUST pass `helm lint` with zero warnings

---

## Entity Relationships Diagram

```
┌─────────────────┐
│  Container      │
│  Image          │
└────────┬────────┘
         │ referenced by
         ▼
┌─────────────────┐      manages      ┌─────────────────┐
│  Deployment     │─────────────────▶│  Pod            │
└────────┬────────┘                   └────────┬────────┘
         │                                     │
         │ references                          │ runs
         ▼                                     ▼
┌─────────────────┐                   ┌─────────────────┐
│  ConfigMap      │                   │  Container      │
└─────────────────┘                   └─────────────────┘
         ▲
         │ references
┌────────┴────────┐
│  Deployment     │
└────────┬────────┘
         │ references
         ▼
┌─────────────────┐
│  Secret         │
└─────────────────┘

┌─────────────────┐      exposes      ┌─────────────────┐
│  Service        │─────────────────▶│  Pod            │
└─────────────────┘                   └─────────────────┘

┌─────────────────┐      mounts       ┌─────────────────┐
│  PVC            │─────────────────▶│  Pod            │
└─────────────────┘                   └─────────────────┘

┌─────────────────┐      generates    ┌─────────────────┐
│  Helm Chart     │─────────────────▶│  All Resources  │
└─────────────────┘                   └─────────────────┘
```

---

## State Transitions

### Deployment State Machine

```
[Created] → [Progressing] → [Available] → [Updated] → [Available]
                ↓                ↓
           [Failed]         [Degraded]
```

**States**:
- **Created**: Deployment manifest applied
- **Progressing**: Pods being created/updated
- **Available**: All replicas ready and available
- **Updated**: Rolling update in progress
- **Degraded**: Some replicas unavailable
- **Failed**: Deployment failed (image pull error, crash loop, etc.)

### Pod State Machine

```
[Pending] → [Running] → [Succeeded]
     ↓          ↓
[Failed]   [CrashLoopBackOff]
```

**States**:
- **Pending**: Waiting for scheduling or image pull
- **Running**: Container(s) running
- **Succeeded**: Container(s) completed successfully
- **Failed**: Container(s) failed
- **CrashLoopBackOff**: Container repeatedly crashing

---

## Summary

This data model defines 7 key entities for Kubernetes deployment:

1. **Container Image**: Immutable application package
2. **Deployment**: Manages pod replicas with desired state
3. **Service**: Provides stable network endpoint
4. **ConfigMap**: Non-sensitive configuration
5. **Secret**: Sensitive credentials
6. **PersistentVolumeClaim**: Persistent storage
7. **Helm Chart**: Deployment package with templates

All entities follow Kubernetes API conventions and align with constitution principles (Container-First Architecture, Kubernetes-Native Deployment, Infrastructure as Code).
