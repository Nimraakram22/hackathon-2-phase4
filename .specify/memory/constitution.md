<!--
Sync Impact Report:
Version: 1.1.0 → 1.2.0
Change Type: MINOR (Added Phase 4 containerization and Kubernetes deployment principles)
Modified Principles: None
Added Sections:
  - Principle VIII: Container-First Architecture
  - Principle IX: Kubernetes-Native Deployment
  - Principle X: Infrastructure as Code
  - Updated Technology Standards with containerization stack
Removed Sections: None
Templates Status:
  ✅ plan-template.md - Constitution Check section aligns with all principles
  ✅ spec-template.md - User story prioritization aligns with simplicity principle
  ✅ tasks-template.md - TDD workflow and containerization phases enforced
Follow-up TODOs: None
Amendment Rationale: Phase 4 requires local Kubernetes deployment with Docker containerization, Helm charts, and AI-assisted DevOps tools (Gordon, kubectl-ai, kagent). Added three new principles based on Docker, Kubernetes, and Helm official documentation best practices researched via Context7 MCP server.
-->

# Agentic Todo Constitution

## Core Principles

### I. Test-Driven Development (NON-NEGOTIABLE)

TDD is mandatory for all feature development. The Red-Green-Refactor cycle MUST be strictly enforced:

- **Red**: Write tests FIRST that capture acceptance criteria. Tests MUST fail initially.
- **Green**: Implement minimal code to make tests pass. No premature optimization.
- **Refactor**: Clean up code while keeping tests green. Improve design incrementally.

**Rationale**: TDD ensures code correctness, prevents regressions, and creates living documentation. Tests written after implementation often miss edge cases and become validation theater rather than design tools.

**Enforcement**:
- Tests MUST be written and approved by user before implementation begins
- Implementation MUST NOT start until tests exist and fail
- All PRs MUST include tests that were written first
- Code without tests is considered incomplete

### II. Documentation-First via MCP Context7

All technical decisions and implementations MUST reference current, authoritative documentation using the Context7 MCP server:

- **Never assume**: Do not rely on internal knowledge or outdated information
- **Verify first**: Use Context7 to fetch latest documentation for frameworks, libraries, and APIs
- **Document sources**: Reference documentation URLs and versions in code comments and ADRs
- **Stay current**: Check for breaking changes and deprecations before implementation

**Rationale**: Technology evolves rapidly. Using Context7 ensures we build against current best practices, avoid deprecated patterns, and reduce technical debt from outdated approaches.

**Enforcement**:
- All architectural decisions MUST cite current documentation via Context7
- Implementation MUST verify API contracts and patterns against latest docs
- ADRs MUST include documentation references with timestamps

### III. Type Safety First

Strong typing is mandatory across the entire codebase:

- **Python**: Use type hints for all function signatures, class attributes, and return values
- **Database**: Use SQLModel for type-safe ORM with Pydantic validation
- **API Contracts**: Use Pydantic models for request/response validation
- **Configuration**: Type all environment variables and configuration objects
- **No `Any` types**: Avoid `Any` unless absolutely necessary; document justification

**Rationale**: Type safety catches errors at development time, improves IDE support, serves as inline documentation, and reduces runtime errors. In an AI-powered system with complex data flows, type safety is critical for reliability.

**Enforcement**:
- Mypy or similar type checker MUST pass with strict mode
- All public APIs MUST have complete type annotations
- PRs with untyped code will be rejected unless justified in ADR

### IV. Git Versioning on Milestones

Semantic versioning MUST be applied at significant project milestones:

- **MAJOR (X.0.0)**: Breaking changes to API contracts, database schema, or MCP tool signatures
- **MINOR (0.X.0)**: New features, user stories completed, or significant enhancements
- **PATCH (0.0.X)**: Bug fixes, documentation updates, refactoring without behavior changes

**Milestone Tagging**:
- Tag releases when user stories are completed and tested
- Create release notes documenting changes, migrations, and breaking changes
- Maintain CHANGELOG.md with version history

**Rationale**: Clear versioning enables rollback, tracks progress, and communicates changes to stakeholders. For an MCP-based system, version tracking is essential for tool compatibility.

**Enforcement**:
- Each completed user story MUST result in a version bump
- Breaking changes MUST be documented in migration guides
- Git tags MUST follow semver format

### V. Simplicity First (YAGNI)

Always choose the simplest solution that solves the current problem:

