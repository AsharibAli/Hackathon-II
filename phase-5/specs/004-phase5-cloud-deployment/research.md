# Research: Phase 5 Advanced Cloud Deployment

**Feature**: 004-phase5-cloud-deployment
**Date**: 2025-12-25
**Status**: Complete

## Research Summary

This document captures technology decisions, patterns, and best practices research for Phase 5 implementation.

---

## R-001: Dapr Pub/Sub with Kafka

### Decision
Use Dapr's pub/sub building block with Kafka as the underlying message broker.

### Rationale
- **Abstraction**: Application code uses simple HTTP POST to Dapr sidecar (`http://localhost:3500/v1.0/publish/{pubsub}/{topic}`)
- **No client libraries**: Zero Kafka client dependencies in application code
- **Portability**: Can swap Kafka for Redis Streams, RabbitMQ, or cloud pub/sub by changing only Dapr component YAML
- **CloudEvents**: Dapr wraps messages in CloudEvents format for interoperability

### Implementation Pattern
```python
# Publishing events via Dapr (FastAPI)
import httpx

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

async def publish_event(topic: str, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}",
            json=data
        )
        response.raise_for_status()
```

### Alternatives Considered
| Alternative | Rejected Because |
|------------|------------------|
| Direct kafka-python | Violates constitution principle II (Dapr Abstraction) |
| confluent-kafka | Same as above, plus heavier dependency |
| Redis pub/sub only | Doesn't support persistence/replay needed for reliability |

---

## R-002: Dapr Subscription Configuration

### Decision
Use declarative subscription via Kubernetes Subscription CRD, not programmatic subscription.

### Rationale
- **GitOps friendly**: Subscriptions defined as YAML, version controlled
- **Separation of concerns**: App doesn't need to know pub/sub implementation
- **Easier debugging**: kubectl can inspect subscription state

### Implementation Pattern
```yaml
# Subscription CRD
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  route: /api/events/task
  scopes:
    - recurring-service
```

### Alternatives Considered
| Alternative | Rejected Because |
|------------|------------------|
| Programmatic subscription | Couples app to Dapr SDK |
| /dapr/subscribe endpoint | Less flexible, harder to update |

---

## R-003: Kafka Deployment Strategy

### Decision
Use Strimzi Kafka Operator for Minikube, Redpanda Cloud for cloud deployments.

### Rationale
- **Strimzi**: Production-ready Kafka on Kubernetes, handles ZooKeeper/KRaft complexity
- **Redpanda Cloud**: Managed Kafka-compatible service, reduces operational burden
- **Helm abstraction**: Same Helm chart, different values files select the broker

### Minikube Configuration
```yaml
# Minimal Kafka cluster via Strimzi
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
spec:
  kafka:
    version: 3.6.0
    replicas: 1  # Single node for local dev
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
```

### Alternatives Considered
| Alternative | Rejected Because |
|------------|------------------|
| Confluent Platform | Heavier, more complex for local dev |
| Redpanda everywhere | Less battle-tested than Strimzi for production |
| NATS/JetStream | Not Kafka-compatible, would need different Dapr config |

---

## R-004: Natural Language Date Parsing

### Decision
Use `python-dateutil` with `dateparser` as fallback for complex natural language.

### Rationale
- **dateutil**: Standard library adjacent, handles "next Monday", "tomorrow" well
- **dateparser**: Handles more complex phrases like "in 3 days", "next Friday at 2pm"
- **Timezone**: Store all dates in UTC, convert on display

### Implementation Pattern
```python
import dateparser
from datetime import datetime, timezone

def parse_natural_date(text: str) -> datetime | None:
    settings = {
        'TIMEZONE': 'UTC',
        'RETURN_AS_TIMEZONE_AWARE': True,
        'PREFER_DATES_FROM': 'future'
    }
    return dateparser.parse(text, settings=settings)
```

### Alternatives Considered
| Alternative | Rejected Because |
|------------|------------------|
| parsedatetime | Less accurate for complex phrases |
| Custom regex | Maintenance burden, limited coverage |
| LLM parsing | Overkill for date parsing, adds latency |

---

## R-005: Recurring Task Service Architecture

### Decision
Recurring service creates tasks via HTTP call to backend API, not direct database access.

### Rationale
- **Single source of truth**: Backend owns task business logic
- **Event publishing**: Backend publishes task.created event automatically
- **Validation**: Backend validates task data consistently
- **Simpler microservice**: Recurring service doesn't need DB credentials

### Flow
```
1. Backend publishes task.completed to task-events
2. Recurring service receives via Dapr subscription
3. Recurring service filters: if recurrence != "none"
4. Recurring service calculates next due date
5. Recurring service POSTs to backend /api/tasks
6. Backend creates task and publishes task.created
```

