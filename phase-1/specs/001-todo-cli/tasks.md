# Tasks: Todo In-Memory Python Console App

**Input**: Design documents from `/specs/001-todo-cli/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, research.md

**Tests**: Tests are OPTIONAL - not included in this task list per constitution Principle V (TDD conditional).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)
- All file paths are relative to repository root: `G:\Projects To Work On\Hackathon-II\phase-1\`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize UV project with Python 3.13+ in repository root
- [x] T002 [P] Create src/models/ directory with __init__.py
- [x] T003 [P] Create src/services/ directory with __init__.py
- [x] T004 [P] Create src/cli/ directory with __init__.py
- [x] T005 [P] Configure pyproject.toml with dev dependencies (mypy, ruff)
- [x] T006 [P] Create README.md with project overview and setup instructions per quickstart.md
- [x] T007 [P] Create .gitignore for Python (.venv/, __pycache__/, *.pyc, .mypy_cache/, .ruff_cache/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 [P] Create exception hierarchy in src/models/exceptions.py (TodoAppError, TaskNotFoundError, InvalidInputError)
- [x] T009 [P] Create Task dataclass in src/models/task.py with id, title, description, completed attributes
- [x] T010 Create TaskService class in src/services/task_service.py with _tasks dict and _next_id counter
- [x] T011 Create TodoCLI class skeleton in src/cli/todo_cli.py with __init__ accepting TaskService
- [x] T012 Create application entry point in src/__main__.py that wires TaskService and TodoCLI

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks and view the task list with status indicators

**Independent Test**: Launch application, add a task with title and description, view all tasks to confirm it appears with ID and "incomplete" status

### Implementation for User Story 1

- [x] T013 [P] [US1] Implement Task.mark_complete() method in src/models/task.py
- [x] T014 [P] [US1] Implement Task.mark_incomplete() method in src/models/task.py
- [x] T015 [US1] Implement TaskService.create_task(title, description) in src/services/task_service.py (validate inputs, generate ID, create Task, store in _tasks dict)
- [x] T016 [US1] Implement TaskService.get_all_tasks() in src/services/task_service.py (return list of tasks ordered by ID)
- [x] T017 [US1] Implement TodoCLI.display_menu() in src/cli/todo_cli.py (show 7 menu options)
- [x] T018 [US1] Implement TodoCLI.get_menu_choice() in src/cli/todo_cli.py (validate input 1-7)
- [x] T019 [US1] Implement TodoCLI.get_string_input(prompt) in src/cli/todo_cli.py (get non-empty string, strip whitespace)
- [x] T020 [US1] Implement TodoCLI.handle_add_task() in src/cli/todo_cli.py (collect title/description, call create_task, display success/error)
- [x] T021 [US1] Implement TodoCLI.format_task_list(tasks) in src/cli/todo_cli.py (tabular format with ID|Title|Description|Status, use ✓/✗ indicators)
- [x] T022 [US1] Implement TodoCLI.handle_view_tasks() in src/cli/todo_cli.py (call get_all_tasks, format and display, handle empty list)
- [x] T023 [US1] Implement TodoCLI.run() main loop in src/cli/todo_cli.py (display menu, get choice, route to handlers, loop until exit)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (MVP complete!)

---

## Phase 4: User Story 2 - Mark Tasks Complete/Incomplete (Priority: P2)

**Goal**: Enable users to toggle task completion status

**Independent Test**: Add a task, mark it complete, view list to confirm status shows "✓ Complete", mark it incomplete, view list to confirm status shows "✗ Incomplete"

### Implementation for User Story 2

- [x] T024 [US2] Implement TaskService.get_task(task_id) in src/services/task_service.py (lookup in _tasks, raise TaskNotFoundError if missing)
- [x] T025 [P] [US2] Implement TaskService.mark_complete(task_id) in src/services/task_service.py (get task, call mark_complete(), return task)
- [x] T026 [P] [US2] Implement TaskService.mark_incomplete(task_id) in src/services/task_service.py (get task, call mark_incomplete(), return task)
- [x] T027 [US2] Implement TodoCLI.get_int_input(prompt) in src/cli/todo_cli.py (parse int, handle ValueError with clear error)
- [x] T028 [P] [US2] Implement TodoCLI.handle_mark_complete() in src/cli/todo_cli.py (get task ID, call mark_complete, display success/error)
- [x] T029 [P] [US2] Implement TodoCLI.handle_mark_incomplete() in src/cli/todo_cli.py (get task ID, call mark_incomplete, display success/error)
- [x] T030 [US2] Update TodoCLI.run() in src/cli/todo_cli.py to route menu options 5 and 6 to mark complete/incomplete handlers

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Enable users to edit task title and/or description

**Independent Test**: Create a task, update its title, view list to confirm title changed; update its description, view list to confirm description changed

### Implementation for User Story 3

- [x] T031 [P] [US3] Implement Task.update_title(new_title) in src/models/task.py (validate non-empty after strip, update self.title)
- [x] T032 [P] [US3] Implement Task.update_description(new_description) in src/models/task.py (validate non-empty after strip, update self.description)
- [x] T033 [US3] Implement TaskService.update_task(task_id, title=None, description=None) in src/services/task_service.py (get task, call Task update methods if values provided)
- [x] T034 [US3] Implement TodoCLI.handle_update_task() in src/cli/todo_cli.py (get task ID, prompt for new title/description with option to skip, call update_task, display success/error)
- [x] T035 [US3] Update TodoCLI.run() in src/cli/todo_cli.py to route menu option 3 to update handler

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Enable users to permanently remove tasks

**Independent Test**: Create a task, note its ID, delete it by ID, view list to confirm task no longer appears

### Implementation for User Story 4

- [x] T036 [US4] Implement TaskService.delete_task(task_id) in src/services/task_service.py (get task to verify exists, delete from _tasks dict)
- [x] T037 [US4] Implement TodoCLI.handle_delete_task() in src/cli/todo_cli.py (get task ID, call delete_task, display success/error)
- [x] T038 [US4] Update TodoCLI.run() in src/cli/todo_cli.py to route menu option 4 to delete handler

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T039 [P] Add type hints to all functions in src/models/task.py (verify with mypy)
- [x] T040 [P] Add type hints to all functions in src/services/task_service.py (verify with mypy)
- [x] T041 [P] Add type hints to all functions in src/cli/todo_cli.py (verify with mypy)
- [x] T042 [P] Add docstrings to all classes and public methods in src/models/task.py
- [x] T043 [P] Add docstrings to all classes and public methods in src/services/task_service.py
- [x] T044 [P] Add docstrings to all classes and public methods in src/cli/todo_cli.py
- [x] T045 Run ruff linter on all source files and fix PEP 8 violations
- [x] T046 Run mypy type checker on all source files and fix type errors
- [x] T047 Manual end-to-end test: Add task → View → Mark complete → View → Update → View → Delete → View → Exit
- [x] T048 Verify no file I/O or persistence (check no open(), no database imports, data clears on exit)
- [x] T049 Update README.md with final usage examples and verify all commands work per quickstart.md
- [x] T050 Verify all 5 required features work: (1) Add task (2) View tasks (3) Update task (4) Delete task (5) Mark complete/incomplete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ MVP COMPLETE
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 (needs tasks to exist, uses view to verify)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 (needs tasks to exist, uses view to verify)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Integrates with US1 (needs tasks to exist, uses view to verify)

### Within Each User Story

- Foundation tasks (T008-T012) create base classes needed by all stories
- Each story builds on foundation but is independently testable
- Story complete when all tasks in that phase pass independent test criteria

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T007)
- All Foundational tasks marked [P] can run in parallel within Phase 2 (T008-T009)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within User Story 1: T013-T014 can run in parallel (Task methods)
- Within User Story 2: T025-T026 can run in parallel (TaskService methods), T028-T029 can run in parallel (CLI handlers)
- Within User Story 3: T031-T032 can run in parallel (Task methods)
- All Polish docstring tasks can run in parallel (T042-T044)
- All Polish type hint tasks can run in parallel (T039-T041)

---

## Parallel Example: User Story 1

```bash
# Launch Task model methods together:
Task: "Implement Task.mark_complete() method in src/models/task.py"
Task: "Implement Task.mark_incomplete() method in src/models/task.py"