- **Start simple**: Implement the most straightforward approach first
- **YAGNI**: You Aren't Gonna Need It - avoid premature abstraction and over-engineering
- **Refactor when needed**: Add complexity only when requirements demand it
- **Prefer composition**: Use simple functions and classes over complex inheritance hierarchies
- **Avoid premature optimization**: Optimize only when profiling identifies bottlenecks

**Rationale**: Simple code is easier to understand, test, debug, and modify. Complexity should be justified by actual requirements, not hypothetical future needs.

**Enforcement**:
- Code reviews MUST challenge unnecessary complexity
- Abstractions MUST be justified in comments or ADRs
- Complexity violations flagged in Constitution Check MUST be documented in plan.md

### VI. Architecture Plan First

Comprehensive architectural planning MUST precede implementation:

- **Spec-Driven Development**: Follow the workflow: spec.md → plan.md → tasks.md → implementation
- **Research phase**: Investigate technical approaches, document alternatives, justify decisions
- **Design artifacts**: Create data models, API contracts, and architecture diagrams before coding
- **Constitution Check**: Validate design against all principles before implementation
- **ADR for decisions**: Document architecturally significant decisions with rationale and tradeoffs

**Rationale**: Planning prevents costly rework, ensures alignment with requirements, and creates shared understanding. For a complex system with MCP servers, AI agents, and multiple integrations, upfront design is critical.

**Enforcement**:
- Implementation MUST NOT begin without approved plan.md
- All user stories MUST have acceptance criteria before task breakdown
- Architectural decisions MUST be captured in ADRs
- Constitution Check MUST pass before Phase 0 research

### VII. MCP Server for Tools

All AI agent capabilities MUST be exposed through standardized MCP tools:

- **Tool-based architecture**: AI agents interact with the system exclusively through MCP tools
- **Stateless tools**: MCP tools MUST be stateless; persist state to database
- **Clear contracts**: Each tool MUST have well-defined input/output schemas with type safety
- **Error handling**: Tools MUST return structured errors with actionable messages
- **Composability**: Tools MUST be independently testable and composable

**Rationale**: MCP provides a standardized interface for AI agents, enabling tool reuse, testing, and evolution without coupling to specific AI frameworks. Stateless tools ensure scalability and resilience.

**Enforcement**:
- All task operations MUST be exposed as MCP tools
- MCP tool schemas MUST use Pydantic models for validation
- Tools MUST NOT maintain internal state between calls
- Integration tests MUST verify tool contracts

### VIII. Container-First Architecture

All applications MUST be containerized using Docker with production-grade best practices:

- **Multi-stage builds**: Separate build, development, and production stages to minimize final image size
- **Security hardening**: Run as non-root user, use minimal base images (Alpine, distroless), scan for vulnerabilities
- **Layer optimization**: Order Dockerfile instructions to maximize cache hits (dependencies before source code)
- **Environment parity**: Development and production containers MUST use identical base images and dependencies
- **Health checks**: Containers MUST define HEALTHCHECK instructions for orchestration

**Rationale**: Containers ensure consistent environments across development, testing, and production. Multi-stage builds reduce attack surface and deployment size. Security hardening prevents privilege escalation and reduces vulnerability exposure.

**Enforcement**:
- All services MUST have Dockerfiles with multi-stage builds
- Final production images MUST run as non-root user (UID 1001 or similar)
- Base images MUST be pinned to specific versions (e.g., `node:24.11.1-alpine`, not `node:latest`)
- Dockerfiles MUST be linted with hadolint or similar tool
- Images MUST be scanned for vulnerabilities before deployment
- `.dockerignore` MUST exclude unnecessary files (node_modules, .git, tests)

### IX. Kubernetes-Native Deployment

All deployments MUST follow Kubernetes best practices for reliability and observability:

- **Resource management**: All containers MUST define resource requests and limits (CPU, memory)
- **Health probes**: All deployments MUST define liveness and readiness probes
- **Rolling updates**: Use RollingUpdate strategy with maxSurge and maxUnavailable for zero-downtime deployments
- **Configuration management**: Use ConfigMaps for configuration, Secrets for sensitive data (never hardcode)
- **Service discovery**: Use Kubernetes Services for internal communication, Ingress for external access
- **Namespace isolation**: Use namespaces to separate environments (dev, staging, prod)

