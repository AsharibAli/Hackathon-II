---
id: 003
title: Phase 5 cloud native constitution update
stage: constitution
date: 2025-12-25
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: unknown
command: /sp.constitution
labels: ["constitution", "amendment", "phase-5", "cloud-native", "microservices", "dapr", "kubernetes", "event-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - specs/speckit.constitution
tests:
  - None (documentation only)
---

## Prompt

```text
# /sp.constitution - Phase 5: Advanced Cloud Deployment

## PROJECT IDENTITY

**Project Name:** TaskAI - Phase 5 Advanced Cloud Deployment
**Version:** 2.0.0
**Phase:** 5 of 5
**Foundation:** Phase 4 Local Kubernetes Deployment (Completed & Working)

---

## CORE PRINCIPLES (Non-Negotiable)

### P1: Event-Driven First
- All inter-service communication MUST go through Kafka/Dapr pub/sub
- No direct HTTP calls between microservices for business events
- Synchronous calls allowed ONLY for user-facing request/response

### P2: Dapr Abstraction Layer
- Applications MUST NOT have direct dependencies on Kafka client libraries
- All pub/sub, state, and secrets accessed via Dapr sidecar HTTP API
- Infrastructure swappable by changing Dapr component YAML, not code

### P3: Cloud-Native Portability
- Deployment MUST work on: Minikube (local), AKS (Azure), GKE (Google), OKE (Oracle)
- Use Helm values files for environment-specific configuration
- No hardcoded cloud provider specifics in application code

### P4: Spec-Driven Development
- No code written without corresponding Task ID
- All features trace back to speckit.specify requirements
- Every PR must reference Task IDs and acceptance criteria

### P5: AI-Assisted Development
- Use kubectl-ai for Kubernetes operations where possible
- Use Gordon (docker ai) for container operations where possible
- Document AI tool usage in implementation notes

---

## TECHNOLOGY CONSTRAINTS

### MUST USE:
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

### MUST NOT USE:
- Direct Kafka client libraries (kafka-python) - use Dapr
- LoadBalancer service type on Minikube - use NodePort
- Hardcoded connection strings - use Dapr secrets or K8s secrets
- `latest` image tags in production - use semantic versioning

---

## ARCHITECTURE CONSTRAINTS

### Microservices Boundaries:
- frontend: UI only, no business logic
- backend (chat-api): Chat + Task CRUD + Event publishing
- notification-service: Consume reminders, send notifications
- recurring-service: Consume task.completed, create next

### Event Topics (Kafka):
- task-events: backend → recurring-service, audit
- reminders: backend → notification-service
- task-updates: backend → websocket-service (future)

### Dapr Components Required:
- pubsub.kafka - Kafka abstraction
- state.postgresql - State management
- secretstores.kubernetes - Secrets
- Dapr Jobs API - Scheduled reminders

---

## QUALITY CONSTRAINTS

### Performance:
- API response time < 500ms (p95)
- Event processing latency < 2 seconds
- Pod startup time < 30 seconds

### Reliability:
- All services must have health endpoints
- Kubernetes liveness and readiness probes required
- Graceful shutdown handling for all services

### Security:
- No secrets in code or config maps
- Use Kubernetes secrets or Dapr secret stores
- Non-root container users

### Observability:
- Structured JSON logging
- Dapr observability enabled
- Health endpoints: /health, /ready

---

## DEPLOYMENT CONSTRAINTS

### Environment Hierarchy:
minikube (local) → staging (cloud) → production (cloud)

### Helm Values Strategy:
values.yaml, values-minikube.yaml, values-staging.yaml, values-production.yaml

### CI/CD Rules:
- Push to main → Deploy to staging
- Git tag v* → Deploy to production
- All deployments via Helm
- Rollback capability required

---

## DEFINITION OF DONE

A feature is complete when:
1. Code implements the Task specification exactly
2. Unit tests pass (>80% coverage for new code)
3. Works on Minikube locally
4. Works on cloud (AKS/GKE/OKE)
5. Dapr integration verified
6. Events published/consumed correctly
7. Documentation updated
8. CI/CD pipeline passes

---

Generate the constitution file at specs/speckit.constitution based on these principles.
```

## Response snapshot

Successfully amended the project constitution from v1.1.0 to v2.0.0 (MAJOR version bump).

**Version Bump Rationale**: MAJOR bump because this is a complete architectural pivot from a monolithic full-stack application to a cloud-native microservices architecture with fundamentally different principles.

**Key Changes:**

**New Core Principles (I-V):**
- **I. Event-Driven First**: All inter-service communication via Kafka/Dapr pub/sub
- **II. Dapr Abstraction Layer**: No direct infrastructure dependencies (kafka-python forbidden)
- **III. Cloud-Native Portability**: Works on Minikube, AKS, GKE, OKE without code changes
- **IV. Spec-Driven Development**: Enhanced with Task ID traceability requirements
- **V. AI-Assisted Development**: kubectl-ai and Gordon (docker ai) usage

**Replaced Principles:**
- Tool-Driven AI Behavior (MCP) → replaced by Dapr Abstraction Layer
- Conversation Persistence → replaced by Event-Driven First

**Retained & Enhanced Principles (VI-XII):**
- Single Code Authority
- Microservices Separation (expanded from Separation of Concerns)
- Authentication & Authorization (adapted for K8s secrets)
- Test-First When Specified (added K8s manifest testing)
- Database Persistence First
- Observability & Debuggability (enhanced for cloud-native)
- Stateless Server Architecture

**New Sections Added:**
- Technology Constraints (MUST USE / MUST NOT USE tables)
- Event Architecture (Kafka topics, Dapr components)
- Quality Constraints (Performance, Reliability, Security, Observability)
- Deployment Constraints (Environment hierarchy, Helm strategy, CI/CD rules)
- Updated project structure for Phase-5

**Files Created/Updated:**
- `.specify/memory/constitution.md` - Full constitution (v2.0.0)
- `specs/speckit.constitution` - Quick reference pointing to main constitution

## Outcome

- ✅ Impact: Constitution completely rewritten for Phase-5 cloud-native microservices architecture with 12 principles covering event-driven design, Dapr abstraction, multi-cloud portability, and comprehensive quality/deployment constraints
- 🧪 Tests: None (governance document)
- 📁 Files: Updated .specify/memory/constitution.md (v1.1.0 → v2.0.0, 445 lines), created specs/speckit.constitution
- 🔁 Next prompts: Ready for `/sp.specify` to create Phase-5 cloud deployment feature specification, then `/sp.plan` for architecture
- 🧠 Reflection: MAJOR version bump appropriate due to fundamental architectural shift from monolithic to microservices, replacement of MCP/AI-agent principles with Dapr/event-driven principles, and complete restructuring of technology constraints

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable (documentation amendment)
- Prompt variant (if applicable): Phase-5 constitution amendment with cloud-native focus
- Next experiment (smallest change to try): Validate new Dapr/event-driven principles against Phase-5 implementation to ensure sufficient coverage for microservices communication patterns
