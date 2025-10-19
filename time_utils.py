"""Time and date utility functions."""

import datetime as dt


def today_local() -> dt.date:
    """Return today's date in local timezone."""
    return dt.datetime.now().date()
