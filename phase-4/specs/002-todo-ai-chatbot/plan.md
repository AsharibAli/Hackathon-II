# Implementation Plan: Todo AI Chatbot

**Branch**: `002-todo-ai-chatbot` | **Date**: 2025-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todo-ai-chatbot/spec.md`

## Summary

Extend the Phase-2 Todo application with an AI-powered Conversational User Interface (CUI). Users will manage tasks via natural language through a chat interface. The AI agent interprets intent and invokes MCP tools for all task operations. All conversation state is persisted to PostgreSQL, ensuring stateless server architecture.

**Key Components:**
1. **Chat API** - Single POST `/api/chat` endpoint for all interactions
2. **MCP Tools** - 5 tools (add, list, complete, update, delete) for task operations
3. **Conversation Persistence** - New Conversation and Message database entities
4. **Chat UI** - @assistant-ui/react components replacing task CRUD UI

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK
- Frontend: Next.js 16, @assistant-ui/react, ai (Vercel AI SDK)

**Storage**: Neon PostgreSQL (existing) + new Conversation/Message tables
**Testing**: pytest (backend), manual acceptance testing (frontend)
**Target Platform**: Web (all modern browsers)
**Project Type**: Web application (monorepo with backend/ and frontend/)
**Performance Goals**: <5s task creation, <3s task listing via chat
**Constraints**: Stateless server (no in-memory state), JWT authentication required
**Scale/Scope**: Single user conversation at a time, unlimited message history

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-First Development | ✅ PASS | Specification approved before planning |
| II. Single Code Authority | ✅ PASS | Claude Code performs all implementation |
| III. Separation of Concerns | ✅ PASS | Backend: AI/MCP/API; Frontend: Chat UI only |
| IV. Authentication & Authorization | ✅ PASS | JWT required on /api/chat; user_id from token |
| V. Test-First When Specified | ✅ PASS | Tests not explicitly required; manual acceptance |
| VI. Database Persistence First | ✅ PASS | Conversation/Message in PostgreSQL |
| VII. Observability & Debuggability | ✅ PASS | Structured logging for AI tool calls |
| VIII. Stateless Server Architecture | ✅ PASS | No in-memory state; DB-backed conversations |
| IX. Tool-Driven AI Behavior | ✅ PASS | All task ops via MCP tools only |
| X. Conversation Persistence | ✅ PASS | Messages stored in database |

**Constraint Validations:**
- ✅ TypeScript strict mode (existing from Phase-2)
- ✅ FastAPI with CORS, middleware, exception handlers (existing)
- ✅ SQLModel with proper type annotations (existing + new entities)
- ✅ JWT authentication (existing from Phase-2)
- ✅ Neon database connection (existing)
- ✅ OpenAI Agents SDK configured (new - API key in .env)
- ✅ MCP server exposes task tools (new - 5 tools defined)
- ✅ Chat UI renders message history (new - @assistant-ui/react)

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-ai-chatbot/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology research findings
├── data-model.md        # Conversation/Message entity definitions
├── quickstart.md        # Setup and verification guide
├── contracts/
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoints
│   └── mcp-tools.md     # MCP tool definitions
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py          # Existing - add conversations relationship
│   │   ├── task.py          # Existing - unchanged
│   │   ├── conversation.py  # NEW - Conversation entity
│   │   └── message.py       # NEW - Message entity
│   ├── services/
│   │   ├── auth.py          # Existing - unchanged
│   │   ├── tasks.py         # Existing - unchanged
│   │   ├── chat.py          # NEW - Chat orchestration service
│   │   └── conversations.py # NEW - Conversation CRUD service
│   ├── api/
│   │   ├── auth.py          # Existing - unchanged
│   │   ├── tasks.py         # Existing - unchanged
│   │   └── chat.py          # NEW - POST /api/chat endpoint
│   ├── mcp/
│   │   ├── __init__.py      # NEW - MCP module init
│   │   ├── tools.py         # NEW - MCP tool implementations
│   │   └── agent.py         # NEW - AI agent configuration
│   ├── core/
│   │   ├── config.py        # Existing - add OPENAI_API_KEY
│   │   ├── database.py      # Existing - unchanged
│   │   └── security.py      # Existing - unchanged
│   ├── middleware/          # Existing - unchanged
│   └── main.py              # Existing - add chat router
├── alembic/
│   └── versions/
│       └── xxx_add_conversation_tables.py  # NEW - Migration
└── tests/
    └── test_mcp_tools.py    # NEW - Tool unit tests (optional)

frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx         # MODIFY - Replace TaskList with ChatInterface
│   │   ├── layout.tsx       # Existing - unchanged
│   │   └── (auth)/          # Existing - unchanged
│   ├── components/
│   │   ├── ChatInterface.tsx    # NEW - Main chat component
│   │   ├── ChatMessage.tsx      # NEW - Individual message display
│   │   ├── ChatInput.tsx        # NEW - Message input field
│   │   ├── TaskList.tsx         # Existing - keep for reference/fallback
│   │   ├── TaskItem.tsx         # Existing - unchanged
│   │   └── ui/                  # Existing - unchanged
│   ├── lib/
│   │   ├── api.ts           # MODIFY - Add chat API client
│   │   └── auth.ts          # Existing - unchanged
│   └── types/
│       ├── task.ts          # Existing - unchanged
│       └── chat.ts          # NEW - Chat type definitions
└── package.json             # MODIFY - Add @assistant-ui/react, ai
```

