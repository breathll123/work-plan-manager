from __future__ import annotations

from datetime import date
from typing import Union

from app.services.china_holidays import HolidayReminder, holiday_reminders_for_day
from app.services.china_solar_terms import (
    SolarTermReminder,
    solar_term_reminders_for_day,
)

SystemReminder = Union[HolidayReminder, SolarTermReminder]


def system_reminders_for_day(day: date) -> list[SystemReminder]:
    return [
        *holiday_reminders_for_day(day),
        *solar_term_reminders_for_day(day),
    ]


def system_reminder_kind(reminder: SystemReminder) -> str:
    if isinstance(reminder, HolidayReminder):
        return "holiday"
    return "solar_term"
