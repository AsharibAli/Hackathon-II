# [Task]: T024
# [Spec]: F-008 (R-008.1)
# [Description]: Event schemas for Kafka messages
"""
Pydantic schemas for Kafka events published via Dapr pub/sub.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TaskEventData(BaseModel):
    """Task data included in task events."""
    id: UUID
    title: str
    description: Optional[str] = None
    is_completed: bool
    priority: str
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence: str
    parent_task_id: Optional[UUID] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None,
        }


class TaskEvent(BaseModel):
    """
    Event published to task-events topic.

    Event types:
    - task.created: New task created
    - task.updated: Task modified
    - task.completed: Task marked complete
    - task.deleted: Task deleted
    """
    event_type: str
    task_id: UUID
    task_data: TaskEventData
    user_id: UUID
    timestamp: datetime

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class ReminderEvent(BaseModel):
    """
    Event published to reminders topic when a reminder is due.
    """
    task_id: UUID
    title: str
    due_at: Optional[datetime] = None
    remind_at: datetime
    user_id: UUID

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None,
        }
