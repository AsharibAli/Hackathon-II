# [Task]: T025
# [Spec]: F-003 (R-003.1, R-003.2)
# [Description]: Natural language date parsing utility
"""
Natural language date parsing utility.
Supports phrases like "tomorrow", "next Friday", "in 3 days", etc.
"""
import dateparser
from datetime import datetime, timezone
from typing import Optional, NamedTuple
import logging

logger = logging.getLogger(__name__)


class DateParseResult(NamedTuple):
    """Result of date parsing attempt."""
    success: bool
    date: Optional[datetime]
    original_text: str
    error: Optional[str] = None


def parse_natural_date(
    text: str,
    prefer_future: bool = True,
    timezone_str: str = "UTC",
) -> DateParseResult:
    """
    Parse natural language date text into a datetime.

    Supports formats like:
    - "tomorrow"
    - "next Friday"
    - "in 3 days"
    - "next week"
    - "2025-01-15"
    - "January 15, 2025"
    - "1/15/2025"

    Args:
        text: Natural language date string
        prefer_future: If True, prefer future dates for ambiguous inputs
        timezone_str: Timezone for interpretation (default UTC)

    Returns:
        DateParseResult with success status and parsed date
    """
    if not text or not text.strip():
        return DateParseResult(
            success=False,
            date=None,
            original_text=text,
            error="Empty date text",
        )

    text = text.strip()

    settings = {
        "TIMEZONE": timezone_str,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future" if prefer_future else "past",
        "PREFER_DAY_OF_MONTH": "first",
    }

    try:
        parsed = dateparser.parse(text, settings=settings)

        if parsed is None:
            logger.warning(f"Could not parse date: {text}")
            return DateParseResult(
                success=False,
                date=None,
                original_text=text,
                error=f"Could not parse '{text}' as a date",
            )

        # Ensure UTC timezone
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)

        logger.debug(f"Parsed '{text}' as {parsed.isoformat()}")

        return DateParseResult(
            success=True,
            date=parsed,
            original_text=text,
            error=None,
        )

    except Exception as e:
        logger.error(f"Error parsing date '{text}': {e}")
        return DateParseResult(
            success=False,
            date=None,
            original_text=text,
            error=str(e),
        )


def format_relative_date(dt: datetime) -> str:
    """
    Format a datetime as a relative string for display.

    Args:
        dt: Datetime to format

    Returns:
        Relative date string (e.g., "tomorrow", "in 3 days", "overdue by 2 days")
    """
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = dt - now
    days = diff.days

    if days == 0:
        return "today"
    elif days == 1:
        return "tomorrow"
    elif days == -1:
        return "yesterday"
    elif days > 1:
        return f"in {days} days"
    else:
        return f"overdue by {abs(days)} days"
