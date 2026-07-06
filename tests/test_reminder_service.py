from datetime import date

from app.services.plan_service import PlanService
from app.services.reminder_service import get_reminders

TODAY = date(2026, 7, 6)


def test_overdue_and_due_today_split(conn):
    svc = PlanService(conn)
    overdue = svc.create("昨天到期", date(2026, 7, 2), date(2026, 7, 5))
    due = svc.create("今天到期", TODAY, TODAY)
    svc.create("明天到期", TODAY, date(2026, 7, 7))
    svc.create("已完成的逾期", date(2026, 7, 1), date(2026, 7, 1), status=2)
    got_overdue, got_due = get_reminders(conn, TODAY)
    assert [p.id for p in got_overdue] == [overdue.id]
    assert [p.id for p in got_due] == [due.id]


def test_no_plans_returns_empty(conn):
    assert get_reminders(conn, TODAY) == ([], [])
