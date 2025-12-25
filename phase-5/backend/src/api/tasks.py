"""
Tasks API endpoints.
Handles task CRUD operations with authentication and user isolation.

[Task]: T030-T054, T061-T071, T085-T088
[Spec]: F-001 to F-006, F-008
[Description]: Phase 5 enhanced task endpoints with priority, tags, due dates, filters, search
"""
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session
from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from core.database import get_session
from services.tasks import TasksService
from api.dependencies import get_current_user
from models.user import User
from models.task import Task, Priority, Recurrence


router = APIRouter()


# Enums for query parameters
class SortField(str, Enum):
    """Fields available for sorting."""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    TITLE = "title"


class SortOrder(str, Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"


# Request/Response Models
class TaskRead(BaseModel):
    """Response model for task data with Phase 5 fields."""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    is_completed: bool
    created_at: str
    updated_at: str
    # Phase 5 additions
    priority: str
    due_date: Optional[str] = None
    remind_at: Optional[str] = None
    reminder_sent: bool = False
    recurrence: str
    parent_task_id: Optional[str] = None
    tags: List[str] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21c-32d1-b654-321456987000",
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "is_completed": False,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z",
                "priority": "medium",
                "due_date": "2025-01-20T14:00:00Z",
                "remind_at": "2025-01-20T13:00:00Z",
                "reminder_sent": False,
                "recurrence": "none",
                "parent_task_id": None,
                "tags": ["work", "documentation"]
            }
        }
    }


class TaskCreate(BaseModel):
    """Request model for creating a task with Phase 5 fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    # Phase 5 additions
    priority: Optional[str] = Field("medium", description="Priority: low, medium, high")
    due_date: Optional[str] = Field(None, description="Due date (ISO format or natural language)")
    remind_at: Optional[str] = Field(None, description="Reminder time (ISO format or natural language)")
    recurrence: Optional[str] = Field("none", description="Recurrence: none, daily, weekly, monthly")
    parent_task_id: Optional[str] = Field(None, description="Parent task ID for recurring instances")
    tags: Optional[List[str]] = Field(None, description="List of tag names")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "priority": "high",
                "due_date": "next Friday",
                "remind_at": "1 hour before",
                "recurrence": "weekly",
                "tags": ["work", "documentation"]
            }
        }
    }


class TaskUpdate(BaseModel):
    """Request model for updating a task with Phase 5 fields."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    is_completed: Optional[bool] = Field(None, description="Completion status")
    # Phase 5 additions
    priority: Optional[str] = Field(None, description="Priority: low, medium, high")
    due_date: Optional[str] = Field(None, description="Due date (ISO format or natural language)")
    remind_at: Optional[str] = Field(None, description="Reminder time (ISO format or natural language)")
    recurrence: Optional[str] = Field(None, description="Recurrence: none, daily, weekly, monthly")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Updated task title",
                "description": "Updated description",
                "is_completed": True,
                "priority": "high",
                "due_date": "2025-01-25T14:00:00Z"
            }
        }
    }


class TagRequest(BaseModel):
    """Request model for adding a tag."""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")


def task_to_read(task: Task) -> TaskRead:
    """Convert Task model to TaskRead response."""
    # Extract tag names
    tag_names = [tag.name for tag in task.tags] if task.tags else []

    return TaskRead(
        id=str(task.id),
        user_id=str(task.user_id),
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        # Phase 5 fields
        priority=task.priority.value if hasattr(task.priority, 'value') else task.priority,
        due_date=task.due_date.isoformat() if task.due_date else None,
        remind_at=task.remind_at.isoformat() if task.remind_at else None,
        reminder_sent=task.reminder_sent,
        recurrence=task.recurrence.value if hasattr(task.recurrence, 'value') else task.recurrence,
        parent_task_id=str(task.parent_task_id) if task.parent_task_id else None,
        tags=tag_names,
    )


@router.get(
    "",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="Get all tasks with filters",
    description="Retrieve tasks with optional filters for priority, tags, completion, due dates, and sorting."
)
async def get_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    # Phase 5 filter parameters
    priority: Annotated[Optional[str], Query(description="Filter by priority: low, medium, high")] = None,
    tag: Annotated[Optional[str], Query(description="Filter by tag name")] = None,
    is_completed: Annotated[Optional[bool], Query(description="Filter by completion status")] = None,
    overdue: Annotated[Optional[bool], Query(description="Filter for overdue tasks only")] = None,
    has_due_date: Annotated[Optional[bool], Query(description="Filter for tasks with/without due date")] = None,
    sort_by: Annotated[SortField, Query(description="Sort field")] = SortField.CREATED_AT,
    sort_order: Annotated[SortOrder, Query(description="Sort order")] = SortOrder.DESC,
) -> List[TaskRead]:
    """
    Get all tasks for the authenticated user with optional filters.

    Phase 5 filters:
    - priority: Filter by priority level
    - tag: Filter by tag name (case-insensitive)
    - is_completed: Filter by completion status
    - overdue: Show only overdue tasks
    - has_due_date: Filter tasks with/without due dates
    - sort_by: Field to sort by
    - sort_order: Sort direction (asc/desc)
    """
    tasks = TasksService.get_user_tasks(
        session=session,
        user_id=current_user.id,
        priority=priority,
        tag=tag,
        is_completed=is_completed,
        overdue=overdue,
        has_due_date=has_due_date,
        sort_by=sort_by.value if sort_by else None,
        sort_order=sort_order.value if sort_order else None,
    )
    return [task_to_read(task) for task in tasks]


