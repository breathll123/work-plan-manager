from datetime import date

from app.services.china_holidays import (
    china_mainland_holiday,
    holiday_reminders_for_day,
)


def test_2026_spring_festival_range():
    assert china_mainland_holiday(date(2026, 2, 15)).name == "春节"
    assert china_mainland_holiday(date(2026, 2, 23)).name == "春节"


def test_2026_holiday_outside_known_range_is_none():
    assert china_mainland_holiday(date(2026, 2, 24)) is None


def test_holiday_reminder_is_system_title():
    reminders = holiday_reminders_for_day(date(2026, 10, 1))
    assert len(reminders) == 1
    assert reminders[0].title == "国庆"
