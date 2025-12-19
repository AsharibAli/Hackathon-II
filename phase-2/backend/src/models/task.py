"""
Task entity model representing todo tasks.
Each task belongs to a single user (many-to-one relationship).
"""
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Task(SQLModel, table=True):
    """
    Task entity with title, description, and completion status.
    Belongs to a user via user_id foreign key.
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

    # Relationship: Many tasks belong to one user
    owner: "User" = Relationship(back_populates="tasks")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "is_completed": False
            }
        }
