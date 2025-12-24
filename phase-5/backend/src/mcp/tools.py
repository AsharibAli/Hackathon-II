"""
MCP tools for task management.
Wraps existing task service logic for AI agent consumption.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session
import logging
from services.tasks import TasksService
from models.task import Task

logger = logging.getLogger(__name__)

def add_task(
    session: Session,
    user_id: UUID,
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task.
    """
    logger.info(f"Tool: add_task called for user {user_id} with title='{title}'")
    try:
        task = TasksService.create_task(
            session=session,
            user_id=user_id,
            title=title,
            description=description
        )
        return {
            "success": True,
            "message": f"Task '{task.title}' created successfully.",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to create task: {str(e)}"}

def list_tasks(
    session: Session,
    user_id: UUID,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    List all tasks for the user.
    """
    logger.info(f"Tool: list_tasks called for user {user_id} with completed={completed}")
    try:
        tasks = TasksService.get_user_tasks(session, user_id)
        
        # Filter if requested
        if completed is not None:
            tasks = [t for t in tasks if t.is_completed == completed]
            
        task_list = [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "is_completed": t.is_completed
            }
            for t in tasks
        ]
        
        return {
            "success": True,
            "count": len(task_list),
            "tasks": task_list
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to list tasks: {str(e)}"}

def _find_task(session: Session, user_id: UUID, task_identifier: str) -> Optional[Task]:
    """Helper to find task by ID or fuzzy title match."""
    # Try as UUID first
    try:
        task_id = UUID(task_identifier)
        return TasksService.get_task_by_id(session, task_id, user_id)
    except:
        pass
        
    # Fuzzy match by title
    tasks = TasksService.get_user_tasks(session, user_id)
    matches = [t for t in tasks if task_identifier.lower() in t.title.lower()]
    
    if len(matches) == 1:
        return matches[0]
    return None

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
        if not task:
            return {"success": False, "message": f"Task '{task_identifier}' not found or ambiguous."}
            
        task = TasksService.update_task(session, task.id, user_id, is_completed=True)
        return {
            "success": True,
            "message": f"Task '{task.title}' marked as completed.",
            "task": {"id": str(task.id), "is_completed": True}
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to complete task: {str(e)}"}

def update_task(
    session: Session,
    user_id: UUID,
    task_identifier: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a task's title or description.
    """
    logger.info(f"Tool: update_task called for user {user_id} with task_identifier='{task_identifier}'")
    try:
        task = _find_task(session, user_id, task_identifier)
        if not task:
            return {"success": False, "message": f"Task '{task_identifier}' not found or ambiguous."}
            
        task = TasksService.update_task(
            session, 
            task.id, 
            user_id, 
            title=title, 
            description=description
        )
        return {
            "success": True,
            "message": f"Task '{task.title}' updated.",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description
            }
        }
    except Exception as e:
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
        if not task:
            return {"success": False, "message": f"Task '{task_identifier}' not found or ambiguous."}
            
        TasksService.delete_task(session, task.id, user_id)
        return {
            "success": True,
            "message": f"Task '{task.title}' deleted."
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to delete task: {str(e)}"}
