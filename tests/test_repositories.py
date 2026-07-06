import sqlite3
from datetime import date

import pytest

from app.data.models import Plan
from app.data.repositories import CategoryRepo, PlanLinkRepo, PlanRepo


def make_plan(
    title="t", start="2026-07-06", end=None, category_id=None, status=0
):
    return Plan(
        id=None,
        title=title,
        note="",
        category_id=category_id,
        start_date=date.fromisoformat(start),
        end_date=date.fromisoformat(end or start),
        status=status,
    )


def test_category_add_and_list_sorted(conn):
    repo = CategoryRepo(conn)
    repo.add("乙", "#111111", sort_order=2)
    repo.add("甲", "#222222", sort_order=1)
    assert [c.name for c in repo.list_all()] == ["甲", "乙"]


def test_category_unique_name(conn):
    repo = CategoryRepo(conn)
    repo.add("同名", "#111111")
    with pytest.raises(sqlite3.IntegrityError):
        repo.add("同名", "#222222")


def test_plan_roundtrip_dates_are_date_objects(conn):
    repo = PlanRepo(conn)
    saved = repo.add(make_plan(start="2026-07-06", end="2026-07-09"))
    got = repo.get(saved.id)
    assert got.start_date == date(2026, 7, 6)
    assert got.end_date == date(2026, 7, 9)
    assert got.created_at != ""


def test_plan_update_touches_updated_at(conn):
    repo = PlanRepo(conn)
    p = repo.add(make_plan())
    p.title = "改"
    p.updated_at = ""
    repo.update(p)
    assert repo.get(p.id).title == "改"
    assert repo.get(p.id).updated_at != ""


def test_delete_category_sets_plan_uncategorized(conn):
    cats, plans = CategoryRepo(conn), PlanRepo(conn)
    c = cats.add("项目A", "#4A90D9")
    p = plans.add(make_plan(category_id=c.id))
    cats.delete(c.id)
    assert plans.get(p.id).category_id is None


def test_delete_plan_cascades_links(conn):
    plans, links = PlanRepo(conn), PlanLinkRepo(conn)
    p = plans.add(make_plan())
    links.replace_for_plan(p.id, ["D:\\工作\\a", "D:\\工作\\b"])
    plans.delete(p.id)
    assert links.list_for_plan(p.id) == []


def test_links_replace_keeps_order(conn):
    plans, links = PlanRepo(conn), PlanLinkRepo(conn)
    p = plans.add(make_plan())
    links.replace_for_plan(p.id, ["c", "a", "b"])
    assert [l.path for l in links.list_for_plan(p.id)] == ["c", "a", "b"]


def test_list_overlapping_boundaries(conn):
    repo = PlanRepo(conn)
    p = repo.add(make_plan(start="2026-07-06", end="2026-07-09"))
    assert [
        x.id for x in repo.list_overlapping(date(2026, 7, 1), date(2026, 7, 6))
    ] == [p.id]
    assert [
        x.id for x in repo.list_overlapping(date(2026, 7, 9), date(2026, 7, 31))
    ] == [p.id]
    assert repo.list_overlapping(date(2026, 7, 10), date(2026, 7, 31)) == []


def test_list_filtered(conn):
    cats, repo = CategoryRepo(conn), PlanRepo(conn)
    c = cats.add("项目A", "#4A90D9")
    p1 = repo.add(make_plan("有分类", category_id=c.id, status=1))
    p2 = repo.add(make_plan("未分类", status=0))
    assert [x.id for x in repo.list_filtered(category_ids=[c.id])] == [p1.id]
    assert [x.id for x in repo.list_filtered(category_ids=[None])] == [p2.id]
    assert [x.id for x in repo.list_filtered(status=1)] == [p1.id]
    assert [
        x.id
        for x in repo.list_filtered(
            date_from=date(2026, 7, 1), date_to=date(2026, 7, 31)
        )
    ] == [p1.id, p2.id]
