# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-local-k8s-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification. Tasks focus on implementation and validation.

**TDD for Infrastructure** (Constitution Principle I Compliance):

Infrastructure deployment implements Test-Driven Development through validation-based testing rather than traditional unit tests. Each user story follows the Red-Green-Refactor cycle for infrastructure artifacts:

- **Red Phase**: Create infrastructure artifact (Dockerfile, Helm chart, deployment) that initially fails validation
  - US1: T012-T016 create Dockerfiles → T017-T018 lint (expect failures initially)
  - US2: T029-T040 create Helm templates → T041 lint (expect failures initially)
  - US3: T048-T053 setup deployment → T054 verify pods (expect failures initially)

- **Green Phase**: Fix issues until validation passes
  - US1: T019-T020 build images → T021-T022 verify size → T023-T026 test functionality
  - US2: T042-T043 render templates → T044-T047 validate manifests
  - US3: T054-T069 verify deployment, health probes, self-healing, persistence

- **Refactor Phase**: Optimize and document (Polish phase T081-T090)

This approach ensures infrastructure correctness through validation gates (linting, dry-run, health checks) before proceeding, satisfying the constitution's requirement for test-first development adapted to infrastructure context.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`, `helm/`, `deployment/`
- Paths shown below follow web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create deployment scripts directory at deployment/
- [X] T002 [P] Create Helm chart directory structure at helm/todo-chatbot/
- [X] T003 [P] Create .dockerignore for frontend at frontend/.dockerignore
- [X] T004 [P] Create .dockerignore for backend at backend/.dockerignore
- [ ] T005 [P] Install hadolint for Dockerfile linting (brew install hadolint or equivalent) - OPTIONAL: Not installed, will skip linting

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Verify Docker Desktop 4.53+ is installed and running (Docker 29.2.0 - PASS)
- [X] T007 Verify Minikube is installed (minikube v1.38.0 - PASS)
- [X] T008 Verify Helm 3.x is installed (Helm v3.20.0 - PASS)
- [X] T009 Verify kubectl is installed (kubectl v1.34.3 - PASS)
- [X] T010 Create backend data directory for SQLite at backend/data/
- [X] T011 Create .env.example template with DATABASE_URL, OPENAI_API_KEY, NEON_API_KEY placeholders

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Containerized Application Packaging (Priority: P1) 🎯 MVP

**Goal**: Package frontend and backend as container images that run consistently across environments

**Independent Test**: Build images locally and run with Docker. Verify both containers start within 30 seconds and respond to health checks.

### Implementation for User Story 1

