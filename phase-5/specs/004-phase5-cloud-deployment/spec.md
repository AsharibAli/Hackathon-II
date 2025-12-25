# Feature Specification: Phase 5 Advanced Cloud Deployment

**Feature Branch**: `004-phase5-cloud-deployment`
**Created**: 2025-12-25
**Status**: Draft
**Input**: Phase 5 Requirements - Event-driven microservices with Dapr, Kafka, and multi-cloud Kubernetes deployment

## Overview

Phase 5 extends the existing TaskAI application (Phase 4 complete with Minikube deployment) into a fully cloud-native, event-driven microservices architecture. This phase introduces:

- Enhanced task features (priorities, tags, due dates, reminders, recurring tasks)
- Event-driven architecture using Kafka via Dapr abstraction
- Two new microservices (notification-service, recurring-service)
- Multi-cloud deployment support (Minikube, AKS, GKE, OKE)
- CI/CD pipeline with GitHub Actions

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Priorities (Priority: P1)

As a user, I want to assign priorities to my tasks so I can focus on what's most important.

**Why this priority**: Priority management is fundamental to task organization and directly impacts user productivity. It's a core enhancement that many users expect from a task management system.

**Independent Test**: Can be tested by creating tasks with different priorities and verifying visual indicators and filtering work correctly.

**Acceptance Scenarios**:

1. **Given** I have a task "Buy groceries", **When** I say "set priority of Buy groceries to high", **Then** the task priority should be "high" and display with a red indicator
2. **Given** I have tasks with different priorities, **When** I say "show high priority tasks", **Then** I should only see tasks with priority "high"
3. **Given** I create a new task without specifying priority, **When** the task is created, **Then** it should have "medium" as the default priority

---

### User Story 2 - Task Tags (Priority: P1)

As a user, I want to add tags to tasks so I can categorize and find them easily.

**Why this priority**: Tags enable flexible categorization that works alongside priorities, essential for organizing tasks across projects or contexts.

**Independent Test**: Can be tested by adding tags to tasks and filtering by tag through chat commands.

**Acceptance Scenarios**:

1. **Given** I have a task "Finish report", **When** I say "add tag work to Finish report", **Then** the task should have tag "work" displayed as a chip/badge
2. **Given** I have tasks with tag "work", **When** I say "show tasks tagged work", **Then** I should only see tasks with that tag
3. **Given** I add tags "Work" and "WORK" to different tasks, **When** I filter by "work", **Then** both tasks should appear (case-insensitive)

---

### User Story 3 - Due Dates & Overdue Tracking (Priority: P1)

As a user, I want to set due dates on tasks so I know when things need to be done, and see which tasks are overdue.

**Why this priority**: Due dates are critical for time-sensitive task management and enable the reminder feature.

**Independent Test**: Can be tested by setting due dates using natural language and verifying overdue highlighting.

**Acceptance Scenarios**:

1. **Given** I have a task "Submit report", **When** I say "set due date of Submit report to next Friday", **Then** the task should have due date of next Friday
2. **Given** I have tasks past their due date, **When** I say "show overdue tasks", **Then** I see only tasks with due_date < today
3. **Given** I have an overdue task, **When** I view the task list, **Then** the overdue task should be visually highlighted (different color/icon)

---

### User Story 4 - Search Tasks (Priority: P2)

As a user, I want to search tasks by keyword so I can quickly find what I'm looking for.

**Why this priority**: Search becomes important as task count grows, but basic filtering by priority/tags covers most immediate needs.

**Independent Test**: Can be tested by creating tasks with specific keywords and verifying search results.

**Acceptance Scenarios**:

1. **Given** I have tasks "Buy groceries" and "Grocery list review", **When** I say "search for grocery", **Then** I should see both tasks in results
2. **Given** I search for a keyword, **When** results are displayed, **Then** matching text should be highlighted
3. **Given** I search for "GROCERY" (uppercase), **When** results are displayed, **Then** I should see all tasks containing "grocery" (case-insensitive)

---

### User Story 5 - Filter & Sort Tasks (Priority: P2)

As a user, I want to filter and sort tasks so I can organize my view.

**Why this priority**: Advanced filtering builds on priorities and tags, enabling power users to create custom views.

**Independent Test**: Can be tested by applying multiple filters and sort options through chat commands.

**Acceptance Scenarios**:

