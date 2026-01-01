"""
MCP tools for task management.
Wraps existing task service logic for AI agent consumption.

[Task]: T033-T034, T042-T043, T051-T052, T057, T064-T065, T071, T078
[Spec]: F-001 to F-007
[Description]: Phase 5 enhanced MCP tools for priority, tags, due dates, search, filter/sort, reminders, recurrence
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session
import logging
from services.tasks import TasksService
from models.task import Task, Priority, Recurrence
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert task to dictionary with all Phase 5 fields."""
    try:
        # Handle timezone-aware/naive datetime comparison safely
        is_overdue = False
        if task.due_date is not None and not task.is_completed:
            now = datetime.now(timezone.utc)
            due = task.due_date
            # Make due_date timezone-aware if it's naive
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            is_overdue = due < now

        # Safely get tags list
        tags_list = []
        try:
            if task.tags:
                tags_list = [t.name for t in task.tags]
        except Exception as e:
            logger.warning(f"Failed to load tags for task {task.id}: {e}")

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description or "",
            "is_completed": task.is_completed,
            "priority": task.priority.value if task.priority else "medium",
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "remind_at": task.remind_at.isoformat() if task.remind_at else None,
            "recurrence": task.recurrence.value if task.recurrence else "none",
            "tags": tags_list,
            "is_overdue": is_overdue,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        }
    except Exception as e:
        logger.error(f"Error converting task {task.id} to dict: {e}")
        # Return minimal task info on error
        return {
            "id": str(task.id),
            "title": task.title or "Unknown",
            "is_completed": task.is_completed,
            "error": str(e)
        }