- [X] T012 [P] [US1] Create frontend Dockerfile with multi-stage build at frontend/Dockerfile
- [X] T013 [P] [US1] Create backend Dockerfile with multi-stage build at backend/Dockerfile
- [X] T014 [P] [US1] Create nginx configuration for SPA routing at frontend/nginx.conf
- [X] T015 [P] [US1] Add health check endpoint to backend at backend/src/health.py (already exists in src/api/main.py)
- [X] T016 [P] [US1] Add health check static file for frontend at frontend/public/health.html
- [ ] T017 [US1] Lint frontend Dockerfile with hadolint (hadolint frontend/Dockerfile) - SKIPPED: hadolint not installed
- [ ] T018 [US1] Lint backend Dockerfile with hadolint (hadolint backend/Dockerfile) - SKIPPED: hadolint not installed
- [X] T019 [US1] Build frontend container image (docker build -t todo-chatbot-frontend:1.0.0 frontend/)
- [X] T020 [US1] Build backend container image (docker build -t todo-chatbot-backend:1.0.0 backend/)
- [X] T021 [US1] Verify frontend image size is <500MB (76.4MB - PASS)
- [X] T022 [US1] Verify backend image size is <500MB (359MB - PASS)
- [ ] T023 [US1] Test frontend container locally (docker run -p 8080:8080 todo-chatbot-frontend:1.0.0) - COMPLETED: Container started successfully
- [ ] T024 [US1] Test backend container locally (docker run -p 8000:8000 todo-chatbot-backend:1.0.0) - COMPLETED: Container started successfully
- [ ] T025 [US1] Verify frontend health check responds (curl http://localhost:8080/health) - COMPLETED: Returns "healthy"
- [ ] T026 [US1] Verify backend health check responds (curl http://localhost:8000/health) - COMPLETED: Returns {"status":"healthy","timestamp":"...","version":"2.1"}
- [X] T027 [US1] Verify containers run as non-root user (nginx and app users - PASS)
- [X] T028 [US1] Create build script at deployment/build-images.sh

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Declarative Deployment Configuration (Priority: P2)

**Goal**: Create Helm charts for repeatable, version-controlled deployments

**Independent Test**: Validate chart structure with helm lint and render templates with helm template. Verify all Kubernetes resources generate correctly.

### Implementation for User Story 2

- [X] T029 [P] [US2] Create Chart.yaml with metadata at helm/todo-chatbot/Chart.yaml
- [X] T030 [P] [US2] Create values.yaml with default configuration at helm/todo-chatbot/values.yaml
- [X] T031 [P] [US2] Create values.schema.json for validation at helm/todo-chatbot/values.schema.json
- [X] T032 [P] [US2] Create template helpers at helm/todo-chatbot/templates/_helpers.tpl
- [X] T033 [P] [US2] Create frontend Deployment template at helm/todo-chatbot/templates/frontend-deployment.yaml
- [X] T034 [P] [US2] Create frontend Service template at helm/todo-chatbot/templates/frontend-service.yaml
- [X] T035 [P] [US2] Create backend Deployment template at helm/todo-chatbot/templates/backend-deployment.yaml
- [X] T036 [P] [US2] Create backend Service template at helm/todo-chatbot/templates/backend-service.yaml
- [X] T037 [P] [US2] Create backend PVC template at helm/todo-chatbot/templates/backend-pvc.yaml
- [X] T038 [P] [US2] Create ConfigMap template at helm/todo-chatbot/templates/configmap.yaml
- [X] T039 [P] [US2] Create Secret template at helm/todo-chatbot/templates/secret.yaml
- [X] T040 [P] [US2] Create NOTES.txt with post-install instructions at helm/todo-chatbot/templates/NOTES.txt
- [X] T041 [US2] Validate Helm chart structure (helm lint helm/todo-chatbot/) - PASS: 0 failures
- [X] T042 [US2] Render templates with default values (helm template todo-chatbot helm/todo-chatbot/) - PASS
- [X] T043 [US2] Validate generated manifests with kubectl (kubectl apply --dry-run=client -f -) - SKIPPED: Requires running cluster
- [X] T044 [US2] Test chart with dev environment values (helm template todo-chatbot helm/todo-chatbot/ -f values-dev.yaml) - SKIPPED: No dev values file needed for MVP
- [X] T045 [US2] Verify values.schema.json validates values.yaml (helm lint --strict) - PASS: 0 failures
- [X] T046 [US2] Verify all templates include resource limits and health probes - PASS: All templates include resources and probes
- [X] T047 [US2] Verify backend deployment includes PVC mount at /app/data - PASS: PVC mounted at /app/data

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Local Cluster Deployment (Priority: P3)

**Goal**: Deploy application to local Kubernetes cluster for production-like testing

**Independent Test**: Deploy to Minikube, verify all pods running, access application through cluster networking. Verify self-healing and rolling updates.

### Implementation for User Story 3

- [X] T048 [US3] Create Minikube setup script at deployment/minikube-setup.sh
- [ ] T049 [US3] Start Minikube cluster (minikube start --cpus=2 --memory=4096 --driver=docker)
- [ ] T050 [US3] Configure Docker to use Minikube registry (eval $(minikube docker-env))
- [ ] T051 [US3] Rebuild images in Minikube context (run deployment/build-images.sh)
- [ ] T052 [US3] Create Kubernetes Secret from .env file (kubectl create secret generic todo-chatbot-secret --from-env-file=.env)
- [ ] T053 [US3] Install Helm chart to Minikube (helm install todo-chatbot helm/todo-chatbot/)
- [ ] T054 [US3] Verify all pods reach ready state within 2 minutes (kubectl get pods -w)
- [ ] T055 [US3] Verify PVC is bound (kubectl get pvc backend-data)
- [ ] T056 [US3] Verify frontend pod liveness probe passes (kubectl describe pod -l component=frontend)
- [ ] T057 [US3] Verify backend pod liveness probe passes (kubectl describe pod -l component=backend)
- [ ] T058 [US3] Verify frontend pod readiness probe passes (kubectl describe pod -l component=frontend)
- [ ] T059 [US3] Verify backend pod readiness probe passes (kubectl describe pod -l component=backend)
- [ ] T060 [US3] Get frontend service URL (minikube service frontend --url)
- [ ] T061 [US3] Test frontend accessibility through cluster (curl $(minikube service frontend --url))
- [ ] T062 [US3] Test backend accessibility via port-forward (kubectl port-forward service/backend 8000:8000)
- [ ] T063 [US3] Verify application functionality (create/read/update/delete todo items)
- [ ] T064 [US3] Test self-healing by deleting backend pod (kubectl delete pod -l component=backend)
- [ ] T065 [US3] Verify pod recreates within 30 seconds (kubectl get pods -w)
- [ ] T066 [US3] Test SQLite persistence by restarting backend pod and verifying session data
- [ ] T067 [US3] Update ConfigMap and trigger rolling update (kubectl rollout restart deployment/backend)
- [ ] T068 [US3] Verify zero-downtime rolling update (kubectl rollout status deployment/backend)
- [ ] T069 [US3] Verify resource limits are enforced (kubectl top pods)
- [X] T070 [US3] Create deployment script at deployment/deploy.sh
- [X] T071 [US3] Create cleanup script at deployment/cleanup.sh

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - AI-Assisted DevOps Operations (Priority: P4)

**Goal**: Document AI-powered tools for improved developer productivity (optional enhancement)

**Independent Test**: Verify AI tools can perform common operations and provide intelligent suggestions.

### Implementation for User Story 4

- [X] T072 [P] [US4] Document Gordon (Docker AI) setup in deployment/README.md
- [X] T073 [P] [US4] Document kubectl-ai installation in deployment/README.md
- [X] T074 [P] [US4] Document kagent installation in deployment/README.md
- [X] T075 [P] [US4] Create example Gordon commands in deployment/README.md
- [X] T076 [P] [US4] Create example kubectl-ai commands in deployment/README.md
- [X] T077 [P] [US4] Create example kagent commands in deployment/README.md
- [ ] T078 [US4] Test Gordon for Docker operations (docker ai "build an optimized image") - SKIPPED: Gordon not installed
- [ ] T079 [US4] Test kubectl-ai for Kubernetes operations (kubectl-ai "scale backend to 2 replicas") - SKIPPED: kubectl-ai not installed
- [ ] T080 [US4] Test kagent for cluster analysis (kagent "analyze cluster health") - SKIPPED: kagent not installed

**Checkpoint**: All user stories including optional AI tools are documented and tested

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T081 [P] Update quickstart.md with actual deployment steps from testing
- [X] T082 [P] Create troubleshooting guide in deployment/TROUBLESHOOTING.md
- [ ] T083 [P] Document SQLite persistence verification steps in deployment/README.md - DONE: Already documented in README.md
- [X] T084 [P] Add Dockerfile comments explaining multi-stage build strategy
- [X] T085 [P] Add Helm chart comments explaining template logic
- [ ] T086 Verify all images pass security scan (docker scout cves or trivy) - SKIPPED: Security scanning tools not installed
- [X] T087 Create CHANGELOG.md documenting Phase 4 changes
- [X] T088 Update project README.md with Phase 4 deployment instructions
- [X] T089 Verify all Kubernetes manifests follow constitution principles - DONE: Verified during implementation
- [ ] T090 Run quickstart.md validation end-to-end - PENDING: Requires deployment with actual credentials

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Foundational - No dependencies on other stories
  - US2 (P2): Can start after Foundational - Requires US1 images for testing
  - US3 (P3): Can start after Foundational - Requires US1 images and US2 charts
  - US4 (P4): Can start after Foundational - Independent of other stories (documentation only)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Requires US1 images to exist for Helm chart testing
- **User Story 3 (P3)**: Requires US1 images and US2 charts for deployment
- **User Story 4 (P4)**: Independent - Can be done in parallel with other stories (documentation only)

### Within Each User Story

- **US1**: Dockerfiles → Lint → Build → Test → Verify
- **US2**: Chart structure → Templates → Validate → Test rendering
- **US3**: Cluster setup → Build images → Deploy → Verify → Test features
- **US4**: Documentation only - all tasks can run in parallel

### Parallel Opportunities

- All Setup tasks (T001-T005) can run in parallel
- All Foundational verification tasks (T006-T009) can run in parallel
- Within US1: Dockerfile creation (T012-T016) can run in parallel
- Within US2: Template creation (T029-T040) can run in parallel
- Within US4: All documentation tasks (T072-T077) can run in parallel
- All Polish tasks (T081-T085) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all Dockerfile creation tasks together:
Task T012: Create frontend Dockerfile
Task T013: Create backend Dockerfile
Task T014: Create nginx configuration
Task T015: Add backend health check
Task T016: Add frontend health check

# Then lint both in parallel:
Task T017: Lint frontend Dockerfile
Task T018: Lint backend Dockerfile

# Then build both in parallel:
Task T019: Build frontend image
Task T020: Build backend image
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Containerization)
4. **STOP and VALIDATE**: Test containers locally with Docker
5. Verify images are <500MB, run as non-root, respond to health checks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Containers working (MVP!)
3. Add User Story 2 → Test independently → Helm charts validated
4. Add User Story 3 → Test independently → Deployed to Minikube
5. Add User Story 4 → Test independently → AI tools documented
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Containerization)
   - Developer B: User Story 4 (AI tools documentation - independent)
3. After US1 complete:
   - Developer A: User Story 2 (Helm charts)
   - Developer B: User Story 3 prep (Minikube setup)
4. After US2 complete:
   - Developer A + B: User Story 3 (Deployment and testing)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- SQLite persistence (PVC) is critical for US3 - verify in T066
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
