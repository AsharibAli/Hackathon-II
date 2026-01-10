# [Task]: T025
# [Spec]: F-003 (R-003.1, R-003.2)
# [Description]: Natural language date parsing utility
"""
Natural language date parsing utility.
Supports phrases like "tomorrow", "next Friday", "in 3 days", etc.

Uses standard library only - no external dependencies.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, NamedTuple
import logging
import re

logger = logging.getLogger(__name__)

# Day names for pattern matching
_DAY_NAMES = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
_MONTH_NAMES = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12,
}


class DateParseResult(NamedTuple):
    """Result of date parsing attempt."""
    success: bool
    date: Optional[datetime]
    original_text: str
    error: Optional[str] = None


def _get_next_weekday(target_day: int, include_today: bool = False) -> datetime:
    """Get the next occurrence of a weekday (0=Monday, 6=Sunday)."""
    today = datetime.now(timezone.utc)
    current_day = today.weekday()
    days_ahead = target_day - current_day

    if include_today:
        if days_ahead < 0:
            days_ahead += 7
    else:
        if days_ahead <= 0:
            days_ahead += 7

    return today + timedelta(days=days_ahead)


def _parse_relative_date(text: str) -> Optional[datetime]:
    """Parse relative date expressions like 'tomorrow', 'in 3 days', etc."""
    text_lower = text.lower().strip()
    today = datetime.now(timezone.utc)

    # Today
    if text_lower in ('today', 'now'):
        return today

    # Tomorrow
    if text_lower == 'tomorrow':
        return today + timedelta(days=1)

    # Yesterday
    if text_lower == 'yesterday':
        return today - timedelta(days=1)

    # In X days/weeks/months
    in_pattern = r'^in\s+(\d+)\s+(day|days|week|weeks|month|months)$'
    in_match = re.match(in_pattern, text_lower)
    if in_match:
        amount = int(in_match.group(1))
        unit = in_match.group(2)
        if unit.startswith('day'):
            return today + timedelta(days=amount)
        elif unit.startswith('week'):
            return today + timedelta(weeks=amount)
        elif unit.startswith('month'):
            # Approximate months as 30 days
            return today + timedelta(days=amount * 30)

    # X days/weeks/months ago
    ago_pattern = r'^(\d+)\s+(day|days|week|weeks|month|months)\s+ago$'
    ago_match = re.match(ago_pattern, text_lower)
    if ago_match:
        amount = int(ago_match.group(1))
        unit = ago_match.group(2)
        if unit.startswith('day'):
            return today - timedelta(days=amount)
        elif unit.startswith('week'):
            return today - timedelta(weeks=amount)
        elif unit.startswith('month'):
            return today - timedelta(days=amount * 30)

    # Next week/month
    if text_lower == 'next week':
        return today + timedelta(weeks=1)
    if text_lower == 'next month':
        return today + timedelta(days=30)

    # This week/month (start of)
    if text_lower == 'this week':
        days_since_monday = today.weekday()
        return today - timedelta(days=days_since_monday)

    return None


def _parse_weekday(text: str) -> Optional[datetime]:
    """Parse weekday expressions like 'Monday', 'next Friday', etc."""
    text_lower = text.lower().strip()

    # Pattern: "next [day]" - always next week's occurrence
    next_pattern = r'^next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'
    next_match = re.match(next_pattern, text_lower)
    if next_match:
        target_day_name = next_match.group(1)
        target_day_num = _DAY_NAMES.index(target_day_name)
        return _get_next_weekday(target_day_num, include_today=False)

    # Pattern: "this [day]" - this week's occurrence
    this_pattern = r'^this\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'
    this_match = re.match(this_pattern, text_lower)
    if this_match:
        target_day_name = this_match.group(1)
        target_day_num = _DAY_NAMES.index(target_day_name)
        today = datetime.now(timezone.utc)
        current_day = today.weekday()
        days_diff = target_day_num - current_day
        return today + timedelta(days=days_diff)

    # Pattern: "on [day]" - next occurrence including today
    on_pattern = r'^on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'
    on_match = re.match(on_pattern, text_lower)
    if on_match:
        target_day_name = on_match.group(1)
        target_day_num = _DAY_NAMES.index(target_day_name)
        return _get_next_weekday(target_day_num, include_today=True)

    # Pattern: bare day name "[day]" - next occurrence including today
    bare_pattern = r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'
    bare_match = re.match(bare_pattern, text_lower)
    if bare_match:
        target_day_name = bare_match.group(1)
        target_day_num = _DAY_NAMES.index(target_day_name)
        return _get_next_weekday(target_day_num, include_today=True)

    return None


def _parse_absolute_date(text: str) -> Optional[datetime]:
    """Parse absolute date formats like 'YYYY-MM-DD', 'MM/DD/YYYY', 'January 15, 2025'."""
    text = text.strip()

    # ISO format: YYYY-MM-DD
    iso_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})$'
    iso_match = re.match(iso_pattern, text)
    if iso_match:
        year, month, day = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        try:
            return datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError:
            pass

    # US format: MM/DD/YYYY or M/D/YYYY
    us_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    us_match = re.match(us_pattern, text)
    if us_match:
        month, day, year = int(us_match.group(1)), int(us_match.group(2)), int(us_match.group(3))
        try:
            return datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError:
            pass

    # EU format: DD/MM/YYYY (try if US format seems invalid)
    # We'll prefer US format but this is here for completeness

    # Named month format: "January 15, 2025" or "Jan 15 2025" or "15 January 2025"
    text_lower = text.lower()

    # "Month Day, Year" or "Month Day Year"
    month_day_year = r'^([a-z]+)\s+(\d{1,2}),?\s+(\d{4})$'
    mdy_match = re.match(month_day_year, text_lower)
    if mdy_match:
        month_name, day, year = mdy_match.group(1), int(mdy_match.group(2)), int(mdy_match.group(3))
        month = _MONTH_NAMES.get(month_name)
        if month:
            try:
                return datetime(year, month, day, tzinfo=timezone.utc)
            except ValueError:
                pass

    # "Day Month Year"
    day_month_year = r'^(\d{1,2})\s+([a-z]+)\s+(\d{4})$'
    dmy_match = re.match(day_month_year, text_lower)
    if dmy_match:
        day, month_name, year = int(dmy_match.group(1)), dmy_match.group(2), int(dmy_match.group(3))
        month = _MONTH_NAMES.get(month_name)
        if month:
            try:
                return datetime(year, month, day, tzinfo=timezone.utc)
            except ValueError:
                pass

    # "Month Day" (assume current/next year)
    month_day = r'^([a-z]+)\s+(\d{1,2})$'
    md_match = re.match(month_day, text_lower)
    if md_match:
        month_name, day = md_match.group(1), int(md_match.group(2))
        month = _MONTH_NAMES.get(month_name)
        if month:
            today = datetime.now(timezone.utc)
            year = today.year
            try:
                date = datetime(year, month, day, tzinfo=timezone.utc)
                # If date is in the past, use next year
                if date < today:
                    date = datetime(year + 1, month, day, tzinfo=timezone.utc)
                return date
            except ValueError:
                pass

    return None


def _parse_datetime_with_time(text: str) -> Optional[datetime]:
    """Parse date with time like '2025-01-15 14:30' or 'tomorrow at 3pm'."""
    text = text.strip()

    # ISO datetime: YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM
    iso_datetime_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})[T\s](\d{1,2}):(\d{2})(?::(\d{2}))?$'
    iso_match = re.match(iso_datetime_pattern, text)
    if iso_match:
        year = int(iso_match.group(1))
        month = int(iso_match.group(2))
        day = int(iso_match.group(3))
        hour = int(iso_match.group(4))
        minute = int(iso_match.group(5))
        second = int(iso_match.group(6)) if iso_match.group(6) else 0
        try:
            return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
        except ValueError:
            pass

    # "tomorrow at 3pm" or "monday at 2:30pm"
    at_time_pattern = r'^(.+?)\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$'
    at_match = re.match(at_time_pattern, text.lower())
    if at_match:
        date_part = at_match.group(1)
        hour = int(at_match.group(2))
        minute = int(at_match.group(3)) if at_match.group(3) else 0
        am_pm = at_match.group(4)

        # Convert to 24-hour format
        if am_pm == 'pm' and hour != 12:
            hour += 12
        elif am_pm == 'am' and hour == 12:
            hour = 0

        # Parse the date part
        parsed_date = (
            _parse_relative_date(date_part) or
            _parse_weekday(date_part) or
            _parse_absolute_date(date_part)
        )
        if parsed_date:
            return parsed_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    return None


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
        timezone_str: Timezone for interpretation (default UTC) - not currently used

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

    try:
        # Try parsing in order of specificity
        parsed = (
            _parse_datetime_with_time(text) or
            _parse_relative_date(text) or
            _parse_weekday(text) or
            _parse_absolute_date(text)
        )

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
