"""
Tasks service layer.
Handles task CRUD operations with user isolation.

[Task]: T030-T054, T061-T071, T085-T088
[Spec]: F-001 to F-008
[Description]: Phase 5 enhanced task service with priority, tags, due dates, filters, events
"""
from sqlmodel import Session, select, or_, and_
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

from models.task import Task, Priority, Recurrence
from models.tag import Tag, TaskTag
from models.user import User
from datetime import datetime, timezone
from utils.date_parser import parse_natural_date

logger = logging.getLogger(__name__)


class TasksService:
    """Service class for task operations with Phase 5 enhancements."""

    @staticmethod
    def get_user_tasks(
        session: Session,
        user_id: UUID,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        is_completed: Optional[bool] = None,
        overdue: Optional[bool] = None,
        has_due_date: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> List[Task]:
        """
        Get all tasks for a specific user with optional filters.

        Args:
            session: Database session
            user_id: User's UUID
            priority: Filter by priority (low, medium, high)
            tag: Filter by tag name
            is_completed: Filter by completion status
            overdue: Filter for overdue tasks only
            has_due_date: Filter tasks with/without due date
            sort_by: Sort field (created_at, updated_at, due_date, priority, title)
            sort_order: Sort order (asc, desc)

        Returns:
            List of tasks belonging to the user
        """
        statement = select(Task).where(Task.user_id == user_id)

        # Apply filters
        if priority:
            try:
                priority_enum = Priority(priority.lower())
                statement = statement.where(Task.priority == priority_enum)
            except ValueError:
                pass  # Invalid priority, ignore filter

        if is_completed is not None:
            statement = statement.where(Task.is_completed == is_completed)

        if overdue:
            now = datetime.now(timezone.utc)
            statement = statement.where(
                and_(
                    Task.due_date < now,
                    Task.is_completed == False
                )
            )

        if has_due_date is not None:
            if has_due_date:
                statement = statement.where(Task.due_date.isnot(None))
            else:
                statement = statement.where(Task.due_date.is_(None))

        # Apply sorting
        sort_column = Task.created_at  # default
        if sort_by == "updated_at":
            sort_column = Task.updated_at
        elif sort_by == "due_date":
            sort_column = Task.due_date
        elif sort_by == "priority":
            sort_column = Task.priority
        elif sort_by == "title":
            sort_column = Task.title

        if sort_order == "asc":
            statement = statement.order_by(sort_column.asc())
        else:
            statement = statement.order_by(sort_column.desc())

        tasks = list(session.exec(statement).all())

        # Filter by tag (requires post-query filtering due to many-to-many)
        if tag:
            tag_lower = tag.lower()
            tasks = [
                t for t in tasks
                if any(tg.name == tag_lower for tg in t.tags)
            ]

        return tasks

    @staticmethod
    def search_tasks(
        session: Session,
        user_id: UUID,
        query: str,
    ) -> List[Task]:
        """
        Search tasks by keyword in title and description.

        Args:
            session: Database session
            user_id: User's UUID
            query: Search query string

        Returns:
            List of matching tasks
        """
        search_pattern = f"%{query.lower()}%"

        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(
                or_(
                    func.lower(Task.title).like(search_pattern),
                    func.lower(Task.description).like(search_pattern)
                )
            )
            .order_by(Task.created_at.desc())
        )

        return list(session.exec(statement).all())

    @staticmethod
    def get_task_by_id(session: Session, task_id: UUID, user_id: UUID) -> Task:
        """
        Get a specific task by ID, verifying ownership.

        Args:
            session: Database session
            task_id: Task's UUID
            user_id: User's UUID for ownership verification

        Returns:
            Task object

        Raises:
            HTTPException: 404 if task not found or doesn't belong to user
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task

    @staticmethod
    def create_task(
        session: Session,
        user_id: UUID,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        remind_at: Optional[str] = None,
        recurrence: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Task:
        """
        Create a new task with Phase 5 features.

        Args:
            session: Database session
            user_id: User's UUID
            title: Task title
            description: Optional task description
            priority: Priority level (low, medium, high)
            due_date: Due date (ISO format or natural language)
            remind_at: Reminder time (ISO format or natural language)
            recurrence: Recurrence pattern (none, daily, weekly, monthly)
            parent_task_id: Reference to parent recurring task
            tags: List of tag names

        Returns:
            Created task object

        Raises:
            HTTPException: 400 if validation fails
        """
        if not title or not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )

        if len(title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be 200 characters or less"
            )

        if description and len(description) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Description must be 2000 characters or less"
            )

        # Parse priority
        priority_enum = Priority.MEDIUM
        if priority:
            try:
                priority_enum = Priority(priority.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid priority: {priority}. Must be low, medium, or high"
                )

        # Parse recurrence
        recurrence_enum = Recurrence.NONE
        if recurrence:
            try:
                recurrence_enum = Recurrence(recurrence.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid recurrence: {recurrence}. Must be none, daily, weekly, or monthly"
                )

        # Parse due date
        parsed_due_date = None
        if due_date:
            result = parse_natural_date(due_date)
            if result.success:
                parsed_due_date = result.date
            else:
                # Try ISO format
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Could not parse due date: {due_date}"
                    )

        # Parse remind_at
        parsed_remind_at = None
        if remind_at:
            result = parse_natural_date(remind_at)
            if result.success:
                parsed_remind_at = result.date
            else:
                try:
                    parsed_remind_at = datetime.fromisoformat(remind_at.replace("Z", "+00:00"))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Could not parse reminder time: {remind_at}"
                    )

        # Parse parent_task_id
        parsed_parent_id = None
        if parent_task_id:
            try:
                parsed_parent_id = UUID(parent_task_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid parent_task_id: {parent_task_id}"
                )

        now = datetime.now(timezone.utc)
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            is_completed=False,
            created_at=now,
            updated_at=now,
            priority=priority_enum,
            due_date=parsed_due_date,
            remind_at=parsed_remind_at,
            reminder_sent=False,
            recurrence=recurrence_enum,
            parent_task_id=parsed_parent_id,
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        # Add tags if provided
        if tags:
            for tag_name in tags:
                TasksService._add_tag_to_task(session, task, user_id, tag_name)
            session.refresh(task)

        # Publish task.created event
        TasksService._publish_task_event(task, user_id, "task.created")

        return task

    @staticmethod
    def update_task(
        session: Session,
        task_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_completed: Optional[bool] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        remind_at: Optional[str] = None,
        recurrence: Optional[str] = None,
    ) -> Task:
        """
        Update an existing task with Phase 5 fields.

        Args:
            session: Database session
            task_id: Task's UUID
            user_id: User's UUID for ownership verification
            title: Optional new title
            description: Optional new description
            is_completed: Optional new completion status
            priority: Optional new priority
            due_date: Optional new due date
            remind_at: Optional new reminder time
            recurrence: Optional new recurrence pattern

        Returns:
            Updated task object

        Raises:
            HTTPException: 404 if task not found, 400 if validation fails
        """
        task = TasksService.get_task_by_id(session, task_id, user_id)
        was_completed = task.is_completed

        # Validate and update fields
        if title is not None:
            if not title.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Title cannot be empty"
                )
            if len(title) > 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Title must be 200 characters or less"
                )
            task.title = title.strip()

        if description is not None:
            if len(description) > 2000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Description must be 2000 characters or less"
                )
            task.description = description.strip() if description else None

        if is_completed is not None:
            task.is_completed = is_completed

        # Phase 5 fields
        if priority is not None:
            try:
                task.priority = Priority(priority.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid priority: {priority}"
                )

        if due_date is not None:
            if due_date == "":
                task.due_date = None
            else:
                result = parse_natural_date(due_date)
                if result.success:
                    task.due_date = result.date
                else:
                    try:
                        task.due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    except ValueError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Could not parse due date: {due_date}"
                        )

        if remind_at is not None:
            if remind_at == "":
                task.remind_at = None
                task.reminder_sent = False
            else:
                result = parse_natural_date(remind_at)
                if result.success:
                    task.remind_at = result.date
                    task.reminder_sent = False
                else:
                    try:
                        task.remind_at = datetime.fromisoformat(remind_at.replace("Z", "+00:00"))
                        task.reminder_sent = False
                    except ValueError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Could not parse reminder time: {remind_at}"
                        )

        if recurrence is not None:
            try:
                task.recurrence = Recurrence(recurrence.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid recurrence: {recurrence}"
                )

        task.updated_at = datetime.now(timezone.utc)

        session.add(task)
        session.commit()
        session.refresh(task)

        # Publish event
        if is_completed is not None and is_completed and not was_completed:
            TasksService._publish_task_event(task, user_id, "task.completed")
        else:
            TasksService._publish_task_event(task, user_id, "task.updated")

        return task

    @staticmethod
    def toggle_task_completion(session: Session, task_id: UUID, user_id: UUID) -> Task:
        """
        Toggle a task's completion status.

        Args:
            session: Database session
            task_id: Task's UUID
            user_id: User's UUID for ownership verification

        Returns:
            Updated task object

        Raises:
            HTTPException: 404 if task not found
        """
        task = TasksService.get_task_by_id(session, task_id, user_id)

        task.is_completed = not task.is_completed
        task.updated_at = datetime.now(timezone.utc)

        session.add(task)
        session.commit()
        session.refresh(task)

        # Publish event
        if task.is_completed:
            TasksService._publish_task_event(task, user_id, "task.completed")
        else:
            TasksService._publish_task_event(task, user_id, "task.updated")

        return task

    @staticmethod
    def delete_task(session: Session, task_id: UUID, user_id: UUID) -> None:
        """
        Delete a task.

        Args:
            session: Database session
            task_id: Task's UUID
            user_id: User's UUID for ownership verification

        Raises:
            HTTPException: 404 if task not found
        """
        task = TasksService.get_task_by_id(session, task_id, user_id)

        # Publish delete event before deleting
        TasksService._publish_task_event(task, user_id, "task.deleted")

        session.delete(task)
        session.commit()

    @staticmethod
    def add_tag_to_task(
        session: Session,
        task_id: UUID,
        user_id: UUID,
        tag_name: str,
    ) -> Task:
        """
        Add a tag to a task.

        Args:
            session: Database session
            task_id: Task's UUID
            user_id: User's UUID for ownership verification
            tag_name: Tag name to add

        Returns:
            Updated task object
        """
        task = TasksService.get_task_by_id(session, task_id, user_id)
        TasksService._add_tag_to_task(session, task, user_id, tag_name)
        session.refresh(task)
        return task

    @staticmethod
    def _add_tag_to_task(
        session: Session,
        task: Task,
        user_id: UUID,
        tag_name: str,
    ) -> None:
        """Internal method to add a tag to a task."""
        tag_name_lower = tag_name.lower().strip()

        if not tag_name_lower:
            return

        # Find or create tag
        statement = select(Tag).where(
            Tag.name == tag_name_lower,
            Tag.user_id == user_id
        )
        tag = session.exec(statement).first()

        if not tag:
            tag = Tag(name=tag_name_lower, user_id=user_id)
            session.add(tag)
            session.commit()
            session.refresh(tag)

        # Check if already linked
        link_statement = select(TaskTag).where(
            TaskTag.task_id == task.id,
            TaskTag.tag_id == tag.id
        )
        existing = session.exec(link_statement).first()

        if not existing:
            link = TaskTag(task_id=task.id, tag_id=tag.id)
            session.add(link)
            session.commit()

    @staticmethod
    def remove_tag_from_task(
        session: Session,
        task_id: UUID,
        user_id: UUID,
        tag_name: str,
    ) -> Task:
        """
        Remove a tag from a task.

        Args:
            session: Database session
            task_id: Task's UUID
            user_id: User's UUID for ownership verification
            tag_name: Tag name to remove

        Returns:
            Updated task object
        """
        task = TasksService.get_task_by_id(session, task_id, user_id)
        tag_name_lower = tag_name.lower().strip()

        # Find tag
        statement = select(Tag).where(
            Tag.name == tag_name_lower,
            Tag.user_id == user_id
        )
        tag = session.exec(statement).first()

        if tag:
            # Remove link
            link_statement = select(TaskTag).where(
                TaskTag.task_id == task.id,
                TaskTag.tag_id == tag.id
            )
            link = session.exec(link_statement).first()
            if link:
                session.delete(link)
                session.commit()

        session.refresh(task)
        return task

    @staticmethod
    def set_reminder(
        session: Session,
        task_id: UUID,
        user_id: UUID,
        remind_at: str,
    ) -> Task:
        """
        Set a reminder for a task.

        Args:
            session: Database session
            task_id: Task's UUID
            user_id: User's UUID for ownership verification
            remind_at: Reminder time (ISO format, natural language, or relative like "1 hour before")

        Returns:
            Updated task object
        """
        from datetime import timedelta
        import re

        task = TasksService.get_task_by_id(session, task_id, user_id)

        # Check for relative reminder patterns like "1 hour before", "30 minutes before"
        relative_pattern = r'(\d+)\s*(hour|hours|minute|minutes|day|days)\s*before'
        match = re.search(relative_pattern, remind_at.lower())

        if match and task.due_date:
            amount = int(match.group(1))
            unit = match.group(2).rstrip('s')  # Remove trailing 's' for consistency

            if unit == 'hour':
                task.remind_at = task.due_date - timedelta(hours=amount)
            elif unit == 'minute':
                task.remind_at = task.due_date - timedelta(minutes=amount)
            elif unit == 'day':
                task.remind_at = task.due_date - timedelta(days=amount)
        elif match and not task.due_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set relative reminder - task has no due date. Please set a due date first."
            )
        else:
            # Try natural language parsing
            result = parse_natural_date(remind_at)
            if result.success:
                task.remind_at = result.date
            else:
                try:
                    task.remind_at = datetime.fromisoformat(remind_at.replace("Z", "+00:00"))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Could not parse reminder time: {remind_at}"
                    )

        task.reminder_sent = False
        task.updated_at = datetime.now(timezone.utc)

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def _publish_task_event(task: Task, user_id: UUID, event_type: str) -> None:
        """
        Publish a task event to Kafka via Dapr.

        Args:
            task: The task object
            user_id: User who triggered the event
            event_type: Event type (task.created, task.updated, task.completed, task.deleted)
        """
        try:
            import asyncio
            from services.events import event_publisher

            # Run async publish in sync context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create task
                asyncio.create_task(
                    event_publisher.publish_task_event(event_type, task, user_id)
                )
            else:
                loop.run_until_complete(
                    event_publisher.publish_task_event(event_type, task, user_id)
                )
        except Exception as e:
            # Log but don't fail the request
            logger.warning(f"Failed to publish {event_type} event: {e}")