@router.get(
    "/search",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="Search tasks",
    description="Search tasks by keyword in title and description."
)
async def search_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    q: Annotated[str, Query(min_length=1, description="Search query")],
) -> List[TaskRead]:
    """
    Search tasks by keyword.

    Performs case-insensitive partial match on title and description.
    """
    tasks = TasksService.search_tasks(
        session=session,
        user_id=current_user.id,
        query=q,
    )
    return [task_to_read(task) for task in tasks]


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task with Phase 5 features."
)
async def create_task(
    request: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Create a new task with Phase 5 features.

    - **title**: Task title (required, max 200 characters)
    - **description**: Task description (optional)
    - **priority**: low, medium, high (default: medium)
    - **due_date**: Due date (ISO format or natural language like "tomorrow")
    - **remind_at**: Reminder time (ISO format or natural language)
    - **recurrence**: none, daily, weekly, monthly (default: none)
    - **tags**: List of tag names

    Returns the created task.
    """
    task = TasksService.create_task(
        session=session,
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        due_date=request.due_date,
        remind_at=request.remind_at,
        recurrence=request.recurrence,
        parent_task_id=request.parent_task_id,
        tags=request.tags,
    )
    return task_to_read(task)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
    description="Retrieve a specific task by ID. User must own the task."
)
async def get_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Get a specific task by ID.

    Returns 404 if task doesn't exist or doesn't belong to the user.
    """
    task = TasksService.get_task_by_id(
        session=session,
        task_id=task_id,
        user_id=current_user.id
    )
    return task_to_read(task)


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Update task with Phase 5 fields. User must own the task."
)
async def update_task(
    task_id: UUID,
    request: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Update an existing task with Phase 5 fields.

    - **title**: New title (optional)
    - **description**: New description (optional)
    - **is_completed**: New completion status (optional)
    - **priority**: New priority (optional)
    - **due_date**: New due date (optional)
    - **remind_at**: New reminder time (optional)
    - **recurrence**: New recurrence pattern (optional)

    Returns 404 if task doesn't exist or doesn't belong to the user.
    """
    task = TasksService.update_task(
        session=session,
        task_id=task_id,
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        is_completed=request.is_completed,
        priority=request.priority,
        due_date=request.due_date,
        remind_at=request.remind_at,
        recurrence=request.recurrence,
    )
    return task_to_read(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task. User must own the task."
)
async def delete_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> None:
    """
    Delete a task permanently.

    Returns 204 No Content on success.
    Returns 404 if task doesn't exist or doesn't belong to the user.
    """
    TasksService.delete_task(
        session=session,
        task_id=task_id,
        user_id=current_user.id
    )


@router.patch(
    "/{task_id}/complete",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion",
    description="Toggle a task's completion status. User must own the task."
)
async def toggle_task_completion(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Toggle task completion status.

    If task is completed, marks it as incomplete. If incomplete, marks it as completed.
    For recurring tasks, publishes task.completed event.
    Returns 404 if task doesn't exist or doesn't belong to the user.
    """
    task = TasksService.toggle_task_completion(
        session=session,
        task_id=task_id,
        user_id=current_user.id
    )
    return task_to_read(task)


# Phase 5: Tag Management Endpoints
@router.post(
    "/{task_id}/tags",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Add tag to task",
    description="Add a tag to a task. Creates the tag if it doesn't exist."
)
async def add_tag_to_task(
    task_id: UUID,
    request: TagRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Add a tag to a task.

    - Creates the tag if it doesn't exist for the user
    - Tags are case-insensitive (stored lowercase)
    - No-op if tag is already on the task
    """
    task = TasksService.add_tag_to_task(
        session=session,
        task_id=task_id,
        user_id=current_user.id,
        tag_name=request.name,
    )
    return task_to_read(task)


@router.delete(
    "/{task_id}/tags/{tag_name}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Remove tag from task",
    description="Remove a tag from a task."
)
async def remove_tag_from_task(
    task_id: UUID,
    tag_name: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Remove a tag from a task.

    - Tag matching is case-insensitive
    - No-op if tag is not on the task
    """
    task = TasksService.remove_tag_from_task(
        session=session,
        task_id=task_id,
        user_id=current_user.id,
        tag_name=tag_name,
    )
    return task_to_read(task)


# Phase 5: Reminder Endpoint
@router.post(
    "/{task_id}/reminder",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Set task reminder",
    description="Set a reminder for a task."
)
async def set_task_reminder(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    remind_at: Annotated[str, Query(description="Reminder time (ISO format or natural language)")],
) -> TaskRead:
    """
    Set a reminder for a task.

    - Accepts ISO format or natural language (e.g., "1 hour before", "tomorrow at 9am")
    - Resets reminder_sent to false
    """
    task = TasksService.set_reminder(
        session=session,
        task_id=task_id,
        user_id=current_user.id,
        remind_at=remind_at,
    )
    return task_to_read(task)
