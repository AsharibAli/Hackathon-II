---
id: 002
title: Phase 5 implementation planning
stage: plan
date: 2025-12-25
surface: agent
model: claude-opus-4-5-20251101
feature: 004-phase5-cloud-deployment
branch: 004-phase5-cloud-deployment
user: unknown
command: /sp.plan
labels: ["planning", "architecture", "microservices", "dapr", "kafka", "helm", "kubernetes"]
links:
  spec: specs/004-phase5-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-phase5-cloud-deployment/plan.md
  - specs/004-phase5-cloud-deployment/research.md
  - specs/004-phase5-cloud-deployment/data-model.md
  - specs/004-phase5-cloud-deployment/quickstart.md
  - specs/004-phase5-cloud-deployment/contracts/api.yaml
  - specs/004-phase5-cloud-deployment/contracts/events.md
  - specs/speckit.plan
tests:
  - Constitution Check: 12/12 principles PASS
---

## Prompt

```text
# /sp.plan - Phase 5: Architecture & Technical Design

## CONTEXT

Read first:
- `specs/speckit.constitution` (principles)
- `specs/speckit.specify` (requirements)

Now design the HOW.

---

## SYSTEM ARCHITECTURE

### High-Level Architecture
- Frontend (Next.js) → Backend (FastAPI) → Dapr Sidecar → Kafka
- Kafka topics: task-events, reminders, task-updates
- Consumer services: recurring-service, notification-service

## COMPONENT SPECIFICATIONS

### C-001: Backend Service (chat-api)
- FastAPI + Python 3.11, Port 8000
- Task CRUD, chat, event publishing via Dapr

### C-002: Frontend Service
- Next.js 14, Port 3000
- Chat UI, task list with filters

### C-003: Notification Service (NEW)
- FastAPI + Python 3.11, Port 8001
- Subscribe to reminders topic

### C-004: Recurring Task Service (NEW)
- FastAPI + Python 3.11, Port 8002
- Subscribe to task-events, create next occurrence

## DATABASE SCHEMA
- Extended Task with: priority, tags, due_date, remind_at, recurrence, parent_task_id
- New Tags table with many-to-many to Task

## DAPR COMPONENTS
- pubsub.kafka, state.postgresql, secretstores.kubernetes

## HELM CHART STRUCTURE
- Umbrella chart with sub-charts for each service
- Values files for minikube, staging, production

## CI/CD PIPELINE
- GitHub Actions
- Build on push, deploy staging on main, production on tag
- Helm upgrade with --atomic

## DEPLOYMENT SEQUENCE
- Minikube: Start → Dapr init → Strimzi → Components → Helm
- Cloud: Cluster → Dapr → Redpanda Cloud → CI/CD

Generate the plan file at `specs/speckit.plan`.
```

## Response snapshot

Successfully created comprehensive implementation plan for Phase 5.

**Planning Artifacts Created**:

1. **plan.md** - Complete implementation plan with:
   - System architecture diagram (ASCII)
   - 4 component specifications (backend, frontend, notification-service, recurring-service)
   - Project structure with source code layout
   - Dapr component configurations
   - Helm chart structure
   - CI/CD pipeline design
   - Deployment sequences for Minikube and cloud
   - Constitution compliance check (12/12 PASS)

2. **research.md** - Technology decisions (10 research items):
   - R-001: Dapr Pub/Sub with Kafka
   - R-002: Declarative subscriptions
   - R-003: Strimzi for Minikube, Redpanda Cloud for production
   - R-004: dateparser for natural language dates
   - R-005: Recurring service calls backend API (not direct DB)
   - R-006: Database polling for reminders (vs Dapr Jobs alpha)
   - R-007: Umbrella Helm chart pattern
   - R-008: GitHub Actions with matrix builds
   - R-009: Alembic migrations for schema changes
   - R-010: structlog for JSON logging

3. **data-model.md** - Entity schemas:
   - Task (extended with 6 new columns)
   - Tag (case-insensitive, user-scoped)
   - TaskTag (junction table)
   - TaskEvent (Kafka message schema)
   - ReminderEvent (Kafka message schema)
   - Migration scripts

4. **contracts/api.yaml** - OpenAPI 3.1 specification:
   - 15 endpoints with full schemas
   - Task CRUD with filters, sorting
   - Tag management
   - Search functionality
   - Health endpoints

5. **contracts/events.md** - Kafka event contracts:
   - task-events topic (4 event types)
   - reminders topic
   - Subscription configurations
   - Error handling patterns

6. **quickstart.md** - Developer setup guide:
   - Prerequisites and verification
   - One-command Minikube deployment
   - Local development without Kubernetes
   - Environment variables
   - Troubleshooting guide

7. **speckit.plan** - Quick reference file

**Constitution Check Results**: 12/12 principles PASSED
- No violations requiring justification
- All technology choices align with constraints

## Outcome

- ✅ Impact: Complete Phase 5 implementation plan with architecture, research, data model, API/event contracts, and developer quickstart
- 🧪 Tests: Constitution check 12/12 PASS
- 📁 Files: 7 planning artifacts created
- 🔁 Next prompts: `/sp.tasks` to generate implementation task breakdown
- 🧠 Reflection: Comprehensive planning phase completed; architecture diagram shows clear service boundaries; research decisions documented with rationale and rejected alternatives; all Dapr patterns follow best practices

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution compliance - PASS
- Prompt variant (if applicable): Detailed architecture input with component specs
- Next experiment (smallest change to try): Validate plan completeness by running /sp.tasks to ensure all features can be broken into tasks
