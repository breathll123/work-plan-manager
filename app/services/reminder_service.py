from __future__ import annotations

import sqlite3
from datetime import date

from app.data.models import Plan, STATUS_DONE
from app.data.repositories import PlanRepo


def get_reminders(
    conn: sqlite3.Connection, today: date
) -> tuple[list[Plan], list[Plan]]:
    candidates = PlanRepo(conn).list_filtered(date_to=today)
    overdue = [
        p for p in candidates if p.end_date < today and p.status != STATUS_DONE
    ]
    due_today = [
        p for p in candidates if p.end_date == today and p.status != STATUS_DONE
    ]
    return overdue, due_today
