from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class HolidayInfo:
    name: str


def _daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _build_2026_holidays() -> dict[date, HolidayInfo]:
    ranges = [
        ("元旦", date(2026, 1, 1), date(2026, 1, 3)),
        ("春节", date(2026, 2, 15), date(2026, 2, 23)),
        ("清明", date(2026, 4, 4), date(2026, 4, 6)),
        ("劳动节", date(2026, 5, 1), date(2026, 5, 5)),
        ("端午", date(2026, 6, 19), date(2026, 6, 21)),
        ("中秋", date(2026, 9, 25), date(2026, 9, 27)),
        ("国庆", date(2026, 10, 1), date(2026, 10, 7)),
    ]
    holidays: dict[date, HolidayInfo] = {}
    for name, start, end in ranges:
        for day in _daterange(start, end):
            holidays[day] = HolidayInfo(name)
    return holidays


CHINA_MAINLAND_HOLIDAYS = {
    2026: _build_2026_holidays(),
}


def china_mainland_holiday(day: date) -> HolidayInfo | None:
    return CHINA_MAINLAND_HOLIDAYS.get(day.year, {}).get(day)
