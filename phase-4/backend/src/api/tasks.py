"""
Tasks API endpoints.
Handles task CRUD operations with authentication and user isolation.
"""
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from uuid import UUID

from core.database import get_session
from services.tasks import TasksService
from api.dependencies import get_current_user
from models.user import User
from models.task import Task


router = APIRouter()


# Request/Response Models
class TaskRead(BaseModel):
    """Response model for task data."""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    is_completed: bool
    created_at: str
    updated_at: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21c-32d1-b654-321456987000",
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "is_completed": False,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            }
        }
    }


class TaskCreate(BaseModel):
    """Request model for creating a task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs"
            }
        }
    }


class TaskUpdate(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    is_completed: Optional[bool] = Field(None, description="Completion status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Updated task title",
                "description": "Updated description",
                "is_completed": True
            }
        }
    }


def task_to_read(task: Task) -> TaskRead:
    """Convert Task model to TaskRead response."""
    return TaskRead(
        id=str(task.id),
        user_id=str(task.user_id),
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat()
    )


@router.get(
    "",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="Get all tasks",
    description="Retrieve all tasks for the authenticated user, ordered by creation date (newest first)."
)
async def get_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> List[TaskRead]:
    """
    Get all tasks for the authenticated user.

    Returns list of tasks ordered by creation date (newest first).
    Empty list if user has no tasks.
    """
    tasks = TasksService.get_user_tasks(session=session, user_id=current_user.id)
    return [task_to_read(task) for task in tasks]


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user."
)
async def create_task(
    request: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Create a new task.

    - **title**: Task title (required, max 200 characters)
    - **description**: Task description (optional, max 2000 characters)

    Returns the created task with is_completed set to False.
    """
    task = TasksService.create_task(
        session=session,
        user_id=current_user.id,
        title=request.title,
        description=request.description
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
    description="Update task title, description, or completion status. User must own the task."
)
async def update_task(
    task_id: UUID,
    request: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Update an existing task.

    - **title**: New title (optional)
    - **description**: New description (optional)
    - **is_completed**: New completion status (optional)

    Returns 404 if task doesn't exist or doesn't belong to the user.
    """
    task = TasksService.update_task(
        session=session,
        task_id=task_id,
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        is_completed=request.is_completed
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
    Returns 404 if task doesn't exist or doesn't belong to the user.
    """
    task = TasksService.toggle_task_completion(
        session=session,
        task_id=task_id,
        user_id=current_user.id
    )
    return task_to_read(task)
