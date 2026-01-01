# [Task]: T073, T092
# [Spec]: F-009 (R-009.2)
# [Description]: Reminder handler with CloudEvent parsing and structured logging
"""
Reminder handler for processing reminder events.
Parses CloudEvents and logs notifications with structured JSON logging.
"""
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, ValidationError

from ..core.logging import get_logger

logger = get_logger(__name__)


class ReminderEventData(BaseModel):
    """Schema for reminder event data payload."""
    task_id: str
    title: str
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    user_id: str


class CloudEvent(BaseModel):
    """CloudEvents 1.0 specification schema for Dapr messages."""
    specversion: str = "1.0"
    type: str = "reminder.triggered"
    source: str = "backend"
    id: str
    time: Optional[datetime] = None
    datacontenttype: str = "application/json"
    data: Dict[str, Any]


def parse_cloudevent(raw_event: Dict[str, Any]) -> Optional[ReminderEventData]:
    """
    Parse a CloudEvent or raw event payload into ReminderEventData.

    Dapr may send events in CloudEvent format or as raw data depending on config.
    This function handles both cases.

    Args:
        raw_event: The raw event payload from Dapr

    Returns:
        Parsed ReminderEventData or None if parsing fails
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

        # Parse into our data model
        return ReminderEventData.model_validate(data)

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


async def handle_reminder_event(raw_event: Dict[str, Any]) -> Dict[str, str]:
    """
    Handle a reminder event from the Dapr pub/sub.

    This function:
    1. Parses the CloudEvent
    2. Logs the reminder with structured JSON
    3. Returns success/failure status

    Future: Actually send email/push notifications.

    Args:
        raw_event: The raw CloudEvent payload from Dapr

    Returns:
        Status dict with "status" key (SUCCESS or FAILED)
    """
    # Parse the event
    reminder_data = parse_cloudevent(raw_event)

    if reminder_data is None:
        logger.warning(
            "reminder_skipped_invalid",
            reason="Failed to parse event data",
        )
        # Return SUCCESS to ACK and avoid infinite retries on bad data
        return {"status": "SUCCESS", "note": "Invalid event skipped"}

    # Log the reminder notification (structured JSON logging)
    logger.info(
        "notification_reminder",
        event="reminder_notification",
        task_id=reminder_data.task_id,
        task_title=reminder_data.title,
        user_id=reminder_data.user_id,
        due_at=reminder_data.due_at.isoformat() if reminder_data.due_at else None,
        remind_at=reminder_data.remind_at.isoformat() if reminder_data.remind_at else None,
        notification_type="reminder",
        notification_status="logged",
    )

    # Future implementation points:
    # - Look up user email from user service
    # - Send email notification via email provider
    # - Send push notification if user has mobile app
    # - Store notification in database for history

    return {"status": "SUCCESS"}
