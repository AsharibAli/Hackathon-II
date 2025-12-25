# Tasks: Phase 5 Advanced Cloud Deployment

**Input**: Design documents from `/specs/004-phase5-cloud-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are included where independently testable verification is needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Notification Service**: `notification-service/src/`
- **Recurring Service**: `recurring-service/src/`
- **Helm Charts**: `helm/`
- **Dapr Components**: `dapr/components/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and infrastructure configuration

- [x] T001 Create Phase 5 project structure with new service directories per plan.md
- [x] T002 [P] Initialize notification-service with FastAPI scaffold in notification-service/
- [x] T003 [P] Initialize recurring-service with FastAPI scaffold in recurring-service/
- [x] T004 [P] Create Dapr pubsub.kafka component in dapr/components/kafka-pubsub.yaml
- [x] T005 [P] Create Dapr state.postgresql component in dapr/components/statestore.yaml
- [x] T006 [P] Create Dapr secretstores.kubernetes component in dapr/components/secrets.yaml
- [x] T007 [P] Create Dapr subscription for task-events in dapr/components/subscription-task-events.yaml
- [x] T008 [P] Create Dapr subscription for reminders in dapr/components/subscription-reminders.yaml
- [x] T009 Add dateparser dependency to backend/pyproject.toml
- [x] T010 Add httpx dependency to backend/pyproject.toml for Dapr HTTP calls

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 Create Alembic migration for Phase 5 Task model columns in backend/alembic/versions/
- [x] T012 [P] Update Task SQLModel with priority field (enum: low/medium/high, default: medium) in backend/src/models/task.py
- [x] T013 [P] Update Task SQLModel with due_date field (optional datetime) in backend/src/models/task.py
- [x] T014 [P] Update Task SQLModel with remind_at field (optional datetime) in backend/src/models/task.py
- [x] T015 [P] Update Task SQLModel with reminder_sent field (boolean, default: false) in backend/src/models/task.py
- [x] T016 [P] Update Task SQLModel with recurrence field (enum: none/daily/weekly/monthly, default: none) in backend/src/models/task.py
- [x] T017 [P] Update Task SQLModel with parent_task_id field (optional FK to tasks) in backend/src/models/task.py
- [x] T018 Create Tag SQLModel with name, user_id, created_at in backend/src/models/tag.py
- [x] T019 Create TaskTag junction model in backend/src/models/task_tag.py
- [x] T020 Update TaskCreate Pydantic schema with new fields in backend/src/schemas/task.py
- [x] T021 Update TaskUpdate Pydantic schema with new fields in backend/src/schemas/task.py
- [x] T022 Update TaskResponse Pydantic schema with new fields in backend/src/schemas/task.py
- [x] T023 Create EventPublisher class using httpx to call Dapr sidecar in backend/src/services/event_publisher.py
- [x] T024 Create TaskEvent and ReminderEvent Pydantic schemas in backend/src/schemas/events.py
- [x] T025 Create date_parser utility with natural language support in backend/src/utils/date_parser.py
- [ ] T026 Run Alembic migration to apply Phase 5 schema changes
- [x] T027 Create /health and /ready endpoints in backend/src/api/health.py
- [x] T028 [P] Create /health and /ready endpoints in notification-service/src/api/health.py
- [x] T029 [P] Create /health and /ready endpoints in recurring-service/src/api/health.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Priorities (Priority: P1)

**Goal**: Users can assign and filter tasks by priority (high/medium/low)

**Independent Test**: Create tasks with different priorities, verify visual indicators and filtering work

### Implementation for User Story 1

- [x] T030 [US1] Update task_service.py to handle priority on create/update in backend/src/services/tasks.py
- [x] T031 [US1] Add priority filter parameter to GET /api/tasks endpoint in backend/src/api/tasks.py
- [x] T032 [US1] Implement priority filtering in TasksService in backend/src/services/tasks.py
- [ ] T033 [US1] Add set_priority MCP tool to handle "set priority of X to high" in backend/src/mcp/tools/task_tools.py
- [ ] T034 [US1] Add filter_by_priority MCP tool to handle "show high priority tasks" in backend/src/mcp/tools/task_tools.py
- [ ] T035 [US1] Update TaskCard component with priority color indicators in frontend/src/components/tasks/TaskCard.tsx
- [ ] T036 [US1] Add priority filter dropdown to TaskFilters component in frontend/src/components/tasks/TaskFilters.tsx

**Checkpoint**: User Story 1 fully functional - users can set and filter by priority

---

## Phase 4: User Story 2 - Task Tags (Priority: P1)

**Goal**: Users can add/remove tags and filter tasks by tag

