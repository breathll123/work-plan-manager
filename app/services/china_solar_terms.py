from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SolarTermReminder:
    day: date
    name: str

    @property
    def title(self) -> str:
        return self.name


SOLAR_TERMS_2026 = {
    date(2026, 1, 5): "小寒",
    date(2026, 1, 20): "大寒",
    date(2026, 2, 4): "立春",
    date(2026, 2, 18): "雨水",
    date(2026, 3, 5): "惊蛰",
    date(2026, 3, 20): "春分",
    date(2026, 4, 5): "清明",
    date(2026, 4, 20): "谷雨",
    date(2026, 5, 5): "立夏",
    date(2026, 5, 21): "小满",
    date(2026, 6, 5): "芒种",
    date(2026, 6, 21): "夏至",
    date(2026, 7, 7): "小暑",
    date(2026, 7, 23): "大暑",
    date(2026, 8, 7): "立秋",
    date(2026, 8, 23): "处暑",
    date(2026, 9, 7): "白露",
    date(2026, 9, 23): "秋分",
    date(2026, 10, 8): "寒露",
    date(2026, 10, 23): "霜降",
    date(2026, 11, 7): "立冬",
    date(2026, 11, 22): "小雪",
    date(2026, 12, 7): "大雪",
    date(2026, 12, 22): "冬至",
}

CHINA_SOLAR_TERMS = {
    2026: SOLAR_TERMS_2026,
}


def china_solar_term(day: date) -> str | None:
    return CHINA_SOLAR_TERMS.get(day.year, {}).get(day)


def solar_term_reminder_for(day: date) -> SolarTermReminder | None:
    name = china_solar_term(day)
    if name is None:
        return None
    return SolarTermReminder(day=day, name=name)


def solar_term_reminders_for_day(day: date) -> list[SolarTermReminder]:
    reminder = solar_term_reminder_for(day)
    return [reminder] if reminder is not None else []
