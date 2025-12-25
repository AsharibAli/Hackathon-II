# [Task]: T079
# [Spec]: F-010 (R-010.2)
# [Description]: Task event handler endpoint for Dapr subscription
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..core.logging import get_logger
from ..services.recurrence import calculate_next_due
from ..services.backend_client import backend_client

router = APIRouter(tags=["events"])
logger = get_logger(__name__)


class TaskData(BaseModel):
    """Schema for task data in events."""
    id: str
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    priority: str = "medium"
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence: str = "none"
    parent_task_id: Optional[str] = None
    tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaskEventData(BaseModel):
    """Schema for task event data."""
    event_type: str
    task_id: str
    task_data: TaskData
    user_id: str
    timestamp: datetime


@router.post("/api/events/task")
async def handle_task_event(request: Request) -> dict:
    """
    Handle task events from Dapr pub/sub.

    This endpoint receives CloudEvents from the task-events topic
    and creates the next occurrence for recurring tasks when completed.
    """
    try:
        body = await request.json()

        # Extract data from CloudEvent wrapper or raw event
        data = body.get("data", body)

        event_type = data.get("event_type")
        task_data = data.get("task_data", {})
        user_id = data.get("user_id")

        logger.info(
            "task_event_received",
            event_type=event_type,
            task_id=data.get("task_id"),
            recurrence=task_data.get("recurrence"),
        )

        # Only process task.completed events
        if event_type != "task.completed":
            logger.debug("ignoring_non_completion_event", event_type=event_type)
            return {"status": "IGNORED", "reason": "not a completion event"}

        # Check if task has recurrence
        recurrence = task_data.get("recurrence", "none")
        if recurrence == "none":
            logger.debug("ignoring_non_recurring_task", task_id=data.get("task_id"))
            return {"status": "IGNORED", "reason": "task is not recurring"}

        # Calculate next due date
        current_due = None
        if task_data.get("due_date"):
            current_due = datetime.fromisoformat(
                task_data["due_date"].replace("Z", "+00:00")
            )

        next_due = calculate_next_due(
            current_due=current_due,
            recurrence=recurrence,
            completed_at=datetime.utcnow(),
        )

        if not next_due:
            logger.warning(
                "could_not_calculate_next_due",
                task_id=data.get("task_id"),
                recurrence=recurrence,
            )
            return {"status": "FAILED", "reason": "could not calculate next due date"}

        # Create next occurrence via backend API
        # Note: In production, we'd need to get a valid token
        # For now, we'll use a service-to-service authentication mechanism
        try:
            # Extract authorization header from the original request if available
            auth_header = request.headers.get("Authorization", "")
            token = auth_header.replace("Bearer ", "") if auth_header else ""

            # If no token, we'd need service-to-service auth
            # This is a placeholder - in production use proper service auth
            if not token:
                logger.warning(
                    "no_auth_token_available",
                    task_id=data.get("task_id"),
                )
                # For now, skip task creation without auth
                return {
                    "status": "SKIPPED",
                    "reason": "no authentication token available",
                }

            new_task = await backend_client.create_task(
                title=task_data.get("title"),
                user_id=user_id,
                token=token,
                description=task_data.get("description"),
                priority=task_data.get("priority", "medium"),
                tags=task_data.get("tags", []),
                due_date=next_due,
                recurrence=recurrence,
                parent_task_id=str(data.get("task_id")),
            )

            logger.info(
                "recurring_task_created",
                original_task_id=data.get("task_id"),
                new_task_id=new_task.get("id"),
                next_due=str(next_due),
                user_id=user_id,
            )

            return {"status": "SUCCESS", "new_task_id": new_task.get("id")}

        except Exception as e:
            logger.error(
                "failed_to_create_recurring_task",
                task_id=data.get("task_id"),
                error=str(e),
            )
            # Return 503 to trigger Dapr retry
            return {"status": "RETRY", "error": str(e)}

    except Exception as e:
        logger.error("task_event_processing_failed", error=str(e))
        # Return 200 to ACK the message (don't retry on parse errors)
        return {"status": "FAILED", "error": str(e)}
