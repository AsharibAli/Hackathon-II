# Research: Todo AI Chatbot (Phase-3)

**Feature Branch**: `002-todo-ai-chatbot`
**Created**: 2025-12-19
**Status**: Complete

## Overview

This document captures research findings for integrating AI-powered conversational capabilities into the existing Phase-2 Todo application.

---

## 1. OpenAI Agents SDK Integration

### Decision
Use the **OpenAI Agents SDK** (Python) for AI agent orchestration.

### Rationale
- Official SDK from OpenAI designed for building AI agents
- Native tool/function calling support
- Streaming response support for real-time feedback
- Built-in conversation management primitives
- Active development and community support

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| LangChain | Heavier dependency, more complex abstraction for simple use case |
| Direct OpenAI API | Missing agent orchestration primitives, more boilerplate |
| Anthropic Claude | Constitution mandates OpenAI Agents SDK |

### Integration Pattern
```python
from openai import OpenAI
from agents import Agent, Runner

# Agent definition with MCP tools
agent = Agent(
    name="TodoAssistant",
    instructions="You help users manage their todo tasks...",
    tools=[add_task, list_tasks, complete_task, update_task, delete_task]
)

# Stateless execution (no in-memory state)
result = Runner.run_sync(agent, messages=conversation_history)
```

### Dependencies to Add
```toml
# pyproject.toml
"openai>=1.40.0"
"openai-agents>=0.1.0"  # OpenAI Agents SDK
```

---

## 2. MCP (Model Context Protocol) Implementation

### Decision
Use the **Official MCP SDK** for defining and exposing task operations as tools.

### Rationale
- Standard protocol for AI tool interaction
- Schema validation for inputs/outputs
- Structured JSON responses
- Compatible with OpenAI function calling format
- Constitution mandates MCP-based tool access (Principle IX)

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Custom function decorator | Non-standard, no schema validation |
| LangChain Tools | Different abstraction, not MCP-compliant |
| Direct function calls | Violates Constitution Principle IX (Tool-Driven AI Behavior) |

### Tool Schema Pattern
```python
from mcp import Tool, ToolResult
from pydantic import BaseModel

class AddTaskInput(BaseModel):
    user_id: str
    title: str
    description: str | None = None

@mcp_tool
def add_task(input: AddTaskInput) -> ToolResult:
    """Create a new task for the user."""
    # Database operation
    task = create_task_in_db(input.user_id, input.title, input.description)
    return ToolResult(success=True, data={"task_id": str(task.id), "title": task.title})
```

### Dependencies to Add
```toml
# pyproject.toml
"mcp>=1.0.0"  # Official MCP SDK
```

---

## 3. Chat UI Implementation

### Decision
Use **@assistant-ui/react** (ChatKit-style component library) for the chat interface.

### Rationale
- React-native components designed for AI chat interfaces
- Built-in message rendering, loading states, and streaming support
- Compatible with Next.js App Router
- Customizable with Tailwind CSS
- Lightweight compared to full chat SDKs

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Custom chat components | More development time, reinventing wheel |
| Vercel AI SDK Chat | Heavier integration, server components complexity |
| Raw textarea + messages | Poor UX, no streaming support |

### Integration Pattern
```tsx
import { AssistantRuntimeProvider, Thread } from "@assistant-ui/react";
import { useVercelAI } from "@assistant-ui/react-ai-sdk";

export function ChatInterface() {
  const runtime = useVercelAI({
    api: "/api/chat",
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <Thread />
    </AssistantRuntimeProvider>
  );
}
```

### Dependencies to Add
```json
{
  "@assistant-ui/react": "^0.5.0",
  "ai": "^3.0.0"  // Vercel AI SDK for streaming
}
```

---

## 4. Conversation Persistence Strategy

### Decision
Create new **Conversation** and **Message** SQLModel entities with database persistence.

### Rationale
- Constitution Principle X mandates conversation persistence
- Constitution Principle VIII mandates stateless server
- Enables horizontal scaling
- Supports conversation resumption across sessions

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Redis session storage | In-memory, not truly persistent |
| File-based storage | Not scalable, doesn't support multi-instance |
| Client-side only | Would lose history on logout, no cross-device sync |

### Schema Design
```python
class Conversation(SQLModel, table=True):
    id: UUID
    user_id: UUID  # FK to users
    created_at: datetime
    updated_at: datetime

class Message(SQLModel, table=True):
    id: UUID
    conversation_id: UUID  # FK to conversations
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime
```

---

## 5. Stateless Request Handling

### Decision
Fetch full conversation context from database on each request; no in-memory caching.

### Rationale
- Constitution Principle VIII mandates stateless server
- Enables horizontal scaling without session affinity
- Every request is self-contained
- Simplifies deployment and failover

### Request Flow
1. Receive chat request with user message
2. Extract user_id from JWT token
3. Fetch or create Conversation for user
4. Load recent Message history (last N messages)
5. Store user message in database
6. Build conversation context for AI agent
7. Execute agent with MCP tools
8. Store assistant response in database
9. Return response to client

### Performance Considerations
- Limit conversation history to last 50 messages for context window
- Use database indexing on (conversation_id, created_at)
- Consider connection pooling for database efficiency

---

## 6. Chat API Endpoint Design

### Decision
Single `POST /api/chat` endpoint for all chat interactions.

### Rationale
- Simple API surface
- Stateless (no session management)
- Compatible with streaming responses
- Constitution mandates JWT authentication

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| `/api/{user_id}/chat` | User ID should come from JWT, not URL |
| WebSocket connection | More complex, stateful by nature |
| Multiple endpoints per action | Unnecessary complexity, agent decides actions |

### Endpoint Design
```
POST /api/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
  "message": "Add a task to buy groceries"
}

Response:
{
  "id": "msg_uuid",
  "role": "assistant",
  "content": "I've added 'buy groceries' to your task list.",
  "created_at": "2025-12-19T10:00:00Z"
}
```

---

## 7. Error Handling Strategy

### Decision
AI agent communicates errors in natural language; API returns structured error responses for client handling.

### Rationale
- User-friendly error messages from agent
- Programmatic error handling for client
- Graceful degradation on AI service failures

### Error Categories
| Category | Handling |
|----------|----------|
| Authentication failure | 401 response, redirect to login |
| Rate limiting | 429 response, retry-after header |
| AI service unavailable | 503 response, friendly message |
| Tool execution error | Agent explains in natural language |
| Invalid input | 400 response with validation details |

---

## Summary of Technical Decisions

| Component | Decision | Key Dependency |
|-----------|----------|----------------|
| AI Agent | OpenAI Agents SDK | `openai-agents>=0.1.0` |
| Tool Protocol | Official MCP SDK | `mcp>=1.0.0` |
| Chat UI | @assistant-ui/react | `@assistant-ui/react>=0.5.0` |
| Persistence | SQLModel + PostgreSQL | Existing infrastructure |
| API Design | Single POST /api/chat | FastAPI |
| Authentication | JWT from existing Phase-2 | No changes |

---

## Outstanding Questions Resolved

All technical decisions are now complete. No NEEDS CLARIFICATION items remain.

## Next Steps

1. Create data-model.md with Conversation and Message entities
2. Create API contracts in contracts/
3. Create quickstart.md with setup instructions
4. Proceed to task generation with `/sp.tasks`
