# Event Contracts: Phase 5

**Feature**: 004-phase5-cloud-deployment
**Date**: 2025-12-25

## Overview

All events are published via Dapr pub/sub building block. Events follow CloudEvents specification.

---

## Dapr Pub/Sub Configuration

### Component
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
      value: "kafka-cluster-kafka-bootstrap:9092"
    - name: consumerGroup
      value: "todo-services"
    - name: authType
      value: "none"
```

### Publishing (Python)
```python
import httpx

DAPR_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

async def publish(topic: str, data: dict):
    url = f"http://localhost:{DAPR_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
```

### Subscribing (Declarative)
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-sub
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  route: /api/events/task
  scopes:
    - recurring-service
```

---

## Topic: task-events

### Description
Published by backend when task state changes.

### Producers
- `todo-backend`

### Consumers
- `recurring-service` - Creates next occurrence for recurring tasks
- `audit-service` (future) - Logs all task operations

### Event Types

#### task.created
Published when a new task is created.

```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-backend",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "time": "2025-01-15T10:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "task.created",
    "task_id": 123,
    "task_data": {
      "id": 123,
      "title": "Buy groceries",
      "description": null,
      "is_completed": false,
      "priority": "medium",
      "due_date": null,
      "remind_at": null,
      "recurrence": "none",
      "parent_task_id": null,
      "tags": [],
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    },
    "user_id": "user-123",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

#### task.updated
Published when task is modified (title, description, priority, due_date, remind_at, recurrence, tags).

```json
{
  "data": {
    "event_type": "task.updated",
    "task_id": 123,
    "task_data": { /* full task object */ },
    "user_id": "user-123",
    "timestamp": "2025-01-15T10:35:00Z"
  }
}
```

#### task.completed
Published when task is marked complete. **Triggers recurring-service** to create next occurrence.

```json
{
  "data": {
    "event_type": "task.completed",
    "task_id": 123,
    "task_data": {
      "id": 123,
      "title": "Weekly standup",
      "is_completed": true,
      "recurrence": "weekly",
      /* ... */
    },
    "user_id": "user-123",
    "timestamp": "2025-01-15T10:40:00Z"
  }
}
```

#### task.deleted
Published when task is deleted.

```json
{
  "data": {
    "event_type": "task.deleted",
    "task_id": 123,
    "task_data": { /* task state before deletion */ },
    "user_id": "user-123",
    "timestamp": "2025-01-15T10:45:00Z"
  }
}
```

---

## Topic: reminders

### Description
Published by backend when a reminder is due. Consumed by notification-service.

### Producers
- `todo-backend` (via background scheduler)

### Consumers
- `notification-service` - Logs reminder (future: sends email/push)

### Event Schema

```json
{
  "specversion": "1.0",
  "type": "reminder.due",
  "source": "todo-backend",
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "time": "2025-01-15T13:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "title": "Submit report",
    "due_at": "2025-01-15T14:00:00Z",
    "remind_at": "2025-01-15T13:00:00Z",
    "user_id": "user-123"
  }
}
```

### Handler (notification-service)

```python
from cloudevents.http import from_http
from fastapi import Request

@app.post("/api/reminders/handle")
async def handle_reminder(request: Request):
    event = from_http(request.headers, await request.body())
    data = event.data

    logger.info(
        "reminder_received",
        task_id=data["task_id"],
        title=data["title"],
        due_at=data["due_at"],
        user_id=data["user_id"]
    )

    # Future: send email/push notification

    return {"status": "SUCCESS"}
```

---

## Topic: task-updates

### Description
Reserved for future real-time updates via WebSocket. Not consumed in Phase 5.

### Producers
- `todo-backend`

### Consumers
- `websocket-service` (future)

### Event Types
- `task.realtime.created`
- `task.realtime.updated`
- `task.realtime.completed`
- `task.realtime.deleted`

---

## Subscription Configurations

### recurring-service
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: recurring-task-sub
  namespace: todo-app
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  route: /api/events/task
  scopes:
    - recurring-service
```

### notification-service
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: reminder-sub
  namespace: todo-app
spec:
  pubsubname: kafka-pubsub
  topic: reminders
  route: /api/reminders/handle
  scopes:
    - notification-service
```

---

## Error Handling

### Retry Policy
Events are retried automatically by Dapr with exponential backoff:
- Initial delay: 1 second
- Max retries: 3
- Max delay: 30 seconds

### Dead Letter Queue
Failed events after max retries go to `{topic}-dlq` for manual inspection.

### Handler Response Codes
| Code | Meaning | Dapr Action |
|------|---------|-------------|
| 200 | Success | ACK message |
| 400 | Bad request | ACK (don't retry) |
| 500 | Server error | RETRY |
| 503 | Service unavailable | RETRY |

---

## Testing Events

### Publish Test Event (curl)
```bash
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.completed",
    "task_id": 1,
    "task_data": {
      "id": 1,
      "title": "Test task",
      "is_completed": true,
      "recurrence": "weekly"
    },
    "user_id": "test-user",
    "timestamp": "2025-01-15T10:00:00Z"
  }'
```

### Verify Subscription
```bash
# Check Dapr subscriptions
dapr dashboard
# Navigate to Pub/Sub tab

# Or via API
curl http://localhost:3500/v1.0/metadata
```
