"""
Task entity model representing todo tasks.
Each task belongs to a single user (many-to-one relationship).

[Task]: T012-T017
[Spec]: F-001, F-002, F-003, F-006, F-007
[Description]: Extended Task model with Phase 5 fields
"""
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .user import User
    from .tag import Tag


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recurrence(str, Enum):
    """Task recurrence patterns."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Task(SQLModel, table=True):
    """
    Task entity with title, description, and completion status.
    Belongs to a user via user_id foreign key.

    Phase 5 additions:
    - priority: Task priority level (low, medium, high)
    - due_date: Optional deadline for the task
    - remind_at: Optional reminder time
    - reminder_sent: Whether reminder notification was sent
    - recurrence: Repeating pattern (none, daily, weekly, monthly)
    - parent_task_id: Reference to parent recurring task
    """
    __tablename__ = "tasks"

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

    title: str = Field(
        max_length=200,
        nullable=False
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000
    )

    is_completed: bool = Field(
        default=False,
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

    # Phase 5 additions - T012: Priority
    priority: Priority = Field(
        default=Priority.MEDIUM,
        nullable=False,
        index=True
    )

    # T013: Due date
    due_date: Optional[datetime] = Field(
        default=None,
        index=True
    )

    # T014: Reminder time
    remind_at: Optional[datetime] = Field(
        default=None
    )

    # T015: Reminder sent flag
    reminder_sent: bool = Field(
        default=False,
        nullable=False
    )

    # T016: Recurrence pattern
    recurrence: Recurrence = Field(
        default=Recurrence.NONE,
        nullable=False
    )

    # T017: Parent task reference for recurring instances
    parent_task_id: Optional[UUID] = Field(
        default=None,
        foreign_key="tasks.id",
        index=True
    )

    # Relationship: Many tasks belong to one user
    owner: "User" = Relationship(back_populates="tasks")

    # Relationship: Many-to-many with tags
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        link_model="TaskTag"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "is_completed": False,
                "priority": "medium",
                "due_date": "2025-01-15T14:00:00Z",
                "recurrence": "none"
            }
        }
