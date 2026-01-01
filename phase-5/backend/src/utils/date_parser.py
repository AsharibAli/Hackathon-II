# [Task]: T025
# [Spec]: F-003 (R-003.1, R-003.2)
# [Description]: Natural language date parsing utility
"""
Natural language date parsing utility.
Supports phrases like "tomorrow", "next Friday", "in 3 days", etc.

Enhanced with custom preprocessing for patterns that dateparser doesn't handle:
- "next Monday", "next Friday", etc.
"""
import dateparser
from datetime import datetime, timezone, timedelta
from typing import Optional, NamedTuple
import logging
import re

logger = logging.getLogger(__name__)

# Day names for "next [day]" pattern matching
_DAY_NAMES = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


def _preprocess_day_pattern(text: str) -> str:
    """
    Preprocess day-related patterns that dateparser doesn't handle well.

    Handles patterns like:
    - "next Monday", "next Friday" -> next occurrence (at least 1 day ahead)
    - "this Monday", "this Friday" -> this week's occurrence
    - "on Monday", "on Friday" -> next occurrence (including today)

    Args:
        text: Natural language date string

    Returns:
        Preprocessed string (ISO date if pattern matched, original otherwise)
    """
    text_lower = text.lower().strip()
    today = datetime.now(timezone.utc)
    current_day_num = today.weekday()

    # Pattern: "next [day]" - always next week's occurrence
    next_pattern = r'^next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'
    next_match = re.match(next_pattern, text_lower)
    if next_match:
        target_day_name = next_match.group(1)
        target_day_num = _DAY_NAMES.index(target_day_name)
        days_ahead = target_day_num - current_day_num
        if days_ahead <= 0:
            days_ahead += 7
        result_date = today + timedelta(days=days_ahead)
        iso_date = result_date.strftime('%Y-%m-%d')
        logger.debug(f"Preprocessed 'next {target_day_name}' to '{iso_date}'")
        return iso_date

    # Pattern: "this [day]" - this week's occurrence (may be past or future)
    this_pattern = r'^this\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'
    this_match = re.match(this_pattern, text_lower)
    if this_match:
        target_day_name = this_match.group(1)
        target_day_num = _DAY_NAMES.index(target_day_name)
        days_diff = target_day_num - current_day_num
        result_date = today + timedelta(days=days_diff)
        iso_date = result_date.strftime('%Y-%m-%d')
        logger.debug(f"Preprocessed 'this {target_day_name}' to '{iso_date}'")
        return iso_date

    # Pattern: "on [day]" - next occurrence including today
    on_pattern = r'^on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'
    on_match = re.match(on_pattern, text_lower)
    if on_match:
        target_day_name = on_match.group(1)
        target_day_num = _DAY_NAMES.index(target_day_name)
        days_ahead = target_day_num - current_day_num
        if days_ahead < 0:
            days_ahead += 7
        result_date = today + timedelta(days=days_ahead)
        iso_date = result_date.strftime('%Y-%m-%d')
        logger.debug(f"Preprocessed 'on {target_day_name}' to '{iso_date}'")
        return iso_date

    # Pattern: bare day name "[day]" - next occurrence including today
    bare_pattern = r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'
    bare_match = re.match(bare_pattern, text_lower)
    if bare_match:
        target_day_name = bare_match.group(1)
        target_day_num = _DAY_NAMES.index(target_day_name)
        days_ahead = target_day_num - current_day_num
        if days_ahead < 0:
            days_ahead += 7
        result_date = today + timedelta(days=days_ahead)
        iso_date = result_date.strftime('%Y-%m-%d')
        logger.debug(f"Preprocessed '{target_day_name}' to '{iso_date}'")
        return iso_date

    return text


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

    # Preprocess patterns that dateparser doesn't handle well
    preprocessed_text = _preprocess_day_pattern(text)

    settings = {
        "TIMEZONE": timezone_str,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future" if prefer_future else "past",
        "PREFER_DAY_OF_MONTH": "first",
    }

    try:
        parsed = dateparser.parse(preprocessed_text, settings=settings)

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
