"""
User entity model representing application users.
Handles user authentication and relationships with tasks.
"""
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation


class User(SQLModel, table=True):
    """
    User entity with authentication credentials.
    Each user can have multiple tasks (one-to-many relationship).
    """
    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        nullable=False
    )

    hashed_password: str = Field(
        nullable=False
    )

    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's full name"
    )

    profile_picture: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to user's profile picture"
    )

    is_active: bool = Field(
        default=True,
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

    # Relationship: One user has many tasks
    tasks: List["Task"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Relationship: One user has many conversations
    conversations: List["Conversation"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "is_active": True
            }
        }
