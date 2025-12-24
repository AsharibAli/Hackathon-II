# Quickstart: Todo AI Chatbot (Phase-3)

**Feature Branch**: `002-todo-ai-chatbot`
**Created**: 2025-12-19
**Prerequisites**: Phase-2 application running successfully

## Overview

This guide walks through setting up the Phase-3 AI chatbot features on top of the existing Phase-2 Todo application.

---

## Prerequisites

Before starting, ensure you have:

1. **Phase-2 application running** (backend + frontend + database)
2. **OpenAI API key** with access to GPT-4 or gpt-4.1-2025-04-14
3. **Python 3.11+** with `uv` package manager
4. **Node.js 18+** with `pnpm` package manager
5. **Neon PostgreSQL** database with existing users and tasks

---

## Step 1: Backend Setup

### 1.1 Install New Dependencies

```bash
cd backend

# Add OpenAI Agents SDK and MCP SDK
uv add openai openai-agents mcp

# Verify installation
uv pip list | grep -E "(openai|mcp)"
# Or just run: uv sync
```

### 1.2 Configure Environment Variables

Add to `backend/.env`:

```env
# Existing Phase-2 variables...
DATABASE_URL=postgresql://...
JWT_SECRET=...

# New Phase-3 variables
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4.1-2025-04-14  # or gpt-4
```

### 1.3 Run Database Migration

```bash
cd backend

# Create migration for conversations and messages tables
uv run alembic revision --autogenerate -m "Add conversation and message tables for Phase-3"

# Apply migration
uv run alembic upgrade head

# Verify tables exist
# Connect to Neon and check: SELECT * FROM conversations LIMIT 1;
```

### 1.4 Start Backend Server

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

Verify the new endpoints are available:
- Open http://localhost:8000/docs
- Look for `/api/chat` and `/api/conversations` endpoints

---

## Step 2: Frontend Setup

### 2.1 Install New Dependencies

```bash
cd frontend

# Add chat UI components and AI SDK
pnpm add @assistant-ui/react ai

# Verify installation
pnpm list @assistant-ui/react ai
```

### 2.2 Configure Environment Variables

Add to `frontend/.env.local`:

```env
# Existing Phase-2 variables...
NEXT_PUBLIC_API_URL=http://localhost:8000

# No new frontend-specific env vars needed
# OpenAI calls go through backend
```

### 2.3 Start Frontend Server

```bash
cd frontend
pnpm dev
```

Open http://localhost:3000 to see the chat interface.

---

## Step 3: Verify Installation

### 3.1 Health Check

1. **Backend**: `curl http://localhost:8000/health` → `{"status": "ok"}`
2. **Frontend**: Open http://localhost:3000 → See chat interface

### 3.2 Test Chat Flow

1. Log in with an existing user account
2. In the chat interface, type: "Show me my tasks"
3. Verify the assistant responds with your task list (or indicates no tasks)
4. Type: "Add a task to test the AI chatbot"
5. Verify a new task is created and confirmed

### 3.3 Verify Database Persistence

1. Send a few chat messages
2. Refresh the page
3. Verify conversation history is still visible
4. Check database:
   ```sql
   SELECT * FROM conversations WHERE user_id = 'your-user-id';
   SELECT * FROM messages WHERE conversation_id = 'conversation-id';
   ```

---

## Step 4: Acceptance Test Scenarios

### Scenario 1: Natural Language Task Creation (P1)

**Test Steps:**
1. Log in as a test user
2. Type: "Add a task to buy groceries"
3. Verify assistant confirms task creation
4. Type: "Show my tasks"
5. Verify "buy groceries" appears in the list

**Expected Result:** Task created and visible in list

### Scenario 2: View Tasks via Chat (P2)

**Test Steps:**
1. Ensure user has at least 3 tasks (some completed, some pending)
2. Type: "Show me my tasks"
3. Verify all tasks are listed with completion status
4. Type: "List my incomplete tasks"
5. Verify only pending tasks are shown

**Expected Result:** Correct task filtering

### Scenario 3: Complete Task via Chat (P3)

**Test Steps:**
1. Create a task "test completion"
2. Type: "Mark test completion as done"
3. Verify assistant confirms completion
4. Type: "Show my completed tasks"
5. Verify "test completion" appears as completed

**Expected Result:** Task status updated

### Scenario 4: Conversation Continuity (P6)

**Test Steps:**
1. Send 5+ messages in a conversation
2. Note the last message content
3. Refresh the browser
4. Verify all messages are still visible
5. Verify conversation context is maintained

**Expected Result:** Messages persist across page refresh

---

## Troubleshooting

### Issue: Chat endpoint returns 401

**Cause:** JWT token missing or expired
**Solution:** Log out and log back in to get a fresh token

### Issue: AI service unavailable (503)

**Cause:** OpenAI API unreachable or rate limited
**Solution:**
1. Check `OPENAI_API_KEY` is valid
2. Check OpenAI status page
3. Wait and retry if rate limited

### Issue: Tasks not appearing in chat

**Cause:** MCP tools not properly registered
**Solution:**
1. Check backend logs for tool registration errors
2. Verify MCP tool implementations exist
3. Restart backend server

### Issue: Messages not persisting

**Cause:** Database migration not applied
**Solution:**
1. Run `uv run alembic upgrade head`
2. Verify `conversations` and `messages` tables exist
3. Check database connection in logs

---

## Development Tips

### Testing MCP Tools Directly

```python
# backend/tests/test_mcp_tools.py
from src.mcp.tools import add_task, list_tasks

def test_add_task():
    result = add_task(user_id="test-user-id", title="Test task")
    assert result["success"] == True
    assert result["task"]["title"] == "Test task"
```

### Viewing AI Agent Logs

Set log level in `backend/.env`:

```env
LOG_LEVEL=DEBUG
```

Agent tool calls and responses will be logged to console.

### Testing Streaming Responses

Use the browser's Network tab to observe streaming:
1. Open DevTools → Network tab
2. Send a chat message
3. Look for the `/api/chat` request
4. Check "EventStream" in response

---

## Next Steps

After successful verification:

1. Run `/sp.tasks` to generate implementation task list
2. Follow the task order for implementation
3. Run acceptance tests after each user story completion