def add_task(
    session: Session,
    user_id: UUID,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a new task with optional priority, due date, and tags.
    """
    logger.info(f"Tool: add_task called for user {user_id} with title='{title}', priority={priority}, due_date={due_date}, tags={tags}")
    try:
        task = TasksService.create_task(
            session=session,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags,
        )
        logger.info(f"Task created successfully: id={task.id}, title='{task.title}'")

        task_dict = _task_to_dict(task)

        return {
            "success": True,
            "message": f"Task '{task.title}' created successfully.",
            "task": task_dict
        }
    except Exception as e:
        logger.error(f"Failed to create task: {e}", exc_info=True)
        return {"success": False, "message": f"Failed to create task: {str(e)}"}

def list_tasks(
    session: Session,
    user_id: UUID,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    overdue: Optional[bool] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List all tasks for the user with optional filters.
    """
    logger.info(f"Tool: list_tasks called for user {user_id} with filters: completed={completed}, priority={priority}, tag={tag}, overdue={overdue}")
    try:
        tasks = TasksService.get_user_tasks(
            session=session,
            user_id=user_id,
            priority=priority,
            tag=tag,
            is_completed=completed,
            overdue=overdue,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        logger.info(f"Retrieved {len(tasks)} tasks from database")

        task_list = []
        for t in tasks:
            try:
                task_dict = _task_to_dict(t)
                task_list.append(task_dict)
            except Exception as e:
                logger.error(f"Error converting task {t.id} to dict: {e}")
                # Add minimal task info on error
                task_list.append({
                    "id": str(t.id),
                    "title": t.title or "Unknown",
                    "is_completed": t.is_completed,
                    "error": str(e)
                })

        logger.info(f"Successfully converted {len(task_list)} tasks to dicts")

        return {
            "success": True,
            "count": len(task_list),
            "tasks": task_list,
            "message": f"Found {len(task_list)} tasks" + (f" (completed={completed})" if completed is not None else "")
        }
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}", exc_info=True)
        return {"success": False, "message": f"Failed to list tasks: {str(e)}"}

class TaskNotFoundError(Exception):
    """Raised when a task cannot be found."""
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(message)


def _find_task(session: Session, user_id: UUID, task_identifier: str) -> Task:
    """
    Helper to find task by ID or fuzzy title match.

    Args:
        session: Database session
        user_id: User's UUID
        task_identifier: Task UUID or partial title

    Returns:
        Task object

    Raises:
        TaskNotFoundError: If task not found or multiple matches
    """
    if not task_identifier or not task_identifier.strip():
        raise TaskNotFoundError("Task identifier cannot be empty")

    task_identifier = task_identifier.strip()

    # Try as UUID first
    try:
        task_id = UUID(task_identifier)
        return TasksService.get_task_by_id(session, task_id, user_id)
    except ValueError:
        pass  # Not a valid UUID, try title match
    except Exception:
        pass  # Task not found by ID

    # Fuzzy match by title
    tasks = TasksService.get_user_tasks(session, user_id)

    # Exact match first (case-insensitive)
    exact_matches = [t for t in tasks if task_identifier.lower() == t.title.lower()]
    if len(exact_matches) == 1:
        return exact_matches[0]

    # Partial match
    partial_matches = [t for t in tasks if task_identifier.lower() in t.title.lower()]

    if len(partial_matches) == 1:
        return partial_matches[0]
    elif len(partial_matches) > 1:
        suggestions = [t.title for t in partial_matches[:5]]
        raise TaskNotFoundError(
            f"Multiple tasks match '{task_identifier}'. Please be more specific.",
            suggestions=suggestions
        )
    else:
        # No matches - suggest similar tasks
        similar = [t.title for t in tasks[:5]] if tasks else []
        raise TaskNotFoundError(
            f"No task found matching '{task_identifier}'.",
            suggestions=similar
        )

def complete_task(
    session: Session,
    user_id: UUID,
    task_identifier: str
) -> Dict[str, Any]:
    """
    Mark a task as completed.
    Accepts UUID or partial title.
    """
    logger.info(f"Tool: complete_task called for user {user_id} with task_identifier='{task_identifier}'")
    try:
        task = _find_task(session, user_id, task_identifier)
        task = TasksService.update_task(session, task.id, user_id, is_completed=True)
        return {
            "success": True,
            "message": f"Task '{task.title}' marked as completed.",
            "task": _task_to_dict(task)
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return {"success": False, "message": f"Failed to complete task: {str(e)}"}

def update_task(
    session: Session,
    user_id: UUID,
    task_identifier: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    recurrence: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update a task's title, description, priority, due date, or recurrence.
    """
    logger.info(f"Tool: update_task called for user {user_id} with task_identifier='{task_identifier}'")
    try:
        task = _find_task(session, user_id, task_identifier)
        task = TasksService.update_task(
            session,
            task.id,
            user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            recurrence=recurrence,
        )
        return {
            "success": True,
            "message": f"Task '{task.title}' updated.",
            "task": _task_to_dict(task)
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return {"success": False, "message": f"Failed to update task: {str(e)}"}

def delete_task(
    session: Session,
    user_id: UUID,
    task_identifier: str
) -> Dict[str, Any]:
    """
    Delete a task.
    """
    logger.info(f"Tool: delete_task called for user {user_id} with task_identifier='{task_identifier}'")
    try:
        task = _find_task(session, user_id, task_identifier)
        task_title = task.title
        TasksService.delete_task(session, task.id, user_id)
        return {
            "success": True,
            "message": f"Task '{task_title}' deleted."
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return {"success": False, "message": f"Failed to delete task: {str(e)}"}


# =============================================================================
# Phase 5 MCP Tools: Priority Management (T033, T034)
# =============================================================================

def set_priority(
    session: Session,
    user_id: UUID,
    task_identifier: str,
    priority: str,
) -> Dict[str, Any]:
    """
    [T033] Set the priority of a task.

    Args:
        task_identifier: Task title (partial match) or UUID
        priority: Priority level (low, medium, high)
    """
    logger.info(f"Tool: set_priority called - task='{task_identifier}', priority='{priority}'")
    try:
        # Validate priority first
        if priority.lower() not in ["low", "medium", "high"]:
            return {"success": False, "message": f"Invalid priority '{priority}'. Must be low, medium, or high."}

        task = _find_task(session, user_id, task_identifier)
        task = TasksService.update_task(session, task.id, user_id, priority=priority.lower())
        return {
            "success": True,
            "message": f"Set priority of '{task.title}' to {priority}.",
            "task": _task_to_dict(task)
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        logger.error(f"Error setting priority: {e}")
        return {"success": False, "message": f"Failed to set priority: {str(e)}"}


def filter_by_priority(
    session: Session,
    user_id: UUID,
    priority: str,
) -> Dict[str, Any]:
    """
    [T034] Filter tasks by priority level.

    Args:
        priority: Priority level to filter by (low, medium, high)
    """
    logger.info(f"Tool: filter_by_priority called - priority='{priority}'")
    try:
        if priority.lower() not in ["low", "medium", "high"]:
            return {"success": False, "message": f"Invalid priority '{priority}'. Must be low, medium, or high."}

        tasks = TasksService.get_user_tasks(session, user_id, priority=priority.lower())
        task_list = [_task_to_dict(t) for t in tasks]

        return {
            "success": True,
            "message": f"Found {len(task_list)} {priority} priority tasks.",
            "count": len(task_list),
            "tasks": task_list
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to filter by priority: {str(e)}"}


# =============================================================================
# Phase 5 MCP Tools: Tag Management (T042, T043)
# =============================================================================

def add_tag(
    session: Session,
    user_id: UUID,
    task_identifier: str,
    tag: str,
) -> Dict[str, Any]:
    """
    [T042] Add a tag to a task.

    Args:
        task_identifier: Task title (partial match) or UUID
        tag: Tag name to add
    """
    logger.info(f"Tool: add_tag called - task='{task_identifier}', tag='{tag}'")
    try:
        if not tag or not tag.strip():
            return {"success": False, "message": "Tag name cannot be empty."}

        task = _find_task(session, user_id, task_identifier)
        task = TasksService.add_tag_to_task(session, task.id, user_id, tag.strip())
        return {
            "success": True,
            "message": f"Added tag '{tag}' to '{task.title}'.",
            "task": _task_to_dict(task)
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        logger.error(f"Error adding tag: {e}")
        return {"success": False, "message": f"Failed to add tag: {str(e)}"}


def remove_tag(
    session: Session,
    user_id: UUID,
    task_identifier: str,
    tag: str,
) -> Dict[str, Any]:
    """
    Remove a tag from a task.

    Args:
        task_identifier: Task title (partial match) or UUID
        tag: Tag name to remove
    """
    logger.info(f"Tool: remove_tag called - task='{task_identifier}', tag='{tag}'")
    try:
        if not tag or not tag.strip():
            return {"success": False, "message": "Tag name cannot be empty."}

        task = _find_task(session, user_id, task_identifier)
        task = TasksService.remove_tag_from_task(session, task.id, user_id, tag.strip())
        return {
            "success": True,
            "message": f"Removed tag '{tag}' from '{task.title}'.",
            "task": _task_to_dict(task)
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        logger.error(f"Error removing tag: {e}")
        return {"success": False, "message": f"Failed to remove tag: {str(e)}"}


def filter_by_tag(
    session: Session,
    user_id: UUID,
    tag: str,
) -> Dict[str, Any]:
    """
    [T043] Filter tasks by tag.

    Args:
        tag: Tag name to filter by
    """
    logger.info(f"Tool: filter_by_tag called - tag='{tag}'")
    try:
        tasks = TasksService.get_user_tasks(session, user_id, tag=tag)
        task_list = [_task_to_dict(t) for t in tasks]

        return {
            "success": True,
            "message": f"Found {len(task_list)} tasks with tag '{tag}'.",
            "count": len(task_list),
            "tasks": task_list
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to filter by tag: {str(e)}"}


# =============================================================================
# Phase 5 MCP Tools: Due Date Management (T051, T052)
# =============================================================================

def set_due_date(
    session: Session,
    user_id: UUID,
    task_identifier: str,
    due_date: str,
) -> Dict[str, Any]:
    """
    [T051] Set the due date of a task using natural language or ISO format.

    Args:
        task_identifier: Task title (partial match) or UUID
        due_date: Due date (e.g., "tomorrow", "next Friday", "2025-01-15")
    """
    logger.info(f"Tool: set_due_date called - task='{task_identifier}', due_date='{due_date}'")
    try:
        if not due_date or not due_date.strip():
            return {"success": False, "message": "Due date cannot be empty. Use a date like 'tomorrow', 'next Monday', or 'January 15'."}

        task = _find_task(session, user_id, task_identifier)
        task = TasksService.update_task(session, task.id, user_id, due_date=due_date.strip())

        due_str = task.due_date.strftime("%A, %B %d, %Y") if task.due_date else "none"
        return {
            "success": True,
            "message": f"Set due date of '{task.title}' to {due_str}.",
            "task": _task_to_dict(task)
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        logger.error(f"Error setting due date: {e}")
        return {"success": False, "message": f"Failed to set due date: {str(e)}"}


def show_overdue(
    session: Session,
    user_id: UUID,
) -> Dict[str, Any]:
    """
    [T052] Show all overdue tasks (past due date and not completed).
    """
    logger.info(f"Tool: show_overdue called")
    try:
        tasks = TasksService.get_user_tasks(session, user_id, overdue=True)
        task_list = [_task_to_dict(t) for t in tasks]

        if not task_list:
            return {
                "success": True,
                "message": "No overdue tasks found. Great job staying on track!",
                "count": 0,
                "tasks": []
            }

        return {
            "success": True,
            "message": f"Found {len(task_list)} overdue tasks.",
            "count": len(task_list),
            "tasks": task_list
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to get overdue tasks: {str(e)}"}


# =============================================================================
# Phase 5 MCP Tools: Search (T057)
# =============================================================================

def search_tasks(
    session: Session,
    user_id: UUID,
    query: str,
) -> Dict[str, Any]:
    """
    [T057] Search tasks by keyword in title and description.

    Args:
        query: Search keyword
    """
    logger.info(f"Tool: search_tasks called - query='{query}'")
    try:
        tasks = TasksService.search_tasks(session, user_id, query)
        task_list = [_task_to_dict(t) for t in tasks]

        if not task_list:
            return {
                "success": True,
                "message": f"No tasks found matching '{query}'.",
                "count": 0,
                "tasks": []
            }

        return {
            "success": True,
            "message": f"Found {len(task_list)} tasks matching '{query}'.",
            "count": len(task_list),
            "tasks": task_list
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to search tasks: {str(e)}"}


# =============================================================================
# Phase 5 MCP Tools: Combined Filter & Sort (T064, T065)
# =============================================================================

def combined_filter(
    session: Session,
    user_id: UUID,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    completed: Optional[bool] = None,
    overdue: Optional[bool] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> Dict[str, Any]:
    """
    [T064] Filter tasks with multiple criteria combined.

    Args:
        priority: Filter by priority (low, medium, high)
        tag: Filter by tag name
        completed: Filter by completion status (true/false)
        overdue: Filter for overdue tasks only (true)
        sort_by: Sort field (created_at, due_date, priority, title)
        sort_order: Sort order (asc, desc)
    """
    logger.info(f"Tool: combined_filter called")
    try:
        tasks = TasksService.get_user_tasks(
            session=session,
            user_id=user_id,
            priority=priority,
            tag=tag,
            is_completed=completed,
            overdue=overdue,
            sort_by=sort_by,
            sort_order=sort_order or "desc",
        )
        task_list = [_task_to_dict(t) for t in tasks]

        # Build filter description
        filters = []
        if priority:
            filters.append(f"priority={priority}")
        if tag:
            filters.append(f"tag={tag}")
        if completed is not None:
            filters.append(f"completed={completed}")
        if overdue:
            filters.append("overdue=true")
        filter_desc = ", ".join(filters) if filters else "none"

        return {
            "success": True,
            "message": f"Found {len(task_list)} tasks (filters: {filter_desc}).",
            "count": len(task_list),
            "tasks": task_list
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to filter tasks: {str(e)}"}


def sort_tasks(
    session: Session,
    user_id: UUID,
    sort_by: str,
    sort_order: Optional[str] = None,
) -> Dict[str, Any]:
    """
    [T065] Sort tasks by a specific field.

    Args:
        sort_by: Field to sort by (created_at, due_date, priority, title)
        sort_order: Sort order (asc, desc) - default: desc
    """
    logger.info(f"Tool: sort_tasks called - sort_by='{sort_by}', sort_order='{sort_order}'")
    try:
        valid_sort_fields = ["created_at", "updated_at", "due_date", "priority", "title"]
        if sort_by not in valid_sort_fields:
            return {
                "success": False,
                "message": f"Invalid sort field '{sort_by}'. Must be one of: {', '.join(valid_sort_fields)}"
            }

        tasks = TasksService.get_user_tasks(
            session=session,
            user_id=user_id,
            sort_by=sort_by,
            sort_order=sort_order or "desc",
        )
        task_list = [_task_to_dict(t) for t in tasks]

        return {
            "success": True,
            "message": f"Sorted {len(task_list)} tasks by {sort_by} ({sort_order or 'desc'}).",
            "count": len(task_list),
            "tasks": task_list
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to sort tasks: {str(e)}"}


# =============================================================================
# Phase 5 MCP Tools: Reminders (T071)
# =============================================================================

def set_reminder(
    session: Session,
    user_id: UUID,
    task_identifier: str,
    remind_at: str,
) -> Dict[str, Any]:
    """
    [T071] Set a reminder for a task.

    Args:
        task_identifier: Task title (partial match) or UUID
        remind_at: Reminder time (e.g., "1 hour before", "tomorrow at 9am", ISO format)
    """
    logger.info(f"Tool: set_reminder called - task='{task_identifier}', remind_at='{remind_at}'")
    try:
        if not remind_at or not remind_at.strip():
            return {"success": False, "message": "Reminder time cannot be empty. Use '1 hour before', 'tomorrow at 9am', etc."}

        task = _find_task(session, user_id, task_identifier)
        task = TasksService.set_reminder(session, task.id, user_id, remind_at.strip())

        remind_str = task.remind_at.strftime("%A, %B %d, %Y at %I:%M %p") if task.remind_at else "none"
        return {
            "success": True,
            "message": f"Reminder set for '{task.title}' at {remind_str}.",
            "task": _task_to_dict(task)
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        error_msg = str(e)
        # Provide helpful message for relative reminder without due date
        if "no due date" in error_msg.lower():
            return {"success": False, "message": "Cannot set relative reminder (like '1 hour before') because the task has no due date. Please set a due date first, or use an absolute time like 'tomorrow at 9am'."}
        logger.error(f"Error setting reminder: {e}")
        return {"success": False, "message": f"Failed to set reminder: {error_msg}"}


# =============================================================================
# Phase 5 MCP Tools: Recurrence (T078)
# =============================================================================

def set_recurrence(
    session: Session,
    user_id: UUID,
    task_identifier: str,
    recurrence: str,
) -> Dict[str, Any]:
    """
    [T078] Set recurrence pattern for a task.

    Args:
        task_identifier: Task title (partial match) or UUID
        recurrence: Recurrence pattern (none, daily, weekly, monthly)
    """
    logger.info(f"Tool: set_recurrence called - task='{task_identifier}', recurrence='{recurrence}'")
    try:
        # Validate recurrence first
        if not recurrence or not recurrence.strip():
            return {"success": False, "message": "Recurrence cannot be empty. Use 'none', 'daily', 'weekly', or 'monthly'."}

        recurrence_lower = recurrence.lower().strip()
        if recurrence_lower not in ["none", "daily", "weekly", "monthly"]:
            return {
                "success": False,
                "message": f"Invalid recurrence '{recurrence}'. Must be none, daily, weekly, or monthly."
            }

        task = _find_task(session, user_id, task_identifier)
        task = TasksService.update_task(session, task.id, user_id, recurrence=recurrence_lower)

        if recurrence_lower == "none":
            msg = f"Removed recurrence from '{task.title}'."
        else:
            msg = f"Set '{task.title}' to repeat {recurrence_lower}."

        return {
            "success": True,
            "message": msg,
            "task": _task_to_dict(task)
        }
    except TaskNotFoundError as e:
        result = {"success": False, "message": e.message}
        if e.suggestions:
            result["suggestions"] = e.suggestions
        return result
    except Exception as e:
        logger.error(f"Error setting recurrence: {e}")
        return {"success": False, "message": f"Failed to set recurrence: {str(e)}"}
