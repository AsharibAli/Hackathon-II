<!--
Sync Impact Report:
Version Change: 1.1.0 → 2.0.0 (MAJOR - complete architectural pivot to cloud-native microservices)
Modified Principles:
  - Principle I: Renamed "Spec-First Development" → "Spec-Driven Development" (P4 in user input)
  - Principle II: "Single Code Authority" retained as is
  - Principle III: "Separation of Concerns" → expanded to microservices boundaries
  - Principle IV: "Authentication & Authorization" retained, adapted for Kubernetes secrets
  - Principle V: "Test-First When Specified" retained with cloud testing requirements
  - Principle VI: "Database Persistence First" retained for Neon PostgreSQL
  - Principle VII: "Observability & Debuggability" enhanced for cloud-native
  - Principle VIII: "Stateless Server Architecture" retained, applied to all microservices
  - Principle IX: "Tool-Driven AI Behavior (MCP)" → replaced by "Dapr Abstraction Layer" (P2)
  - Principle X: "Conversation Persistence" → replaced by "Event-Driven First" (P1)
Added Sections:
  - NEW Principle: Cloud-Native Portability (P3)
  - NEW Principle: AI-Assisted Development (P5)
  - Technology Constraints (MUST USE / MUST NOT USE)
  - Microservices Boundaries Table
  - Kafka Event Topics
  - Dapr Components Required
  - Quality Constraints (Performance, Reliability, Security, Observability)
  - Deployment Constraints (Environment Hierarchy, Helm Strategy, CI/CD Rules)
  - Updated folder structure for Phase-5 layout
Removed Sections:
  - OpenAI Agents SDK, MCP SDK references (replaced by Dapr)
  - ChatKit UI references
  - Phase-specific principle markers "(Phase-3)"
Templates Status:
  - ✅ .specify/templates/plan-template.md (Constitution Check section compatible)
  - ✅ .specify/templates/spec-template.md (Requirements alignment verified)
  - ✅ .specify/templates/tasks-template.md (Task categorization aligned)
  - ⚠ specs/ folder structure needs update post-implementation
Follow-up TODOs:
  - Create specs/speckit.specify for Phase 5 requirements
  - Create specs/speckit.plan for Phase 5 architecture
  - Create specs/speckit.tasks for Phase 5 task breakdown
  - Set up Helm chart structure under helm/
  - Create Dapr components under dapr/components/
-->

# TaskAI Constitution - Phase 5 Advanced Cloud Deployment

## Project Identity

**Project Name**: TaskAI - Phase 5 Advanced Cloud Deployment
**Version**: 2.0.0
**Phase**: 5 of 5
**Foundation**: Phase 4 Local Kubernetes Deployment (Completed & Working)

## Core Principles

### I. Event-Driven First (NON-NEGOTIABLE)

All inter-service communication MUST go through Kafka/Dapr pub/sub:

- No direct HTTP calls between microservices for business events
- Synchronous calls allowed ONLY for user-facing request/response patterns
- Event producers MUST NOT know about consumers (loose coupling)
- Events MUST be immutable and carry all necessary context

**Rationale**: Enables loose coupling between services, supports horizontal scaling, provides
natural audit trail, allows adding new consumers without modifying producers, and supports
eventual consistency patterns required for distributed systems.

### II. Dapr Abstraction Layer (NON-NEGOTIABLE)

Applications MUST NOT have direct dependencies on infrastructure client libraries:

- All pub/sub accessed via Dapr sidecar HTTP API (`/v1.0/publish/`, `/v1.0/subscribe`)
- All state management via Dapr state API (`/v1.0/state/`)
- All secrets accessed via Dapr secrets API (`/v1.0/secrets/`)
- Infrastructure swappable by changing Dapr component YAML, not application code
- Direct Kafka client libraries (kafka-python, confluent-kafka) are FORBIDDEN

**Rationale**: Provides infrastructure abstraction, enables multi-cloud portability, simplifies
application code, supports local development with different backends, and allows infrastructure
upgrades without code changes.

