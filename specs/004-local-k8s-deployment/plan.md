# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-local-k8s-deployment` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-local-k8s-deployment/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable local Kubernetes deployment of the Todo Chatbot application using Docker containerization, Helm charts, and Minikube. This provides developers with a production-like environment for testing before cloud deployment. The implementation follows container-first architecture with multi-stage Docker builds, Kubernetes-native deployment patterns with health probes and resource limits, and Infrastructure as Code using Helm charts for repeatable deployments.

## Technical Context

**Language/Version**: Python 3.11+ (backend), React 18+ with TypeScript (frontend), Bash (deployment scripts)
**Primary Dependencies**: Docker 24.0.0+, Kubernetes (Minikube 1.32.0+), Helm 3.x, kubectl 1.28.0+, FastAPI, OpenAI Agents SDK
**Storage**: Neon Serverless PostgreSQL (external, structured data), SQLite (local, agent sessions with PersistentVolumeClaim)
**Testing**: pytest (backend), Playwright (E2E), Vitest (frontend unit), hadolint (Dockerfile linting), helm lint (chart validation)
**Target Platform**: Local development (Minikube on Docker driver), cross-platform (Windows 10/11 with WSL2, macOS 10.15+, Linux Ubuntu 20.04+)
**Project Type**: Web application (frontend + backend containerized services)
**Performance Goals**: Container builds <5 minutes (incremental), deployment <2 minutes (all pods ready), images <500MB each, application response <1 second
**Constraints**: Minimum 8GB RAM and 4 CPU cores for local cluster, 20GB free disk space, Docker daemon running, network connectivity for image pulls
**Scale/Scope**: Local development environment, 2 containerized services (frontend + backend), 5 user stories (P0-P4), Helm chart for repeatable deployments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Test-Driven Development (NON-NEGOTIABLE)
- **Status**: ✅ PASS
- **Application**: Tests will validate Dockerfile builds, Helm chart rendering, deployment success, and health checks
- **Enforcement**: Dockerfile linting (hadolint), Helm validation (helm lint, helm template), deployment verification scripts

### Principle II: Documentation-First via MCP Context7
- **Status**: ✅ PASS
- **Application**: All Docker, Kubernetes, and Helm patterns must reference official documentation
- **Enforcement**: Research phase will use Context7 to fetch current best practices from Docker docs, Kubernetes docs, and Helm docs

### Principle III: Type Safety First
- **Status**: ⚠️ PARTIAL (Infrastructure code has limited type safety)
- **Application**: Helm values.schema.json provides type validation for chart configuration
- **Enforcement**: values.schema.json required for all Helm charts, bash scripts validated with shellcheck

### Principle IV: Git Versioning on Milestones
- **Status**: ✅ PASS
- **Application**: Helm charts versioned with semver, container images tagged with Git commit SHA + latest
- **Enforcement**: Chart.yaml version field required, image tagging automated in build scripts

### Principle V: Simplicity First (YAGNI)
- **Status**: ✅ PASS
- **Application**: Start with minimal Minikube setup, avoid premature optimization (no service mesh, no complex networking)
- **Enforcement**: Complexity Tracking table documents any deviations from simple approach

### Principle VI: Architecture Plan First
- **Status**: ✅ PASS (in progress)
- **Application**: This planning phase precedes implementation, research.md will document technical decisions
- **Enforcement**: Following spec → plan → tasks → implementation workflow

### Principle VII: MCP Server for Tools
- **Status**: ✅ PASS (not directly applicable)
- **Application**: Infrastructure deployment does not modify MCP tool architecture
- **Enforcement**: N/A for Phase 4

### Principle VIII: Container-First Architecture
- **Status**: ✅ PASS (CRITICAL for Phase 4)
- **Application**: Multi-stage Dockerfiles, non-root users, Alpine/distroless base images, layer optimization, health checks
- **Enforcement**: hadolint validation, image scanning (Docker Scout/Trivy), .dockerignore required, images <500MB