1. **Given** I have various tasks, **When** I say "show high priority pending tasks sorted by due date", **Then** I see only high priority incomplete tasks sorted by due date ascending
2. **Given** I have tasks with different statuses, **When** I say "show completed tasks", **Then** I should only see completed tasks
3. **Given** I have tasks, **When** I say "sort by priority", **Then** tasks should appear with High first, then Medium, then Low

---

### User Story 6 - Reminders (Priority: P2)

As a user, I want to set reminders so I don't forget about important tasks.

**Why this priority**: Reminders depend on due dates and require the event-driven infrastructure to be in place.

**Independent Test**: Can be tested by setting a reminder and verifying the notification service receives the event.

**Acceptance Scenarios**:

1. **Given** I have a task with due date tomorrow at 2pm, **When** I say "remind me about this task 1 hour before", **Then** a reminder should be scheduled for tomorrow at 1pm
2. **Given** a reminder time arrives, **When** the system processes it, **Then** the notification-service should receive and log the reminder event
3. **Given** I set a reminder, **When** I view the task, **Then** I should see the reminder time displayed

---

### User Story 7 - Recurring Tasks (Priority: P3)

As a user, I want tasks to automatically repeat so I don't have to recreate them.

**Why this priority**: Recurring tasks are a power feature that requires the event-driven architecture to work correctly.

**Independent Test**: Can be tested by completing a recurring task and verifying the next occurrence is created.

**Acceptance Scenarios**:

1. **Given** I have a weekly recurring task "Team standup", **When** I complete the task, **Then** a new task should be created for next week with the same title and tags
2. **Given** I have a task, **When** I say "make this task repeat weekly", **Then** the task should be marked as recurring with weekly pattern
3. **Given** a recurring task is completed, **When** the next occurrence is created, **Then** it should link to the original task via parent_task_id

---

### User Story 8 - Event-Driven Architecture (Priority: P1)

As a system operator, I want all inter-service communication to go through Kafka/Dapr so services are loosely coupled and scalable.

**Why this priority**: This is the foundational infrastructure that enables reminders, recurring tasks, and future features.

**Independent Test**: Can be tested by publishing an event and verifying it's consumed by the appropriate service.

**Acceptance Scenarios**:

1. **Given** a task is created/updated/completed/deleted, **When** the operation completes, **Then** an event should be published to the "task-events" topic via Dapr
2. **Given** the backend publishes events, **When** I inspect the code, **Then** there should be no direct Kafka client library usage (only Dapr HTTP API)
3. **Given** an event is published, **When** the consumer service is running, **Then** it should receive and process the event within 2 seconds

---

### User Story 9 - Notification Service (Priority: P2)

As a system operator, I want a dedicated service to handle reminders so the main backend remains focused on task management.

**Why this priority**: Required for the reminder feature to work but can be developed after core event infrastructure.

**Independent Test**: Can be tested by publishing a reminder event and verifying the service logs it.

**Acceptance Scenarios**:

1. **Given** a reminder event is published to "reminders" topic, **When** notification-service is running, **Then** it should consume the event and log the notification
2. **Given** notification-service is deployed, **When** I check its configuration, **Then** it should have a Dapr sidecar enabled
3. **Given** notification-service receives a reminder, **When** it processes it, **Then** it should log the task title, due date, and user ID

---

### User Story 10 - Recurring Task Service (Priority: P3)

As a system operator, I want a dedicated service to handle recurring task creation so the main backend remains focused on task management.

**Why this priority**: Required for recurring tasks feature but depends on event infrastructure being complete.

**Independent Test**: Can be tested by publishing a task.completed event for a recurring task and verifying a new task is created.

**Acceptance Scenarios**:

1. **Given** a task.completed event for a recurring task is published, **When** recurring-service processes it, **Then** a new task occurrence should be created
2. **Given** recurring-service creates a new task, **When** I view the new task, **Then** it should have the same title, tags, and priority as the original
3. **Given** a non-recurring task is completed, **When** the event is published, **Then** recurring-service should ignore it (no new task created)

---

### User Story 11 - Minikube Deployment (Priority: P1)

As a developer, I want to deploy the entire stack to Minikube with a single command so I can test locally.

**Why this priority**: Local development and testing is foundational - developers need this working before cloud deployment.

**Independent Test**: Can be tested by running the deploy script and verifying all services are running.

**Acceptance Scenarios**:

