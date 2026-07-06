from datetime import date

from app.services.china_holidays import china_mainland_holiday


def test_2026_spring_festival_range():
    assert china_mainland_holiday(date(2026, 2, 15)).name == "春节"
    assert china_mainland_holiday(date(2026, 2, 23)).name == "春节"


def test_2026_holiday_outside_known_range_is_none():
    assert china_mainland_holiday(date(2026, 2, 24)) is None
