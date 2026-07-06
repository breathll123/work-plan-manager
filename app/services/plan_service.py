from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from collections.abc import Sequence

from app.data.models import Plan, PlanLink
from app.data.repositories import PlanLinkRepo, PlanRepo


def month_grid_range(year: int, month: int) -> tuple[date, date]:
    first = date(year, month, 1)
    last = (
        date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    ) - timedelta(days=1)
    start = first - timedelta(days=first.weekday())
    end = last + timedelta(days=6 - last.weekday())
    return start, end


class PlanService:
    def __init__(self, conn: sqlite3.Connection):
        self.plans = PlanRepo(conn)
        self.links = PlanLinkRepo(conn)

    def _validate(self, title: str, start: date, end: date) -> str:
        title = title.strip()
        if not title:
            raise ValueError("标题不能为空")
        if end < start:
            raise ValueError("结束日期不能早于开始日期")
        return title

    def create(
        self,
        title: str,
        start_date: date,
        end_date: date,
        category_id: int | None = None,
        note: str = "",
        status: int = 0,
        paths: Sequence[str] = (),
    ) -> Plan:
        title = self._validate(title, start_date, end_date)
        plan = self.plans.add(
            Plan(
                id=None,
                title=title,
                note=note,
                category_id=category_id,
                start_date=start_date,
                end_date=end_date,
                status=status,
            )
        )
        if paths:
            self.links.replace_for_plan(plan.id, list(paths))
        return plan

    def update(self, plan: Plan, paths: list[str] | None = None) -> None:
        plan.title = self._validate(plan.title, plan.start_date, plan.end_date)
        self.plans.update(plan)
        if paths is not None:
            self.links.replace_for_plan(plan.id, paths)

    def delete(self, plan_id: int) -> None:
        self.plans.delete(plan_id)

    def get_with_links(self, plan_id: int) -> tuple[Plan, list[PlanLink]]:
        plan = self.plans.get(plan_id)
        if plan is None:
            raise ValueError("计划不存在")
        return plan, self.links.list_for_plan(plan_id)

    def plans_for_month(self, year: int, month: int) -> list[Plan]:
        start, end = month_grid_range(year, month)
        return self.plans.list_overlapping(start, end)

    def list_filtered(self, **kwargs) -> list[Plan]:
        return self.plans.list_filtered(**kwargs)