### Principle IX: Kubernetes-Native Deployment
- **Status**: ✅ PASS (CRITICAL for Phase 4)
- **Application**: Resource limits/requests, liveness/readiness probes, rolling updates, ConfigMaps/Secrets, Services for discovery
- **Enforcement**: kubectl dry-run validation, all Deployments must specify resources and probes

### Principle X: Infrastructure as Code (Helm Charts)
- **Status**: ✅ PASS (CRITICAL for Phase 4)
- **Application**: All Kubernetes resources defined in Helm charts, values.schema.json for validation, flat values structure
- **Enforcement**: helm lint with zero warnings, Chart.yaml versioning, parameterized values.yaml

**Overall Gate Status**: ✅ PASS - All critical principles satisfied, proceed to Phase 0 research

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design completion (research.md, data-model.md, contracts/, quickstart.md)*

### Principle VIII: Container-First Architecture
- **Status**: ✅ PASS (VERIFIED)
- **Evidence**:
  - Multi-stage Dockerfiles designed for frontend (Node.js builder + nginx-unprivileged) and backend (Python 3.11-alpine)
  - Non-root users specified (nginx:nginx for frontend, app:app UID 1001 for backend)
  - Alpine base images selected for minimal size (<100MB frontend, <200MB backend)
  - Layer optimization documented in research.md
  - Health checks planned for both services

### Principle IX: Kubernetes-Native Deployment
- **Status**: ✅ PASS (VERIFIED)
- **Evidence**:
  - Resource limits/requests defined in contracts/ (Frontend: 512Mi/1Gi RAM, 250m/500m CPU; Backend: 1Gi/2Gi RAM, 500m/1000m CPU)
  - Liveness/readiness probes specified (HTTP GET /health, 30s/10s/3)
  - Rolling update strategy documented (maxSurge: 1, maxUnavailable: 1)
  - ConfigMaps and Secrets designed for configuration management
  - Services defined for discovery (NodePort with kubectl port-forward)
  - PVC designed for SQLite persistence

### Principle X: Infrastructure as Code (Helm Charts)
- **Status**: ✅ PASS (VERIFIED)
- **Evidence**:
  - Helm chart structure documented in research.md
  - Flat values structure planned (frontendImage, frontendTag, etc.)
  - values.schema.json validation planned
  - Chart versioning strategy defined (semver)
  - Templates organized by resource type

**Final Gate Status**: ✅ PASS - All principles verified in design phase, ready for implementation

## Project Structure

### Documentation (this feature)

```text
specs/004-local-k8s-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (existing)
backend/
├── src/
│   ├── models/          # SQLModel entities
│   ├── services/        # Business logic
│   └── api/             # FastAPI routes
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile           # NEW: Multi-stage build for backend
├── .dockerignore        # NEW: Exclude unnecessary files
└── requirements.txt     # Python dependencies

frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   └── services/        # API clients
├── tests/
│   ├── unit/
│   └── e2e/
├── Dockerfile           # NEW: Multi-stage build for frontend
├── .dockerignore        # NEW: Exclude unnecessary files
└── package.json         # Node dependencies

# NEW: Kubernetes deployment infrastructure
k8s/
├── helm/
│   └── todo-chatbot/
│       ├── Chart.yaml           # Helm chart metadata
│       ├── values.yaml          # Default configuration
│       ├── values.schema.json   # Type validation
│       └── templates/
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── configmap.yaml
│           ├── secrets.yaml
│           └── pvc.yaml         # PersistentVolumeClaim for SQLite
└── scripts/
    ├── verify-tools.sh          # Check kubectl, minikube, docker
    ├── build-images.sh          # Build and tag container images
    ├── deploy-local.sh          # Deploy to Minikube
    └── cleanup.sh               # Remove deployment

# NEW: Documentation
docs/
└── deployment/
    ├── local-setup.md           # Tool installation guide
    ├── docker-guide.md          # Container build guide
    └── troubleshooting.md       # Common issues and fixes
```

**Structure Decision**: Web application structure (Option 2) with added containerization and Kubernetes infrastructure. The existing backend/ and frontend/ directories will receive Dockerfiles. New k8s/ directory contains Helm charts and deployment scripts. This structure separates application code from infrastructure code while keeping deployment artifacts version-controlled alongside the application.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
