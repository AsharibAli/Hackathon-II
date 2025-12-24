# Advanced Todo Frontend

Next.js 16-based frontend for the Advanced Todo Application with dual interfaces (CUI + GUI).

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript 5.x (strict mode)
- **Styling:** Tailwind CSS 4
- **UI Components:** shadcn/ui (Radix UI)
- **Icons:** Lucide React
- **Notifications:** Sonner
- **Package Manager:** pnpm

## Dual Interface Architecture

This frontend supports two interaction modes:

### CUI Mode (Conversational User Interface)
- ChatGPT-style chat interface
- Natural language task management
- Conversation history with sidebar
- AI-powered task operations

### GUI Mode (Graphical User Interface)
- Traditional forms and buttons
- Task list with checkboxes
- Edit/delete dialogs
- Direct CRUD operations

## Project Structure

```
frontend/
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── page.tsx                # Main page (landing + dual-mode app)
│   │   ├── layout.tsx              # Root layout
│   │   ├── globals.css             # Global styles
│   │   └── (auth)/                 # Authentication routes
│   │       ├── login/              # Login page
│   │       ├── register/           # Registration page
│   │       └── layout.tsx          # Auth layout
│   ├── components/
│   │   ├── chat/                   # CUI Components
│   │   │   ├── ChatLayout.tsx      # Chat page layout with sidebar
│   │   │   ├── Sidebar.tsx         # Conversation list sidebar
│   │   │   ├── ConversationItem.tsx # Single conversation in sidebar
│   │   │   └── WelcomeScreen.tsx   # New chat welcome screen
│   │   ├── tasks/                  # GUI Components
│   │   │   ├── TasksView.tsx       # GUI mode container
│   │   │   ├── TaskList.tsx        # Task list display
│   │   │   ├── TaskItem.tsx        # Single task component
│   │   │   ├── TaskForm.tsx        # Task creation form
│   │   │   ├── EditTaskDialog.tsx  # Edit task modal
│   │   │   └── DeleteTaskDialog.tsx # Delete confirmation modal
│   │   ├── navigation/             # Navigation Components
│   │   │   ├── AppHeader.tsx       # Main header with mode toggle
│   │   │   └── ModeToggle.tsx      # CUI/GUI mode switcher
│   │   ├── ui/                     # shadcn/ui components
│   │   ├── ChatInterface.tsx       # Main chat display
│   │   ├── ChatInput.tsx           # Chat message input
│   │   ├── ChatMessage.tsx         # Single chat message
│   │   ├── AuthForm.tsx            # Login/Register form
│   │   ├── ErrorBoundary.tsx       # Error handling
│   │   └── Providers.tsx           # App providers
│   ├── lib/                        # Utilities
│   │   ├── api.ts                  # API client (auth, tasks, chat)
│   │   ├── auth.ts                 # Auth utilities
│   │   └── utils.ts                # Helper functions
│   └── types/                      # TypeScript types
│       ├── task.ts                 # Task interface
│       └── chat.ts                 # Chat interfaces
├── package.json                    # Dependencies
├── tsconfig.json                   # TypeScript config
└── tailwind.config.ts              # Tailwind config
```

## Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
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

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
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
- User registration with validation
- Login with JWT tokens
- Protected routes
- Automatic redirect logic
- Logout functionality

### CUI Mode Features
- Chat interface with message history
- Conversation sidebar with rename/delete
- New chat creation
- Welcome screen with starter prompts
- AI-powered task operations
- Real-time loading indicators

### GUI Mode Features
- Create tasks with title and description
- View all personal tasks
- Toggle completion status with checkbox
- Edit task details via modal
- Delete tasks with confirmation
- Multi-user isolation
- Optimistic UI updates

### UX Enhancements
- Loading states with skeletons
- Error boundaries
- Toast notifications
- Responsive design (mobile + desktop)
- Empty state messaging
- Mode switching animation

## API Integration

The `lib/api.ts` module provides type-safe API client:

```typescript
import { authApi, tasksApi, chatApi, conversationsApi } from "@/lib/api";

// Authentication
await authApi.register({ email, password });
await authApi.login({ email, password });
await authApi.logout();
await authApi.getProfile();

// Tasks (GUI mode)
const tasks = await tasksApi.getAll();
const task = await tasksApi.create({ title, description });
await tasksApi.update(taskId, { title, description });
await tasksApi.delete(taskId);
await tasksApi.toggleComplete(taskId);

// Chat (CUI mode)
const response = await chatApi.sendMessage("Add a task", conversationId);
const history = await chatApi.getConversation(conversationId);

// Conversations
const conversations = await conversationsApi.list();
await conversationsApi.rename(id, "New Title");
await conversationsApi.delete(id);
```

## Component Architecture

### Mode Switching
```
Home Page (page.tsx)
├── Not Authenticated → Landing Page
└── Authenticated → Dual Mode App
    ├── AppHeader (mode toggle + user menu)
    └── Content Area
        ├── Chat Mode → ChatLayout
        └── Tasks Mode → TasksView
```

### CUI Components
```
ChatLayout
├── Sidebar (conversations list)
│   └── ConversationItem
└── ChatInterface
    ├── WelcomeScreen (when no messages)
    ├── ChatMessage (list of messages)
    └── ChatInput
```

### GUI Components
```
TasksView
├── TaskForm (create new task)
└── TaskList
    └── TaskItem
        ├── EditTaskDialog
        └── DeleteTaskDialog
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
3. Configure environment variables:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL
4. Deploy