**Independent Test**: Add tags to tasks, verify chips display and filtering works

### Implementation for User Story 2

- [x] T037 [US2] Create tag handling in TasksService in backend/src/services/tasks.py
- [x] T038 [US2] Add POST /api/tasks/{id}/tags endpoint to add tag in backend/src/api/tasks.py
- [x] T039 [US2] Add DELETE /api/tasks/{id}/tags/{tag_name} endpoint to remove tag in backend/src/api/tasks.py
- [x] T040 [US2] Add tag filter parameter to GET /api/tasks endpoint in backend/src/api/tasks.py
- [x] T041 [US2] Implement tag filtering (case-insensitive) in TasksService in backend/src/services/tasks.py
- [ ] T042 [US2] Add add_tag MCP tool to handle "add tag work to X" in backend/src/mcp/tools/task_tools.py
- [ ] T043 [US2] Add filter_by_tag MCP tool to handle "show tasks tagged work" in backend/src/mcp/tools/task_tools.py
- [ ] T044 [US2] Create TagChip component for displaying tags in frontend/src/components/tasks/TagChip.tsx
- [ ] T045 [US2] Update TaskCard to display tags as chips in frontend/src/components/tasks/TaskCard.tsx
- [ ] T046 [US2] Add tag filter input to TaskFilters component in frontend/src/components/tasks/TaskFilters.tsx

**Checkpoint**: User Story 2 fully functional - users can manage and filter by tags

---

## Phase 5: User Story 3 - Due Dates (Priority: P1)

**Goal**: Users can set due dates with natural language and see overdue highlighting

**Independent Test**: Set due dates using "tomorrow", "next Friday", verify overdue styling

### Implementation for User Story 3

- [x] T047 [US3] Integrate date_parser into task creation/update flow in backend/src/services/tasks.py
- [x] T048 [US3] Add due_date parameter to task create/update endpoints in backend/src/api/tasks.py
- [x] T049 [US3] Add overdue filter parameter to GET /api/tasks endpoint in backend/src/api/tasks.py
- [x] T050 [US3] Implement overdue filtering logic in TasksService in backend/src/services/tasks.py
- [ ] T051 [US3] Add set_due_date MCP tool with natural language parsing in backend/src/mcp/tools/task_tools.py
- [ ] T052 [US3] Add show_overdue MCP tool to handle "show overdue tasks" in backend/src/mcp/tools/task_tools.py
- [ ] T053 [US3] Update TaskCard with due date display and overdue styling in frontend/src/components/tasks/TaskCard.tsx
- [ ] T054 [US3] Add overdue filter toggle to TaskFilters in frontend/src/components/tasks/TaskFilters.tsx

**Checkpoint**: User Story 3 fully functional - users can set due dates and see overdue tasks

---

## Phase 6: User Story 4 - Search Tasks (Priority: P2)

**Goal**: Users can search tasks by keyword in title and description

**Independent Test**: Create tasks with specific keywords, verify search returns matches

### Implementation for User Story 4

- [x] T055 [US4] Create GET /api/tasks/search endpoint with q parameter in backend/src/api/tasks.py
- [x] T056 [US4] Implement case-insensitive partial match search in TasksService in backend/src/services/tasks.py
- [ ] T057 [US4] Add search MCP tool to handle "search for grocery" in backend/src/mcp/tools/task_tools.py
- [ ] T058 [US4] Create SearchBar component for task search in frontend/src/components/tasks/SearchBar.tsx
- [ ] T059 [US4] Add search result highlighting utility in frontend/src/lib/highlight.ts
- [ ] T060 [US4] Integrate SearchBar into task list view in frontend/src/app/tasks/page.tsx

**Checkpoint**: User Story 4 fully functional - users can search tasks by keyword

---

## Phase 7: User Story 5 - Filter & Sort (Priority: P2)

**Goal**: Users can combine multiple filters and sort tasks

**Independent Test**: Apply combined filters, verify correct results and sort order

### Implementation for User Story 5

- [x] T061 [US5] Add sort_by and sort_order parameters to GET /api/tasks in backend/src/api/tasks.py
- [x] T062 [US5] Implement multi-filter combination logic in TasksService in backend/src/services/tasks.py
- [x] T063 [US5] Implement sorting by created_at, due_date, priority, title in TasksService in backend/src/services/tasks.py
- [ ] T064 [US5] Add combined_filter MCP tool for complex queries in backend/src/mcp/tools/task_tools.py
- [ ] T065 [US5] Add sort_tasks MCP tool for "sort by due date" in backend/src/mcp/tools/task_tools.py
- [ ] T066 [US5] Add sort dropdown to TaskFilters component in frontend/src/components/tasks/TaskFilters.tsx
- [ ] T067 [US5] Update task list to support multiple active filters in frontend/src/app/tasks/page.tsx

