# [Task]: T082, T097
# [Spec]: F-010 (R-010.2, R-010.4)
# [Description]: Task completion handler with CloudEvent parsing and recurrence logic
"""
Task completion handler for processing task.completed events.
Parses CloudEvents and creates the next occurrence for recurring tasks.
"""
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, ValidationError

from ..core.logging import get_logger

logger = get_logger(__name__)


class TaskEventData(BaseModel):
    """Schema for task event data payload."""
    id: str
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    priority: str = "medium"
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence: str = "none"
    parent_task_id: Optional[str] = None
    tags: list[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CloudEvent(BaseModel):
    """CloudEvents 1.0 specification schema for Dapr messages."""
    specversion: str = "1.0"
    type: str = "task.completed"
    source: str = "backend"
    id: str
    time: Optional[datetime] = None
    datacontenttype: str = "application/json"
    data: Dict[str, Any]


class TaskCompletedEvent(BaseModel):
    """Schema for task.completed event payload."""
    event_type: str
    task_id: str
    task_data: TaskEventData
    user_id: str
    timestamp: datetime


def parse_cloudevent(raw_event: Dict[str, Any]) -> Optional[TaskCompletedEvent]:
    """
    Parse a CloudEvent or raw event payload into TaskCompletedEvent.

    Dapr may send events in CloudEvent format or as raw data depending on config.
    This function handles both cases.

    Args:
        raw_event: The raw event payload from Dapr

    Returns:
        Parsed TaskCompletedEvent or None if parsing fails
    """
    try:
        # Check if this is a CloudEvent (has 'data' field with nested data)
        if "data" in raw_event and isinstance(raw_event["data"], dict):
            # CloudEvent format - extract inner data
            data = raw_event["data"]
            logger.debug(
                "cloudevent_parsed",
                event_id=raw_event.get("id"),
                event_type=raw_event.get("type"),
                source=raw_event.get("source"),
            )
        else:
            # Raw event format - use as-is
            data = raw_event

        # Parse task_data if it's a dict, convert datetime strings
        task_data = data.get("task_data", {})
        if task_data.get("due_date") and isinstance(task_data["due_date"], str):
            task_data["due_date"] = datetime.fromisoformat(
                task_data["due_date"].replace("Z", "+00:00")
            )
        if task_data.get("remind_at") and isinstance(task_data["remind_at"], str):
            task_data["remind_at"] = datetime.fromisoformat(
                task_data["remind_at"].replace("Z", "+00:00")
            )
        if task_data.get("created_at") and isinstance(task_data["created_at"], str):
            task_data["created_at"] = datetime.fromisoformat(
                task_data["created_at"].replace("Z", "+00:00")
            )
        if task_data.get("updated_at") and isinstance(task_data["updated_at"], str):
            task_data["updated_at"] = datetime.fromisoformat(
                task_data["updated_at"].replace("Z", "+00:00")
            )

        # Parse timestamp if it's a string
        timestamp = data.get("timestamp")
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        elif not timestamp:
            timestamp = datetime.utcnow()

        # Create validated model
        return TaskCompletedEvent(
            event_type=data.get("event_type", "task.completed"),
            task_id=data.get("task_id", task_data.get("id", "")),
            task_data=TaskEventData.model_validate(task_data),
            user_id=data.get("user_id", ""),
            timestamp=timestamp,
        )

    except ValidationError as e:
        logger.error(
            "cloudevent_parse_error",
            error=str(e),
            raw_event=raw_event,
        )
        return None
    except Exception as e:
        logger.error(
            "cloudevent_parse_unexpected_error",
            error=str(e),
            raw_event=raw_event,
        )
        return None


def should_process_event(event: TaskCompletedEvent) -> bool:
    """
    Determine if a task completion event should create a new occurrence.

    Args:
        event: The parsed task completion event

    Returns:
        True if the event should be processed (task has recurrence)
    """
    # Only process if task has recurrence configured
    recurrence = event.task_data.recurrence
    if recurrence == "none" or not recurrence:
        logger.debug(
            "skipping_non_recurring_task",
            task_id=event.task_id,
            recurrence=recurrence,
        )
        return False

    # Log that we will process this event
    logger.info(
        "will_process_recurring_task",
        task_id=event.task_id,
        recurrence=recurrence,
        title=event.task_data.title,
    )
    return True


async def handle_task_completed(
    raw_event: Dict[str, Any],
    create_next_occurrence_fn
) -> Dict[str, str]:
    """
    Handle a task.completed event from the Dapr pub/sub.

    This function:
    1. Parses the CloudEvent
    2. Checks if the task has recurrence
    3. If recurring, calls the provided function to create the next occurrence

    Args:
        raw_event: The raw CloudEvent payload from Dapr
        create_next_occurrence_fn: Async function to create the next task occurrence

    Returns:
        Status dict with "status" key (SUCCESS, IGNORED, FAILED)
    """
    # Parse the event
    event = parse_cloudevent(raw_event)

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

    # Create next occurrence
    try:
        result = await create_next_occurrence_fn(event)
        return result
    except Exception as e:
        logger.error(
            "failed_to_create_next_occurrence",
            task_id=event.task_id,
            error=str(e),
        )
        return {"status": "RETRY", "error": str(e)}
