# [Task]: T072
# [Spec]: F-009 (R-009.2)
# [Description]: Reminder event handler endpoint for Dapr subscription
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..core.logging import get_logger

router = APIRouter(tags=["reminders"])
logger = get_logger(__name__)


class ReminderEventData(BaseModel):
    """Schema for reminder event data."""
    task_id: str
    title: str
    due_at: Optional[datetime] = None
    remind_at: datetime
    user_id: str


class CloudEventWrapper(BaseModel):
    """CloudEvents wrapper for Dapr messages."""
    specversion: str = "1.0"
    type: str
    source: str
    id: str
    time: datetime
    datacontenttype: str = "application/json"
    data: ReminderEventData


@router.post("/api/reminders/handle")
async def handle_reminder(request: Request) -> dict:
    """
    Handle reminder events from Dapr pub/sub.

    This endpoint receives CloudEvents from the reminders topic
    and logs the notification (future: sends email/push).
    """
    try:
        body = await request.json()

        # Extract data from CloudEvent wrapper or raw event
        data = body.get("data", body)

        task_id = data.get("task_id")
        title = data.get("title")
        due_at = data.get("due_at")
        remind_at = data.get("remind_at")
        user_id = data.get("user_id")

        logger.info(
            "reminder_received",
            task_id=task_id,
            title=title,
            due_at=due_at,
            remind_at=remind_at,
            user_id=user_id,
        )

        # Future: Send actual notification (email, push, etc.)
        # For now, we just log the reminder

        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error("reminder_processing_failed", error=str(e))
        # Return 200 to ACK the message (don't retry on parse errors)
        return {"status": "FAILED", "error": str(e)}
