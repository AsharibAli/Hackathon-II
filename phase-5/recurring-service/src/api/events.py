# [Task]: T079, T082, T097
# [Spec]: F-010 (R-010.2)
# [Description]: Task event handler endpoint for Dapr subscription
from fastapi import APIRouter, Request
from datetime import datetime

from ..core.logging import get_logger
from ..services.recurrence import calculate_next_due
from ..services.backend_client import backend_client
from ..handlers import parse_cloudevent, should_process_event, TaskCompletedEvent

router = APIRouter(tags=["events"])
logger = get_logger(__name__)


async def create_next_occurrence(event: TaskCompletedEvent, token: str = "") -> dict:
    """
    Create the next occurrence of a recurring task.

    Args:
        event: The parsed task completion event
        token: JWT token for backend authentication

    Returns:
        Status dict with result of operation
    """
    task_data = event.task_data
    recurrence = task_data.recurrence

    # Calculate next due date
    next_due = calculate_next_due(
        current_due=task_data.due_date,
        recurrence=recurrence,
        completed_at=datetime.utcnow(),
    )

    if not next_due:
        logger.warning(
            "could_not_calculate_next_due",
            task_id=event.task_id,
            recurrence=recurrence,
        )
        return {"status": "FAILED", "reason": "could not calculate next due date"}

    # If no token, we'd need service-to-service auth
    if not token:
        logger.warning(
            "no_auth_token_available",
            task_id=event.task_id,
        )
        return {
            "status": "SKIPPED",
            "reason": "no authentication token available",
        }

    try:
        new_task = await backend_client.create_task(
            title=task_data.title,
            user_id=event.user_id,
            token=token,
            description=task_data.description,
            priority=task_data.priority,
            tags=task_data.tags,
            due_date=next_due,
            recurrence=recurrence,
            parent_task_id=event.task_id,
        )

        logger.info(
            "recurring_task_created",
            original_task_id=event.task_id,
            new_task_id=new_task.get("id"),
            next_due=str(next_due),
            user_id=event.user_id,
        )

        return {"status": "SUCCESS", "new_task_id": new_task.get("id")}

    except Exception as e:
        logger.error(
            "failed_to_create_recurring_task",
            task_id=event.task_id,
            error=str(e),
        )
        return {"status": "RETRY", "error": str(e)}


@router.post("/api/events/task")
async def handle_task_event(request: Request) -> dict:
    """
    Handle task events from Dapr pub/sub.

    This endpoint receives CloudEvents from the task-events topic
    and creates the next occurrence for recurring tasks when completed.
    """
    try:
        body = await request.json()

        logger.info(
            "task_event_received",
            raw_type=body.get("type"),
            has_data="data" in body,
        )

        # Parse the CloudEvent using handler module
        event = parse_cloudevent(body)

        if event is None:
            logger.warning(
                "event_skipped_invalid",
                reason="Failed to parse event data",
            )
            # Return SUCCESS to ACK and avoid infinite retries on bad data
            return {"status": "SUCCESS", "note": "Invalid event skipped"}

        # Check event type
        if event.event_type != "task.completed":
            logger.debug(
                "ignoring_non_completion_event",
                event_type=event.event_type,
            )
            return {"status": "IGNORED", "reason": "not a completion event"}

        # Check if we should process this event
        if not should_process_event(event):
            return {"status": "IGNORED", "reason": "task is not recurring"}

        # Log the event processing (structured JSON logging)
        logger.info(
            "processing_task_completion",
            event="task_completed",
            task_id=event.task_id,
            task_title=event.task_data.title,
            user_id=event.user_id,
            recurrence=event.task_data.recurrence,
            due_date=event.task_data.due_date.isoformat() if event.task_data.due_date else None,
        )

        # Extract authorization header from the original request if available
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if auth_header else ""

        # Create next occurrence
        return await create_next_occurrence(event, token)

    except Exception as e:
        logger.error("task_event_processing_failed", error=str(e))
        # Return 200 to ACK the message (don't retry on parse errors)
        return {"status": "FAILED", "error": str(e)}
