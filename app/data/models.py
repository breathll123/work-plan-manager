from __future__ import annotations

from dataclasses import dataclass
from datetime import date

STATUS_NOT_STARTED = 0
STATUS_IN_PROGRESS = 1
STATUS_DONE = 2
STATUS_NAMES = {
    STATUS_NOT_STARTED: "未开始",
    STATUS_IN_PROGRESS: "进行中",
    STATUS_DONE: "已完成",
}


@dataclass
class Category:
    id: int | None
    name: str
    color: str
    sort_order: int = 0


@dataclass
class Plan:
    id: int | None
    title: str
    note: str
    category_id: int | None
    start_date: date
    end_date: date
    status: int = STATUS_NOT_STARTED
    created_at: str = ""
    updated_at: str = ""


@dataclass
class PlanLink:
    id: int | None
    plan_id: int
    path: str
    sort_order: int = 0
