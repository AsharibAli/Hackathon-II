# [Task]: T018
# [Spec]: F-002 (R-002.1, R-002.2, R-002.3)
# [Description]: Tag entity model for task categorization
"""
Tag entity model for task categorization.
Tags are case-insensitive (stored lowercase) and user-scoped.
"""
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .user import User


class Tag(SQLModel, table=True):
    """
    Tag entity for task categorization.

    - Names are case-insensitive (stored lowercase)
    - Tags are scoped to individual users
    - Many-to-many relationship with tasks via TaskTag
    """
    __tablename__ = "tags"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    name: str = Field(
        max_length=50,
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

    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="tags",
        link_model="TaskTag"
    )

    def __init__(self, **data):
        """Ensure tag name is stored lowercase."""
        if "name" in data and data["name"]:
            data["name"] = data["name"].lower().strip()
        super().__init__(**data)

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "work",
            }
        }


class TaskTag(SQLModel, table=True):
    """
    Junction table for many-to-many relationship between Task and Tag.
    """
    __tablename__ = "task_tags"

    task_id: UUID = Field(
        foreign_key="tasks.id",
        primary_key=True,
        nullable=False
    )

    tag_id: UUID = Field(
        foreign_key="tags.id",
        primary_key=True,
        nullable=False
    )
