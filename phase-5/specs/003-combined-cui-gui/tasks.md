# Tasks: Combined CUI & GUI Todo Application

**Input**: Design documents from `/specs/003-combined-cui-gui/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md
**Date**: 2025-12-23

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup & Verification

**Purpose**: Verify Phase-4 has all necessary Phase-3 code and prepare for integration

- [ ] T001 Verify phase-4/backend has all Phase-3 backend code (models, services, api, mcp)
- [ ] T002 Verify phase-4/frontend has all Phase-3 frontend code (chat components, api client)
- [ ] T003 [P] Verify phase-4 dependencies are installed (backend: uv, frontend: pnpm)
- [ ] T004 [P] Verify backend runs without errors (uvicorn src.main:app)
- [ ] T005 [P] Verify frontend runs without errors (pnpm dev)

**Checkpoint**: Phase-3 functionality confirmed working in Phase-4

---

## Phase 2: GUI Component Migration (From Phase-2)

**Purpose**: Migrate and adapt GUI components from Phase-2 into Phase-4

### Component Migration

- [ ] T006 Create `frontend/src/components/tasks/` directory
- [ ] T007 [P] [US2] Copy TaskList.tsx from phase-2 to `frontend/src/components/tasks/TaskList.tsx`
- [ ] T008 [P] [US2] Copy TaskItem.tsx from phase-2 to `frontend/src/components/tasks/TaskItem.tsx`
- [ ] T009 [P] [US2] Copy TaskForm.tsx from phase-2 to `frontend/src/components/tasks/TaskForm.tsx`
- [ ] T010 [P] [US2] Copy EditTaskDialog.tsx from phase-2 to `frontend/src/components/tasks/EditTaskDialog.tsx`
- [ ] T011 [P] [US2] Copy DeleteTaskDialog.tsx from phase-2 to `frontend/src/components/tasks/DeleteTaskDialog.tsx`

### Component Adaptation

- [ ] T012 [US2] Update TaskList.tsx imports to use Phase-4 api.ts and types
- [ ] T013 [US2] Update TaskItem.tsx imports and props for Phase-4 context
- [ ] T014 [US2] Update TaskForm.tsx imports and API calls for Phase-4
- [ ] T015 [US2] Update EditTaskDialog.tsx imports for Phase-4
- [ ] T016 [US2] Update DeleteTaskDialog.tsx imports for Phase-4
- [ ] T017 [US2] Create `frontend/src/components/tasks/index.ts` barrel export file

**Checkpoint**: All GUI components migrated and adapted for Phase-4

---

## Phase 3: User Story 1 - Dual Interface Navigation (Priority: P1)

**Goal**: Enable users to switch between CUI and GUI modes seamlessly

**Independent Test**: Log in, verify both modes accessible via navigation, switch between them

### Navigation Components

- [ ] T018 Create `frontend/src/components/navigation/` directory
- [ ] T019 [P] [US1] Create ModeToggle.tsx in `frontend/src/components/navigation/ModeToggle.tsx`
  - Tabs or buttons for "Chat" (CUI) and "Tasks" (GUI)
  - Active state styling
  - Mode change callback
- [ ] T020 [P] [US1] Create AppHeader.tsx in `frontend/src/components/navigation/AppHeader.tsx`
  - Logo "Advanced Todo Application"
  - ModeToggle component
  - User profile/logout section
- [ ] T021 [US1] Create `frontend/src/components/navigation/index.ts` barrel export

### Layout Integration

- [ ] T022 [US1] Modify `frontend/src/app/(app)/layout.tsx` to include AppHeader
- [ ] T023 [US1] Modify `frontend/src/app/(app)/page.tsx` to handle mode state
  - Add useState for activeMode ('chat' | 'tasks')
  - Render ChatLayout when mode is 'chat'
  - Render TasksView when mode is 'tasks'

### Tasks View Container

- [ ] T024 [US1] Create TasksView.tsx in `frontend/src/components/tasks/TasksView.tsx`
  - Container component for GUI mode
  - Includes TaskForm and TaskList
  - Handles task state management
  - Loading and error states

**Checkpoint**: Users can navigate between CUI and GUI modes

---

## Phase 4: User Story 2 - GUI Task Management (Priority: P2)

**Goal**: Full CRUD operations via traditional GUI controls

**Independent Test**: Create, view, edit, complete, delete tasks entirely via GUI

### API Verification

- [ ] T025 [US2] Verify `frontend/src/lib/api.ts` has all task endpoints
  - getTasks()
  - createTask()
  - updateTask()
  - deleteTask()
  - toggleTaskComplete() or similar

### Wire Up Components

- [ ] T026 [US2] Wire TasksView to fetch tasks on mount using api.getTasks()
- [ ] T027 [US2] Wire TaskForm submit to api.createTask() and refresh list
- [ ] T028 [US2] Wire TaskItem checkbox to api.toggleTaskComplete()
- [ ] T029 [US2] Wire TaskItem edit button to open EditTaskDialog
- [ ] T030 [US2] Wire EditTaskDialog save to api.updateTask() and refresh
- [ ] T031 [US2] Wire TaskItem delete button to open DeleteTaskDialog
- [ ] T032 [US2] Wire DeleteTaskDialog confirm to api.deleteTask() and refresh

### Error Handling & UX

- [ ] T033 [US2] Add toast notifications for GUI operations (success/error)
- [ ] T034 [US2] Add loading states to TaskList and operations
- [ ] T035 [US2] Add empty state message when no tasks exist

**Checkpoint**: All GUI CRUD operations functional

---

## Phase 5: User Story 3 - CUI Task Management (Priority: P3)

**Goal**: Verify existing CUI functionality works within dual-mode context

**Independent Test**: Create, view, complete, update, delete tasks via chat

### CUI Verification

- [ ] T036 [US3] Verify ChatLayout works within new app layout
- [ ] T037 [US3] Verify chat messages send and receive correctly
- [ ] T038 [US3] Test "Add a task" via CUI creates task visible in GUI
- [ ] T039 [US3] Test "Show my tasks" via CUI lists tasks
- [ ] T040 [US3] Test task completion via CUI
- [ ] T041 [US3] Test task deletion via CUI

### CUI Integration

- [ ] T042 [US3] Ensure ChatLayout receives user profile from parent
- [ ] T043 [US3] Ensure logout from ChatLayout works in dual-mode context

**Checkpoint**: CUI mode fully functional within dual-mode application

---

## Phase 6: User Story 4 - Data Synchronization (Priority: P4)

**Goal**: Tasks created/modified in one mode reflect in the other

**Independent Test**: Create task in CUI, switch to GUI, see task; vice versa

### Synchronization Implementation

- [ ] T044 [US4] Add data refresh callback when switching from CUI to GUI
- [ ] T045 [US4] Add data refresh callback when switching from GUI to CUI (conversation refresh)
- [ ] T046 [US4] Test: Create task in GUI → switch to CUI → ask "Show tasks" → verify new task appears
- [ ] T047 [US4] Test: Create task in CUI → switch to GUI → verify new task in list
- [ ] T048 [US4] Test: Complete task in GUI → switch to CUI → verify status changed
- [ ] T049 [US4] Test: Delete task in CUI → switch to GUI → verify task removed

**Checkpoint**: Data consistent between both modes

---

## Phase 7: User Story 5 - Landing Page (Priority: P5)

**Goal**: Update landing page with dual-interface value proposition

**Independent Test**: Visit app without auth, see landing page with CUI+GUI info

### Landing Page Updates

- [ ] T050 [US5] Read current `frontend/src/app/page.tsx` landing page content
- [ ] T051 [US5] Update hero section title to "Manage tasks with AI Chat or Traditional UI"
- [ ] T052 [US5] Update hero section subtitle with dual-interface messaging
- [ ] T053 [US5] Update feature cards (3 columns):
  - Card 1: "Conversational AI" (chat icon) - natural language task management
  - Card 2: "Classic Interface" (list icon) - forms, buttons, familiar controls
  - Card 3: "Switch Anytime" (toggle icon) - both interfaces share your tasks
- [ ] T054 [US5] Update CTA buttons: "Start for Free" and "Sign In"
- [ ] T055 [US5] Update page title/metadata to "Advanced Todo Application with CUI & GUI"
- [ ] T056 [US5] Update footer copyright text

**Checkpoint**: Landing page clearly communicates dual-interface value

---

## Phase 8: User Story 6 - Conversation Persistence (Priority: P6)

**Goal**: Verify conversation history persists across sessions and mode switches

**Independent Test**: Have conversation, switch modes, return to CUI, history preserved

### Persistence Verification

- [ ] T057 [US6] Test: Send messages in CUI → switch to GUI → switch back to CUI → messages preserved
- [ ] T058 [US6] Test: Have conversation → refresh page → history restored
- [ ] T059 [US6] Test: Logout → login → previous conversations accessible in sidebar
- [ ] T060 [US6] Test: Create new conversation → switch modes → return → correct conversation active

**Checkpoint**: Conversation persistence working correctly

---

## Phase 9: Documentation & Polish

**Purpose**: Update documentation and final testing

### README Updates

- [ ] T061 [P] Update `phase-4/README.md` with:
  - Project description (Advanced Todo with CUI & GUI)
  - Features list (both interfaces)
  - Quick start instructions
  - Architecture overview
- [ ] T062 [P] Update `phase-4/frontend/README.md` with:
  - Frontend architecture
  - Component structure (chat/, tasks/, navigation/)
  - Development commands
- [ ] T063 [P] Update `phase-4/backend/README.md` with:
  - Backend architecture
  - API endpoints summary
  - MCP tools reference

### Quickstart Guide

- [ ] T064 Create `specs/003-combined-cui-gui/quickstart.md` with:
  - Prerequisites
  - Installation steps
  - Running the application
  - Verification steps for both modes

### Requirements Checklist

- [ ] T065 Create `specs/003-combined-cui-gui/checklists/requirements.md`
  - List all functional requirements from spec
  - Checkboxes for verification

### Final Testing

- [ ] T066 Run all acceptance scenarios from spec.md
- [ ] T067 Verify responsive design (mobile and desktop)
- [ ] T068 Verify no console errors in browser
- [ ] T069 Verify all navigation paths work correctly

**Checkpoint**: Documentation complete, all acceptance tests passing

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1: Setup & Verification (no dependencies)
    ↓
Phase 2: GUI Component Migration (depends on Phase 1)
    ↓
Phase 3: Dual Interface Navigation (depends on Phase 2)
    ↓
Phases 4-6 can run in parallel after Phase 3:
├── Phase 4: GUI Task Management (US2)
├── Phase 5: CUI Task Management (US3)
└── Phase 6: Data Synchronization (US4)
    ↓
Phase 7: Landing Page (can start after Phase 3)
    ↓
Phase 8: Conversation Persistence (can start after Phase 5)
    ↓
Phase 9: Documentation & Polish (depends on all above)
```

### Parallel Opportunities

Within each phase, tasks marked [P] can run in parallel:
- Phase 1: T003, T004, T005 can run in parallel
- Phase 2: T007-T011 (component copies) can run in parallel
- Phase 3: T019, T020 can run in parallel
- Phase 9: T061, T062, T063 can run in parallel

### User Story Independence

Each user story (US1-US6) can be tested independently:
- US1: Navigate between modes
- US2: Complete all GUI operations
- US3: Complete all CUI operations
- US4: Verify data sync between modes
- US5: View landing page information
- US6: Verify conversation persistence

---

## Implementation Strategy

### MVP (Minimum Viable Product)

1. Complete Phases 1-3 → Dual navigation working
2. Complete Phase 4 → GUI functional
3. Complete Phase 5 → CUI functional
4. **Deploy/Demo**: Both interfaces working

### Full Feature Set

5. Complete Phase 6 → Data sync verified
6. Complete Phase 7 → Landing page updated
7. Complete Phase 8 → Persistence verified
8. Complete Phase 9 → Documentation done

---

## Notes

- Backend code is unchanged (no new backend tasks)
- All changes are frontend-focused
- Existing Phase-3 CUI should continue working
- Phase-2 components need import path updates only
- Test each user story independently before moving on