### III. Cloud-Native Portability (NON-NEGOTIABLE)

Deployment MUST work on multiple Kubernetes platforms without code changes:

- Minikube (local development)
- AKS (Azure Kubernetes Service)
- GKE (Google Kubernetes Engine)
- OKE (Oracle Kubernetes Engine)

Requirements:
- Use Helm values files for environment-specific configuration
- No hardcoded cloud provider specifics in application code
- Use NodePort on Minikube, LoadBalancer on cloud (via Helm values)
- All configuration via ConfigMaps, Secrets, or Dapr components

**Rationale**: Prevents vendor lock-in, supports development/staging/production parity,
enables team flexibility in choosing deployment targets, and reduces migration costs.

### IV. Spec-Driven Development (NON-NEGOTIABLE)

No code implementation shall begin before a complete specification is written, reviewed,
and approved. Every feature MUST follow this workflow:

1. Specification (`/sp.specify`) → User approval
2. Planning (`/sp.plan`) → User approval
3. Task generation (`/sp.tasks`) → User approval
4. Implementation (`/sp.implement`) → Only after all approvals

Additional Phase-5 requirements:
- No code written without corresponding Task ID
- All features trace back to speckit.specify requirements
- Every PR must reference Task IDs and acceptance criteria

**Rationale**: Prevents rework, ensures alignment with requirements, maintains project
documentation quality, enables proper architectural review, and provides traceability
from requirements to implementation.

### V. AI-Assisted Development

Use AI-powered tools where possible for Kubernetes and container operations:

- kubectl-ai for Kubernetes resource management and debugging
- Gordon (docker ai) for container operations and troubleshooting
- Document AI tool usage in implementation notes
- AI suggestions MUST be reviewed before applying

**Rationale**: Accelerates development velocity, reduces boilerplate, provides intelligent
suggestions for complex configurations, and helps catch common mistakes in YAML manifests.

### VI. Single Code Authority

Claude Code is the ONLY entity permitted to write code. Human developers provide
specifications, review outputs, and approve decisions, but MUST NOT directly write
implementation code.

**Rationale**: Ensures consistent code quality, enforces spec-driven workflow, maintains
architectural coherence, and prevents drift from specifications.

### VII. Microservices Separation

Frontend and backend responsibilities MUST remain strictly separated, with additional
microservices isolation:

| Service | Responsibility |
|---------|----------------|
| frontend | UI only, no business logic |
| backend (chat-api) | Chat + Task CRUD + Event publishing |
| notification-service | Consume reminders, send notifications |
| recurring-service | Consume task.completed, create next occurrence |

Rules:
- Each service owns its domain completely
- Cross-service communication ONLY via events or API gateway
- No shared databases between services (except for migration phases)
- Each service deployable and scalable independently

**Rationale**: Enables independent development, testing, and deployment; improves
maintainability; supports team specialization; and allows per-service scaling.

### VIII. Authentication & Authorization Enforcement

Every API request MUST enforce authentication and authorization:

- All endpoints (except public routes like `/auth/login`, `/auth/register`) MUST
  verify JWT tokens
- User identity MUST be extracted from validated tokens
- Data access MUST be scoped to the authenticated user
- Multi-user isolation MUST be guaranteed at the database query level
- Secrets MUST be stored in Kubernetes Secrets or Dapr secret stores, never in code

**Rationale**: Ensures secure multi-user operation, prevents unauthorized data access,
maintains data privacy, and meets security compliance requirements.

### IX. Test-First When Specified

When tests are explicitly requested in specifications:

- Tests MUST be written BEFORE implementation
- Tests MUST FAIL initially (Red phase)
- Implementation makes tests pass (Green phase)
- Code is then refactored while keeping tests passing (Refactor phase)
- Contract tests verify API boundaries
- Integration tests verify user journeys
- Kubernetes manifests tested via dry-run and lint

**Rationale**: Validates requirements understanding, prevents regression, ensures
testable architecture, and provides executable specifications.

### X. Database Persistence First

