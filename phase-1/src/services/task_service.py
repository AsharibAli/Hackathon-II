"""Service for managing tasks."""

from typing import Optional

from ..models.task import Task
from ..models.exceptions import TaskNotFoundError, InvalidInputError


class TaskService:
    """
    Service for managing tasks in memory.

    Handles all business logic for task operations including
    creation, retrieval, updates, deletion, and status management.
    """

    def __init__(self) -> None:
        """Initialize task service with empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def create_task(self, title: str, description: str) -> Task:
        """
        Create a new task with auto-generated ID.

        Args:
            title: Task title (will be stripped)
            description: Task description (will be stripped)

        Returns:
            Created task with unique ID and completed=False

        Raises:
            InvalidInputError: If title or description is empty after strip
        """
        # Validate inputs
        title_stripped = title.strip()
        description_stripped = description.strip()

        if not title_stripped:
            raise InvalidInputError("Title cannot be empty")
        if not description_stripped:
            raise InvalidInputError("Description cannot be empty")

        # Generate ID and create task
        task_id = self._generate_id()
        task = Task(
            id=task_id,
            title=title_stripped,
            description=description_stripped,
            completed=False
        )

        # Store task
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: int) -> Task:
        """
        Retrieve a task by ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task with matching ID

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def get_all_tasks(self) -> list[Task]:
        """
        Retrieve all tasks.

        Returns:
            List of all tasks ordered by ID (insertion order)
        """
        return list(self._tasks.values())

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Task:
        """
        Update task title and/or description.

        Args:
            task_id: ID of task to update
            title: New title (None means no change)
            description: New description (None means no change)

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
            InvalidInputError: If provided values are empty after strip
        """
        task = self.get_task(task_id)

        if title is not None:
            task.update_title(title)
        if description is not None:
            task.update_description(description)

        return task

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task permanently.

        Args:
            task_id: ID of task to delete

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def mark_complete(self, task_id: int) -> Task:
        """
        Mark a task as completed.

        Args:
            task_id: ID of task to mark complete

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        task = self.get_task(task_id)
        task.mark_complete()
        return task

    def mark_incomplete(self, task_id: int) -> Task:
        """
        Mark a task as incomplete.

        Args:
            task_id: ID of task to mark incomplete

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        task = self.get_task(task_id)
        task.mark_incomplete()
        return task

    def _generate_id(self) -> int:
        """Generate next sequential ID."""
        current_id = self._next_id
        self._next_id += 1
        return current_id
