from __future__ import annotations

import sqlite3
from datetime import date

THEME_KEY = "theme"
THEME_LIGHT = "light"
THEME_DARK = "dark"
SYSTEM_REMINDER_PREFIX = "system_reminder_shown:"


def get_setting(conn: sqlite3.Connection, key: str, default: str) -> str:
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()


def get_theme(conn: sqlite3.Connection) -> str:
    return get_setting(conn, THEME_KEY, THEME_LIGHT)


def set_theme(conn: sqlite3.Connection, name: str) -> None:
    if name not in {THEME_LIGHT, THEME_DARK}:
        raise ValueError("主题只能是 light 或 dark")
    set_setting(conn, THEME_KEY, name)


def _system_reminder_key(day: date) -> str:
    return f"{SYSTEM_REMINDER_PREFIX}{day.isoformat()}"


def has_system_reminder_been_shown(conn: sqlite3.Connection, day: date) -> bool:
    return get_setting(conn, _system_reminder_key(day), "0") == "1"


def mark_system_reminder_shown(conn: sqlite3.Connection, day: date) -> None:
    set_setting(conn, _system_reminder_key(day), "1")