### Alternatives Considered
| Alternative | Rejected Because |
|------------|------------------|
| Direct DB access | Violates microservices separation, duplicates logic |
| Shared database | Constitution prohibits except during migration |
| Saga pattern | Overkill for simple task creation |

---

## R-006: Reminder Scheduling

### Decision
Use database polling with scheduled background task instead of Dapr Jobs API.

### Rationale
- **Dapr Jobs API**: Still in alpha, not production ready
- **Database polling**: Simple, reliable, auditable
- **APScheduler**: Mature Python library for background scheduling

### Implementation Pattern
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=1)
async def check_reminders():
    now = datetime.utcnow()
    # Find tasks where remind_at <= now and reminder_sent = false
    tasks = await get_pending_reminders(now)
    for task in tasks:
        await publish_reminder_event(task)
        await mark_reminder_sent(task.id)
```

### Alternatives Considered
| Alternative | Rejected Because |
|------------|------------------|
| Dapr Jobs API | Alpha status, limited documentation |
| Celery + Redis | Adds infrastructure complexity |
| Kubernetes CronJob | Too coarse grained (min 1 minute), no dynamic scheduling |

---

## R-007: Helm Chart Structure

### Decision
Use umbrella chart pattern with sub-charts for each service.

### Rationale
- **Single command deployment**: `helm install todo-chatbot ./helm/todo-chatbot`
- **Override per environment**: Values files for minikube, staging, production
- **Independent updates**: Can upgrade individual sub-charts
- **Dependency management**: Chart.yaml declares dependencies

### Structure
```
helm/todo-chatbot/
├── Chart.yaml
├── values.yaml
├── values-minikube.yaml
├── values-staging.yaml
├── values-production.yaml
├── charts/
│   ├── backend/
│   ├── frontend/
│   ├── notification-service/
│   ├── recurring-service/
│   └── kafka/
└── templates/
    ├── namespace.yaml
    └── dapr-components/
```

### Alternatives Considered
| Alternative | Rejected Because |
|------------|------------------|
| Kustomize only | Less parameterization capability |
| Separate Helm releases | More complex deployment orchestration |
| Raw manifests | No templating, harder to maintain |

---

## R-008: CI/CD Pipeline Design

### Decision
GitHub Actions with matrix builds for multi-architecture images.

### Rationale
- **Native GitHub integration**: PRs, tags, and branches trigger workflows
- **GHCR for images**: Free for public repos, integrated auth
- **Matrix builds**: Build amd64 and arm64 in parallel
- **Atomic Helm**: `--atomic` flag for automatic rollback

### Workflow Structure
```yaml
jobs:
  build:
    strategy:
      matrix:
        service: [backend, frontend, notification-service, recurring-service]
    steps:
      - Build and push ${{ matrix.service }}

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'

  deploy-production:
    needs: build
    if: startsWith(github.ref, 'refs/tags/v')
```

### Alternatives Considered
| Alternative | Rejected Because |
|------------|------------------|
| GitLab CI | Not specified in constitution |
| ArgoCD | Adds operational complexity for this scale |
| Jenkins | Older, more maintenance burden |

---

## R-009: Database Schema Migration

### Decision
Extend existing Task model with new columns using Alembic migrations.

### Rationale
- **Non-breaking**: Add nullable columns first
- **Reversible**: Each migration has upgrade and downgrade
- **Existing data**: Default values for existing rows

### Migration Script (Example)
```python
# alembic/versions/xxx_add_phase5_columns.py
def upgrade():
    op.add_column('tasks', sa.Column('priority', sa.String(10), default='medium'))
    op.add_column('tasks', sa.Column('tags', sa.ARRAY(sa.String), nullable=True))
    op.add_column('tasks', sa.Column('due_date', sa.DateTime, nullable=True))
    op.add_column('tasks', sa.Column('remind_at', sa.DateTime, nullable=True))
    op.add_column('tasks', sa.Column('reminder_sent', sa.Boolean, default=False))
    op.add_column('tasks', sa.Column('recurrence', sa.String(10), default='none'))
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer, nullable=True))

    # Indexes
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
```

---

## R-010: Structured Logging

### Decision
Use `structlog` for JSON logging across all Python services.

### Rationale
- **JSON format**: Easy parsing by log aggregators
- **Context binding**: Add request IDs, user IDs to all logs
- **Performance**: Lazy formatting, minimal overhead

### Implementation Pattern
```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

async def some_endpoint():
    log = logger.bind(user_id=current_user.id, request_id=request.state.request_id)
    log.info("processing_request", action="list_tasks")
```

---

## Summary

All technology decisions align with constitution principles:
- ✅ Event-Driven First: Dapr pub/sub with Kafka
- ✅ Dapr Abstraction: No direct Kafka libraries
- ✅ Cloud-Native Portability: Helm values per environment
- ✅ Database Persistence: Alembic migrations
- ✅ Observability: structlog JSON logging
- ✅ Stateless Architecture: No in-memory state, scheduler polls DB
