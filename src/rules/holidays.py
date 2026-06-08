"""
Festivos colombianos usando la librería `holidays`.
"""

from datetime import date

import holidays


_cache: dict[int, set[date]] = {}


def _get_holidays(year: int) -> set[date]:
    if year not in _cache:
        _cache[year] = set(holidays.Colombia(years=year).keys())
    return _cache[year]


def is_holiday(d: date) -> bool:
    return d in _get_holidays(d.year)
