# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/002-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/

**Tests**: Tests are NOT explicitly required in the specification. Implementation-only tasks below.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and dependency installation

- [ ] T001 [P] Add OpenAI and MCP dependencies to backend/pyproject.toml
- [ ] T002 [P] Add @assistant-ui/react and ai dependencies to frontend/package.json
- [ ] T003 [P] Add OPENAI_API_KEY and OPENAI_MODEL to backend/.env.example
- [ ] T004 Update backend/src/core/config.py to load OpenAI settings from environment

**Checkpoint**: Dependencies installed, configuration updated

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [ ] T005 [P] Create Conversation model in backend/src/models/conversation.py
- [ ] T006 [P] Create Message model in backend/src/models/message.py
- [ ] T007 Update User model to add conversations relationship in backend/src/models/user.py
- [ ] T008 Export new models in backend/src/models/__init__.py
- [ ] T009 Create database migration for conversations and messages tables in backend/alembic/versions/

### MCP Module Structure

- [ ] T010 Create MCP module init file in backend/src/mcp/__init__.py
- [ ] T011 Create MCP tools base structure in backend/src/mcp/tools.py (empty implementations)
- [ ] T012 Create AI agent configuration in backend/src/mcp/agent.py

### Services

- [ ] T013 Create conversation service in backend/src/services/conversations.py (get_or_create, store_message, get_recent_messages)
- [ ] T014 Create chat orchestration service in backend/src/services/chat.py (process_message skeleton)

### Frontend Types

- [ ] T015 Create chat type definitions in frontend/src/types/chat.ts (Message, Conversation, ChatRequest, ChatResponse)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by typing natural language like "Add a task to buy groceries"

**Independent Test**: Send "Add a task to buy groceries" and verify task appears in database

### MCP Tool Implementation

- [ ] T016 [US1] Implement add_task MCP tool in backend/src/mcp/tools.py

### Agent Configuration

- [ ] T017 [US1] Configure AI agent with add_task tool and system instructions in backend/src/mcp/agent.py

### Chat Service Integration

- [ ] T018 [US1] Implement chat orchestration logic in backend/src/services/chat.py (load history, invoke agent, store response)

### API Endpoint

- [ ] T019 [US1] Create POST /api/chat endpoint in backend/src/api/chat.py
- [ ] T020 [US1] Register chat router in backend/src/main.py

### Frontend Chat UI

- [ ] T021 [P] [US1] Create ChatMessage component in frontend/src/components/ChatMessage.tsx
- [ ] T022 [P] [US1] Create ChatInput component in frontend/src/components/ChatInput.tsx
- [ ] T023 [US1] Create ChatInterface component in frontend/src/components/ChatInterface.tsx
- [ ] T024 [US1] Add chat API client methods to frontend/src/lib/api.ts (sendMessage, getConversation)
- [ ] T025 [US1] Replace main page content with ChatInterface in frontend/src/app/page.tsx

**Checkpoint**: User Story 1 complete - users can create tasks via chat

---

## Phase 4: User Story 2 - Viewing Tasks via Chat (Priority: P2)

**Goal**: Users can ask "Show me my tasks" and see their task list in chat

**Independent Test**: Send "Show me my tasks" and verify assistant lists all user's tasks

### MCP Tool Implementation

- [ ] T026 [US2] Implement list_tasks MCP tool in backend/src/mcp/tools.py

### Agent Update

- [ ] T027 [US2] Register list_tasks tool with AI agent in backend/src/mcp/agent.py

**Checkpoint**: User Story 2 complete - users can view tasks via chat

---

## Phase 5: User Story 3 - Completing Tasks via Chat (Priority: P3)

**Goal**: Users can say "Mark 'buy groceries' as done" to complete tasks

**Independent Test**: Create a task, send "Mark it as complete", verify is_completed=true

### MCP Tool Implementation

- [ ] T028 [US3] Implement complete_task MCP tool with fuzzy matching in backend/src/mcp/tools.py

### Agent Update

- [ ] T029 [US3] Register complete_task tool with AI agent in backend/src/mcp/agent.py

**Checkpoint**: User Story 3 complete - users can complete tasks via chat

---

## Phase 6: User Story 4 - Updating Tasks via Chat (Priority: P4)

**Goal**: Users can say "Rename 'call mom' to 'call mom about birthday'" to update tasks

**Independent Test**: Create a task, send rename command, verify title changed

### MCP Tool Implementation

- [ ] T030 [US4] Implement update_task MCP tool in backend/src/mcp/tools.py

### Agent Update

- [ ] T031 [US4] Register update_task tool with AI agent in backend/src/mcp/agent.py

**Checkpoint**: User Story 4 complete - users can update tasks via chat

---

