"""Custom exceptions for the Todo application."""


class TodoAppError(Exception):
    """Base exception for all todo app errors."""
    pass


class TaskNotFoundError(TodoAppError):
    """Raised when attempting to access a non-existent task."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task with ID {task_id} not found")
        self.task_id = task_id


class InvalidInputError(TodoAppError):
    """Raised when user provides invalid input."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