**Structure Decision**: Web application structure with backend/ and frontend/ directories. Phase-3 adds new modules (mcp/, chat components) while preserving all Phase-2 code intact.

## Complexity Tracking

> **No violations detected.** All design decisions comply with constitution principles.

| Potential Complexity | Resolution |
|---------------------|------------|
| AI agent state management | Resolved: Stateless - fetch history from DB per request |
| Tool-to-function mapping | Resolved: MCP SDK provides clean abstraction |
| Streaming responses | Resolved: @assistant-ui/react handles streaming natively |

## Implementation Phases Overview

### Phase 3.1: Backend Foundation
- Add new dependencies (OpenAI Agents SDK, MCP SDK)
- Create Conversation and Message models
- Run database migration
- Update configuration with OpenAI settings

### Phase 3.2: MCP Tools Implementation
- Create MCP module structure
- Implement 5 task management tools
- Configure AI agent with tools
- Add structured logging for tool calls

### Phase 3.3: Chat API Implementation
- Create chat service for orchestration
- Create conversation service for persistence
- Implement POST /api/chat endpoint
- Implement GET /api/conversations endpoint
- Add JWT authentication to chat routes

### Phase 3.4: Frontend Chat UI
- Add frontend dependencies (@assistant-ui/react, ai)
- Create chat type definitions
- Implement ChatInterface component
- Update API client with chat methods
- Replace main page with chat interface

### Phase 3.5: Validation & Polish
- Verify stateless architecture
- Test all MCP tools via chat
- Test conversation persistence
- Run acceptance scenarios from spec
- Error handling and edge cases

## Dependencies Summary

### Backend Dependencies (pyproject.toml)

```toml
# New Phase-3 dependencies
"openai>=1.40.0",
"openai-agents>=0.1.0",
"mcp>=1.0.0",
```

### Frontend Dependencies (package.json)

```json
{
  "@assistant-ui/react": "^0.5.0",
  "ai": "^3.0.0"
}
```

## Environment Variables

### Backend (.env)

```env
# Existing
DATABASE_URL=postgresql://...
JWT_SECRET=...

# New
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-2025-04-14
```

## API Endpoints Summary

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/chat | Send message, get AI response | JWT |
| GET | /api/conversations | Get conversation history | JWT |

## MCP Tools Summary

| Tool | Purpose | Inputs |
|------|---------|--------|
| add_task | Create new task | user_id, title, description? |
| list_tasks | Get all user tasks | user_id, completed? |
| complete_task | Mark task done | user_id, task_identifier |
| update_task | Modify task | user_id, task_identifier, title?, description? |
| delete_task | Remove task | user_id, task_identifier |

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| OpenAI API rate limits | Implement retry with exponential backoff |
| Long AI response times | Show loading state; implement timeout |
| Ambiguous task matching | Return multiple matches for user clarification |
| Large conversation history | Limit context to last 50 messages |

## Definition of Done

- [ ] All MCP tools implemented and returning structured JSON
- [ ] Chat endpoint accepts messages and returns AI responses
- [ ] Conversation and messages persist in database
- [ ] Chat UI displays conversation history
- [ ] Page refresh preserves conversation
- [ ] All acceptance scenarios from spec passing
- [ ] No hardcoded secrets (all from .env)
- [ ] Constitution principles validated

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement in phase order (3.1 → 3.2 → 3.3 → 3.4 → 3.5)
3. Run acceptance tests after each phase
4. Document any ADRs for significant decisions
