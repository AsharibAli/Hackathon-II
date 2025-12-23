# Tasks: Todo Full-Stack Web Application - Baseline

**Input**: Design documents from `/specs/001-todo-app-baseline/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/api.yaml

**Tests**: This specification does NOT explicitly request automated tests. All testing will be manual per acceptance scenarios documented in spec.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow monorepo web application structure per plan.md

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETED

**Purpose**: Project initialization and basic structure

- [x] T001 Create root-level monorepo configuration files (.gitignore, pnpm-workspace.yaml, README.md)
- [x] T002 [P] Create backend directory structure (backend/src/{models,services,api,core,middleware}, backend/tests, backend/alembic)
- [x] T003 [P] Create frontend directory structure (frontend/src/{app,components,lib,types}, frontend/public)
- [x] T004 [P] Initialize backend Python project with uv in backend/pyproject.toml
- [x] T005 [P] Initialize frontend Next.js project with pnpm in frontend/package.json
- [x] T006 Configure backend dependencies (FastAPI, SQLModel, python-jose, passlib, uvicorn, alembic, psycopg2-binary) in backend/pyproject.toml
- [x] T007 [P] Configure frontend dependencies (Next.js 14, Better Auth, Tailwind CSS) in frontend/package.json
- [x] T008 [P] Create backend environment configuration template in backend/.env.example
- [x] T009 [P] Create frontend environment configuration template in frontend/.env.local.example
- [x] T010 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [x] T011 [P] Configure Tailwind CSS in frontend/tailwind.config.ts
- [x] T012 [P] Initialize Alembic for database migrations in backend/alembic.ini

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETED

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T013 Create database configuration in backend/src/core/database.py (SQLModel engine, session management, Neon connection)
- [x] T014 [P] Create environment settings loader in backend/src/core/config.py (Pydantic BaseSettings for DATABASE_URL, JWT_SECRET, CORS_ORIGINS)
- [x] T015 [P] Create password hashing utilities in backend/src/core/security.py (bcrypt hash, verify functions)
- [x] T016 Create JWT token utilities in backend/src/core/security.py (create_access_token, verify_token, extract_user_id)
- [x] T017 [P] Create User SQLModel in backend/src/models/user.py (id, email, hashed_password, created_at, updated_at, is_active)
- [x] T018 [P] Create Task SQLModel in backend/src/models/task.py (id, user_id FK, title, description, is_completed, created_at, updated_at)
- [x] T019 Create initial database migration in backend/alembic/versions/001_create_users_and_tasks.py (users table, tasks table, indexes, FK constraints)
- [x] T020 [P] Create authentication dependency in backend/src/api/dependencies.py (get_current_user: verify JWT, extract user_id, fetch User from DB)
- [x] T021 [P] Create database session dependency in backend/src/api/dependencies.py (get_session: SQLModel session lifecycle)
- [x] T022 Create CORS middleware configuration in backend/src/main.py
- [x] T023 [P] Create structured logging middleware in backend/src/middleware/logging.py
- [x] T024 Create exception handlers in backend/src/middleware/errors.py (ValidationError, HTTPException, generic Exception with proper error responses)
- [x] T025 Initialize FastAPI app in backend/src/main.py (app creation, middleware registration, router registration)
- [x] T026 [P] Create Better Auth configuration in frontend/src/lib/auth.ts (JWT plugin, session management)
- [x] T027 [P] Create authenticated API client wrapper in frontend/src/lib/api.ts (fetch wrapper with Authorization header injection)
- [x] T028 [P] Create root layout with auth provider in frontend/src/app/layout.tsx
- [x] T029 [P] Install shadcn/ui base components (Button, Input, Card, Form, Dialog, Checkbox, Label, Toast) in frontend/src/components/ui/

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1) 🎯 MVP ✅ COMPLETED

**Goal**: Enable users to create accounts and authenticate to access the application

**Independent Test**: Create a new account, logout, login, and verify access. Multi-user isolation foundation established through authentication.

**Acceptance Scenarios** (from spec.md US1):
1. Register new user with valid credentials → account created + logged in
2. Login with existing credentials → JWT token received + access granted
3. Access protected resource without token → redirected to login
4. Logout → session terminated, must re-login for access

### Implementation for User Story 1

- [x] T030 [P] [US1] Create user registration service in backend/src/services/auth.py (validate email, hash password, create user in DB, return JWT)
- [x] T031 [P] [US1] Create user login service in backend/src/services/auth.py (verify email+password, generate JWT)
- [x] T032 [P] [US1] Create logout service in backend/src/services/auth.py (client-side token invalidation, optional server-side blacklist)
- [x] T033 [US1] Create POST /api/auth/register endpoint in backend/src/api/auth.py (validate request, call registration service, return AuthResponse)
- [x] T034 [P] [US1] Create POST /api/auth/login endpoint in backend/src/api/auth.py (validate credentials, call login service, return AuthResponse)
- [x] T035 [P] [US1] Create POST /api/auth/logout endpoint in backend/src/api/auth.py (requires authentication, returns success message)
- [x] T036 Register auth router in backend/src/main.py
- [x] T037 [P] [US1] Create registration page UI in frontend/src/app/(auth)/register/page.tsx (email+password form, Better Auth integration)
- [x] T038 [P] [US1] Create login page UI in frontend/src/app/(auth)/login/page.tsx (email+password form, Better Auth integration)
- [x] T039 [P] [US1] Create auth form component in frontend/src/components/AuthForm.tsx (reusable form with validation)
- [x] T040 [US1] Create auth layout with redirect logic in frontend/src/app/(auth)/layout.tsx (redirect if already authenticated)
- [x] T041 [P] [US1] Create protected route wrapper in frontend/src/app/(app)/layout.tsx (verify auth, redirect to login if not authenticated)
- [x] T042 [US1] Add logout functionality to app layout in frontend/src/app/(app)/layout.tsx (logout button, clear session)

**Checkpoint**: ✅ User Story 1 is fully functional and testable independently. Users can register, login, and logout.

---

## Phase 4: User Story 2 - View Personal Todo List (Priority: P2) ✅ COMPLETED

**Goal**: Display authenticated user's tasks with guaranteed multi-user isolation

**Independent Test**: Login as different users, verify each sees only their own tasks. Empty state displays correctly for new users.

**Acceptance Scenarios** (from spec.md US2):
1. User with existing tasks → see list with title + completion status
2. User with no tasks → see empty state with prompt to create first task
3. Two different users → User A sees only their tasks, not User B's
4. Refresh page → task list persists

### Implementation for User Story 2

- [x] T043 [P] [US2] Create get user tasks service in backend/src/services/tasks.py (query tasks filtered by user_id, order by created_at DESC)
- [x] T044 [US2] Create GET /api/tasks endpoint in backend/src/api/tasks.py (requires auth, calls service with current_user.id, returns TaskRead list)
- [x] T045 Register tasks router in backend/src/main.py
- [x] T046 [P] [US2] Create Task TypeScript interface in frontend/src/types/task.ts (matches TaskRead schema from API)
- [x] T047 [P] [US2] Create TaskList component in frontend/src/components/TaskList.tsx (fetches tasks from API, displays list or empty state)
- [x] T048 [P] [US2] Create TaskItem component in frontend/src/components/TaskItem.tsx (displays single task with title, description, completion status)
- [x] T049 [US2] Create main todo list page in frontend/src/app/(app)/page.tsx (renders TaskList component, protected route)
- [x] T050 [US2] Add loading and error states to TaskList in frontend/src/components/TaskList.tsx

**Checkpoint**: ✅ User Stories 1 AND 2 both work independently. Users can login and view their personal task list.

---

## Phase 5: User Story 3 - Create New Tasks (Priority: P3) ✅ COMPLETED

**Goal**: Enable users to add new tasks to their todo list

**Independent Test**: Create tasks with various inputs (title only, title+description), verify they appear in list. Validation prevents empty titles.

**Acceptance Scenarios** (from spec.md US3):
1. Submit task with title → task created and appears in list
2. Submit task with title + description → both fields saved and displayed
3. Create task → marked as incomplete by default
4. Attempt to create task without title → validation error

### Implementation for User Story 3

- [x] T051 [P] [US3] Create task creation service in backend/src/services/tasks.py (validate title, set user_id from auth, create task in DB, return TaskRead)
- [x] T052 [US3] Create POST /api/tasks endpoint in backend/src/api/tasks.py (requires auth, validates TaskCreate schema, calls service, returns 201 + TaskRead)
- [x] T053 [P] [US3] Create TaskForm component in frontend/src/components/TaskForm.tsx (title+description inputs, validation, submit handler)
- [x] T054 [US3] Integrate TaskForm into main page in frontend/src/app/(app)/page.tsx (create mode, API call on submit, optimistic update)
- [x] T055 [US3] Add validation error display to TaskForm in frontend/src/components/TaskForm.tsx (empty title, title too long, description too long)

**Checkpoint**: ✅ User Stories 1, 2, AND 3 all work independently. Users can create tasks and see them in their list.

---

## Phase 6: User Story 4 - Toggle Task Completion (Priority: P4) ✅ COMPLETED

**Goal**: Allow users to mark tasks as complete or incomplete

**Independent Test**: Toggle task completion status, verify persistence across refresh. Visual distinction between completed and incomplete tasks.

**Acceptance Scenarios** (from spec.md US4):
1. Click toggle on incomplete task → marked complete + visually distinguished
2. Click toggle on completed task → marked incomplete
3. Toggle task + refresh → completion status persists
4. View task list → completed and incomplete tasks visually distinguishable

### Implementation for User Story 4

- [x] T056 [P] [US4] Create toggle completion service in backend/src/services/tasks.py (verify task belongs to user, toggle is_completed, update updated_at, return TaskRead)
- [x] T057 [US4] Create PATCH /api/tasks/{task_id}/complete endpoint in backend/src/api/tasks.py (requires auth, validates ownership, calls service, returns 200 + TaskRead)
- [x] T058 [P] [US4] Add completion toggle UI to TaskItem in frontend/src/components/TaskItem.tsx (checkbox/button, API call on click)
- [x] T059 [US4] Add visual styling for completed tasks in frontend/src/components/TaskItem.tsx (strikethrough, opacity, different color)
- [x] T060 [US4] Add optimistic UI update for toggle in frontend/src/components/TaskList.tsx (immediate visual feedback before API response)

**Checkpoint**: ✅ User Stories 1-4 work independently. Core todo list value (task creation + completion tracking) delivered.

---

## Phase 7: User Story 5 - Update Task Details (Priority: P5) ✅ COMPLETED

**Goal**: Allow users to edit existing task titles and descriptions

**Independent Test**: Edit task title/description, verify changes persist. Cancel edit preserves original data. Empty title validation prevents invalid updates.

**Acceptance Scenarios** (from spec.md US5):
1. Edit title → updated title saved and displayed
2. Edit description → updated description saved
3. Cancel edit → original data unchanged
4. Save empty title → validation error

### Implementation for User Story 5

- [x] T061 [P] [US5] Create task update service in backend/src/services/tasks.py (verify ownership, validate TaskUpdate, update fields, return TaskRead)
- [x] T062 [US5] Create PUT /api/tasks/{task_id} endpoint in backend/src/api/tasks.py (requires auth, validates ownership, calls service, returns 200 + TaskRead)
- [x] T063 [P] [US5] Add edit mode to EditTaskDialog component in frontend/src/components/EditTaskDialog.tsx (pre-populate fields, update logic)
- [x] T064 [US5] Add edit trigger to TaskItem in frontend/src/components/TaskItem.tsx (edit button, toggle edit mode)
- [x] T065 [US5] Add cancel edit functionality in frontend/src/components/EditTaskDialog.tsx (reset to original values, exit edit mode)
- [x] T066 [US5] Add modal edit UI pattern via EditTaskDialog in frontend/src/components/EditTaskDialog.tsx (modal dialog for editing)

**Checkpoint**: ✅ User Stories 1-5 work independently. Users can fully manage task lifecycle (create, read, update, complete).

---

## Phase 8: User Story 6 - Delete Tasks (Priority: P6) ✅ COMPLETED

**Goal**: Allow users to permanently remove tasks

**Independent Test**: Delete task with confirmation, verify removal persists. Cancel deletion preserves task.

**Acceptance Scenarios** (from spec.md US6):
1. Click delete → confirmation dialog appears
2. Confirm deletion → task permanently removed
3. Cancel deletion → task remains unchanged
4. Delete + refresh → deleted task does not reappear

### Implementation for User Story 6

- [x] T067 [P] [US6] Create task deletion service in backend/src/services/tasks.py (verify ownership, delete from DB, return success)
- [x] T068 [US6] Create DELETE /api/tasks/{task_id} endpoint in backend/src/api/tasks.py (requires auth, validates ownership, calls service, returns 204 No Content)
- [x] T069 [P] [US6] Add delete confirmation dialog via DeleteTaskDialog in frontend/src/components/DeleteTaskDialog.tsx (using shadcn Dialog)
- [x] T070 [US6] Add delete button to TaskItem in frontend/src/components/TaskItem.tsx (triggers confirmation dialog)
- [x] T071 [US6] Implement delete API call in TaskList in frontend/src/components/TaskList.tsx (remove from list on success)

**Checkpoint**: ✅ All user stories (P1-P6) are independently functional. Complete todo application delivered.

---

## Phase 9: Polish & Cross-Cutting Concerns ✅ COMPLETED

**Purpose**: Improvements that affect multiple user stories and final touches

- [x] T072 [P] Add request logging to all API endpoints in backend/src/middleware/logging.py
- [x] T073 [P] Add error boundary to frontend app layout via ErrorBoundary component and Providers in frontend/src/app/layout.tsx
- [x] T074 [P] Add loading skeletons to task list in frontend/src/components/TaskList.tsx
- [x] T075 [P] Add toast notifications for success/error feedback using Sonner in frontend/src/app/layout.tsx
- [x] T076 [P] Database queries optimized with SQLModel indexing (user_id, created_at on tasks table)
- [x] T077 [P] Responsive mobile layout implemented via Tailwind breakpoints in all frontend/src/components/
- [x] T078 Create project README.md in root with setup instructions, architecture overview, development workflow
- [x] T079 [P] Create backend README.md in backend/ with API documentation link, environment variables
- [x] T080 [P] Create frontend README.md in frontend/ with component structure, development commands
- [x] T081 Manual testing procedures documented - ready for verification per quickstart.md (US1-US6)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Foundational - No dependencies on other stories
  - US2 (P2): Can start after Foundational - No dependencies on other stories
  - US3 (P3): Can start after Foundational - No dependencies on other stories
  - US4 (P4): Can start after Foundational - Functionally depends on US3 (needs tasks to toggle)
  - US5 (P5): Can start after Foundational - Functionally depends on US3 (needs tasks to edit)
  - US6 (P6): Can start after Foundational - Functionally depends on US3 (needs tasks to delete)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

**Technical Dependencies** (can parallelize):
- All user stories are **technically independent** after Foundational phase
- Each story has its own services, endpoints, and UI components

**Functional Dependencies** (for meaningful testing):
- **US1 (Auth)**: No dependencies - foundation for all others
- **US2 (View)**: Auth (US1) required for access, but no task dependencies
- **US3 (Create)**: Auth (US1) required, makes US2 useful
- **US4 (Toggle)**: Auth (US1) + Create (US3) for tasks to toggle
- **US5 (Update)**: Auth (US1) + Create (US3) for tasks to edit
- **US6 (Delete)**: Auth (US1) + Create (US3) for tasks to delete

### Within Each User Story

- Backend services before API endpoints
- API endpoints before frontend integration
- Core functionality before error handling/validation
- Basic UI before optimistic updates/loading states
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T003, T004-T005, T006-T007, T008-T009, T010-T012)
- All Foundational tasks marked [P] can run in parallel within Phase 2
- Once Foundational phase completes, **all user stories can start in parallel** (if team capacity allows)
- Within each story, tasks marked [P] can run in parallel:
  - US1: T030-T032 (services), T034-T035 (endpoints), T037-T039 (UI components)
  - US2: T043 (service), T046-T048 (UI components)
  - US3: T051 (service), T053 (UI component)
  - US4: T056 (service), T058-T059 (UI changes)
  - US5: T061 (service), T063-T064 (UI changes)
  - US6: T067 (service), T069-T070 (UI changes)
- Polish tasks (T072-T080) can run in parallel

---

## Parallel Example: User Story 1 (Authentication)

```bash
# After Foundational phase completes, launch these US1 tasks in parallel:

