# Quickstart: Todo Full-Stack Web Application - Baseline

**Feature**: 001-todo-app-baseline
**Purpose**: Get the development environment running and test the application

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **uv** (Python package manager): `pip install uv`
- **pnpm** (Node package manager): `npm install -g pnpm`
- **Neon PostgreSQL account**: Sign up at https://neon.tech (free tier available)

## Project Structure Overview

```
phase-2/
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── specs/            # Feature specifications
└── .specify/         # Spec-Kit Plus configuration
```

## Step 1: Clone and Setup

```bash
# Navigate to project root
cd phase-2

# Verify you're on the feature branch
git branch --show-current  # Should show: 001-todo-app-baseline
```

## Step 2: Backend Setup

### 2.1 Install Dependencies

```bash
cd backend

# Initialize uv project
uv init

# Install dependencies
uv add fastapi sqlmodel python-jose[cryptography] passlib[bcrypt] python-multipart uvicorn alembic psycopg2-binary

# Install dev dependencies
uv add --dev pytest httpx
```

### 2.2 Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# backend/.env
DATABASE_URL=postgresql://<username>:<password>@<neon-host>/<database>?sslmode=require
JWT_SECRET=<generate-32-character-random-string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=http://localhost:3000
```

**Generate JWT Secret**:
```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

**Get Neon Database URL**:
1. Go to https://console.neon.tech
2. Create a new project
3. Copy the connection string from the dashboard
4. Replace `<username>`, `<password>`, `<neon-host>`, and `<database>` in `.env`

### 2.3 Initialize Database

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Create users and tasks tables"

# Apply migrations
alembic upgrade head
```

### 2.4 Run Backend Server

```bash
# Development mode with auto-reload
fastapi dev src/main.py

# Server will start at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

## Step 3: Frontend Setup

### 3.1 Install Dependencies

```bash
cd frontend

# Initialize Next.js project (if not already done)
# Skip this if project already initialized

# Install dependencies
pnpm install

# Add additional dependencies
pnpm add better-auth
pnpm add -D tailwindcss postcss autoprefixer
pnpm add class-variance-authority clsx tailwind-merge lucide-react

# Initialize shadcn/ui
npx shadcn-ui@latest init
```

### 3.2 Configure Environment Variables

Create `.env.local` file in `frontend/` directory:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<generate-random-string>
BETTER_AUTH_URL=http://localhost:3000
```

**Generate Better Auth Secret**:
```bash
# Any random string (32+ characters)
openssl rand -hex 32
```

### 3.3 Run Frontend Server

```bash
# Development mode
pnpm dev

# Server will start at http://localhost:3000
```

## Step 4: Verify Setup

### 4.1 Backend Health Check

```bash
# Test backend is running
curl http://localhost:8000/docs

