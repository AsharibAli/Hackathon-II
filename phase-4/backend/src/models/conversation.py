"""
Conversation entity model representing a chat session.
Each conversation belongs to a user and contains messages.
"""
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING, Optional

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

    title: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Conversation title (auto-generated or user-defined)"
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
