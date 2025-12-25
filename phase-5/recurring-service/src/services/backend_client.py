# [Task]: T081
# [Spec]: F-010 (R-010.5)
# [Description]: Backend API client for creating tasks
import httpx
from typing import Optional, List
from datetime import datetime

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class BackendClient:
    """HTTP client for communicating with the backend API."""

    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or settings.backend_url
        self.timeout = timeout or settings.backend_timeout

    async def create_task(
        self,
        title: str,
        user_id: str,
        token: str,
        description: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        recurrence: str = "none",
        parent_task_id: Optional[str] = None,
    ) -> dict:
        """
        Create a new task via the backend API.

        Args:
            title: Task title
            user_id: Owner user ID
            token: JWT token for authentication
            description: Optional task description
            priority: Task priority (low, medium, high)
            tags: Optional list of tag names
            due_date: Optional due date
            recurrence: Recurrence pattern (none, daily, weekly, monthly)
            parent_task_id: Reference to parent recurring task

        Returns:
            Created task data from backend
        """
        payload = {
            "title": title,
            "description": description,
            "priority": priority,
            "recurrence": recurrence,
        }

        if due_date:
            payload["due_date"] = due_date.isoformat()

        if parent_task_id:
            payload["parent_task_id"] = parent_task_id

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/tasks",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                task_data = response.json()

                logger.info(
                    "task_created_via_api",
                    task_id=task_data.get("id"),
                    title=title,
                    parent_task_id=parent_task_id,
                    user_id=user_id,
                )

                # Add tags if provided
                if tags:
                    await self._add_tags(
                        client, task_data["id"], tags, headers
                    )

                return task_data

        except httpx.HTTPStatusError as e:
            logger.error(
                "task_creation_failed",
                status_code=e.response.status_code,
                error=str(e),
                user_id=user_id,
            )
            raise
        except Exception as e:
            logger.error(
                "task_creation_error",
                error=str(e),
                user_id=user_id,
            )
            raise

    async def _add_tags(
        self,
        client: httpx.AsyncClient,
        task_id: str,
        tags: List[str],
        headers: dict,
    ) -> None:
        """Add tags to a task."""
        for tag in tags:
            try:
                await client.post(
                    f"{self.base_url}/api/tasks/{task_id}/tags",
                    json={"name": tag},
                    headers=headers,
                )
            except Exception as e:
                logger.warning(
                    "tag_addition_failed",
                    task_id=task_id,
                    tag=tag,
                    error=str(e),
                )


# Singleton instance
backend_client = BackendClient()
