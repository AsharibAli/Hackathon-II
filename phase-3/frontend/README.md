# Todo Frontend

Next.js 16-based frontend for the Todo Full-Stack Web Application.

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript 5.x (strict mode)
- **Authentication:** Better Auth with JWT plugin
- **Styling:** Tailwind CSS 4
- **UI Components:** shadcn/ui (Radix UI)
- **Icons:** Lucide React
- **Notifications:** Sonner
- **Package Manager:** pnpm

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (app)/              # Protected app routes
│   │   │   ├── layout.tsx      # App layout with logout
│   │   │   └── page.tsx        # Main todo list page
│   │   ├── (auth)/             # Authentication routes
│   │   │   ├── login/          # Login page
│   │   │   ├── register/       # Registration page
│   │   │   └── layout.tsx      # Auth layout
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css         # Global styles
│   ├── components/             # React components
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── AuthForm.tsx        # Login/Register form
│   │   ├── TaskForm.tsx        # Task creation form
│   │   ├── TaskList.tsx        # Task list container
│   │   ├── TaskItem.tsx        # Single task display
│   │   ├── EditTaskDialog.tsx  # Edit task modal
│   │   └── DeleteTaskDialog.tsx # Delete confirmation modal
│   ├── lib/                    # Utilities
│   │   ├── auth.ts             # Better Auth config
│   │   ├── api.ts              # API client
│   │   └── utils.ts            # Helper functions
│   └── types/                  # TypeScript types
│       └── task.ts             # Task interface
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
└── tailwind.config.ts          # Tailwind config
```

## Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-better-auth-secret-here-minimum-32-characters
BETTER_AUTH_URL=http://localhost:3000
```

## Setup

### Prerequisites

- Node.js 18+
- pnpm package manager: `npm install -g pnpm`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install

# Copy environment template
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

### Development

```bash
# Start development server
pnpm dev

# The app will be available at http://localhost:3000
```

### Production Build

```bash
# Build for production
pnpm build

# Start production server
pnpm start

# Type check
pnpm type-check

# Lint
pnpm lint
```

## Features

### Authentication
- ✅ User registration with validation
- ✅ Login with JWT tokens
- ✅ Protected routes
- ✅ Automatic redirect logic
- ✅ Logout functionality

### Task Management
- ✅ Create tasks with title and description
- ✅ View all personal tasks
- ✅ Toggle completion status
- ✅ Edit task details
- ✅ Delete tasks with confirmation
- ✅ Multi-user isolation

### UX Enhancements
- ✅ Loading states with skeletons
- ✅ Error boundaries
- ✅ Toast notifications
- ✅ Optimistic UI updates
- ✅ Responsive design (mobile + desktop)
- ✅ Empty state messaging

## API Integration

The `lib/api.ts` module provides type-safe API client:

```typescript
import { authApi, tasksApi } from "@/lib/api";

// Authentication
await authApi.register({ email, password });
await authApi.login({ email, password });
await authApi.logout();

// Tasks
const tasks = await tasksApi.getAll();
const task = await tasksApi.create({ title, description });
await tasksApi.update(taskId, { title, description });
await tasksApi.delete(taskId);
await tasksApi.toggleComplete(taskId);
```

## Type Safety

Strict TypeScript configuration enabled:
- `strict: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`
- `noUncheckedIndexedAccess: true`

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project to Vercel
3. Configure environment variables
4. Deploy