All application data MUST be persisted in PostgreSQL (Neon):

- No in-memory-only data structures for user data
- SQLModel ORM MUST be used for all database operations
- Migrations MUST be version-controlled and reversible
- Schema changes MUST be applied via migrations, never manual SQL
- Database connection strings stored in Kubernetes Secrets

**Rationale**: Ensures data durability, enables rollback capabilities, maintains schema
consistency across environments, and supports multiple concurrent users.

### XI. Observability & Debuggability

All code MUST support operational visibility:

- Structured JSON logging at appropriate levels (INFO, WARNING, ERROR)
- Request correlation IDs for distributed tracing
- Error responses MUST include actionable context (without leaking sensitive data)
- Performance-critical operations MUST be instrumented
- Dapr observability enabled for sidecar metrics
- Health endpoints: `/health` (liveness), `/ready` (readiness)
- Kubernetes probes configured for all deployments

**Rationale**: Enables rapid debugging, supports production monitoring, facilitates
performance optimization, and reduces mean time to resolution for incidents.

### XII. Stateless Server Architecture

All backend services MUST be stateless:

- No in-memory session storage; all session data MUST be persisted in the database
- No request-scoped caches that cannot be reconstructed from persistent storage
- Server instances MUST be horizontally scalable without sticky sessions
- Every request MUST be self-contained with all required context
- Graceful shutdown handling for all services

**Rationale**: Enables horizontal scaling, simplifies deployment, supports container
orchestration, eliminates session affinity requirements, and ensures fault tolerance.

## Technology Constraints

### MUST USE

| Category | Technology | Version |
|----------|------------|---------|
| Runtime | Dapr | 1.12+ |
| Messaging | Kafka (via Redpanda/Strimzi) | 3.x |
| Orchestration | Kubernetes | 1.28+ |
| Package Manager | Helm | 3.x |
| CI/CD | GitHub Actions | - |
| Backend | FastAPI + Python | 3.11+ |
| Frontend | Next.js | 14+ |
| Database | Neon PostgreSQL | - |
| Backend Pkg | uv (ONLY) | - |
| Frontend Pkg | pnpm (ONLY) | - |

### MUST NOT USE

- Direct Kafka client libraries (kafka-python, confluent-kafka) - use Dapr
- LoadBalancer service type on Minikube - use NodePort
- Hardcoded connection strings - use Dapr secrets or K8s secrets
- `latest` image tags in production - use semantic versioning
- npm or yarn - use pnpm for frontend
- pip or poetry - use uv for backend

## Event Architecture

### Kafka Topics

| Topic | Producers | Consumers |
|-------|-----------|-----------|
| task-events | backend | recurring-service, audit |
| reminders | backend | notification-service |
| task-updates | backend | websocket-service (future) |

### Dapr Components Required

- `pubsub.kafka` - Kafka abstraction for event publishing/subscribing
- `state.postgresql` - State management for distributed state
- `secretstores.kubernetes` - Secrets management via K8s secrets
- Dapr Jobs API - Scheduled reminders and recurring task processing

## Quality Constraints

### Performance

- API response time < 500ms (p95)
- Event processing latency < 2 seconds
- Pod startup time < 30 seconds

### Reliability

- All services must have health endpoints (`/health`, `/ready`)
- Kubernetes liveness and readiness probes required for all deployments
- Graceful shutdown handling for all services
- At-least-once delivery for events

### Security

- No secrets in code or ConfigMaps
- Use Kubernetes secrets or Dapr secret stores exclusively
- Non-root container users
- Network policies for inter-service communication

### Observability

- Structured JSON logging
- Dapr observability enabled
- Health endpoints: `/health`, `/ready`
- Correlation IDs for distributed tracing

## Deployment Constraints

### Environment Hierarchy

```
minikube (local) → staging (cloud) → production (cloud)
```

### Helm Values Strategy

```
values.yaml              # Defaults
values-minikube.yaml     # Local overrides
values-staging.yaml      # Staging overrides
values-production.yaml   # Production overrides
```

### CI/CD Rules