# Should open interactive API documentation
```

### 4.2 Frontend Health Check

Open browser and navigate to:
- http://localhost:3000 (should show landing page)

## Step 5: Manual Testing (Per Acceptance Scenarios)

### Test P1: Authentication

**Register a new user**:
1. Go to http://localhost:3000/register
2. Enter email: `test@example.com`
3. Enter password: `password123` (min 8 characters)
4. Click "Register"
5. ✅ Should create account and redirect to main page

**Login**:
1. Go to http://localhost:3000/login
2. Enter email: `test@example.com`
3. Enter password: `password123`
4. Click "Login"
5. ✅ Should receive JWT token and redirect to main page

**Access without token**:
1. Open browser incognito/private window
2. Try to access http://localhost:3000/app
3. ✅ Should redirect to login page

**Logout**:
1. Click "Logout" button
2. ✅ Should terminate session and redirect to login

### Test P2: View Tasks

**Empty state**:
1. Login as newly created user
2. ✅ Should see "No tasks yet" message with prompt to create first task

**View tasks**:
1. Create a few tasks (see P3)
2. ✅ Should see list of tasks with title and completion status

**Multi-user isolation**:
1. Register User A (`usera@example.com`)
2. Create 2 tasks as User A
3. Logout
4. Register User B (`userb@example.com`)
5. ✅ Should NOT see User A's tasks

### Test P3: Create Tasks

**Create task with title only**:
1. Enter title: "Buy groceries"
2. Leave description empty
3. Click "Create"
4. ✅ Task should appear in list, marked as incomplete

**Create task with title and description**:
1. Enter title: "Complete project"
2. Enter description: "Finish implementation and testing"
3. Click "Create"
4. ✅ Task should appear with both fields

**Validation - empty title**:
1. Leave title empty
2. Click "Create"
3. ✅ Should show validation error: "Title cannot be empty"

### Test P4: Toggle Completion

**Mark as complete**:
1. Click checkbox/toggle on incomplete task
2. ✅ Task should be visually distinguished (strikethrough, different color)

**Mark as incomplete**:
1. Click checkbox/toggle on completed task
2. ✅ Task should return to incomplete state

**Persistence**:
1. Toggle task status
2. Refresh page (Ctrl+R / Cmd+R)
3. ✅ Task status should persist

### Test P5: Update Tasks

**Edit title**:
1. Click "Edit" on a task
2. Change title: "Buy groceries and cook dinner"
3. Click "Save"
4. ✅ Updated title should display

**Edit description**:
1. Click "Edit" on a task
2. Change description
3. Click "Save"
4. ✅ Updated description should display

**Cancel edit**:
1. Click "Edit" on a task
2. Make changes
3. Click "Cancel"
4. ✅ Original data should remain unchanged

### Test P6: Delete Tasks

**Delete task**:
1. Click "Delete" on a task
2. ✅ Should show confirmation dialog
3. Click "Confirm"
4. ✅ Task should be removed from list

**Cancel delete**:
1. Click "Delete" on a task
2. Click "Cancel" in confirmation dialog
3. ✅ Task should remain in list

**Persistence**:
1. Delete a task
2. Refresh page
3. ✅ Deleted task should NOT reappear

## Common Issues and Solutions

### Backend won't start

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Run `uv add fastapi` in backend directory

**Issue**: `sqlalchemy.exc.OperationalError: could not connect to server`
**Solution**: Verify `DATABASE_URL` in `.env` is correct and Neon database is accessible

**Issue**: `JWT_SECRET not found`
**Solution**: Ensure `.env` file exists in backend directory with `JWT_SECRET` set

### Frontend won't start

**Issue**: `Module not found: Can't resolve 'better-auth'`
**Solution**: Run `pnpm install` in frontend directory

**Issue**: Network error when calling API
**Solution**: Verify `NEXT_PUBLIC_API_URL` in `.env.local` matches backend URL (http://localhost:8000)

**Issue**: CORS error in browser console
**Solution**: Verify `CORS_ORIGINS` in backend `.env` includes frontend URL (http://localhost:3000)

### Authentication issues

**Issue**: Token invalid/expired
**Solution**: Logout and login again to get new token

**Issue**: Unable to see other user's tasks (expected behavior!)
**Solution**: This is correct - multi-user isolation is working as designed

## API Documentation

Once backend is running, access interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these to:
- Test API endpoints manually
- View request/response schemas
- Understand authentication requirements

## Development Workflow

### Making Changes

1. **Backend changes**:
   - Edit files in `backend/src/`
   - FastAPI auto-reloads on file changes
   - Test at http://localhost:8000/docs

2. **Frontend changes**:
   - Edit files in `frontend/src/`
   - Next.js auto-reloads on file changes (Hot Module Replacement)
   - Test at http://localhost:3000

3. **Database changes**:
   - Edit SQLModel models in `backend/src/models/`
   - Generate migration: `alembic revision --autogenerate -m "description"`
   - Apply migration: `alembic upgrade head`

### Debugging

**Backend logs**:
- FastAPI automatically logs requests to console
- Add `print()` or `logger.info()` statements in code
- Check console output where `fastapi dev` is running

**Frontend logs**:
- Browser DevTools Console (F12)
- Check Network tab for API call failures
- Use React DevTools extension for component inspection

**Database queries**:
- Use Neon dashboard SQL editor to run queries manually
- Enable SQLAlchemy query logging: set `echo=True` in `create_engine()`

## Next Steps

After verifying the application works:

1. **Review code**: Explore `backend/src/` and `frontend/src/` to understand structure
2. **Run tests**: Execute pytest tests (if available)
3. **Explore API**: Use Swagger UI to test all endpoints
4. **Test edge cases**: Try long titles (200 chars), many tasks (100+), rapid creation
5. **Performance testing**: Test with 100 concurrent users (if needed)

## Support

For issues specific to:
- **Spec-Kit Plus**: See `.specify/` documentation
- **Feature specification**: See `specs/001-todo-app-baseline/spec.md`
- **Architecture decisions**: See `specs/001-todo-app-baseline/plan.md`
- **Technology choices**: See `specs/001-todo-app-baseline/research.md`
