from datetime import date

from app.services.china_solar_terms import (
    china_solar_term,
    solar_term_reminders_for_day,
)
from app.services.system_reminders import system_reminders_for_day


def test_default_july_2026_has_solar_terms():
    assert china_solar_term(date(2026, 7, 7)) == "小暑"
    assert china_solar_term(date(2026, 7, 23)) == "大暑"


def test_solar_term_reminder_is_system_title():
    reminders = solar_term_reminders_for_day(date(2026, 7, 7))
    assert len(reminders) == 1
    assert reminders[0].title == "小暑"


def test_system_reminders_include_solar_terms():
    reminders = system_reminders_for_day(date(2026, 7, 23))
    assert [r.title for r in reminders] == ["大暑"]
