# [Task]: T023
# [Spec]: F-008 (R-008.1, R-008.2)
# [Description]: Event publisher service using Dapr HTTP API
"""
Event publisher service for publishing events to Kafka via Dapr pub/sub.
Uses Dapr sidecar HTTP API for abstraction from Kafka client libraries.
"""
import httpx
import logging
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID

from .schemas import TaskEvent, TaskEventData, ReminderEvent
from models.task import Task

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes events to Kafka topics via Dapr pub/sub building block.

    Uses HTTP POST to Dapr sidecar at localhost:3500/v1.0/publish/{pubsub}/{topic}
    This abstracts away Kafka client libraries per constitution principle II.
    """

    def __init__(
        self,
        dapr_port: int = 3500,
        pubsub_name: str = "kafka-pubsub",
        enabled: bool = True,
    ):
        self.dapr_port = dapr_port
        self.pubsub_name = pubsub_name
        self.enabled = enabled
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def base_url(self) -> str:
        return f"http://localhost:{self.dapr_port}/v1.0/publish/{self.pubsub_name}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def publish_task_event(
        self,
        event_type: str,
        task: Task,
        user_id: UUID,
    ) -> bool:
        """
        Publish a task event to the task-events topic.

        Args:
            event_type: One of task.created, task.updated, task.completed, task.deleted
            task: The task entity
            user_id: User who triggered the event

        Returns:
            True if published successfully, False otherwise
        """
        if not self.enabled:
            logger.info(
                f"Event publishing disabled - would publish {event_type} for task {task.id}"
            )
            return True

        try:
            # Extract tag names from task
            tag_names = [tag.name for tag in task.tags] if task.tags else []

            task_data = TaskEventData(
                id=task.id,
                title=task.title,
                description=task.description,
                is_completed=task.is_completed,
                priority=task.priority.value if hasattr(task.priority, 'value') else task.priority,
                due_date=task.due_date,
                remind_at=task.remind_at,
                recurrence=task.recurrence.value if hasattr(task.recurrence, 'value') else task.recurrence,
                parent_task_id=task.parent_task_id,
                tags=tag_names,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )

            event = TaskEvent(
                event_type=event_type,
                task_id=task.id,
                task_data=task_data,
                user_id=user_id,
                timestamp=datetime.now(timezone.utc),
            )

            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/task-events",
                json=event.model_dump(mode="json"),
            )
            response.raise_for_status()

            logger.info(
                f"Published {event_type} event for task {task.id}"
            )
            return True

        except httpx.HTTPError as e:
            logger.error(
                f"Failed to publish {event_type} event for task {task.id}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error publishing {event_type} event: {e}"
            )
            return False

    async def publish_reminder_event(
        self,
        task: Task,
        user_id: UUID,
    ) -> bool:
        """
        Publish a reminder event to the reminders topic.

        Args:
            task: The task with a due reminder
            user_id: User who owns the task

        Returns:
            True if published successfully, False otherwise
        """
        if not self.enabled:
            logger.info(
                f"Event publishing disabled - would publish reminder for task {task.id}"
            )
            return True

        try:
            event = ReminderEvent(
                task_id=task.id,
                title=task.title,
                due_at=task.due_date,
                remind_at=task.remind_at,
                user_id=user_id,
            )

            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/reminders",
                json=event.model_dump(mode="json"),
            )
            response.raise_for_status()

            logger.info(f"Published reminder event for task {task.id}")
            return True

        except httpx.HTTPError as e:
            logger.error(
                f"Failed to publish reminder event for task {task.id}: {e}"
            )
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing reminder event: {e}")
            return False


# Singleton instance - can be configured via environment variables
import os

event_publisher = EventPublisher(
    dapr_port=int(os.getenv("DAPR_HTTP_PORT", "3500")),
    pubsub_name=os.getenv("PUBSUB_NAME", "kafka-pubsub"),
    enabled=os.getenv("DAPR_ENABLED", "true").lower() == "true",
)