- Push to `main` → Deploy to staging
- Git tag `v*` → Deploy to production
- All deployments via Helm
- Rollback capability required
- No manual kubectl apply in production

## Project Structure

```
phase-5/
├── specs/
│   ├── speckit.constitution    # Governance (generated from this)
│   ├── speckit.specify         # Requirements
│   ├── speckit.plan            # Architecture
│   └── speckit.tasks           # Task breakdown
├── src/
│   ├── backend/                # FastAPI + Dapr
│   ├── frontend/               # Next.js
│   ├── notification-service/   # Event consumer
│   └── recurring-service/      # Event consumer
├── helm/
│   ├── todo-chatbot/           # Parent chart
│   └── charts/                 # Sub-charts
├── dapr/
│   └── components/             # Dapr component YAMLs
├── .github/
│   └── workflows/              # CI/CD pipelines
└── docs/
    └── PHASE-5-DEPLOYMENT.md
```

## Definition of Done

A feature is complete when:

- [ ] Code implements the Task specification exactly
- [ ] Unit tests pass (>80% coverage for new code)
- [ ] Works on Minikube locally
- [ ] Works on cloud (AKS/GKE/OKE)
- [ ] Dapr integration verified
- [ ] Events published/consumed correctly
- [ ] Documentation updated
- [ ] CI/CD pipeline passes

## Development Workflow

### Workflow Stages

1. **Specification** (`/sp.specify`): Capture user requirements, acceptance criteria
2. **Planning** (`/sp.plan`): Design architecture, define structure, identify dependencies
3. **Task Generation** (`/sp.tasks`): Break down implementation into ordered, testable tasks
4. **Implementation** (`/sp.implement`): Execute tasks with progress tracking
5. **ADR Documentation** (`/sp.adr`): Capture significant architectural decisions

### Quality Gates

Each stage MUST pass these gates before proceeding:

**Specification Gate**:
- All user stories have acceptance criteria
- Edge cases are documented
- Success criteria are measurable
- No unresolved `[NEEDS CLARIFICATION]` markers

**Planning Gate**:
- Constitution compliance verified
- Technology stack matches constraints
- Project structure follows conventions
- Dependencies identified and justified
- Dapr components defined

**Task Gate**:
- Tasks reference specific file paths
- Dependencies between tasks clearly marked
- Parallel execution opportunities identified ([P] markers)
- Each task is independently testable
- Kubernetes manifests included in tasks

**Implementation Gate**:
- All tasks completed and verified
- Tests passing (if specified)
- No hardcoded secrets or credentials
- Code follows language-specific conventions
- Helm charts lint successfully
- Works on Minikube

### Human-as-Tool Strategy

Claude Code MUST invoke the user for:

1. **Ambiguous Requirements**: Ask 2-3 targeted clarifying questions before proceeding
2. **Architectural Uncertainty**: Present options with tradeoffs, get user preference
3. **Unforeseen Dependencies**: Surface them and ask for prioritization
4. **Completion Checkpoints**: Summarize what was done, confirm next steps

## Governance

### Amendment Process

This constitution may be amended through:

1. Documented proposal with rationale
2. User approval
3. Version increment following semantic versioning:
   - **MAJOR**: Backward-incompatible principle removals or redefinitions
   - **MINOR**: New principles or materially expanded sections
   - **PATCH**: Clarifications, wording improvements, non-semantic refinements
4. Update to all dependent templates and guidance files
5. Commit with message: `docs: amend constitution to vX.Y.Z`

### Compliance

All work MUST comply with this constitution:

- PRs and reviews MUST verify compliance
- Violations MUST be justified in plan.md "Complexity Tracking" section
- Templates MUST reference constitution principles where applicable
- ADRs MUST reference relevant constitutional principles when making decisions

### Runtime Guidance

For agent-specific runtime development guidance, refer to `CLAUDE.md` (primary)
and this constitution (governance).

**Version**: 2.0.0 | **Ratified**: 2025-12-18 | **Last Amended**: 2025-12-25