1. **Given** I have Minikube running with Dapr initialized, **When** I run the deploy script, **Then** all services (frontend, backend, notification-service, recurring-service, Kafka) should be deployed
2. **Given** the stack is deployed, **When** I run the verification script, **Then** it should confirm all pods are running and healthy
3. **Given** I deploy to Minikube, **When** I check service types, **Then** they should use NodePort (not LoadBalancer)

---

### User Story 12 - Cloud Deployment (Priority: P3)

As a DevOps engineer, I want to deploy the stack to cloud Kubernetes (AKS/GKE/OKE) using the same Helm charts.

**Why this priority**: Cloud deployment is the ultimate goal but requires local deployment to work first.

**Independent Test**: Can be tested by deploying to a cloud cluster and verifying all services work correctly.

**Acceptance Scenarios**:

1. **Given** I have a cloud Kubernetes cluster, **When** I run Helm install with cloud values, **Then** all services should deploy successfully
2. **Given** I deploy to cloud, **When** I check service types, **Then** they should use LoadBalancer (via values file override)
3. **Given** I deploy to different clouds, **When** I check the application code, **Then** there should be no cloud-provider-specific code

---

### User Story 13 - CI/CD Pipeline (Priority: P3)

As a DevOps engineer, I want automated builds and deployments so releases are consistent and reliable.

**Why this priority**: CI/CD is important for production but can be implemented after manual deployment works.

**Independent Test**: Can be tested by pushing to main and verifying the pipeline builds and deploys correctly.

**Acceptance Scenarios**:

1. **Given** I push to main branch, **When** GitHub Actions runs, **Then** it should build images and deploy to staging
2. **Given** I create a version tag (v*), **When** GitHub Actions runs, **Then** it should deploy to production
3. **Given** a deployment fails, **When** Helm runs with --atomic, **Then** it should automatically rollback to previous version

---

### Edge Cases

- What happens when a user sets a reminder for a past time? (System should reject or immediately trigger)
- What happens when Kafka is temporarily unavailable? (Events should be retried with backoff)
- What happens when a recurring task's next occurrence falls on a weekend? (Keep the calculated date - no smart skipping)
- What happens when a user deletes a recurring task? (Future occurrences should not be created)
- What happens when due date natural language parsing fails? (Return error message suggesting valid formats)
- What happens when search returns no results? (Display friendly "no tasks found" message)
- What happens when notification-service is down when a reminder is due? (Kafka retains message until service recovers)

## Requirements *(mandatory)*

### Functional Requirements - Application Features

#### Task Priorities (F-001)
- **FR-001.1**: Tasks MUST have priority levels: High, Medium, Low
- **FR-001.2**: Default priority MUST be Medium when not specified
- **FR-001.3**: Priority MUST be displayed with visual indicator (red=high, yellow=medium, gray=low)
- **FR-001.4**: Users MUST be able to set priority via chat: "set priority of [task] to [level]"
- **FR-001.5**: Users MUST be able to filter by priority via chat: "show [level] priority tasks"

#### Task Tags (F-002)
- **FR-002.1**: Tasks MUST support multiple tags
- **FR-002.2**: Tags MUST be case-insensitive for filtering
- **FR-002.3**: Users MUST be able to add tags via chat: "add tag [tag] to [task]"
- **FR-002.4**: Users MUST be able to filter by tag via chat: "show tasks tagged [tag]"
- **FR-002.5**: Tags MUST be displayed as chips/badges on task cards

#### Search (F-003)
- **FR-003.1**: Search MUST match partial text in task titles
- **FR-003.2**: Search MUST match partial text in task descriptions
- **FR-003.3**: Search MUST be case-insensitive
- **FR-003.4**: Users MUST be able to search via chat: "search for [keyword]"
- **FR-003.5**: Search results MUST highlight matching text

#### Filter & Sort (F-004)
- **FR-004.1**: Users MUST be able to filter by: status (completed/pending), priority, tags, due date presence
- **FR-004.2**: Users MUST be able to sort by: created date, due date, priority, title
- **FR-004.3**: Users MUST be able to combine filters via chat: "show [filter1] [filter2] tasks sorted by [field]"
- **FR-004.4**: Default sort order MUST be by created date descending

