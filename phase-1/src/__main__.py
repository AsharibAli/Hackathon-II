"""Application entry point."""

from .services.task_service import TaskService
from .cli.todo_cli import TodoCLI


def main() -> None:
    """Initialize and run the todo application."""
    # Create service and CLI
    service = TaskService()
    cli = TodoCLI(service)

    # Run application
    cli.run()


if __name__ == "__main__":
    main()
