"""
Message entity model representing a single chat message.
Each message belongs to a conversation.
"""
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

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