# Then launch TaskService methods together:
Task: "Implement TaskService.create_task(title, description) in src/services/task_service.py"
Task: "Implement TaskService.get_all_tasks() in src/services/task_service.py"

# Then launch CLI helpers together:
Task: "Implement TodoCLI.get_string_input(prompt) in src/cli/todo_cli.py"
Task: "Implement TodoCLI.format_task_list(tasks) in src/cli/todo_cli.py"

# Finally sequential: handlers and main loop (depend on helpers)
Task: "Implement TodoCLI.handle_add_task() in src/cli/todo_cli.py"
Task: "Implement TodoCLI.handle_view_tasks() in src/cli/todo_cli.py"
Task: "Implement TodoCLI.run() main loop in src/cli/todo_cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T012) ⚠️ CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T013-T023)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Launch app
   - Add task "Test task" / "Test description"
   - View all tasks (should show ID 1, incomplete)
   - Exit and verify data clears
5. If working, proceed to User Story 2 or deliver MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T012)
2. Add User Story 1 → Test independently → ✅ MVP Deliverable!
3. Add User Story 2 → Test independently → ✅ Completion tracking added!
4. Add User Story 3 → Test independently → ✅ Task editing added!
5. Add User Story 4 → Test independently → ✅ Full CRUD complete!
6. Polish phase → Code quality validated → ✅ Production ready!

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T012)
2. Once Foundational is done:
   - Developer A: User Story 1 (T013-T023)
   - Developer B: User Story 2 (T024-T030) - waits for T024 before starting others
   - Developer C: User Story 3 (T031-T035)
   - Developer D: User Story 4 (T036-T038)
3. Stories complete and integrate independently
4. Team completes Polish together (T039-T050)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Constitution Principle V: Tests are OPTIONAL - not included in this task list
- Manual validation acceptable (Phase 7 includes end-to-end testing)
- Commit after each task or logical group per constitution commit strategy
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Task Summary

**Total Tasks**: 50
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 5 tasks (BLOCKS all stories)
- Phase 3 (User Story 1 - P1): 11 tasks ✅ MVP
- Phase 4 (User Story 2 - P2): 7 tasks
- Phase 5 (User Story 3 - P3): 5 tasks
- Phase 6 (User Story 4 - P4): 3 tasks
- Phase 7 (Polish): 12 tasks

**Parallel Opportunities**: 18 tasks marked [P] can run in parallel within their phase

**Critical Path**: Setup (7) → Foundational (5) → User Story 1 (11) → Polish (12) = 35 tasks for MVP

**Independent Test Criteria**:
- US1: Add task → View list → Verify task appears with ID and status
- US2: Add task → Mark complete → View → Verify status changed
- US3: Add task → Update title → View → Verify title changed
- US4: Add task → Delete → View → Verify task removed

**MVP Scope**: Complete through Phase 3 (User Story 1) = 23 tasks for working add/view functionality
