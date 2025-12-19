"""Command-line interface for todo application."""

from ..services.task_service import TaskService
from ..models.task import Task
from ..models.exceptions import TaskNotFoundError, InvalidInputError


class TodoCLI:
    """
    Command-line interface for todo application.

    Handles all user I/O and delegates business logic to TaskService.
    """

    def __init__(self, service: TaskService) -> None:
        """Initialize CLI with task service."""
        self.service = service

    def run(self) -> None:
        """Main application loop."""
        print("\nWelcome to Todo CLI!")
        print("====================")

        while True:
            self.display_menu()
            try:
                choice = self.get_menu_choice()

                if choice == 1:
                    self.handle_add_task()
                elif choice == 2:
                    self.handle_view_tasks()
                elif choice == 3:
                    self.handle_update_task()
                elif choice == 4:
                    self.handle_delete_task()
                elif choice == 5:
                    self.handle_mark_complete()
                elif choice == 6:
                    self.handle_mark_incomplete()
                elif choice == 7:
                    print("\nGoodbye! All tasks have been cleared from memory.")
                    break
            except (TaskNotFoundError, InvalidInputError) as e:
                print(f"\n[ERROR] {e}")
            except KeyboardInterrupt:
                print("\n\nGoodbye! All tasks have been cleared from memory.")
                break

    def display_menu(self) -> None:
        """Display menu options."""
        print("\n=== Todo App ===")
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Task Complete")
        print("6. Mark Task Incomplete")
        print("7. Exit")

    def get_menu_choice(self) -> int:
        """Get and validate menu choice from user."""
        while True:
            try:
                choice = int(input("\nEnter choice: "))
                if 1 <= choice <= 7:
                    return choice
                print("[ERROR] Invalid choice. Please enter a number between 1 and 7.")
            except ValueError:
                print("[ERROR] Invalid input. Please enter a number between 1 and 7.")

    def handle_add_task(self) -> None:
        """Handle add task workflow."""
        print("\n--- Add Task ---")
        title = self.get_string_input("Enter title: ")
        description = self.get_string_input("Enter description: ")

        try:
            task = self.service.create_task(title, description)
            print(f"\n[SUCCESS] Task created with ID {task.id}")
        except InvalidInputError as e:
            raise  # Re-raise to be caught in main loop

    def handle_view_tasks(self) -> None:
        """Handle view all tasks workflow."""
        print("\n--- All Tasks ---")
        tasks = self.service.get_all_tasks()

        if not tasks:
            print("No tasks found. Add a task to get started!")
        else:
            print(self.format_task_list(tasks))

    def handle_update_task(self) -> None:
        """Handle update task workflow."""
        print("\n--- Update Task ---")
        task_id = self.get_int_input("Enter task ID: ")

        # Show current task
        task = self.service.get_task(task_id)
        print(f"\nCurrent title: {task.title}")
        print(f"Current description: {task.description}")

        # Get new values (empty = skip)
        print("\nEnter new values (press Enter to skip):")
        new_title = input("New title: ").strip()
        new_description = input("New description: ").strip()

        # Update if values provided
        title_to_update = new_title if new_title else None
        description_to_update = new_description if new_description else None

        if title_to_update or description_to_update:
            self.service.update_task(task_id, title_to_update, description_to_update)
            print(f"\n[SUCCESS] Task {task_id} updated successfully")
        else:
            print(f"\n[SUCCESS] No changes made to task {task_id}")

    def handle_delete_task(self) -> None:
        """Handle delete task workflow."""
        print("\n--- Delete Task ---")
        task_id = self.get_int_input("Enter task ID: ")

        self.service.delete_task(task_id)
        print(f"\n[SUCCESS] Task {task_id} deleted successfully")

    def handle_mark_complete(self) -> None:
        """Handle mark complete workflow."""
        print("\n--- Mark Task Complete ---")
        task_id = self.get_int_input("Enter task ID: ")

        self.service.mark_complete(task_id)
        print(f"\n[SUCCESS] Task {task_id} marked as complete")

    def handle_mark_incomplete(self) -> None:
        """Handle mark incomplete workflow."""
        print("\n--- Mark Task Incomplete ---")
        task_id = self.get_int_input("Enter task ID: ")

        self.service.mark_incomplete(task_id)
        print(f"\n[SUCCESS] Task {task_id} marked as incomplete")

    def format_task_list(self, tasks: list[Task]) -> str:
        """Format tasks for display in tabular format."""
        if not tasks:
            return "No tasks to display."

        # Calculate column widths
        max_title_len = max(len(task.title) for task in tasks)
        max_desc_len = max(len(task.description) for task in tasks)

        # Ensure minimum widths
        title_width = max(20, max_title_len)
        desc_width = max(30, max_desc_len)

        # Build header
        header = f"{'ID':<4} | {'Title':<{title_width}} | {'Description':<{desc_width}} | Status"
        separator = "-" * len(header)

        lines = [header, separator]

        # Build task rows
        for task in tasks:
            status = "[X] Complete" if task.completed else "[ ] Incomplete"
            # Truncate long text for display
            title = task.title[:title_width]
            desc = task.description[:desc_width]
            line = f"{task.id:<4} | {title:<{title_width}} | {desc:<{desc_width}} | {status}"
            lines.append(line)

        return "\n".join(lines)

    def get_string_input(self, prompt: str) -> str:
        """Get non-empty string input from user."""
        while True:
            value = input(prompt)
            if value.strip():
                return value
            print("[ERROR] Input cannot be empty. Please try again.")

    def get_int_input(self, prompt: str) -> int:
        """Get integer input from user."""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("[ERROR] Invalid input. Please enter a valid number.")
