# [Task]: T080
# [Spec]: F-007 (R-007.2)
# [Description]: Recurrence calculation service
from datetime import datetime, timedelta
from typing import Optional
from dateutil.relativedelta import relativedelta

from ..core.logging import get_logger

logger = get_logger(__name__)


def calculate_next_due(
    current_due: Optional[datetime],
    recurrence: str,
    completed_at: Optional[datetime] = None
) -> Optional[datetime]:
    """
    Calculate the next due date based on recurrence pattern.

    Args:
        current_due: The current/previous due date
        recurrence: Recurrence pattern (none, daily, weekly, monthly)
        completed_at: When the task was completed (fallback if no due date)

    Returns:
        Next due date or None if no recurrence
    """
    if recurrence == "none":
        return None

    # Use completed_at as base if no due date
    base_date = current_due or completed_at or datetime.utcnow()

    if recurrence == "daily":
        next_due = base_date + timedelta(days=1)
    elif recurrence == "weekly":
        next_due = base_date + timedelta(weeks=1)
    elif recurrence == "monthly":
        next_due = base_date + relativedelta(months=1)
    else:
        logger.warning("unknown_recurrence_pattern", pattern=recurrence)
        return None

    # Ensure next due date is in the future
    now = datetime.utcnow()
    while next_due <= now:
        if recurrence == "daily":
            next_due += timedelta(days=1)
        elif recurrence == "weekly":
            next_due += timedelta(weeks=1)
        elif recurrence == "monthly":
            next_due += relativedelta(months=1)

    logger.info(
        "calculated_next_due",
        current_due=str(current_due),
        recurrence=recurrence,
        next_due=str(next_due),
    )

    return next_due