# Backend services (T030-T032):
Task: "Create user registration service in backend/src/services/auth.py"
Task: "Create user login service in backend/src/services/auth.py"
Task: "Create logout service in backend/src/services/auth.py"

# Then API endpoints (T034-T035) in parallel:
Task: "Create POST /api/auth/login endpoint in backend/src/api/auth.py"
Task: "Create POST /api/auth/logout endpoint in backend/src/api/auth.py"

# Then frontend UI (T037-T039) in parallel:
Task: "Create registration page UI in frontend/src/app/(auth)/register/page.tsx"
Task: "Create login page UI in frontend/src/app/(auth)/login/page.tsx"
Task: "Create auth form component in frontend/src/components/AuthForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T012)
2. Complete Phase 2: Foundational (T013-T029) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T030-T042)
4. **STOP and VALIDATE**: Test US1 acceptance scenarios manually
5. Deploy/demo authentication flow

**MVP Delivers**: User registration, login, logout, protected routes

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Auth) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (View) → Test independently → Deploy/Demo
4. Add User Story 3 (Create) → Test independently → Deploy/Demo
5. Add User Story 4 (Toggle) → Test independently → Deploy/Demo
6. Add User Story 5 (Update) → Test independently → Deploy/Demo
7. Add User Story 6 (Delete) → Test independently → Deploy/Demo
8. Add Polish (Phase 9) → Final deployment

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T029)
2. Once Foundational is done:
   - Developer A: User Story 1 (T030-T042)
   - Developer B: User Story 2 (T043-T050) - can start in parallel
   - Developer C: User Story 3 (T051-T055) - can start in parallel
3. Stories complete and integrate independently
4. US4-US6 can then be tackled in parallel by different developers

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- NO automated tests included (spec doesn't request them per Constitution Principle V)
- Manual testing per acceptance scenarios documented in spec.md
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Total Tasks**: 81
- **Setup**: 12 tasks (T001-T012)
- **Foundational**: 17 tasks (T013-T029) - BLOCKING
- **User Story 1 (P1)**: 13 tasks (T030-T042) - MVP
- **User Story 2 (P2)**: 8 tasks (T043-T050)
- **User Story 3 (P3)**: 5 tasks (T051-T055)
- **User Story 4 (P4)**: 5 tasks (T056-T060)
- **User Story 5 (P5)**: 6 tasks (T061-T066)
- **User Story 6 (P6)**: 5 tasks (T067-T071)
- **Polish**: 10 tasks (T072-T081)

**Parallel Opportunities**: 42 tasks marked [P] can execute in parallel (within their phase/story constraints)

**MVP Scope**: Phases 1-3 (T001-T042) = 42 tasks for authentication foundation

**Full Feature**: All 81 tasks for complete todo application with all 6 user stories
