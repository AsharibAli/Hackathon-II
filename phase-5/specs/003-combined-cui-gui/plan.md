# Implementation Plan: Combined CUI & GUI Todo Application

**Branch**: `003-combined-cui-gui` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-combined-cui-gui/spec.md`

## Summary

Integrate the **AI-powered Conversational User Interface (CUI)** from Phase-3 with the **Graphical User Interface (GUI)** from Phase-2 into a unified Advanced Todo Application. Users can seamlessly switch between:
- **CUI Mode**: ChatGPT-style natural language task management
- **GUI Mode**: Traditional forms, buttons, and dialogs for direct task manipulation

Both interfaces share the same backend, database, and authentication system.

**Key Components:**
1. **Dual-Mode Navigation** - Tab/button navigation to switch between CUI and GUI
2. **GUI Components** - TaskList, TaskForm, EditTaskDialog, DeleteTaskDialog from Phase-2
3. **CUI Components** - ChatInterface, ChatInput, ChatMessage, Sidebar from Phase-3
4. **Shared Data Layer** - Both modes use the same Task API and database
5. **Updated Landing Page** - Highlights both CUI and GUI capabilities

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK (unchanged from Phase-3)
- Frontend: Next.js 16, React 19, shadcn/ui, Tailwind CSS 4

**Storage**: Neon PostgreSQL (existing - User, Task, Conversation, Message tables)
**Testing**: pytest (backend), manual acceptance testing (frontend)
**Target Platform**: Web (all modern browsers)
**Project Type**: Web application (monorepo with backend/ and frontend/)
**Performance Goals**: <1s mode switch, <500ms GUI operations, <5s CUI responses
**Constraints**: Stateless server, JWT authentication, data consistency between modes
**Scale/Scope**: Single user with unlimited tasks and conversations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-First Development | ✅ PASS | Specification approved before planning |
| II. Single Code Authority | ✅ PASS | Claude Code performs all implementation |
| III. Separation of Concerns | ✅ PASS | CUI and GUI as separate component modules |
| IV. Authentication & Authorization | ✅ PASS | JWT required for both modes |
| V. Test-First When Specified | ✅ PASS | Manual acceptance testing defined |
| VI. Database Persistence First | ✅ PASS | All data in PostgreSQL |
| VII. Observability & Debuggability | ✅ PASS | Existing logging middleware |
| VIII. Stateless Server Architecture | ✅ PASS | No in-memory state |
| IX. Tool-Driven AI Behavior | ✅ PASS | CUI uses MCP tools only |
| X. Conversation Persistence | ✅ PASS | Messages stored in database |

**Constraint Validations:**
- ✅ TypeScript strict mode (existing)
- ✅ FastAPI with CORS, middleware, exception handlers (existing)
- ✅ SQLModel with proper type annotations (existing)
- ✅ JWT authentication (existing)
- ✅ Neon database connection (existing)
- ✅ OpenAI Agents SDK configured (existing from Phase-3)
- ✅ MCP tools for task operations (existing from Phase-3)
- ✅ Chat UI components (existing from Phase-3)
- ✅ Task UI components (to be integrated from Phase-2)

## Project Structure

### Documentation (this feature)

```text
specs/003-combined-cui-gui/
├── spec.md              # Feature specification
├── plan.md              # This file
├── data-model.md        # No changes needed (using existing models)
├── quickstart.md        # Setup and verification guide
├── contracts/
│   └── navigation.md    # Navigation component specification
├── checklists/
│   └── requirements.md  # Feature checklist
└── tasks.md             # Phase 4 task breakdown
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/             # UNCHANGED - User, Task, Conversation, Message
│   ├── services/           # UNCHANGED - auth, tasks, chat, conversations
│   ├── api/                # UNCHANGED - auth, tasks, chat, conversations
│   ├── mcp/                # UNCHANGED - agent, tools
│   ├── core/               # UNCHANGED - config, database, security
│   ├── middleware/         # UNCHANGED - errors, logging
│   └── main.py             # UNCHANGED
├── alembic/                # No new migrations needed
└── README.md               # UPDATE - Add dual-mode documentation

frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx            # MODIFY - Landing page with CUI+GUI info
│   │   ├── (app)/
│   │   │   ├── page.tsx        # MODIFY - Dual-mode main application
│   │   │   └── layout.tsx      # MODIFY - Add mode navigation
│   │   ├── layout.tsx          # UNCHANGED
│   │   └── (auth)/             # UNCHANGED
│   ├── components/
│   │   ├── chat/               # EXISTING - CUI components
│   │   │   ├── ChatLayout.tsx      # MODIFY - Integrate with mode switching
│   │   │   ├── Sidebar.tsx         # UNCHANGED
│   │   │   ├── WelcomeScreen.tsx   # UNCHANGED
│   │   │   └── ConversationItem.tsx # UNCHANGED
│   │   ├── tasks/              # NEW - GUI components folder
│   │   │   ├── TaskList.tsx        # NEW - From Phase-2
│   │   │   ├── TaskItem.tsx        # NEW - From Phase-2
│   │   │   ├── TaskForm.tsx        # NEW - From Phase-2
│   │   │   ├── EditTaskDialog.tsx  # NEW - From Phase-2
│   │   │   └── DeleteTaskDialog.tsx # NEW - From Phase-2
│   │   ├── navigation/         # NEW - Mode navigation components
│   │   │   ├── ModeToggle.tsx      # NEW - Tab/button to switch modes
│   │   │   └── AppHeader.tsx       # NEW - Header with navigation
│   │   ├── ChatInterface.tsx   # UNCHANGED
│   │   ├── ChatInput.tsx       # UNCHANGED
│   │   ├── ChatMessage.tsx     # UNCHANGED
│   │   ├── AuthForm.tsx        # UNCHANGED
│   │   ├── ErrorBoundary.tsx   # UNCHANGED
│   │   ├── Providers.tsx       # UNCHANGED
│   │   └── ui/                 # UNCHANGED - shadcn/ui components
│   ├── lib/
│   │   ├── api.ts              # MODIFY - Ensure task endpoints work
│   │   ├── auth.ts             # UNCHANGED
│   │   └── utils.ts            # UNCHANGED
│   └── types/
│       ├── task.ts             # UNCHANGED (verify exists)
│       └── chat.ts             # UNCHANGED
├── package.json                # UNCHANGED (all deps already present)
└── README.md                   # UPDATE - Add dual-mode documentation
```

**Structure Decision**: Web application structure with backend/ and frontend/ directories. Phase-4 adds GUI components from Phase-2 and navigation components while preserving all Phase-3 code intact.

## Complexity Tracking

> **No violations detected.** All design decisions comply with constitution principles.

| Potential Complexity | Resolution |
|---------------------|------------|
| Data synchronization between modes | Resolved: Both use same API endpoints |
| Mode state management | Resolved: Client-side routing/state |
| Component organization | Resolved: Separate folders for chat/ and tasks/ |
| Landing page redesign | Resolved: Update existing page.tsx |

## Implementation Phases Overview

### Phase 4.1: Project Setup & Component Migration
- Verify phase-4 has all Phase-3 code
- Create tasks/ component folder structure
- Copy and adapt GUI components from Phase-2 (TaskList, TaskItem, TaskForm, EditTaskDialog, DeleteTaskDialog)
- Update imports and paths for Phase-4 context

### Phase 4.2: Navigation System
- Create navigation/ component folder
- Implement ModeToggle component (tabs or buttons for CUI/GUI)
- Implement AppHeader component with navigation
- Integrate navigation into app layout

### Phase 4.3: GUI Mode Implementation
- Create GUI mode page/view
- Wire up TaskList to fetch tasks from existing API
- Wire up TaskForm to create tasks via API
- Wire up TaskItem with edit/delete/complete actions
- Wire up EditTaskDialog and DeleteTaskDialog
- Test all GUI CRUD operations

### Phase 4.4: Dual-Mode Integration
- Implement mode switching logic
- Ensure state/data refreshes when switching modes
- Test data consistency between modes
- Handle edge cases (loading states, errors)

### Phase 4.5: Landing Page Update
- Update landing page title: "Advanced Todo Application with CUI & GUI"
- Add feature sections for both CUI and GUI
- Update call-to-action buttons
- Update hero section content
- Ensure responsive design

### Phase 4.6: Documentation & Polish
- Update root README.md
- Update frontend README.md
- Update backend README.md
- Create quickstart.md
- Final acceptance testing

## Component Integration Plan

### From Phase-2 (GUI Components to Integrate)

| Component | Source | Destination | Modifications |
|-----------|--------|-------------|---------------|
| TaskList.tsx | phase-2/frontend/src/components/ | phase-4/frontend/src/components/tasks/ | Update API imports |
| TaskItem.tsx | phase-2/frontend/src/components/ | phase-4/frontend/src/components/tasks/ | Update API imports |
| TaskForm.tsx | phase-2/frontend/src/components/ | phase-4/frontend/src/components/tasks/ | Update API imports |
| EditTaskDialog.tsx | phase-2/frontend/src/components/ | phase-4/frontend/src/components/tasks/ | Update API imports |
| DeleteTaskDialog.tsx | phase-2/frontend/src/components/ | phase-4/frontend/src/components/tasks/ | Update API imports |

### New Components to Create

| Component | Purpose | Location |
|-----------|---------|----------|
| ModeToggle.tsx | Tab/button navigation between CUI and GUI | components/navigation/ |
| AppHeader.tsx | Header with logo, navigation, user menu | components/navigation/ |
| TasksView.tsx | Container for GUI mode (wraps TaskList, TaskForm) | components/tasks/ |

## API Endpoints Summary

| Method | Path | Description | Used By |
|--------|------|-------------|---------|
| POST | /api/auth/register | User registration | Both |
| POST | /api/auth/login | User login | Both |
| POST | /api/auth/logout | User logout | Both |
| GET | /api/auth/me | Get current user | Both |
| GET | /api/tasks | Get all user tasks | GUI |
| POST | /api/tasks | Create task | GUI |
| PUT | /api/tasks/{id} | Update task | GUI |
| DELETE | /api/tasks/{id} | Delete task | GUI |
| PATCH | /api/tasks/{id}/complete | Toggle completion | GUI |
| POST | /api/chat | Send chat message | CUI |
| GET | /api/conversations | Get conversation list | CUI |
| GET | /api/conversations/{id} | Get conversation with messages | CUI |
| PUT | /api/conversations/{id} | Rename conversation | CUI |
| DELETE | /api/conversations/{id} | Delete conversation | CUI |

## Landing Page Content Plan

```text
Header:
  - Logo: "Advanced Todo Application"
  - Navigation: "Sign In" | "Get Started" buttons

