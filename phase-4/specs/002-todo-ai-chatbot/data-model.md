# Data Model: Todo AI Chatbot (Phase-3)

**Feature Branch**: `002-todo-ai-chatbot`
**Created**: 2025-12-19
**Status**: Complete

## Overview

This document defines the data entities required for the Phase-3 AI chatbot feature. These entities extend the existing Phase-2 data model (User, Task) with conversation management capabilities.

---

## Existing Entities (Phase-2)

### User
> Unchanged from Phase-2. Referenced for relationship context.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique identifier |
| email | string | UNIQUE, NOT NULL, max 255 | User email address |
| hashed_password | string | NOT NULL | Bcrypt hashed password |
| is_active | boolean | NOT NULL, default TRUE | Account status |
| created_at | datetime | NOT NULL | Account creation timestamp |
| updated_at | datetime | NOT NULL | Last update timestamp |

**Relationships**: One User has many Tasks, one User has many Conversations

### Task
> Unchanged from Phase-2. Referenced for MCP tool operations.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique identifier |
| user_id | UUID | FK → users.id, NOT NULL | Owner reference |
| title | string | NOT NULL, max 200 | Task title |
| description | string | NULL, max 2000 | Optional description |
| is_completed | boolean | NOT NULL, default FALSE | Completion status |
| created_at | datetime | NOT NULL | Task creation timestamp |
| updated_at | datetime | NOT NULL | Last update timestamp |

**Relationships**: Many Tasks belong to one User

---

## New Entities (Phase-3)

### Conversation

Represents a chat session between a user and the AI assistant. Each user may have one active conversation (MVP scope).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique identifier |
| user_id | UUID | FK → users.id, NOT NULL, INDEXED | Owner reference |
| created_at | datetime | NOT NULL | Conversation start time |
| updated_at | datetime | NOT NULL | Last activity timestamp |

**Relationships**:
- Many Conversations belong to one User (user_id → users.id)
- One Conversation has many Messages

**Indexes**:
- `idx_conversations_user_id` on (user_id)
- `idx_conversations_user_updated` on (user_id, updated_at DESC)

**Business Rules**:
- MVP: One active conversation per user (get or create pattern)
- Future: Multiple conversations with conversation management

### Message

Represents a single message within a conversation. Can be from the user or the assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique identifier |
| conversation_id | UUID | FK → conversations.id, NOT NULL, INDEXED | Parent conversation |
| role | string | NOT NULL, ENUM('user', 'assistant') | Message sender role |
| content | string | NOT NULL, max 10000 | Message text content |
| created_at | datetime | NOT NULL | Message timestamp |

**Relationships**:
- Many Messages belong to one Conversation (conversation_id → conversations.id)

**Indexes**:
- `idx_messages_conversation_id` on (conversation_id)
- `idx_messages_conversation_created` on (conversation_id, created_at ASC)

**Business Rules**:
- Messages are immutable once created
- Order is determined by created_at timestamp
- Role must be exactly 'user' or 'assistant'
- Content limit of 10,000 characters per message

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id: UUID (PK)   │
│ email: string   │
│ hashed_password │
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐      ┌─────────────────┐
│      Task       │      │  Conversation   │
├─────────────────┤      ├─────────────────┤
│ id: UUID (PK)   │      │ id: UUID (PK)   │
│ user_id: FK     │◄────►│ user_id: FK     │
│ title           │      │ created_at      │
│ description     │      │ updated_at      │
│ is_completed    │      └────────┬────────┘
│ created_at      │               │
│ updated_at      │               │ 1:N
└─────────────────┘               ▼
                         ┌─────────────────┐
                         │     Message     │
                         ├─────────────────┤
                         │ id: UUID (PK)   │
                         │ conversation_id │
                         │ role: string    │
                         │ content: string │
                         │ created_at      │
                         └─────────────────┘
```

---

## SQLModel Definitions

### Conversation Model

```python
# backend/src/models/conversation.py

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session.
    Each conversation belongs to a user and contains messages.
    """
    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    owner: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

### Message Model

```python
# backend/src/models/message.py

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message entity representing a single chat message.
    Each message belongs to a conversation.
    """
    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False
    )

    role: str = Field(
        nullable=False,
        max_length=20
    )  # "user" | "assistant"

    content: str = Field(
        nullable=False,
        max_length=10000
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

### User Model Extension

```python
# Add to backend/src/models/user.py

# Add import
if TYPE_CHECKING:
    from .conversation import Conversation

# Add relationship (inside User class)
conversations: List["Conversation"] = Relationship(
    back_populates="owner",
    sa_relationship_kwargs={"cascade": "all, delete-orphan"}
)
```

---

## Database Migration

### Migration: Add Conversation and Message Tables

```python
# alembic/versions/xxx_add_conversation_tables.py

"""Add conversation and message tables for Phase-3 AI chatbot

Revision ID: xxx
Revises: [previous_revision]
Create Date: 2025-12-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_user_updated', 'conversations', ['user_id', 'updated_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.String(10000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Validation Rules

### Conversation
- `user_id` must reference an existing active user
- `updated_at` must be updated on every new message

### Message
- `conversation_id` must reference an existing conversation
- `role` must be exactly "user" or "assistant"
- `content` must be non-empty (after trimming whitespace)
- `content` must not exceed 10,000 characters

---

## Query Patterns

### Get or Create Conversation for User
```python
def get_or_create_conversation(session: Session, user_id: UUID) -> Conversation:
    conversation = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation
```

### Get Recent Messages (for AI context)
```python
def get_recent_messages(session: Session, conversation_id: UUID, limit: int = 50) -> list[Message]:
    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()[::-1]  # Reverse to chronological order
```

### Store Message
```python
def store_message(session: Session, conversation_id: UUID, role: str, content: str) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(message)
    return message
```
