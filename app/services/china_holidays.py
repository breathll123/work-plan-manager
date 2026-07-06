from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class HolidayInfo:
    name: str


@dataclass(frozen=True)
class HolidayReminder:
    day: date
    name: str

    @property
    def title(self) -> str:
        return f"中国大陆节假日：{self.name}"


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


def holiday_reminder_for(day: date) -> HolidayReminder | None:
    holiday = china_mainland_holiday(day)
    if holiday is None:
        return None
    return HolidayReminder(day=day, name=holiday.name)


def holiday_reminders_for_day(day: date) -> list[HolidayReminder]:
    reminder = holiday_reminder_for(day)
    return [reminder] if reminder is not None else []


def next_holiday_reminder_on_or_after(day: date) -> HolidayReminder | None:
    future_days = sorted(
        holiday_day
        for holiday_year in CHINA_MAINLAND_HOLIDAYS.values()
        for holiday_day in holiday_year
        if holiday_day >= day
    )
    if not future_days:
        return None
    return holiday_reminder_for(future_days[0])
