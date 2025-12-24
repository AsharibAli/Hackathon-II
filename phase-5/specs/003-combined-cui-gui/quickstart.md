# Quickstart: Advanced Todo Application with CUI & GUI

**Feature Branch**: `003-combined-cui-gui`
**Date**: 2025-12-23

## Prerequisites

Before starting, ensure you have:

- **Node.js** 18+ installed
- **Python** 3.11+ installed
- **pnpm** package manager (`npm install -g pnpm`)
- **uv** Python package manager
- **PostgreSQL** database (Neon recommended)
- **OpenAI API Key** for CUI functionality

## Quick Setup

### 1. Clone and Navigate

```bash
cd phase-4
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies (creates .venv automatically)
uv sync

# Copy environment file
cp .env.example .env

# Edit .env with your credentials:
# - DATABASE_URL=postgresql://...
# - JWT_SECRET=your-secret-key
# - OPENAI_API_KEY=sk-...

# Run database migrations
uv run alembic upgrade head

# Start backend server
uv run uvicorn src.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
pnpm install

# Copy environment file (if not exists)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend server
pnpm dev
```

### 4. Access the Application

Open your browser to: **http://localhost:3000**

## Verification Steps

### Verify Dual-Mode Navigation

1. Register a new account or log in
2. Verify you see navigation options for "Chat" and "Tasks"
3. Click between modes and confirm switching works

### Verify GUI Mode

1. Navigate to "Tasks" (GUI) mode
2. Create a new task using the form
3. Mark the task as complete using the checkbox
4. Edit the task title/description
5. Delete the task with confirmation

### Verify CUI Mode

1. Navigate to "Chat" (CUI) mode
2. Type: "Add a task to buy groceries"
3. Verify task creation confirmation
4. Type: "Show me my tasks"
5. Verify your tasks are listed

### Verify Data Synchronization

1. In CUI mode: "Add a task called test sync"
2. Switch to GUI mode
3. Verify "test sync" task appears in list
4. In GUI mode: Mark "test sync" as complete
5. Switch to CUI mode
6. Type: "What are my completed tasks?"
7. Verify "test sync" is listed as completed

### Verify Landing Page

1. Log out
2. Verify landing page displays:
   - Title: "Advanced Todo Application with CUI & GUI"
   - Three feature cards (AI Chat, Classic UI, Switch Anytime)
   - Sign In and Get Started buttons

## Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
uv sync --reinstall

# Check database connection
# Verify DATABASE_URL in .env is correct
```

### Frontend Won't Start

```bash
# Clear node_modules and reinstall
rm -rf node_modules
pnpm install

# Check Node version
node --version  # Should be 18+
```

### Chat Not Working

1. Verify `OPENAI_API_KEY` is set in backend `.env`
2. Check backend logs for OpenAI API errors
3. Ensure you have API credits available

### Tasks Not Syncing

1. Refresh the browser
2. Check browser console for errors
3. Verify backend API is running and responding

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@host/database
JWT_SECRET=your-secure-jwt-secret-key
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4.1-2025-04-14
CORS_ORIGINS=http://localhost:3000
DEBUG=True
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Health Check

```bash
# Check backend is running
curl http://localhost:8000/docs

# Should return Swagger UI HTML
```

## Next Steps

After verification:

1. Explore both CUI and GUI modes
2. Create tasks in both modes
3. Test all CRUD operations
4. Review the architecture in README files