#### Due Dates (F-005)
- **FR-005.1**: Tasks MUST support optional due date
- **FR-005.2**: Due dates MUST support natural language input: "tomorrow", "next Monday", "in 3 days"
- **FR-005.3**: Users MUST be able to set due date via chat: "set due date of [task] to [date]"
- **FR-005.4**: Overdue tasks MUST be visually highlighted with distinct styling
- **FR-005.5**: Users MUST be able to filter overdue tasks via chat: "show overdue tasks"

#### Reminders (F-006)
- **FR-006.1**: Users MUST be able to set reminder time relative to due date or as absolute time
- **FR-006.2**: Users MUST be able to set reminders via chat: "remind me about [task] [time specification]"
- **FR-006.3**: Reminders MUST be published to Kafka topic "reminders" via Dapr
- **FR-006.4**: Notification service MUST consume reminders and log them (email/push is future scope)
- **FR-006.5**: Reminder scheduling MUST use Dapr Jobs API or similar scheduling mechanism

#### Recurring Tasks (F-007)
- **FR-007.1**: Tasks MUST support recurrence patterns: daily, weekly, monthly, none
- **FR-007.2**: Users MUST be able to set recurrence via chat: "make this task repeat [pattern]"
- **FR-007.3**: When a recurring task is completed, a task.completed event MUST be published to Kafka
- **FR-007.4**: Recurring-service MUST create the next occurrence when it receives task.completed for recurring tasks
- **FR-007.5**: New occurrences MUST link to the original task via parent_task_id and inherit title, tags, priority

### Functional Requirements - Infrastructure

#### Kafka Integration via Dapr (F-008)
- **FR-008.1**: Backend MUST publish events via Dapr HTTP API (POST to /v1.0/publish/{pubsub}/{topic})
- **FR-008.2**: System MUST use topics: task-events, reminders, task-updates
- **FR-008.3**: Application code MUST NOT contain direct Kafka client library imports
- **FR-008.4**: Dapr components MUST be configured for Kafka/Redpanda

#### Notification Service (F-009)
- **FR-009.1**: Notification service MUST be a separate Python/FastAPI microservice
- **FR-009.2**: Notification service MUST subscribe to "reminders" topic via Dapr
- **FR-009.3**: Notification service MUST log all received reminders with structured JSON
- **FR-009.4**: Notification service MUST have Dapr sidecar enabled in Kubernetes deployment
- **FR-009.5**: Notification service MUST have its own Helm chart for deployment

#### Recurring Task Service (F-010)
- **FR-010.1**: Recurring service MUST be a separate Python/FastAPI microservice
- **FR-010.2**: Recurring service MUST subscribe to "task-events" topic via Dapr
- **FR-010.3**: Recurring service MUST filter for task.completed events only
- **FR-010.4**: Recurring service MUST create next occurrence via backend API or direct database access
- **FR-010.5**: Recurring service MUST have Dapr sidecar enabled in Kubernetes deployment

#### Minikube Deployment (F-011)
- **FR-011.1**: All services MUST deploy to Minikube successfully
- **FR-011.2**: Kafka MUST be deployed via Strimzi operator or Redpanda
- **FR-011.3**: Dapr MUST be initialized on the cluster before service deployment
- **FR-011.4**: A single deploy script MUST deploy the complete stack
- **FR-011.5**: A verification script MUST confirm all services are running and healthy

#### Cloud Deployment (F-012)
- **FR-012.1**: Helm charts MUST work on AKS, GKE, and OKE without modification
- **FR-012.2**: Cloud Kafka MUST be configurable via Helm values (Redpanda Cloud, Confluent, etc.)
- **FR-012.3**: CI/CD MUST be implemented via GitHub Actions
- **FR-012.4**: Environment-specific configuration MUST be in separate values files
- **FR-012.5**: Cloud deployments MUST have monitoring and logging configured

#### CI/CD Pipeline (F-013)
- **FR-013.1**: Pipeline MUST build and push container images on push to main
- **FR-013.2**: Pipeline MUST deploy to staging on main branch pushes
- **FR-013.3**: Pipeline MUST deploy to production on version tag creation (v*)
- **FR-013.4**: Helm upgrade MUST use --atomic flag for automatic rollback on failure
- **FR-013.5**: Pipeline MUST send notifications on deployment (Slack/Discord webhook)

### Key Entities

- **Task**: Core entity with id, title, description, is_completed, created_at, updated_at, user_id. Extended with: priority (enum: high/medium/low), due_date (optional datetime), reminder_at (optional datetime), recurrence_pattern (enum: none/daily/weekly/monthly), parent_task_id (optional reference to original recurring task)