**Checkpoint**: User Story 5 fully functional - users can combine filters and sort

---

## Phase 8: User Story 6 - Reminders (Priority: P2)

**Goal**: Users can set reminders that trigger notification events

**Independent Test**: Set reminder, verify event published when reminder time arrives

### Implementation for User Story 6

- [ ] T068 [US6] Create reminder_scheduler service with background polling in backend/src/services/reminder_scheduler.py
- [x] T069 [US6] Add POST /api/tasks/{id}/reminder endpoint in backend/src/api/tasks.py
- [ ] T070 [US6] Implement check_pending_reminders job that publishes to reminders topic in backend/src/services/reminder_scheduler.py
- [ ] T071 [US6] Add set_reminder MCP tool for "remind me about X 1 hour before" in backend/src/mcp/tools/task_tools.py
- [x] T072 [US6] Create reminder event handler endpoint in notification-service/src/api/reminders.py
- [ ] T073 [US6] Implement reminder logging with structured JSON in notification-service/src/handlers/reminder_handler.py
- [ ] T074 [US6] Update TaskCard to show reminder time if set in frontend/src/components/tasks/TaskCard.tsx
- [ ] T075 [US6] Integrate reminder_scheduler into FastAPI lifespan in backend/src/main.py

**Checkpoint**: User Story 6 fully functional - reminders are scheduled and notification-service receives events

---

## Phase 9: User Story 7 - Recurring Tasks (Priority: P3)

**Goal**: Completed recurring tasks automatically create next occurrence

**Independent Test**: Complete recurring task, verify new task created for next period

### Implementation for User Story 7

- [x] T076 [US7] Add recurrence field handling to task create/update in backend/src/services/tasks.py
- [x] T077 [US7] Integrate event publisher on task completion in backend/src/services/tasks.py
- [ ] T078 [US7] Add set_recurrence MCP tool for "make this repeat weekly" in backend/src/mcp/tools/task_tools.py
- [x] T079 [US7] Create task event handler endpoint in recurring-service/src/api/events.py
- [x] T080 [US7] Create recurrence calculation service in recurring-service/src/services/recurrence.py
- [x] T081 [US7] Create backend client to create tasks via API in recurring-service/src/services/backend_client.py
- [ ] T082 [US7] Implement handle_task_completed logic in recurring-service/src/handlers/task_event_handler.py
- [ ] T083 [US7] Update TaskCard to show recurrence indicator in frontend/src/components/tasks/TaskCard.tsx
- [ ] T084 [US7] Add recurrence selector to task edit form in frontend/src/components/tasks/TaskForm.tsx

**Checkpoint**: User Story 7 fully functional - recurring tasks create next occurrence on completion

---

## Phase 10: User Story 8 - Event Infrastructure (Priority: P1)

**Goal**: All task operations publish events to Kafka via Dapr

**Independent Test**: Create/update/complete/delete task, verify events in Kafka topics

### Implementation for User Story 8

- [x] T085 [US8] Integrate EventPublisher.publish() on task create in backend/src/services/tasks.py
- [x] T086 [US8] Integrate EventPublisher.publish() on task update in backend/src/services/tasks.py
- [x] T087 [US8] Integrate EventPublisher.publish() on task complete in backend/src/services/tasks.py
- [x] T088 [US8] Integrate EventPublisher.publish() on task delete in backend/src/services/tasks.py
- [x] T089 [US8] Add DAPR_ENABLED config flag with fallback to logging in backend/src/core/config.py
- [ ] T090 [US8] Verify event publishing with Dapr dashboard during local testing

**Checkpoint**: User Story 8 fully functional - all task events flow through Kafka/Dapr

---

## Phase 11: User Story 9 - Notification Service (Priority: P2)

**Goal**: Notification service consumes reminder events and logs them

**Independent Test**: Publish reminder event, verify service logs notification details

### Implementation for User Story 9

- [x] T091 [US9] Complete notification-service FastAPI app structure in notification-service/src/main.py
- [ ] T092 [US9] Implement CloudEvent parsing for Dapr subscription in notification-service/src/handlers/reminder_handler.py
- [x] T093 [US9] Configure structlog JSON logging in notification-service/src/core/logging.py
- [x] T094 [US9] Create Dockerfile for notification-service in notification-service/Dockerfile
- [x] T095 [US9] Create pyproject.toml with dependencies in notification-service/pyproject.toml

