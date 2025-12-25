# Implementation Plan: Phase 5 Advanced Cloud Deployment

**Branch**: `004-phase5-cloud-deployment` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-phase5-cloud-deployment/spec.md`

## Summary

Phase 5 transforms the TaskAI from a monolithic application into a cloud-native, event-driven microservices architecture. The implementation adds enhanced task features (priorities, tags, due dates, reminders, recurring tasks), introduces Kafka messaging via Dapr abstraction, deploys two new microservices (notification-service, recurring-service), and enables multi-cloud deployment to Minikube, AKS, GKE, and OKE using Helm charts.

## Technical Context

**Language/Version**: Python 3.11+ (Backend, Services), TypeScript (Frontend)
**Primary Dependencies**: FastAPI, SQLModel, Dapr SDK, Next.js 14, shadcn/ui, httpx, dateparser
**Storage**: Neon PostgreSQL (via SQLModel ORM)
**Messaging**: Kafka (via Strimzi/Redpanda), accessed through Dapr pub/sub
**Testing**: pytest, vitest
**Target Platform**: Kubernetes 1.28+ (Minikube, AKS, GKE, OKE)
**Project Type**: Web application (microservices)
**Performance Goals**: API < 500ms p95, Event processing < 2s
**Constraints**: Dapr abstraction only (no direct Kafka libraries), NodePort on Minikube
**Scale/Scope**: 100 concurrent users, 4 microservices, 3 Kafka topics

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked post Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Event-Driven First | ✅ PASS | All inter-service communication via Kafka/Dapr pub/sub |
| II. Dapr Abstraction Layer | ✅ PASS | No kafka-python, confluent-kafka in dependencies |
| III. Cloud-Native Portability | ✅ PASS | Helm values files for Minikube/AKS/GKE/OKE |
| IV. Spec-Driven Development | ✅ PASS | Full spec.md before plan.md |
| V. AI-Assisted Development | ✅ PASS | kubectl-ai, Gordon documented in research |
| VI. Single Code Authority | ✅ PASS | Claude Code writes all code |
| VII. Microservices Separation | ✅ PASS | 4 services with clear boundaries |
| VIII. Authentication & Authorization | ✅ PASS | JWT on all endpoints, secrets in K8s |
| IX. Test-First When Specified | ✅ PASS | Contract tests defined in contracts/ |
| X. Database Persistence First | ✅ PASS | All data in PostgreSQL via SQLModel |
| XI. Observability & Debuggability | ✅ PASS | structlog JSON, /health, /ready endpoints |
| XII. Stateless Server Architecture | ✅ PASS | No in-memory state, DB polling for reminders |

**Gate Status**: PASSED - No violations requiring justification.

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              KUBERNETES CLUSTER                                       │
│                                                                                       │
│  ┌─────────────────┐   ┌─────────────────────────────────────────────────────────┐   │
│  │    FRONTEND     │   │                    BACKEND POD                          │   │
│  │   ┌─────────┐   │   │   ┌─────────────┐         ┌─────────────┐              │   │
│  │   │ Next.js │   │   │   │   FastAPI   │◀───────▶│    DAPR     │              │   │
│  │   │   App   │   │   │   │  Chat API   │         │   SIDECAR   │              │   │
│  │   └────┬────┘   │   │   │  + Tasks    │         │  :3500      │              │   │
│  │        │        │   │   └──────┬──────┘         └──────┬──────┘              │   │
│  │   ┌────┴────┐   │   │          │                       │                      │   │
│  │   │  DAPR   │   │   └──────────┼───────────────────────┼──────────────────────┘   │
│  │   │ SIDECAR │   │              │                       │                          │
│  │   └─────────┘   │              │         ┌─────────────┴─────────────┐            │
│  └─────────────────┘              │         │                           │            │
│           │                       │         ▼                           ▼            │
│           │              ┌────────┴───────────────────────────────────────────┐      │
│           │              │                    KAFKA CLUSTER                    │      │
│           │              │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │      │
│           │              │  │ task-events │ │  reminders  │ │task-updates │   │      │
│           │              │  └──────┬──────┘ └──────┬──────┘ └─────────────┘   │      │
│           │              └─────────┼───────────────┼─────────────────────────┘      │
│           │                        │               │                                 │
│           │         ┌──────────────┴───┐     ┌─────┴──────────────┐                 │
│           │         ▼                  │     ▼                    │                 │
│           │  ┌─────────────────┐       │  ┌─────────────────┐     │                 │
│           │  │ RECURRING-SVC   │       │  │ NOTIFICATION-SVC│     │                 │
│           │  │ ┌─────┐ ┌─────┐ │       │  │ ┌─────┐ ┌─────┐ │     │                 │
│           │  │ │ App │◀┼▶Dapr│ │       │  │ │ App │◀┼▶Dapr│ │     │                 │
│           │  │ └─────┘ └─────┘ │       │  │ └─────┘ └─────┘ │     │                 │
│           │  └─────────────────┘       │  └─────────────────┘     │                 │
│           │                            │                          │                 │
│           └────────────────────────────┼──────────────────────────┘                 │
│                                        ▼                                             │
│                               ┌─────────────────┐                                    │
│                               │    NEON DB      │                                    │
│                               │  (PostgreSQL)   │                                    │
│                               └─────────────────┘                                    │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Specifications

### C-001: Backend Service (todo-backend)

**Technology**: FastAPI + Python 3.11
**Port**: 8000
**Dapr App ID**: `todo-backend`

**Responsibilities**:
- Handle chat conversations (NLU to task operations)
- Task CRUD with priorities, tags, due dates
- Publish events to Kafka via Dapr HTTP API
- Background scheduler for reminder polling

**API Endpoints**: See [contracts/api.yaml](./contracts/api.yaml)

**Event Publishing**:
```python
async def publish_task_event(event_type: str, task: Task):
    await httpx.AsyncClient().post(
        f"http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
        json={
            "event_type": event_type,
            "task_id": task.id,
            "task_data": task.model_dump(),
            "user_id": task.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### C-002: Frontend Service (todo-frontend)

**Technology**: Next.js 14 + TypeScript
**Port**: 3000
**Dapr App ID**: `todo-frontend`

**Responsibilities**:
- Chat UI with message history
- Task list with priority colors, tag badges
- Due date highlighting (overdue = red)
- Filter/sort controls

### C-003: Notification Service (notification-service)

**Technology**: FastAPI + Python 3.11
**Port**: 8001
**Dapr App ID**: `notification-service`

**Responsibilities**:
- Subscribe to `reminders` topic via Dapr
- Log notifications (future: email/push)
- Health endpoints

**Subscription**: See [contracts/events.md](./contracts/events.md)

### C-004: Recurring Task Service (recurring-service)

**Technology**: FastAPI + Python 3.11
**Port**: 8002
**Dapr App ID**: `recurring-service`

**Responsibilities**:
- Subscribe to `task-events` topic via Dapr
- Filter for `task.completed` events
- Create next occurrence for recurring tasks
- Call backend API to create new task

**Logic**:
```python
async def handle_task_event(event: CloudEvent):
    data = event.data
    if data["event_type"] != "task.completed":
        return {"status": "IGNORED"}

    task = data["task_data"]
    if task["recurrence"] == "none":
        return {"status": "IGNORED"}

    next_due = calculate_next_due(task["due_date"], task["recurrence"])
    await create_task_via_backend(
        title=task["title"],
        priority=task["priority"],
        tags=task["tags"],
        due_date=next_due,
        recurrence=task["recurrence"],
        parent_task_id=task["id"],
        user_id=data["user_id"]
    )
    return {"status": "SUCCESS"}
```

## Project Structure

### Documentation (this feature)

```text
specs/004-phase5-cloud-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions
├── data-model.md        # Entity schemas
├── quickstart.md        # Developer setup guide
├── contracts/
│   ├── api.yaml         # OpenAPI specification
│   └── events.md        # Kafka event contracts
└── checklists/
    └── requirements.md  # Validation checklist
```

### Source Code (repository root)

```text
phase-5/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── tasks.py          # Task CRUD endpoints
│   │   │   │   ├── chat.py           # Chat endpoint
│   │   │   │   └── health.py         # Health endpoints
│   │   │   └── dependencies.py       # Auth, DB session
│   │   ├── models/
│   │   │   ├── task.py               # Task SQLModel
│   │   │   └── tag.py                # Tag SQLModel
│   │   ├── services/
│   │   │   ├── task_service.py       # Task business logic
│   │   │   ├── event_publisher.py    # Dapr pub/sub client
│   │   │   ├── reminder_scheduler.py # Background reminder polling
│   │   │   └── date_parser.py        # Natural language dates
│   │   ├── core/
│   │   │   ├── config.py             # Settings
│   │   │   └── logging.py            # structlog setup
│   │   └── main.py                   # FastAPI app
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── contract/
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/                      # Next.js App Router
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   ├── tasks/
│   │   │   │   ├── TaskCard.tsx      # With priority, tags, due date
│   │   │   │   └── TaskFilters.tsx   # Filter/sort controls
│   │   │   └── ui/                   # shadcn components
│   │   └── lib/
│   │       └── api.ts                # Backend client
│   ├── package.json
│   └── Dockerfile
│
├── notification-service/
│   ├── src/
│   │   ├── api/
│   │   │   ├── reminders.py          # Event handler
│   │   │   └── health.py
│   │   ├── core/
│   │   │   └── logging.py
│   │   └── main.py
│   ├── pyproject.toml
│   └── Dockerfile
│
├── recurring-service/
│   ├── src/
│   │   ├── api/
│   │   │   ├── events.py             # task-events handler
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── recurrence.py         # Next date calculation
│   │   │   └── backend_client.py     # Create task via API
│   │   ├── core/
│   │   │   └── logging.py
│   │   └── main.py
│   ├── pyproject.toml
│   └── Dockerfile
│
├── helm/
│   ├── todo-chatbot/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-minikube.yaml
│   │   ├── values-staging.yaml
│   │   ├── values-production.yaml
│   │   └── templates/
│   │       ├── namespace.yaml
│   │       └── dapr-components/
│   └── charts/
│       ├── backend/
│       ├── frontend/
│       ├── notification-service/
│       ├── recurring-service/
│       └── kafka/
│
├── dapr/
│   └── components/
│       ├── kafka-pubsub.yaml
│       ├── statestore.yaml
│       ├── secrets.yaml
│       ├── subscription-task-events.yaml
│       └── subscription-reminders.yaml
│
├── .github/
│   └── workflows/
│       ├── ci.yaml                   # Build and test
│       └── deploy.yaml               # Deploy to environments
│
└── scripts/
    ├── deploy-minikube.sh
    └── verify-deployment.sh
```

**Structure Decision**: Microservices architecture with 4 services. Each service has its own Dockerfile and Helm sub-chart. Dapr components are centralized under `/dapr/components/`.

## Dapr Components

### kafka-pubsub.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-cluster-kafka-bootstrap.kafka:9092"
    - name: consumerGroup
      value: "todo-services"
    - name: authType
      value: "none"
```

### statestore.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-credentials
        key: connection-string
```

### secrets.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
```

## Database Schema

See [data-model.md](./data-model.md) for complete schema.

**Summary**:
- Extended `tasks` table with: priority, due_date, remind_at, reminder_sent, recurrence, parent_task_id
- New `tags` table with user-scoped, case-insensitive names
- New `task_tags` junction table for many-to-many relationship
- Indexes on priority, due_date, remind_at, parent_task_id

## Helm Chart Structure

```yaml
# helm/todo-chatbot/Chart.yaml
apiVersion: v2
name: todo-chatbot
description: TaskAI Phase 5
version: 2.0.0
appVersion: "2.0.0"

dependencies:
  - name: backend
    version: "1.0.0"
    repository: "file://./charts/backend"
  - name: frontend
    version: "1.0.0"
    repository: "file://./charts/frontend"
  - name: notification-service
    version: "1.0.0"
    repository: "file://./charts/notification-service"
  - name: recurring-service
    version: "1.0.0"
    repository: "file://./charts/recurring-service"
```

### Values Override Strategy

| File | Service Type | Kafka Broker | Replicas |
|------|--------------|--------------|----------|
| values.yaml | ClusterIP | cluster-internal | 1 |
| values-minikube.yaml | NodePort | strimzi-internal | 1 |
| values-staging.yaml | LoadBalancer | redpanda-cloud | 2 |
| values-production.yaml | LoadBalancer | redpanda-cloud | 3 |

## CI/CD Pipeline

```yaml
# .github/workflows/deploy.yaml
name: Build and Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [backend, frontend, notification-service, recurring-service]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: ./${{ matrix.service }}
          push: true
          tags: ghcr.io/${{ github.repository }}/${{ matrix.service }}:${{ github.sha }}

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: azure/setup-kubectl@v3
      - uses: azure/setup-helm@v3
      - run: |
          helm upgrade --install todo-chatbot ./helm/todo-chatbot \
            -f ./helm/todo-chatbot/values-staging.yaml \
            --set image.tag=${{ github.sha }} \
            --atomic --wait --timeout 10m

  deploy-production:
    needs: build
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: azure/setup-kubectl@v3
      - uses: azure/setup-helm@v3
      - run: |
          helm upgrade --install todo-chatbot ./helm/todo-chatbot \
            -f ./helm/todo-chatbot/values-production.yaml \
            --set image.tag=${{ github.ref_name }} \
            --atomic --wait --timeout 10m
```

## Deployment Sequence

### Minikube (Local)
1. Start Minikube with sufficient resources
2. Initialize Dapr on cluster (`dapr init -k`)
3. Install Strimzi operator and Kafka cluster
4. Create `todo-app` namespace with Dapr injection
5. Apply Dapr components (pubsub, statestore, secrets)
6. Apply Dapr subscriptions
7. Deploy Helm chart with minikube values
8. Run verification script

### Cloud (AKS/GKE/OKE)
1. Create/connect to Kubernetes cluster
2. Initialize Dapr on cluster
3. Configure Redpanda Cloud connection
4. Create namespace with Dapr injection
5. Create Kubernetes secrets for database and Kafka auth
6. Apply Dapr components with cloud config
7. Push to main → CI/CD deploys to staging
8. Create version tag → CI/CD deploys to production

## Complexity Tracking

> No constitution violations requiring justification.

| Item | Decision | Rationale |
|------|----------|-----------|
| 4 microservices | Required | Constitution mandates notification-service and recurring-service separation |
| Database polling for reminders | Chosen over Dapr Jobs API | Dapr Jobs still in alpha; polling is proven pattern |
| Recurring-service calls backend API | vs. direct DB | Maintains single source of truth, avoids shared database |

## Implementation Phases

### Phase 1: Foundation (P1)
- Database migrations for new columns
- Update Task model with priority, due_date, tags
- Backend endpoints for filtering/sorting
- Event publisher service

### Phase 2: Core Features (P1-P2)
- Priority management (set, filter)
- Tag management (add, remove, filter)
- Due date management (natural language parsing)
- Search functionality

### Phase 3: Infrastructure (P1-P2)
- Dapr component configuration
- Kafka cluster setup (Strimzi)
- Event publishing integration
- Background reminder scheduler

### Phase 4: New Services (P2-P3)
- Notification service implementation
- Recurring task service implementation
- Dapr subscriptions

### Phase 5: Deployment (P1-P3)
- Helm charts for all services
- Minikube deployment script
- CI/CD pipeline
- Cloud deployment documentation

## References

- [Specification](./spec.md)
- [Research](./research.md)
- [Data Model](./data-model.md)
- [API Contract](./contracts/api.yaml)
- [Event Contract](./contracts/events.md)
- [Quickstart](./quickstart.md)
- [Constitution](../../.specify/memory/constitution.md)
