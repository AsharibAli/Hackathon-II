"""Task data model."""

from dataclasses import dataclass

from .exceptions import InvalidInputError


@dataclass
class Task:
    """
    Represents a todo item.

    Attributes:
        id: Unique identifier (immutable)
        title: Brief task name
        description: Detailed task information
        completed: Completion status indicator
    """
    id: int
    title: str
    description: str
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete."""
        self.completed = False

    def update_title(self, new_title: str) -> None:
        """
        Update the task title.

        Args:
            new_title: New title (must be non-empty after strip)

        Raises:
            InvalidInputError: If new_title is empty
        """
        stripped = new_title.strip()
        if not stripped:
            raise InvalidInputError("Title cannot be empty")
        self.title = stripped

    def update_description(self, new_description: str) -> None:
        """
        Update the task description.

        Args:
            new_description: New description (must be non-empty after strip)

        Raises:
            InvalidInputError: If new_description is empty
        """
        stripped = new_description.strip()
        if not stripped:
            raise InvalidInputError("Description cannot be empty")
        self.description = stripped
