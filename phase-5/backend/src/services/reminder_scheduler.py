# [Task]: T068, T070
# [Spec]: F-006 (R-006.1, R-006.2)
# [Description]: Reminder scheduler service with background polling
"""
Reminder scheduler service.
Polls for pending reminders and publishes events to the notification service via Dapr.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from core.database import engine
from models.task import Task
from services.events.publisher import event_publisher

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    Background service that polls for tasks with pending reminders
    and publishes reminder events to the notification service.
    """

    def __init__(
        self,
        poll_interval_seconds: int = 60,
        enabled: bool = True,
    ):
        self.poll_interval_seconds = poll_interval_seconds
        self.enabled = enabled
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the reminder scheduler background task."""
        if not self.enabled:
            logger.info("Reminder scheduler is disabled")
            return

        if self._running:
            logger.warning("Reminder scheduler is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(
            f"Reminder scheduler started (polling every {self.poll_interval_seconds}s)"
        )

    async def stop(self) -> None:
        """Stop the reminder scheduler background task."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("Reminder scheduler stopped")

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                await self._check_pending_reminders()
            except Exception as e:
                logger.error(f"Error in reminder scheduler poll loop: {e}")

            # Wait for next poll interval
            await asyncio.sleep(self.poll_interval_seconds)

    async def _check_pending_reminders(self) -> None:
        """
        Check for tasks with remind_at in the past and reminder_sent=False.
        Publish reminder events and mark them as sent.
        """
        now = datetime.now(timezone.utc)
        count = 0

        with Session(engine) as session:
            # Find tasks with pending reminders
            statement = select(Task).where(
                Task.remind_at != None,
                Task.remind_at <= now,
                Task.reminder_sent == False,
                Task.is_completed == False,
            )
            tasks = session.exec(statement).all()

            for task in tasks:
                try:
                    # Publish reminder event
                    success = await event_publisher.publish_reminder_event(
                        task=task,
                        user_id=task.user_id,
                    )

                    if success:
                        # Mark reminder as sent
                        task.reminder_sent = True
                        session.add(task)
                        count += 1
                        logger.info(
                            f"Sent reminder for task '{task.title}' (id={task.id})"
                        )
                    else:
                        logger.warning(
                            f"Failed to send reminder for task {task.id}, will retry"
                        )

                except Exception as e:
                    logger.error(f"Error processing reminder for task {task.id}: {e}")

            # Commit all changes
            if count > 0:
                session.commit()
                logger.info(f"Processed {count} pending reminders")


# Singleton instance
import os

reminder_scheduler = ReminderScheduler(
    poll_interval_seconds=int(os.getenv("REMINDER_POLL_INTERVAL", "60")),
    enabled=os.getenv("REMINDER_SCHEDULER_ENABLED", "true").lower() == "true",
)
