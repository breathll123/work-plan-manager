from datetime import date

import pytest

from app.services.plan_service import PlanService, month_grid_range


def test_month_grid_range_july_2026():
    assert month_grid_range(2026, 7) == (date(2026, 6, 29), date(2026, 8, 2))


def test_month_grid_range_feb_2027_starts_monday():
    start, end = month_grid_range(2027, 2)
    assert start.weekday() == 0 and end.weekday() == 6
    assert start <= date(2027, 2, 1) and end >= date(2027, 2, 28)


def test_create_and_get_with_links(conn):
    svc = PlanService(conn)
    p = svc.create(
        "评审", date(2026, 7, 6), date(2026, 7, 9), paths=["D:\\a", "D:\\b"]
    )
    plan, links = svc.get_with_links(p.id)
    assert plan.title == "评审"
    assert [l.path for l in links] == ["D:\\a", "D:\\b"]


def test_create_empty_title_raises(conn):
    with pytest.raises(ValueError):
        PlanService(conn).create(" ", date(2026, 7, 6), date(2026, 7, 6))


def test_create_end_before_start_raises(conn):
    with pytest.raises(ValueError):
        PlanService(conn).create("x", date(2026, 7, 9), date(2026, 7, 6))


def test_update_replaces_paths_only_when_given(conn):
    svc = PlanService(conn)
    p = svc.create("x", date(2026, 7, 6), date(2026, 7, 6), paths=["D:\\a"])
    p.title = "y"
    svc.update(p)
    plan, links = svc.get_with_links(p.id)
    assert plan.title == "y" and len(links) == 1
    svc.update(p, paths=[])
    _, links = svc.get_with_links(p.id)
    assert links == []


def test_plans_for_month_includes_grid_edges(conn):
    svc = PlanService(conn)
    edge = svc.create("六月末", date(2026, 6, 29), date(2026, 6, 29))
    inside = svc.create("七月", date(2026, 7, 15), date(2026, 7, 15))
    outside = svc.create("六月初", date(2026, 6, 1), date(2026, 6, 1))
    ids = [p.id for p in svc.plans_for_month(2026, 7)]
    assert edge.id in ids and inside.id in ids and outside.id not in ids