## Phase 7: User Story 5 - Deleting Tasks via Chat (Priority: P5)

**Goal**: Users can say "Delete the 'old task'" to remove tasks

**Independent Test**: Create a task, send delete command, verify task removed from database

### MCP Tool Implementation

- [ ] T032 [US5] Implement delete_task MCP tool in backend/src/mcp/tools.py

### Agent Update

- [ ] T033 [US5] Register delete_task tool with AI agent in backend/src/mcp/agent.py

**Checkpoint**: User Story 5 complete - full CRUD via chat operational

---

## Phase 8: User Story 6 - Conversation Continuity (Priority: P6)

**Goal**: Chat history persists across page refreshes and sessions

**Independent Test**: Send 5 messages, refresh page, verify all messages still visible

### Backend Endpoint

- [ ] T034 [US6] Create GET /api/conversations endpoint in backend/src/api/chat.py

### Frontend Persistence

- [ ] T035 [US6] Load conversation history on ChatInterface mount in frontend/src/components/ChatInterface.tsx
- [ ] T036 [US6] Display loading state while fetching history in frontend/src/components/ChatInterface.tsx

**Checkpoint**: User Story 6 complete - conversation persistence working

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and validation

### Error Handling

- [ ] T037 [P] Add error handling for OpenAI API failures in backend/src/services/chat.py
- [ ] T038 [P] Add user-friendly error display in frontend/src/components/ChatInterface.tsx
- [ ] T039 [P] Add loading indicator while AI is processing in frontend/src/components/ChatInterface.tsx

### Edge Cases

- [ ] T040 Handle empty message validation in backend/src/api/chat.py
- [ ] T041 Handle ambiguous task matching (multiple matches) in MCP tools in backend/src/mcp/tools.py

### Logging

- [ ] T042 Add structured logging for MCP tool invocations in backend/src/mcp/tools.py

### Final Validation

- [ ] T043 Run database migration on development database
- [ ] T044 Run acceptance scenarios from specs/002-todo-ai-chatbot/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (BLOCKS all user stories)
    ↓
Phase 3: US1 - Task Creation (MVP) ─────┐
    ↓                                    │
Phase 4: US2 - View Tasks                │ Can run in
    ↓                                    │ parallel if
Phase 5: US3 - Complete Tasks            │ team allows
    ↓                                    │
Phase 6: US4 - Update Tasks              │
    ↓                                    │
Phase 7: US5 - Delete Tasks ─────────────┘
    ↓
Phase 8: US6 - Conversation Persistence
    ↓
Phase 9: Polish & Validation
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (P1) | Phase 2 | Foundational complete |
| US2 (P2) | US1 | US1 complete (needs chat infrastructure) |
| US3 (P3) | US1 | US1 complete |
| US4 (P4) | US1 | US1 complete |
| US5 (P5) | US1 | US1 complete |
| US6 (P6) | US1 | US1 complete |

### Within Each User Story

1. MCP tool implementation
2. Agent configuration update
3. API endpoint (if needed)
4. Frontend integration (if needed)

### Parallel Opportunities

**Phase 1 (all parallel):**
```
T001: Add backend dependencies
T002: Add frontend dependencies
T003: Add .env.example entries
```

**Phase 2 (models parallel, then sequential):**
```
T005 + T006: Create Conversation and Message models
    ↓
T007: Update User model (depends on T005)
    ↓
T009: Create migration (depends on T005, T006, T007)
```

**Phase 3 US1 Frontend (parallel components):**
```
T021 + T022: ChatMessage and ChatInput components
    ↓
T023: ChatInterface (depends on T021, T022)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test task creation via chat
5. Deploy/demo if ready

### Incremental Delivery

| Increment | Stories Complete | Capability |
|-----------|-----------------|------------|
| MVP | US1 | Create tasks via chat |
| v0.2 | US1, US2 | Create + view tasks |
| v0.3 | US1-US3 | Create + view + complete |
| v0.4 | US1-US5 | Full CRUD via chat |
| v1.0 | All | Full CRUD + persistence |

### Task Count Summary

| Phase | Tasks | Parallel | Sequential |
|-------|-------|----------|------------|
| Phase 1: Setup | 4 | 3 | 1 |
| Phase 2: Foundational | 11 | 4 | 7 |
| Phase 3: US1 | 10 | 2 | 8 |
| Phase 4: US2 | 2 | 0 | 2 |
| Phase 5: US3 | 2 | 0 | 2 |
| Phase 6: US4 | 2 | 0 | 2 |
| Phase 7: US5 | 2 | 0 | 2 |
| Phase 8: US6 | 3 | 0 | 3 |
| Phase 9: Polish | 8 | 3 | 5 |
| **Total** | **44** | **12** | **32** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