**Checkpoint**: User Story 9 fully functional - notification service receives and logs reminders

---

## Phase 12: User Story 10 - Recurring Service (Priority: P3)

**Goal**: Recurring service creates next occurrence when recurring task completed

**Independent Test**: Publish task.completed for recurring task, verify new task created

### Implementation for User Story 10

- [x] T096 [US10] Complete recurring-service FastAPI app structure in recurring-service/src/main.py
- [ ] T097 [US10] Implement CloudEvent parsing and filtering in recurring-service/src/handlers/task_event_handler.py
- [x] T098 [US10] Configure structlog JSON logging in recurring-service/src/core/logging.py
- [x] T099 [US10] Create Dockerfile for recurring-service in recurring-service/Dockerfile
- [x] T100 [US10] Create pyproject.toml with dependencies in recurring-service/pyproject.toml

**Checkpoint**: User Story 10 fully functional - recurring service creates next task occurrences

---

## Phase 13: User Story 11 - Minikube Deployment (Priority: P1)

**Goal**: Full stack deploys to Minikube with single command

**Independent Test**: Run deploy script, verify all pods running and healthy

### Implementation for User Story 11

- [x] T101 [US11] Create Helm chart for backend service in helm/charts/backend/
- [x] T102 [US11] Create Helm chart for frontend service in helm/charts/frontend/
- [x] T103 [US11] Create Helm chart for notification-service in helm/charts/notification-service/
- [x] T104 [US11] Create Helm chart for recurring-service in helm/charts/recurring-service/
- [x] T105 [US11] Create parent Helm chart (umbrella) in helm/todo-chatbot/Chart.yaml
- [x] T106 [US11] Create values.yaml with defaults in helm/todo-chatbot/values.yaml
- [x] T107 [US11] Create values-minikube.yaml with NodePort config in helm/todo-chatbot/values-minikube.yaml
- [x] T108 [US11] Add Dapr annotations to all deployment templates in helm/charts/*/templates/deployment.yaml
- [x] T109 [US11] Create Strimzi Kafka cluster manifest in infra/minikube/kafka-cluster.yaml
- [x] T110 [US11] Create deploy-minikube.ps1 script in scripts/deploy-minikube.ps1
- [x] T111 [US11] Create verify-deployment.ps1 script in scripts/verify-deployment.ps1

**Checkpoint**: User Story 11 fully functional - single command deploys full stack to Minikube

---

## Phase 14: User Story 12 - Cloud Deployment (Priority: P3)

**Goal**: Helm charts work on AKS/GKE/OKE with values file changes

**Independent Test**: Deploy to cloud cluster, verify all services accessible

### Implementation for User Story 12

- [x] T112 [US12] Create values-staging.yaml with cloud config in helm/todo-chatbot/values-staging.yaml
- [x] T113 [US12] Create values-production.yaml with production config in helm/todo-chatbot/values-production.yaml
- [x] T114 [US12] Add LoadBalancer service type for cloud in helm/charts/*/templates/service.yaml
- [x] T115 [US12] Configure Redpanda Cloud connection in Dapr component in dapr/components/kafka-pubsub-cloud.yaml
- [x] T116 [US12] Add resource limits and requests to all deployments in helm/charts/*/templates/deployment.yaml
- [x] T117 [US12] Add HorizontalPodAutoscaler for backend in helm/charts/backend/templates/hpa.yaml

**Checkpoint**: User Story 12 fully functional - same charts work on any cloud Kubernetes

---

## Phase 15: User Story 13 - CI/CD Pipeline (Priority: P3)

**Goal**: Automated builds and deployments via GitHub Actions

**Independent Test**: Push to main, verify pipeline builds and deploys to staging

### Implementation for User Story 13

- [x] T118 [US13] Create Docker build workflow in .github/workflows/build.yaml
- [x] T119 [US13] Create deployment workflow in .github/workflows/deploy.yaml
- [x] T120 [US13] Add staging deployment job (on main push) in .github/workflows/deploy.yaml
- [x] T121 [US13] Add production deployment job (on version tag) in .github/workflows/deploy.yaml
- [x] T122 [US13] Configure Helm upgrade with --atomic flag in .github/workflows/deploy.yaml
- [x] T123 [US13] Add Slack/Discord notification step in .github/workflows/deploy.yaml
- [x] T124 [US13] Document required secrets in .github/workflows/README.md

**Checkpoint**: User Story 13 fully functional - CI/CD automates build and deploy

---

## Phase 16: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T125 [P] Create PHASE-5-DEPLOYMENT.md documentation in docs/PHASE-5-DEPLOYMENT.md
- [ ] T126 [P] Update README.md with Phase 5 features and deployment instructions
- [ ] T127 Add request correlation IDs for distributed tracing in backend/src/middleware/correlation.py
- [x] T128 [P] Add Kubernetes liveness probe to all deployment templates
- [x] T129 [P] Add Kubernetes readiness probe to all deployment templates
- [ ] T130 Configure graceful shutdown handlers in all services
- [x] T131 Add pod disruption budget for backend in helm/charts/backend/templates/pdb.yaml
- [ ] T132 Run quickstart.md validation to verify developer experience
- [x] T133 Create end-to-end test script for full workflow validation in scripts/e2e-test.ps1

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-15)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 16)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|-----------|-------------------|
| US1 (Priorities) | Foundational | US2, US3, US8 |
| US2 (Tags) | Foundational | US1, US3, US8 |
| US3 (Due Dates) | Foundational | US1, US2, US8 |
| US4 (Search) | US1, US2, US3 | US5 |
| US5 (Filter/Sort) | US1, US2, US3 | US4 |
| US6 (Reminders) | US3, US8, US9 | US7 |
| US7 (Recurring) | US8, US10 | US6 |
| US8 (Events) | Foundational | US1, US2, US3 |
| US9 (Notification Svc) | Foundational | US8 |
| US10 (Recurring Svc) | Foundational | US8 |
| US11 (Minikube) | US1-US10 | None |
| US12 (Cloud) | US11 | US13 |
| US13 (CI/CD) | US11 | US12 |

### Within Each User Story

- Models before services
- Services before endpoints
- Endpoints before MCP tools
- Backend before frontend components
- Core implementation before integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- US1, US2, US3, US8, US9, US10 can all start after Foundational
- Models within a story marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch these model updates in parallel:
T012: "Update Task SQLModel with priority field"
T013: "Update Task SQLModel with due_date field"
T014: "Update Task SQLModel with remind_at field"
T015: "Update Task SQLModel with reminder_sent field"
T016: "Update Task SQLModel with recurrence field"
T017: "Update Task SQLModel with parent_task_id field"

# Then sequentially:
T011: "Run Alembic migration" (after all model updates)
```

---

## Parallel Example: User Story 1 (Priorities)

```bash
# After Foundational phase, launch US1 tasks:
# Backend first:
T030: "Update task_service.py for priority"
T031-T032: "Add priority filter endpoint and CRUD"

# Then MCP tools:
T033-T034: "Add priority MCP tools"

# Then frontend (can parallel with MCP):
T035-T036: "Add priority UI components"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3, 8, 11)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete US1: Priorities
4. Complete US2: Tags
5. Complete US3: Due Dates
6. Complete US8: Event Infrastructure
7. Complete US11: Minikube Deployment
8. **STOP and VALIDATE**: Test full stack on Minikube

### Incremental Delivery

After MVP:
1. Add US4: Search → Deploy
2. Add US5: Filter/Sort → Deploy
3. Add US6: Reminders + US9: Notification Service → Deploy
4. Add US7: Recurring + US10: Recurring Service → Deploy
5. Add US12: Cloud + US13: CI/CD → Production Ready

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1, US4, US6
   - Developer B: US2, US5, US7
   - Developer C: US3, US8, US9, US10
   - Developer D: US11, US12, US13
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Event infrastructure (US8) should be started early as many features depend on it
- Notification and Recurring services can be developed in parallel with backend features

---

## Task Summary

| Phase | User Story | Task Count | Parallelizable |
|-------|-----------|------------|----------------|
| 1 | Setup | 10 | 8 |
| 2 | Foundational | 19 | 12 |
| 3 | US1 Priorities | 7 | 0 |
| 4 | US2 Tags | 10 | 0 |
| 5 | US3 Due Dates | 8 | 0 |
| 6 | US4 Search | 6 | 0 |
| 7 | US5 Filter/Sort | 7 | 0 |
| 8 | US6 Reminders | 8 | 0 |
| 9 | US7 Recurring | 9 | 0 |
| 10 | US8 Events | 6 | 0 |
| 11 | US9 Notification Svc | 5 | 0 |
| 12 | US10 Recurring Svc | 5 | 0 |
| 13 | US11 Minikube | 11 | 0 |
| 14 | US12 Cloud | 6 | 0 |
| 15 | US13 CI/CD | 7 | 0 |
| 16 | Polish | 9 | 4 |
| **Total** | | **133** | **24** |

**MVP Scope**: Phases 1-5, 10, 13 (Setup + Foundational + US1-3 + US8 + US11) = ~65 tasks