- **Tag**: Represents a label for categorization with id, name (lowercase stored), created_at. Many-to-many relationship with Task.

- **TaskTag**: Junction table linking Task and Tag with task_id, tag_id.

- **TaskEvent**: Represents an event published to Kafka with event_type (created/updated/completed/deleted), task_id, task_data (full task JSON), user_id, timestamp.

- **ReminderEvent**: Represents a scheduled reminder with task_id, title, due_at, remind_at, user_id.

## Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | API response time MUST be < 500ms at p95 |
| NFR-002 | Performance | Event processing latency MUST be < 2 seconds |
| NFR-003 | Availability | Cloud deployment MUST achieve 99.5% uptime |
| NFR-004 | Security | All secrets MUST be stored in Kubernetes secrets or Dapr secret stores |
| NFR-005 | Security | No secrets MUST appear in code or ConfigMaps |
| NFR-006 | Observability | All services MUST use structured JSON logging |
| NFR-007 | Observability | All services MUST expose /health and /ready endpoints |
| NFR-008 | Scalability | Each microservice MUST be independently scalable |
| NFR-009 | Reliability | All services MUST handle graceful shutdown |
| NFR-010 | Portability | Application code MUST NOT contain cloud-provider-specific logic |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can set task priorities and filter by priority within 3 seconds of issuing the command
- **SC-002**: Users can add/remove tags and filter by tags within 3 seconds of issuing the command
- **SC-003**: Users can search tasks and see results within 2 seconds for up to 1000 tasks
- **SC-004**: Users can set due dates using natural language with 95% accuracy for common phrases
- **SC-005**: Reminders are delivered to notification-service within 5 seconds of scheduled time
- **SC-006**: Recurring task next occurrence is created within 5 seconds of completing the previous task
- **SC-007**: Full stack deploys to Minikube in under 10 minutes with single command
- **SC-008**: Full stack deploys to cloud Kubernetes in under 15 minutes via CI/CD
- **SC-009**: System handles 100 concurrent users without performance degradation
- **SC-010**: Event processing completes within 2 seconds end-to-end
- **SC-011**: Zero direct Kafka client library usage in application code (Dapr abstraction only)
- **SC-012**: Same Helm charts work on Minikube, AKS, GKE, and OKE with only values file changes

## Event Schemas

### task-events Topic

```json
{
  "event_type": "task.created | task.updated | task.completed | task.deleted",
  "task_id": 123,
  "task_data": {
    "id": 123,
    "title": "Task title",
    "description": "Task description",
    "is_completed": false,
    "priority": "high",
    "due_date": "2025-01-15T14:00:00Z",
    "reminder_at": "2025-01-15T13:00:00Z",
    "recurrence_pattern": "weekly",
    "parent_task_id": null,
    "tags": ["work", "urgent"],
    "created_at": "2025-01-10T10:00:00Z",
    "updated_at": "2025-01-10T10:00:00Z"
  },
  "user_id": "user-123",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### reminders Topic

```json
{
  "task_id": 123,
  "title": "Submit report",
  "due_at": "2025-01-15T14:00:00Z",
  "remind_at": "2025-01-15T13:00:00Z",
  "user_id": "user-123"
}
```

## Assumptions

- Phase 4 Minikube deployment is complete and working as the foundation
- Neon PostgreSQL is used as the database (existing from Phase 4)
- Better Auth with JWT is already implemented (from Phase 4)
- Frontend uses Next.js 14+ with shadcn/ui (from Phase 4)
- Backend uses FastAPI with SQLModel (from Phase 4)
- Natural language date parsing will use a standard library (dateparser or similar)
- Kafka/Redpanda will be deployed within the Kubernetes cluster for Minikube
- Cloud Kafka (Redpanda Cloud, Confluent) will be used for cloud deployments
- Email/push notifications are out of scope for Phase 5 (notification-service only logs)

## Out of Scope

- Email and push notification delivery (notification-service logs only)
- Task attachments and file uploads
- Collaborative task sharing between users
- Mobile native applications
- Real-time WebSocket updates (task-updates topic prepared but not consumed)
- Advanced recurrence patterns (e.g., "every 2nd Tuesday")
- Task subtasks/checklists
- Time zone handling beyond UTC storage