Hero Section:
  - Title: "Manage tasks with AI Chat or Traditional UI"
  - Subtitle: "The most flexible todo app - choose how you work"
  - CTA: "Start for Free" | "Sign In"

Features Section (3 columns):
  1. AI Chat (CUI)
     - Icon: MessageSquare or Bot
     - Title: "Conversational AI"
     - Description: "Chat naturally with AI to manage tasks"

  2. Traditional UI (GUI)
     - Icon: LayoutList or CheckSquare
     - Title: "Classic Interface"
     - Description: "Forms, buttons, and familiar controls"

  3. Seamless Switching
     - Icon: RefreshCw or Toggle
     - Title: "Switch Anytime"
     - Description: "Both interfaces share your tasks"

Footer:
  - Copyright: "© 2025 Advanced Todo Application. Powered by AI."
```

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| Component compatibility issues | Test each component individually after migration |
| CSS/styling conflicts | Use scoped styles, separate component folders |
| API endpoint differences | Verify all endpoints work, use shared api.ts |
| Mode state management bugs | Simple state management, no complex state libraries |
| Data sync delays | Refresh data on mode switch |

## Definition of Done

- [ ] All Phase-2 GUI components migrated and working
- [ ] Navigation between CUI and GUI modes functional
- [ ] Tasks created in GUI appear in CUI (and vice versa)
- [ ] Landing page updated with dual-interface messaging
- [ ] All acceptance scenarios from spec passing
- [ ] README files updated for all three levels (root, frontend, backend)
- [ ] No regressions in existing CUI functionality
- [ ] Responsive design works on mobile and desktop

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement in phase order (4.1 → 4.2 → 4.3 → 4.4 → 4.5 → 4.6)
3. Test each phase before moving to next
4. Run final acceptance tests against spec
