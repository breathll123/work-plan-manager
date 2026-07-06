from __future__ import annotations

import sqlite3
from datetime import date, datetime

from app.data.models import Category, Plan, PlanLink


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _row_to_plan(r: sqlite3.Row) -> Plan:
    return Plan(
        id=r["id"],
        title=r["title"],
        note=r["note"],
        category_id=r["category_id"],
        start_date=date.fromisoformat(r["start_date"]),
        end_date=date.fromisoformat(r["end_date"]),
        status=r["status"],
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )


class CategoryRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, name: str, color: str, sort_order: int = 0) -> Category:
        cur = self.conn.execute(
            "INSERT INTO categories (name, color, sort_order) VALUES (?, ?, ?)",
            (name, color, sort_order),
        )
        self.conn.commit()
        return Category(cur.lastrowid, name, color, sort_order)

    def list_all(self) -> list[Category]:
        rows = self.conn.execute(
            "SELECT * FROM categories ORDER BY sort_order, id"
        ).fetchall()
        return [
            Category(r["id"], r["name"], r["color"], r["sort_order"])
            for r in rows
        ]

    def update(self, cat: Category) -> None:
        self.conn.execute(
            "UPDATE categories SET name=?, color=?, sort_order=? WHERE id=?",
            (cat.name, cat.color, cat.sort_order, cat.id),
        )
        self.conn.commit()

    def delete(self, cat_id: int) -> None:
        self.conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        self.conn.commit()


class PlanRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, plan: Plan) -> Plan:
        now = _now()
        cur = self.conn.execute(
            "INSERT INTO plans (title, note, category_id, start_date, "
            "end_date, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                plan.title,
                plan.note,
                plan.category_id,
                plan.start_date.isoformat(),
                plan.end_date.isoformat(),
                plan.status,
                now,
                now,
            ),
        )
        self.conn.commit()
        plan.id, plan.created_at, plan.updated_at = cur.lastrowid, now, now
        return plan

    def get(self, plan_id: int) -> Plan | None:
        r = self.conn.execute(
            "SELECT * FROM plans WHERE id=?", (plan_id,)
        ).fetchone()
        return _row_to_plan(r) if r else None

    def update(self, plan: Plan) -> None:
        plan.updated_at = _now()
        self.conn.execute(
            "UPDATE plans SET title=?, note=?, category_id=?, start_date=?, "
            "end_date=?, status=?, updated_at=? WHERE id=?",
            (
                plan.title,
                plan.note,
                plan.category_id,
                plan.start_date.isoformat(),
                plan.end_date.isoformat(),
                plan.status,
                plan.updated_at,
                plan.id,
            ),
        )
        self.conn.commit()

    def delete(self, plan_id: int) -> None:
        self.conn.execute("DELETE FROM plans WHERE id=?", (plan_id,))
        self.conn.commit()

    def list_overlapping(self, start: date, end: date) -> list[Plan]:
        rows = self.conn.execute(
            "SELECT * FROM plans WHERE start_date <= ? AND end_date >= ? "
            "ORDER BY start_date, id",
            (end.isoformat(), start.isoformat()),
        ).fetchall()
        return [_row_to_plan(r) for r in rows]

    def list_filtered(
        self,
        category_ids: list[int | None] | None = None,
        status: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Plan]:
        where: list[str] = []
        args: list[object] = []
        if category_ids is not None:
            ids = [i for i in category_ids if i is not None]
            parts: list[str] = []
            if ids:
                parts.append("category_id IN (%s)" % ",".join("?" * len(ids)))
                args.extend(ids)
            if None in category_ids:
                parts.append("category_id IS NULL")
            where.append("(" + " OR ".join(parts) + ")" if parts else "0=1")
        if status is not None:
            where.append("status = ?")
            args.append(status)
        if date_from is not None:
            where.append("end_date >= ?")
            args.append(date_from.isoformat())
        if date_to is not None:
            where.append("start_date <= ?")
            args.append(date_to.isoformat())
        sql = "SELECT * FROM plans"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY start_date, id"
        return [_row_to_plan(r) for r in self.conn.execute(sql, args)]


class PlanLinkRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def list_for_plan(self, plan_id: int) -> list[PlanLink]:
        rows = self.conn.execute(
            "SELECT * FROM plan_links WHERE plan_id=? ORDER BY sort_order, id",
            (plan_id,),
        ).fetchall()
        return [
            PlanLink(r["id"], r["plan_id"], r["path"], r["sort_order"])
            for r in rows
        ]

    def replace_for_plan(self, plan_id: int, paths: list[str]) -> None:
        self.conn.execute("DELETE FROM plan_links WHERE plan_id=?", (plan_id,))
        self.conn.executemany(
            "INSERT INTO plan_links (plan_id, path, sort_order) VALUES (?, ?, ?)",
            [(plan_id, p, i) for i, p in enumerate(paths)],
        )
        self.conn.commit()