**Rationale**: Kubernetes provides self-healing, scaling, and orchestration. Resource limits prevent resource exhaustion. Health probes enable automatic recovery. ConfigMaps and Secrets separate configuration from code, enabling environment-specific deployments without rebuilding images.

**Enforcement**:
- All Deployment manifests MUST specify resources.requests and resources.limits
- All Deployments MUST define livenessProbe and readinessProbe
- Probes MUST use appropriate mechanisms (httpGet for HTTP services, tcpSocket for TCP, exec for custom checks)
- Secrets MUST be mounted as volumes or environment variables (never committed to git)
- Rolling updates MUST specify maxSurge: 1 and maxUnavailable: 1 for controlled rollouts
- All manifests MUST pass `kubectl apply --dry-run=client` validation

### X. Infrastructure as Code (Helm Charts)

All Kubernetes resources MUST be managed through Helm charts for repeatability and versioning:

- **Chart structure**: Follow standard Helm chart layout (Chart.yaml, values.yaml, templates/)
- **Values schema**: Define values.schema.json for type validation and documentation
- **Parameterization**: Use values.yaml for environment-specific configuration (replicas, resources, images)
- **Template best practices**: Use flat values structure for simplicity, avoid complex logic in templates
- **Version control**: Chart versions MUST follow semver and be tagged in git
- **Testing**: All charts MUST pass `helm lint` and `helm template` validation before deployment

**Rationale**: Helm provides package management, versioning, and rollback capabilities for Kubernetes. Values schema ensures configuration correctness. Parameterization enables single chart for multiple environments. Version control enables auditing and rollback.

**Enforcement**:
- All Kubernetes resources MUST be defined in Helm charts (no raw YAML in production)
- Chart.yaml MUST specify name, version, appVersion, and description
- values.yaml MUST use flat structure (e.g., `imageName`, `imageTag`) over deeply nested
- values.schema.json MUST validate all required fields and types
- Charts MUST pass `helm lint` with zero warnings
- Chart versions MUST be bumped for any template or values changes
- AI-assisted tools (kubectl-ai, kagent) MAY be used for chart generation but MUST be reviewed

## Development Workflow

### Spec-Driven Development Process

1. **Specification** (`/sp.specify`): Define user stories with priorities, acceptance criteria, and success metrics
2. **Planning** (`/sp.plan`): Research technical approaches, design architecture, create data models and contracts
3. **Task Breakdown** (`/sp.tasks`): Generate dependency-ordered, testable tasks organized by user story
4. **Implementation** (`/sp.implement`): Execute tasks following TDD cycle (Red-Green-Refactor)
5. **Analysis** (`/sp.analyze`): Cross-artifact consistency check and quality validation
6. **Commit & PR** (`/sp.git.commit_pr`): Version control with semantic commits and pull requests

### Quality Gates

**Before Implementation**:
- [ ] Constitution Check passes (all principles validated)
- [ ] User stories prioritized and independently testable
- [ ] Tests written and failing (Red phase)
- [ ] Architecture documented in plan.md
- [ ] Data models and contracts defined

**Before PR Approval**:
- [ ] All tests passing (Green phase)
- [ ] Type checking passes (mypy strict mode)
- [ ] Code refactored for simplicity (Refactor phase)
- [ ] ADRs created for significant decisions
- [ ] Documentation updated

**Before Release**:
- [ ] All user story acceptance criteria met
- [ ] Integration tests passing
- [ ] Version bumped according to semver
- [ ] CHANGELOG.md updated
- [ ] Migration guide created (if breaking changes)

## Technology Standards

### Required Stack

**Application Layer**:
- **Backend**: Python 3.11+ with FastAPI
- **AI Framework**: OpenAI Agents SDK
- **MCP Server**: Official MCP SDK (Python)
- **ORM**: SQLModel (type-safe Pydantic + SQLAlchemy)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth
- **Frontend**: OpenAI ChatKit (React 18+)
- **Type Checking**: Mypy (strict mode)
- **Testing**: Pytest with coverage reporting

**Containerization & Orchestration (Phase 4)**:
- **Containerization**: Docker (Docker Desktop 4.53+)
- **Container Registry**: Docker Hub or local registry
- **Orchestration**: Kubernetes (Minikube for local development)
- **Package Manager**: Helm 3.x
- **AI DevOps Tools**:
  - Docker AI Agent (Gordon) - AI-assisted Docker operations
  - kubectl-ai - AI-assisted Kubernetes operations
  - kagent - Advanced Kubernetes cluster analysis and optimization
