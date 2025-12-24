# Advanced Todo Backend API

FastAPI-based REST API for the Advanced Todo Application with AI-powered chat functionality.

## Tech Stack

- **Framework:** FastAPI 0.125+
- **ORM:** SQLModel 0.0.14+
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **AI Integration:** OpenAI Agents SDK + MCP Tools
- **Migrations:** Alembic
- **Package Manager:** uv

## Features

- **User Authentication** - JWT-based registration, login, logout
- **Task Management** - Full CRUD operations for tasks
- **AI Chat** - Natural language task management via OpenAI
- **MCP Tools** - 5 tools for AI-driven task operations
- **Conversation Persistence** - Chat history stored in database
- **Multi-User Isolation** - Each user's data is private

## Project Structure

```
backend/
├── src/
│   ├── api/                  # API endpoints
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── tasks.py          # Task CRUD endpoints (GUI)
│   │   ├── chat.py           # Chat endpoint (CUI)
│   │   ├── conversations.py  # Conversation management
│   │   └── dependencies.py   # Auth dependency injection
│   ├── core/                 # Core utilities
│   │   ├── config.py         # Environment configuration
│   │   ├── database.py       # Database setup
│   │   └── security.py       # JWT & password hashing
│   ├── middleware/           # Custom middleware
│   │   ├── logging.py        # Request logging
│   │   └── errors.py         # Error handling
│   ├── models/               # SQLModel entities
│   │   ├── user.py           # User model
│   │   ├── task.py           # Task model
│   │   ├── conversation.py   # Conversation model
│   │   └── message.py        # Message model
│   ├── services/             # Business logic
│   │   ├── auth.py           # Auth service
│   │   ├── tasks.py          # Tasks service
│   │   ├── chat.py           # Chat orchestration
│   │   └── conversations.py  # Conversation service
│   ├── mcp/                  # AI Agent & Tools
│   │   ├── agent.py          # OpenAI agent configuration
│   │   └── tools.py          # MCP tool implementations
│   └── main.py               # Application entry point
├── alembic/                  # Database migrations
├── tests/                    # pytest tests
└── pyproject.toml            # Dependencies
```

## Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# JWT Configuration
JWT_SECRET=your-secret-key-here-minimum-32-characters-required
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OpenAI Configuration (for CUI mode)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4.1-2025-04-14

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Application Settings
APP_NAME=Advanced Todo API
APP_VERSION=1.0.0
DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Setup

### Prerequisites

- Python 3.11+
- uv package manager: `pip install uv`
- Neon PostgreSQL account: https://neon.tech
- OpenAI API key: https://platform.openai.com

### Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies (creates .venv automatically)
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your credentials
```

### Database Setup

```bash
# Run database migrations
uv run alembic upgrade head
```

### Development

```bash
# Start development server with auto-reload
uv run uvicorn src.main:app --reload --port 8000
```

The API will be available at:
- **Base URL:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/logout` | Logout user (requires auth) |
| GET | `/api/auth/me` | Get current user profile |
| PUT | `/api/auth/me` | Update user profile |

### Tasks (GUI Mode)

All task endpoints require JWT authentication.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks for authenticated user |
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks/{task_id}` | Get specific task |
| PUT | `/api/tasks/{task_id}` | Update task |
| DELETE | `/api/tasks/{task_id}` | Delete task |
| PATCH | `/api/tasks/{task_id}/complete` | Toggle completion status |

### Chat (CUI Mode)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/chat` | Send message to AI assistant |
| GET | `/api/chat/conversations` | Get conversation with messages |

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/conversations` | List all conversations |
| POST | `/api/conversations` | Create new conversation |
| GET | `/api/conversations/{id}` | Get conversation with messages |
| PUT | `/api/conversations/{id}` | Rename conversation |
| DELETE | `/api/conversations/{id}` | Delete conversation |

## MCP Tools

The AI agent uses 5 MCP (Model Context Protocol) tools for task operations:

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_task` | Create new task | `title`, `description?` |
| `list_tasks` | Get all user tasks | `completed?` (filter) |
| `complete_task` | Mark task as done | `task_identifier` |
| `update_task` | Modify task | `task_identifier`, `title?`, `description?` |
| `delete_task` | Remove task | `task_identifier` |

**Security:** All tools receive `user_id` from JWT token (never from user input).

## Database Schema

```
users
├── id (UUID, PK)
├── email (unique, indexed)
├── hashed_password
├── full_name
├── profile_picture
├── is_active
├── created_at
└── updated_at

tasks
├── id (UUID, PK)
├── user_id (FK → users.id)
├── title
├── description
├── is_completed
├── created_at
└── updated_at

conversations
├── id (UUID, PK)
├── user_id (FK → users.id)
├── title
├── created_at
└── updated_at

messages
├── id (UUID, PK)
├── conversation_id (FK → conversations.id)
├── role ('user' | 'assistant')
├── content
└── created_at
```

## Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

## Security

- JWT tokens expire after 24 hours (configurable)
- Passwords hashed with bcrypt (cost factor 12)
- Multi-user isolation enforced at service layer
- All task/chat endpoints require authentication
- CORS configured for frontend origin only
- User ID extracted from JWT, never from request body

## Production Deployment

1. Set `DEBUG=False` in environment variables
2. Use a strong `JWT_SECRET` (min 32 characters)
3. Configure proper `DATABASE_URL` for production database
4. Set `OPENAI_API_KEY` for production
5. Set appropriate `CORS_ORIGINS`
6. Use a production ASGI server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Error Handling

All API errors return structured JSON:

```json
{
  "detail": "Human-readable error message"
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `404` - Not Found
- `500` - Internal Server Error
