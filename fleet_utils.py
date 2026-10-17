
# fleet_utils.py
# Shared helper functions for KM-Waechter.

from datetime import datetime

MILES_PER_KM = 1 / 1.609344


def km_to_miles(km):
    """Convert kilometres to miles."""
    return km * MILES_PER_KM


def format_number(value):
    """Format a number to one decimal place."""
    return "%.1f" % value


def format_percent(value):
    """Format a percentage as a whole number."""
    return "%d%%" % value


def mean(values):
    """Return the arithmetic mean, or 0 for an empty collection."""
    total = 0
    count = 0

    for value in values:
        total += value
        count += 1

    if count == 0:
        return 0

    return total / count


def is_due(pct, threshold):
    """Return whether wear has reached the service threshold."""
    return pct >= threshold


def parse_service_date(text):
    """Parse a date in DD.MM.YYYY format; return None if invalid."""
    try:
        parsed = datetime.strptime(text, "%d.%m.%Y")
        return (parsed.year, parsed.month, parsed.day)
    except (ValueError, TypeError):
        return None


def chunk_list(items, size):
    """Split a list into chunks of the requested size."""
    if size <= 0:
        raise ValueError("Chunk size must be positive")

    chunks = []

    for start in range(0, len(items), size):
        chunks.append(items[start:start + size])

    return chunks