- **Base Images**: Alpine Linux 3.22+ or distroless for production
- **Image Scanning**: Docker Scout or Trivy

### Code Quality Standards

**Application Code**:
- **Type Coverage**: 100% for public APIs, 95%+ overall
- **Test Coverage**: 90%+ line coverage, 100% for critical paths
- **Linting**: Ruff or Black for formatting, Pylint for code quality
- **Documentation**: Docstrings for all public functions and classes
- **Error Handling**: Structured exceptions with context, never bare `except:`

**Infrastructure Code (Phase 4)**:
- **Dockerfile Linting**: All Dockerfiles MUST pass hadolint with zero errors
- **Kubernetes Validation**: All manifests MUST pass `kubectl apply --dry-run=client`
- **Helm Validation**: All charts MUST pass `helm lint` with zero warnings
- **Security Scanning**: All images MUST be scanned with Docker Scout or Trivy before deployment
- **Resource Limits**: All containers MUST define CPU and memory limits (no unbounded resources)
- **Image Size**: Production images SHOULD be <500MB (Alpine/distroless preferred)
- **Build Time**: Multi-stage builds SHOULD complete in <5 minutes for incremental changes

### AI Agent Configuration

**Requirement**: All agents created with OpenAI Agents SDK MUST be configured to use cost-effective LLM providers (Google Gemini free models) instead of paid OpenAI models.

**Rationale**: Using free LLM providers reduces operational costs while maintaining functionality. Google Gemini 2.0 Flash provides sufficient capability for task management operations at zero cost.

**Configuration Levels**: The OpenAI Agents SDK supports three configuration levels:
1. **Agent Level** (PREFERRED) - Configure per agent for optimal model selection
2. **Run Level** - Configure per execution run
3. **Global Level** - Configure once for all agents

**MANDATORY: Use Agent Level Configuration**

Agent Level configuration MUST be used to allow each agent to use the LLM best suited for its specific task:

```python
import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

gemini_api_key = ""  # Set from environment variable

# Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)

async def main():
    # This agent will use the custom LLM provider
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=OpenAIChatCompletionsModel(
            model="gemini-2.0-flash",
            openai_client=client
        ),
    )

    result = await Runner.run(
        agent,
        "Tell me about recursion in programming.",
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

**Alternative: Run Level Configuration** (use when runtime model switching needed):

```python
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

gemini_api_key = ""  # Set from environment variable

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant"
)

result = Runner.run_sync(agent, "Hello, how are you.", run_config=config)
print(result.final_output)
```

**Alternative: Global Level Configuration** (use only for simple single-agent applications):

```python
from agents import (
    Agent, Runner, AsyncOpenAI,
    set_default_openai_client,
    set_tracing_disabled,
    set_default_openai_api
)

gemini_api_key = ""  # Set from environment variable

set_tracing_disabled(True)
set_default_openai_api("chat_completions")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_default_openai_client(external_client)

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model="gemini-2.0-flash"
)

result = Runner.run_sync(agent, "Hello")
print(result.final_output)
```

**Enforcement**:
- All agent instantiations MUST specify a model configuration
- API keys MUST be loaded from environment variables (never hardcoded)
- Agent Level configuration is REQUIRED unless justified in ADR
- Document model selection rationale in agent initialization comments
- Test agents with free models before considering paid alternatives

**Recommended Models**:
- **Primary**: `gemini-2.0-flash` - Fast, free, suitable for most tasks
- **Fallback**: `gemini-1.5-flash` - Stable alternative if 2.0 unavailable
- **Complex reasoning**: `gemini-2.0-flash-thinking-exp` - For tasks requiring deep analysis

## Governance

### Amendment Process

1. **Proposal**: Document proposed change with rationale and impact analysis
2. **Review**: Discuss tradeoffs and alternatives with team
3. **Approval**: Require consensus or designated authority approval
4. **Migration**: Update all dependent templates and documentation
5. **Version Bump**: Increment constitution version according to semver

### Compliance

- All PRs MUST verify compliance with constitution principles
- Code reviews MUST reference specific principles when requesting changes
- Constitution violations MUST be justified in Complexity Tracking table in plan.md
- Unjustified complexity or principle violations will block PR approval

### Runtime Guidance

For detailed development guidance and command usage, refer to `CLAUDE.md` in the repository root.

**Version**: 1.2.0 | **Ratified**: 2026-01-28 | **Last Amended**: 2026-02-01
