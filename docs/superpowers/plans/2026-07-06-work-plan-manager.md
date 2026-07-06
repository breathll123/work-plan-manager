# 工作计划管理系统 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 本地便携版 Windows 工作计划管理软件:分类 + 月历/列表视图 + 文件夹绑定跳转 + 启动提醒 + 浅色/深色主题,PyInstaller 打包单 exe。

**Architecture:** 三层架构 —— UI 层(PySide6)→ 服务层(纯 Python 业务规则)→ 数据层(sqlite3 Repository)。服务层与数据层零 GUI 依赖,用 pytest 全覆盖;GUI 层薄封装走手动冒烟清单。数据库与 exe 同目录便携存储。

**Tech Stack:** Python 3.11+ / PySide6 ≥ 6.7 / sqlite3(标准库)/ pytest / PyInstaller(仅 Windows 打包机需要)

**Spec:** `docs/superpowers/specs/2026-07-06-work-plan-manager-design.md`

## Global Constraints

- 数据便携:`workplan.db` 与 exe 同目录(开发时在项目根目录);备份到 `backups/` 保留最近 5 份
- 日期一律以 ISO 字符串 `YYYY-MM-DD` 存储,业务层用 `datetime.date`;周一为一周第一天
- 计划状态:`0` 未开始 / `1` 进行中 / `2` 已完成;单日计划即 `start_date == end_date`;约束 `end_date >= start_date`
- 删除分类 → 计划 `category_id` 置 NULL(未分类);删除计划 → 级联删除 `plan_links`
- 主题:`light` / `dark`,默认 `light`,存 `settings` 表键 `theme`
- 分层纪律:`app/services/`、`app/data/` 内禁止 import PySide6;`app/ui/` 内禁止写 SQL
- 所有界面文案为简体中文;commit 信息用 `feat:` / `fix:` / `docs:` 前缀 + 中文描述
- 数据层/服务层严格 TDD;GUI 层不写自动化测试,走 spec §7 冒烟清单
- 开发机为 macOS:`os.startfile` 仅 Windows 可用,打开路径必须走 `platform_utils.open_path` 分平台封装

## File Structure

```
app/
├── __init__.py
├── main.py                 入口:可写检查、备份、连接、主题、excepthook、启动提醒
├── platform_utils.py       open_path() 分平台打开文件夹/文件
├── data/
│   ├── __init__.py
│   ├── db.py               连接、建表、WAL、user_version、滚动备份、可写检查
│   ├── models.py           dataclass:Category / Plan / PlanLink + 状态常量
│   └── repositories.py     CategoryRepo / PlanRepo / PlanLinkRepo(全部 SQL 在此)
├── services/
│   ├── __init__.py
│   ├── category_service.py 分类增删改 + 颜色文字亮度计算
│   ├── plan_service.py     计划增删改查 + 日期校验 + 筛选
│   ├── reminder_service.py 启动提醒汇总(逾期/今日到期)
│   └── settings_service.py 设置读写(主题)
└── ui/
    ├── __init__.py
    ├── theme.py            浅色/深色 QPalette+QSS + CAL 调色板
    ├── main_window.py      主窗口:工具栏、侧栏筛选、视图切换
    ├── calendar_view.py    自绘月历(跨天条带、逾期红点、今天高亮)
    ├── list_view.py        列表视图(筛选条 + 表格)
    ├── plan_dialog.py      计划编辑对话框(含路径绑定)
    ├── category_dialog.py  分类管理对话框
    ├── day_panel.py        单击日期的当日计划小窗
    └── reminder_dialog.py  启动提醒对话框
tests/
├── conftest.py             tmp 数据库 fixture
├── test_db.py
├── test_repositories.py
├── test_category_service.py
├── test_plan_service.py
├── test_reminder_service.py
└── test_settings_service.py
build.bat / app.ico / .github/workflows/build.yml / requirements.txt / .gitignore
```

---

### Task 1: 项目骨架与依赖

**Files:**
- Create: `requirements.txt`, `.gitignore`, `app/__init__.py`, `app/data/__init__.py`, `app/services/__init__.py`, `app/ui/__init__.py`, `tests/conftest.py`

**Interfaces:**
- Produces: 包结构 `app.data` / `app.services` / `app.ui`;pytest 可运行;fixture `conn`(内存级临时 SQLite 连接,后续所有测试消费)

- [ ] **Step 1: 创建目录与空包文件**

```bash
mkdir -p app/data app/services app/ui tests
touch app/__init__.py app/data/__init__.py app/services/__init__.py app/ui/__init__.py
```

- [ ] **Step 2: 写 requirements.txt**

```
PySide6>=6.7
pytest>=8.0
pyinstaller>=6.0
```

- [ ] **Step 3: 写 .gitignore**

```
__pycache__/
*.pyc
.venv/
build/
dist/
*.spec
workplan.db
workplan.db-wal
workplan.db-shm
backups/
error.log
.DS_Store
```

- [ ] **Step 4: 写 tests/conftest.py**

```python
import sqlite3
import pytest

from app.data.db import connect


@pytest.fixture
def conn(tmp_path):
    c = connect(tmp_path / "test.db")
    yield c
    c.close()
```

- [ ] **Step 5: 创建虚拟环境并安装依赖**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Expected: 安装成功(PySide6 较大,约 1-2 分钟)

- [ ] **Step 6: 验证 pytest 可运行**

Run: `.venv/bin/pytest --collect-only -q`
Expected: 报错 `ModuleNotFoundError: No module named 'app.data.db'` —— 正常,Task 2 补上;或空收集。conftest 引用了尚未存在的模块,此步允许失败,仅确认 pytest 本身可执行。

- [ ] **Step 7: Commit**

```bash
git add requirements.txt .gitignore app tests
git commit -m "feat: 项目骨架与依赖"
```

---

### Task 2: 数据层 —— models.py 与 db.py

**Files:**
- Create: `app/data/models.py`, `app/data/db.py`
- Test: `tests/test_db.py`

**Interfaces:**
- Produces:
  - `models.Category(id, name, color, sort_order)`、`models.Plan(id, title, note, category_id, start_date: date, end_date: date, status, created_at, updated_at)`、`models.PlanLink(id, plan_id, path, sort_order)`(均为 dataclass)
  - `models.STATUS_NOT_STARTED = 0`、`STATUS_IN_PROGRESS = 1`、`STATUS_DONE = 2`、`STATUS_NAMES = {0: "未开始", 1: "进行中", 2: "已完成"}`
  - `db.connect(db_path: Path) -> sqlite3.Connection`(Row 工厂、外键开、WAL、自动建表)
  - `db.backup(db_path: Path, keep: int = 5) -> None`(拷到 `backups/`,滚动保留)
  - `db.default_db_path() -> Path`、`db.is_dir_writable(d: Path) -> bool`

- [ ] **Step 1: 写失败测试 tests/test_db.py**

```python
import sqlite3
from pathlib import Path

from app.data.db import backup, connect, is_dir_writable


def test_connect_creates_tables(conn):
    names = {
        r["name"]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {"categories", "plans", "plan_links", "settings"} <= names


def test_foreign_keys_enabled(conn):
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_schema_version_set(conn):
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 1


def test_end_date_check_constraint(conn):
    import pytest

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO plans (title, start_date, end_date, status,"
            " created_at, updated_at)"
            " VALUES ('x', '2026-07-10', '2026-07-09', 0, '', '')"
        )


def test_backup_rotates_keep_5(tmp_path):
    db_path = tmp_path / "workplan.db"
    connect(db_path).close()
    for _ in range(7):
        backup(db_path, keep=5)
    files = list((tmp_path / "backups").glob("workplan-*.db"))
    assert len(files) == 5


def test_backup_missing_db_is_noop(tmp_path):
    backup(tmp_path / "nope.db", keep=5)
    assert not (tmp_path / "backups").exists()


def test_is_dir_writable(tmp_path):
    assert is_dir_writable(tmp_path) is True
```

- [ ] **Step 2: 运行确认失败**

Run: `.venv/bin/pytest tests/test_db.py -v`
Expected: FAIL / ERROR,`No module named 'app.data.db'`

- [ ] **Step 3: 写 app/data/models.py**

```python
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
```

- [ ] **Step 4: 写 app/data/db.py**

```python
from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import time
from pathlib import Path

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    color       TEXT NOT NULL,
    sort_order  INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS plans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    note        TEXT NOT NULL DEFAULT '',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    start_date  TEXT NOT NULL,
    end_date    TEXT NOT NULL,
    status      INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    CHECK (end_date >= start_date)
);
CREATE TABLE IF NOT EXISTS plan_links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id     INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    path        TEXT NOT NULL,
    sort_order  INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL
);
"""


def app_dir() -> Path:
    """exe 同目录(打包后)或项目根目录(开发时)。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def default_db_path() -> Path:
    return app_dir() / "workplan.db"


def is_dir_writable(d: Path) -> bool:
    probe = d / ".write_probe"
    try:
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    if conn.execute("PRAGMA user_version").fetchone()[0] < SCHEMA_VERSION:
        conn.executescript(SCHEMA)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()
    return conn


def backup(db_path: Path, keep: int = 5) -> None:
    if not db_path.exists():
        return
    bdir = db_path.parent / "backups"
    bdir.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    target = bdir / f"workplan-{stamp}.db"
    n = 1
    while target.exists():
        target = bdir / f"workplan-{stamp}-{n}.db"
        n += 1
    shutil.copy2(db_path, target)
    old = sorted(bdir.glob("workplan-*.db"), key=os.path.getmtime)
    for f in old[:-keep]:
        f.unlink()
```

- [ ] **Step 5: 运行确认通过**

Run: `.venv/bin/pytest tests/test_db.py -v`
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add app/data tests/test_db.py tests/conftest.py
git commit -m "feat: 数据层模型与数据库连接、建表、滚动备份"
```

---

### Task 3: 数据层 —— repositories.py

**Files:**
- Create: `app/data/repositories.py`
- Test: `tests/test_repositories.py`

**Interfaces:**
- Consumes: `db.connect`、`models.*`(Task 2)
- Produces(全部以 `conn` 构造,如 `CategoryRepo(conn)`):
  - `CategoryRepo.add(name: str, color: str, sort_order: int = 0) -> Category`
  - `CategoryRepo.list_all() -> list[Category]`(按 sort_order, id 排序)
  - `CategoryRepo.update(cat: Category) -> None`、`CategoryRepo.delete(cat_id: int) -> None`
  - `PlanRepo.add(plan: Plan) -> Plan`(回填 id/created_at/updated_at)
  - `PlanRepo.get(plan_id: int) -> Plan | None`、`PlanRepo.update(plan: Plan) -> None`、`PlanRepo.delete(plan_id: int) -> None`
  - `PlanRepo.list_overlapping(start: date, end: date) -> list[Plan]`(与区间有交集的计划,月历用)
  - `PlanRepo.list_filtered(category_ids: list[int | None] | None = None, status: int | None = None, date_from: date | None = None, date_to: date | None = None) -> list[Plan]`(列表视图用;`category_ids` 里的 `None` 表示未分类;返回按 start_date, id 排序)
  - `PlanLinkRepo.list_for_plan(plan_id: int) -> list[PlanLink]`
  - `PlanLinkRepo.replace_for_plan(plan_id: int, paths: list[str]) -> None`(整体替换,编辑对话框保存时用)

- [ ] **Step 1: 写失败测试 tests/test_repositories.py**

```python
import sqlite3
from datetime import date

import pytest

from app.data.models import Plan
from app.data.repositories import CategoryRepo, PlanLinkRepo, PlanRepo


def make_plan(title="t", start="2026-07-06", end=None, category_id=None,
              status=0):
    return Plan(
        id=None, title=title, note="", category_id=category_id,
        start_date=date.fromisoformat(start),
        end_date=date.fromisoformat(end or start), status=status,
    )


def test_category_add_and_list_sorted(conn):
    repo = CategoryRepo(conn)
    repo.add("乙", "#111111", sort_order=2)
    repo.add("甲", "#222222", sort_order=1)
    names = [c.name for c in repo.list_all()]
    assert names == ["甲", "乙"]


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
    assert [x.id for x in repo.list_overlapping(
        date(2026, 7, 1), date(2026, 7, 6))] == [p.id]
    assert [x.id for x in repo.list_overlapping(
        date(2026, 7, 9), date(2026, 7, 31))] == [p.id]
    assert repo.list_overlapping(date(2026, 7, 10), date(2026, 7, 31)) == []


def test_list_filtered(conn):
    cats, repo = CategoryRepo(conn), PlanRepo(conn)
    c = cats.add("项目A", "#4A90D9")
    p1 = repo.add(make_plan("有分类", category_id=c.id, status=1))
    p2 = repo.add(make_plan("未分类", status=0))
    assert [x.id for x in repo.list_filtered(category_ids=[c.id])] == [p1.id]
    assert [x.id for x in repo.list_filtered(category_ids=[None])] == [p2.id]
    assert [x.id for x in repo.list_filtered(status=1)] == [p1.id]
    assert [x.id for x in repo.list_filtered(
        date_from=date(2026, 7, 1), date_to=date(2026, 7, 31))] \
        == [p1.id, p2.id]
```

- [ ] **Step 2: 运行确认失败**

Run: `.venv/bin/pytest tests/test_repositories.py -v`
Expected: ERROR,`No module named 'app.data.repositories'`

- [ ] **Step 3: 写 app/data/repositories.py**

```python
from __future__ import annotations

import sqlite3
from datetime import date, datetime

from app.data.models import Category, Plan, PlanLink


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _row_to_plan(r: sqlite3.Row) -> Plan:
    return Plan(
        id=r["id"], title=r["title"], note=r["note"],
        category_id=r["category_id"],
        start_date=date.fromisoformat(r["start_date"]),
        end_date=date.fromisoformat(r["end_date"]),
        status=r["status"], created_at=r["created_at"],
        updated_at=r["updated_at"],
    )


class CategoryRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, name: str, color: str, sort_order: int = 0) -> Category:
        cur = self.conn.execute(
            "INSERT INTO categories (name, color, sort_order)"
            " VALUES (?, ?, ?)",
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
            "UPDATE categories SET name=?, color=?, sort_order=?"
            " WHERE id=?",
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
            "INSERT INTO plans (title, note, category_id, start_date,"
            " end_date, status, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (plan.title, plan.note, plan.category_id,
             plan.start_date.isoformat(), plan.end_date.isoformat(),
             plan.status, now, now),
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
            "UPDATE plans SET title=?, note=?, category_id=?,"
            " start_date=?, end_date=?, status=?, updated_at=?"
            " WHERE id=?",
            (plan.title, plan.note, plan.category_id,
             plan.start_date.isoformat(), plan.end_date.isoformat(),
             plan.status, plan.updated_at, plan.id),
        )
        self.conn.commit()

    def delete(self, plan_id: int) -> None:
        self.conn.execute("DELETE FROM plans WHERE id=?", (plan_id,))
        self.conn.commit()

    def list_overlapping(self, start: date, end: date) -> list[Plan]:
        rows = self.conn.execute(
            "SELECT * FROM plans WHERE start_date <= ? AND end_date >= ?"
            " ORDER BY start_date, id",
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
        where, args = [], []
        if category_ids is not None:
            ids = [i for i in category_ids if i is not None]
            parts = []
            if ids:
                parts.append(
                    "category_id IN (%s)" % ",".join("?" * len(ids))
                )
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
            "SELECT * FROM plan_links WHERE plan_id=?"
            " ORDER BY sort_order, id",
            (plan_id,),
        ).fetchall()
        return [
            PlanLink(r["id"], r["plan_id"], r["path"], r["sort_order"])
            for r in rows
        ]

    def replace_for_plan(self, plan_id: int, paths: list[str]) -> None:
        self.conn.execute(
            "DELETE FROM plan_links WHERE plan_id=?", (plan_id,)
        )
        self.conn.executemany(
            "INSERT INTO plan_links (plan_id, path, sort_order)"
            " VALUES (?, ?, ?)",
            [(plan_id, p, i) for i, p in enumerate(paths)],
        )
        self.conn.commit()
```

- [ ] **Step 4: 运行确认通过**

Run: `.venv/bin/pytest tests/test_repositories.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add app/data/repositories.py tests/test_repositories.py
git commit -m "feat: 数据层仓库——分类/计划/绑定路径 CRUD 与筛选"
```

---

### Task 4: 服务层 —— category_service.py 与 plan_service.py

**Files:**
- Create: `app/services/category_service.py`, `app/services/plan_service.py`
- Test: `tests/test_category_service.py`, `tests/test_plan_service.py`

**Interfaces:**
- Consumes: `CategoryRepo` / `PlanRepo` / `PlanLinkRepo`(Task 3),`models.*`(Task 2)
- Produces:
  - `category_service.CategoryService(conn)`:`.create(name: str, color: str) -> Category`(空名/重名抛 `ValueError`)、`.update(cat: Category) -> None`、`.delete(cat_id: int) -> None`、`.list_all() -> list[Category]`
  - `category_service.text_color_for(hex_color: str) -> str`(返回 `'#000000'` 或 `'#FFFFFF'`,按底色亮度)
  - `plan_service.PlanService(conn)`:
    - `.create(title, start_date, end_date, category_id=None, note="", status=0, paths=()) -> Plan`(空标题/end<start 抛 `ValueError`)
    - `.update(plan: Plan, paths: list[str] | None = None) -> None`(paths 非 None 时整体替换绑定)
    - `.delete(plan_id: int) -> None`
    - `.get_with_links(plan_id: int) -> tuple[Plan, list[PlanLink]]`
    - `.plans_for_month(year: int, month: int) -> list[Plan]`(覆盖月历整个网格范围)
    - `.list_filtered(**kwargs) -> list[Plan]`(透传 `PlanRepo.list_filtered`)
  - `plan_service.month_grid_range(year: int, month: int) -> tuple[date, date]`(周一起、周日止,覆盖当月的完整周)

- [ ] **Step 1: 写失败测试 tests/test_category_service.py**

```python
import pytest

from app.services.category_service import CategoryService, text_color_for


def test_create_strips_and_returns(conn):
    svc = CategoryService(conn)
    c = svc.create("  项目A ", "#4A90D9")
    assert c.name == "项目A" and c.id is not None


def test_create_empty_name_raises(conn):
    with pytest.raises(ValueError):
        CategoryService(conn).create("   ", "#4A90D9")


def test_create_duplicate_name_raises_value_error(conn):
    svc = CategoryService(conn)
    svc.create("同名", "#111111")
    with pytest.raises(ValueError):
        svc.create("同名", "#222222")


def test_text_color_for_light_bg_is_black():
    assert text_color_for("#FAC775") == "#000000"


def test_text_color_for_dark_bg_is_white():
    assert text_color_for("#0C447C") == "#FFFFFF"
```

- [ ] **Step 2: 写失败测试 tests/test_plan_service.py**

```python
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
    p = svc.create("评审", date(2026, 7, 6), date(2026, 7, 9),
                   paths=["D:\\a", "D:\\b"])
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
```

- [ ] **Step 3: 运行确认失败**

Run: `.venv/bin/pytest tests/test_category_service.py tests/test_plan_service.py -v`
Expected: ERROR,`No module named 'app.services.category_service'`

- [ ] **Step 4: 写 app/services/category_service.py**

```python
from __future__ import annotations

import sqlite3

from app.data.models import Category
from app.data.repositories import CategoryRepo


def text_color_for(hex_color: str) -> str:
    """按底色亮度返回黑或白,保证计划条文字可读。"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#000000" if luminance > 150 else "#FFFFFF"


class CategoryService:
    def __init__(self, conn: sqlite3.Connection):
        self.repo = CategoryRepo(conn)

    def create(self, name: str, color: str) -> Category:
        name = name.strip()
        if not name:
            raise ValueError("分类名称不能为空")
        try:
            return self.repo.add(name, color)
        except sqlite3.IntegrityError:
            raise ValueError(f"分类「{name}」已存在") from None

    def update(self, cat: Category) -> None:
        cat.name = cat.name.strip()
        if not cat.name:
            raise ValueError("分类名称不能为空")
        try:
            self.repo.update(cat)
        except sqlite3.IntegrityError:
            raise ValueError(f"分类「{cat.name}」已存在") from None

    def delete(self, cat_id: int) -> None:
        self.repo.delete(cat_id)

    def list_all(self) -> list[Category]:
        return self.repo.list_all()
```

- [ ] **Step 5: 写 app/services/plan_service.py**

```python
from __future__ import annotations

import sqlite3
from datetime import date, timedelta

from app.data.models import Plan, PlanLink
from app.data.repositories import PlanLinkRepo, PlanRepo


def month_grid_range(year: int, month: int) -> tuple[date, date]:
    """月历网格覆盖的日期范围:周一起,周日止,含当月所有完整周。"""
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

    def create(self, title: str, start_date: date, end_date: date,
               category_id: int | None = None, note: str = "",
               status: int = 0, paths: tuple[str, ...] = ()) -> Plan:
        title = self._validate(title, start_date, end_date)
        plan = self.plans.add(Plan(
            id=None, title=title, note=note, category_id=category_id,
            start_date=start_date, end_date=end_date, status=status,
        ))
        if paths:
            self.links.replace_for_plan(plan.id, list(paths))
        return plan

    def update(self, plan: Plan, paths: list[str] | None = None) -> None:
        plan.title = self._validate(
            plan.title, plan.start_date, plan.end_date
        )
        self.plans.update(plan)
        if paths is not None:
            self.links.replace_for_plan(plan.id, paths)

    def delete(self, plan_id: int) -> None:
        self.plans.delete(plan_id)

    def get_with_links(
        self, plan_id: int
    ) -> tuple[Plan, list[PlanLink]]:
        plan = self.plans.get(plan_id)
        return plan, self.links.list_for_plan(plan_id)

    def plans_for_month(self, year: int, month: int) -> list[Plan]:
        start, end = month_grid_range(year, month)
        return self.plans.list_overlapping(start, end)

    def list_filtered(self, **kwargs) -> list[Plan]:
        return self.plans.list_filtered(**kwargs)
```

- [ ] **Step 6: 运行确认通过**

Run: `.venv/bin/pytest tests/test_category_service.py tests/test_plan_service.py -v`
Expected: 12 passed

- [ ] **Step 7: Commit**

```bash
git add app/services tests/test_category_service.py tests/test_plan_service.py
git commit -m "feat: 服务层——分类与计划业务规则、月历网格范围计算"
```

---

### Task 5: 服务层 —— reminder_service.py 与 settings_service.py

**Files:**
- Create: `app/services/reminder_service.py`, `app/services/settings_service.py`
- Test: `tests/test_reminder_service.py`, `tests/test_settings_service.py`

**Interfaces:**
- Consumes: `PlanRepo`(Task 3)、`models.STATUS_DONE`(Task 2)
- Produces:
  - `reminder_service.get_reminders(conn, today: date) -> tuple[list[Plan], list[Plan]]`,返回 `(overdue, due_today)`:逾期 = `end_date < today 且 status != 已完成`;今日到期 = `end_date == today 且 status != 已完成`
  - `settings_service.get_setting(conn, key: str, default: str) -> str`
  - `settings_service.set_setting(conn, key: str, value: str) -> None`(UPSERT)
  - `settings_service.get_theme(conn) -> str`(`'light'`/`'dark'`,默认 `'light'`)、`settings_service.set_theme(conn, name: str) -> None`

- [ ] **Step 1: 写失败测试 tests/test_reminder_service.py**

```python
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
```

- [ ] **Step 2: 写失败测试 tests/test_settings_service.py**

```python
from app.services.settings_service import (
    get_setting, get_theme, set_setting, set_theme,
)


def test_get_setting_default(conn):
    assert get_setting(conn, "nope", "缺省") == "缺省"


def test_set_then_get_overwrites(conn):
    set_setting(conn, "k", "v1")
    set_setting(conn, "k", "v2")
    assert get_setting(conn, "k", "") == "v2"


def test_theme_default_light(conn):
    assert get_theme(conn) == "light"


def test_theme_roundtrip(conn):
    set_theme(conn, "dark")
    assert get_theme(conn) == "dark"
```

- [ ] **Step 3: 运行确认失败**

Run: `.venv/bin/pytest tests/test_reminder_service.py tests/test_settings_service.py -v`
Expected: ERROR,`No module named 'app.services.reminder_service'`

- [ ] **Step 4: 写 app/services/reminder_service.py**

```python
from __future__ import annotations

import sqlite3
from datetime import date

from app.data.models import Plan, STATUS_DONE
from app.data.repositories import PlanRepo


def get_reminders(
    conn: sqlite3.Connection, today: date
) -> tuple[list[Plan], list[Plan]]:
    """返回 (已逾期, 今日到期),均排除已完成。"""
    candidates = PlanRepo(conn).list_filtered(date_to=today)
    overdue = [
        p for p in candidates
        if p.end_date < today and p.status != STATUS_DONE
    ]
    due_today = [
        p for p in candidates
        if p.end_date == today and p.status != STATUS_DONE
    ]
    return overdue, due_today
```

- [ ] **Step 5: 写 app/services/settings_service.py**

```python
from __future__ import annotations

import sqlite3

THEME_KEY = "theme"
THEME_LIGHT = "light"
THEME_DARK = "dark"


def get_setting(conn: sqlite3.Connection, key: str, default: str) -> str:
    row = conn.execute(
        "SELECT value FROM settings WHERE key=?", (key,)
    ).fetchone()
    return row["value"] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?)"
        " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()


def get_theme(conn: sqlite3.Connection) -> str:
    return get_setting(conn, THEME_KEY, THEME_LIGHT)


def set_theme(conn: sqlite3.Connection, name: str) -> None:
    set_setting(conn, THEME_KEY, name)
```

(注:settings 的 SQL 极简且属于配置存取,归入服务层文件;仓库层不再重复包一层。)

- [ ] **Step 6: 运行确认通过**

Run: `.venv/bin/pytest tests/test_reminder_service.py tests/test_settings_service.py -v`
Expected: 6 passed

- [ ] **Step 7: 全量回归 + Commit**

Run: `.venv/bin/pytest -q`
Expected: 前 5 个 Task 的全部测试通过(34 个左右)

```bash
git add app/services tests/test_reminder_service.py tests/test_settings_service.py
git commit -m "feat: 服务层——启动提醒汇总与主题设置持久化"
```

---

### Task 6: platform_utils.py —— 分平台打开路径

**Files:**
- Create: `app/platform_utils.py`
- Test: `tests/test_platform_utils.py`

**Interfaces:**
- Produces:
  - `platform_utils.open_path(path: str) -> str | None`:成功返回 `None`;失败返回中文错误信息(路径不存在/无法打开)。Windows 用 `os.startfile`,macOS 用 `open`,Linux 用 `xdg-open`
  - `platform_utils.path_exists(path: str) -> bool`(UI 判断失效路径标红用)

- [ ] **Step 1: 写失败测试 tests/test_platform_utils.py**

```python
import app.platform_utils as pu


def test_open_missing_path_returns_error(tmp_path):
    msg = pu.open_path(str(tmp_path / "不存在"))
    assert msg is not None and "不存在" in msg


def test_open_existing_path_calls_launcher(tmp_path, monkeypatch):
    called = {}
    monkeypatch.setattr(pu, "_launch", lambda p: called.setdefault("p", p))
    assert pu.open_path(str(tmp_path)) is None
    assert called["p"] == str(tmp_path)


def test_launcher_failure_returns_error(tmp_path, monkeypatch):
    def boom(p):
        raise OSError("no handler")
    monkeypatch.setattr(pu, "_launch", boom)
    msg = pu.open_path(str(tmp_path))
    assert msg is not None and "无法打开" in msg


def test_path_exists(tmp_path):
    assert pu.path_exists(str(tmp_path)) is True
    assert pu.path_exists(str(tmp_path / "x")) is False
```

- [ ] **Step 2: 运行确认失败**

Run: `.venv/bin/pytest tests/test_platform_utils.py -v`
Expected: ERROR,`No module named 'app.platform_utils'`

- [ ] **Step 3: 写 app/platform_utils.py**

```python
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def path_exists(path: str) -> bool:
    return Path(path).exists()


def _launch(path: str) -> None:
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=True)
    else:
        subprocess.run(["xdg-open", path], check=True)


def open_path(path: str) -> str | None:
    """打开文件夹/文件。成功返回 None,失败返回中文错误信息。"""
    if not path_exists(path):
        return f"路径不存在:{path}"
    try:
        _launch(path)
        return None
    except (OSError, subprocess.SubprocessError):
        return f"无法打开:{path}"
```

- [ ] **Step 4: 运行确认通过**

Run: `.venv/bin/pytest tests/test_platform_utils.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add app/platform_utils.py tests/test_platform_utils.py
git commit -m "feat: 分平台打开文件夹/文件封装"
```

---

### Task 7: UI 主题 —— theme.py

GUI 模块,无 pytest;由 Task 8 的手动运行验证。

**Files:**
- Create: `app/ui/theme.py`

**Interfaces:**
- Produces:
  - `theme.COLORS: dict[str, dict[str, str]]`,键 `'light'` / `'dark'`,每套含:`window, base, text, muted, border, accent, hover, sel_bg, cal_grid, cal_out, cal_today, cal_overdue, cal_done_bg, cal_done_text`
  - `theme.apply_theme(app: QApplication, name: str) -> None`(设置 QPalette + 全局 QSS)
  - `theme.colors(name: str) -> dict[str, str]`(月历自绘取色用)

- [ ] **Step 1: 写 app/ui/theme.py**

```python
from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

COLORS = {
    "light": {
        "window": "#F5F5F5", "base": "#FFFFFF", "text": "#1C1C1C",
        "muted": "#767676", "border": "#D5D5D5", "accent": "#3574F0",
        "hover": "#EAEAEA", "sel_bg": "#D6E4FF",
        "cal_grid": "#DCDCDC", "cal_out": "#B5B5B5",
        "cal_today": "#3574F0", "cal_overdue": "#D93026",
        "cal_done_bg": "#E6E6E6", "cal_done_text": "#9A9A9A",
    },
    "dark": {
        "window": "#2B2B2B", "base": "#1F1F1F", "text": "#E8E8E8",
        "muted": "#9A9A9A", "border": "#454545", "accent": "#5B8DEF",
        "hover": "#3A3A3A", "sel_bg": "#2F4468",
        "cal_grid": "#404040", "cal_out": "#666666",
        "cal_today": "#5B8DEF", "cal_overdue": "#E5534B",
        "cal_done_bg": "#3A3A3A", "cal_done_text": "#808080",
    },
}

QSS = """
QMainWindow, QDialog {{ background: {window}; }}
QWidget {{ color: {text}; font-size: 13px; }}
QToolBar {{ background: {window}; border-bottom: 1px solid {border};
    spacing: 6px; padding: 4px; }}
QPushButton {{ background: {base}; border: 1px solid {border};
    border-radius: 4px; padding: 4px 12px; }}
QPushButton:hover {{ background: {hover}; }}
QPushButton:checked {{ background: {sel_bg}; border-color: {accent}; }}
QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {{
    background: {base}; border: 1px solid {border};
    border-radius: 4px; padding: 3px 6px; }}
QTableWidget {{ background: {base}; gridline-color: {cal_grid};
    border: 1px solid {border}; }}
QHeaderView::section {{ background: {window}; color: {muted};
    border: none; border-bottom: 1px solid {border}; padding: 4px; }}
QCheckBox {{ spacing: 6px; }}
QListWidget {{ background: {base}; border: 1px solid {border};
    border-radius: 4px; }}
QLabel#mutedLabel {{ color: {muted}; }}
"""


def colors(name: str) -> dict[str, str]:
    return COLORS.get(name, COLORS["light"])


def apply_theme(app: QApplication, name: str) -> None:
    c = colors(name)
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(c["window"]))
    pal.setColor(QPalette.Base, QColor(c["base"]))
    pal.setColor(QPalette.Text, QColor(c["text"]))
    pal.setColor(QPalette.WindowText, QColor(c["text"]))
    pal.setColor(QPalette.Button, QColor(c["base"]))
    pal.setColor(QPalette.ButtonText, QColor(c["text"]))
    pal.setColor(QPalette.Highlight, QColor(c["accent"]))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(pal)
    app.setStyleSheet(QSS.format(**c))
```

- [ ] **Step 2: 语法检查**

Run: `.venv/bin/python -c "import ast, pathlib; ast.parse(pathlib.Path('app/ui/theme.py').read_text())" && echo OK`
Expected: OK(GUI 效果在 Task 8 运行验证)

- [ ] **Step 3: Commit**

```bash
git add app/ui/theme.py
git commit -m "feat: 浅色/深色主题调色板与全局样式"
```

---

### Task 8: 主窗口骨架 + main.py 入口(含主题切换、异常兜底)

**Files:**
- Create: `app/ui/main_window.py`, `app/main.py`

**Interfaces:**
- Consumes: `theme.apply_theme/colors`(Task 7)、`CategoryService`(Task 4)、`settings_service.get_theme/set_theme`(Task 5)、`db.connect/backup/default_db_path/is_dir_writable`(Task 2)
- Produces(后续 Task 9-13 挂接点):
  - `MainWindow(conn)`,属性 `self.conn`、`self.cat_svc: CategoryService`、`self.plan_svc: PlanService`
  - `MainWindow.selected_category_ids() -> list[int | None]`(侧栏勾选的分类 id,`None` 代表未分类)
  - `MainWindow.refresh_categories() -> None`(重建侧栏复选框,勾选状态尽量保留)
  - `MainWindow.refresh_views() -> None`(通知当前视图刷新;Task 9/10 实现真实视图后生效)
  - `MainWindow.view_stack: QStackedWidget`(索引 0 = 月历占位,1 = 列表占位)、`MainWindow.toolbar` 上的按钮属性:`btn_prev/btn_next/btn_today/btn_cal/btn_list/btn_new/btn_theme`、`month_label`
  - `MainWindow.current_year/current_month: int`
  - `main.run()` 入口:可写检查 → 备份 → 连接 → 主题 → 主窗口 → 事件循环;`sys.excepthook` 写 `error.log` 并弹窗

- [ ] **Step 1: 写 app/ui/main_window.py**

```python
from __future__ import annotations

import sqlite3
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QSizePolicy, QStackedWidget, QToolBar, QVBoxLayout, QWidget,
)

from app.services.category_service import CategoryService
from app.services.plan_service import PlanService
from app.services.settings_service import get_theme, set_theme
from app.ui.theme import apply_theme

UNCATEGORIZED = None


class MainWindow(QMainWindow):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn
        self.cat_svc = CategoryService(conn)
        self.plan_svc = PlanService(conn)
        today = date.today()
        self.current_year, self.current_month = today.year, today.month
        self.setWindowTitle("工作计划")
        self.resize(1000, 680)
        self._build_toolbar()
        self._build_body()
        self.refresh_categories()
        self._update_month_label()

    def _build_toolbar(self) -> None:
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.btn_today = QPushButton("今天")
        self.month_label = QLabel()
        self.month_label.setStyleSheet("font-weight: bold; padding: 0 8px;")
        self.btn_cal = QPushButton("月历")
        self.btn_list = QPushButton("列表")
        for b in (self.btn_cal, self.btn_list):
            b.setCheckable(True)
        self.btn_cal.setChecked(True)
        self.btn_new = QPushButton("+ 新建")
        self.btn_theme = QPushButton()
        self.toolbar.addWidget(self.btn_prev)
        self.toolbar.addWidget(self.month_label)
        self.toolbar.addWidget(self.btn_next)
        self.toolbar.addWidget(self.btn_today)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(self.btn_cal)
        self.toolbar.addWidget(self.btn_list)
        self.toolbar.addWidget(self.btn_new)
        self.toolbar.addWidget(self.btn_theme)
        self.btn_prev.clicked.connect(lambda: self._shift_month(-1))
        self.btn_next.clicked.connect(lambda: self._shift_month(1))
        self.btn_today.clicked.connect(self._goto_today)
        self.btn_cal.clicked.connect(lambda: self._switch_view(0))
        self.btn_list.clicked.connect(lambda: self._switch_view(1))
        self.btn_theme.clicked.connect(self._toggle_theme)
        self._sync_theme_button()

    def _build_body(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        side = QWidget()
        side.setFixedWidth(170)
        self.side_layout = QVBoxLayout(side)
        cap = QLabel("分类筛选")
        cap.setObjectName("mutedLabel")
        self.side_layout.addWidget(cap)
        self.cat_box_container = QVBoxLayout()
        self.side_layout.addLayout(self.cat_box_container)
        self.side_layout.addStretch()
        self.btn_manage_cats = QPushButton("管理分类")
        self.side_layout.addWidget(self.btn_manage_cats)
        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(QLabel("月历视图(Task 12 实现)",
                                         alignment=Qt.AlignCenter))
        self.view_stack.addWidget(QLabel("列表视图(Task 11 实现)",
                                         alignment=Qt.AlignCenter))
        layout.addWidget(side)
        layout.addWidget(self.view_stack, stretch=1)
        self.setCentralWidget(root)

    def _switch_view(self, index: int) -> None:
        self.btn_cal.setChecked(index == 0)
        self.btn_list.setChecked(index == 1)
        self.view_stack.setCurrentIndex(index)
        self.refresh_views()

    def _shift_month(self, delta: int) -> None:
        m = self.current_month + delta
        if m == 0:
            self.current_year, self.current_month = self.current_year - 1, 12
        elif m == 13:
            self.current_year, self.current_month = self.current_year + 1, 1
        else:
            self.current_month = m
        self._update_month_label()
        self.refresh_views()

    def _goto_today(self) -> None:
        today = date.today()
        self.current_year, self.current_month = today.year, today.month
        self._update_month_label()
        self.refresh_views()

    def _update_month_label(self) -> None:
        self.month_label.setText(
            f"{self.current_year}年{self.current_month}月"
        )

    def refresh_categories(self) -> None:
        checked = {}
        while self.cat_box_container.count():
            item = self.cat_box_container.takeAt(0)
            w = item.widget()
            if w is not None:
                checked[w.property("cat_id")] = w.isChecked()
                w.deleteLater()
        self._cat_boxes: list[QCheckBox] = []
        entries = [(c.id, c.name, c.color) for c in self.cat_svc.list_all()]
        entries.append((UNCATEGORIZED, "未分类", "#888888"))
        for cid, name, color in entries:
            box = QCheckBox(name)
            box.setProperty("cat_id", cid)
            box.setChecked(checked.get(cid, True))
            box.setStyleSheet(
                f"QCheckBox::indicator {{ width: 12px; height: 12px;"
                f" border: 1px solid {color}; border-radius: 3px; }}"
                f"QCheckBox::indicator:checked {{ background: {color}; }}"
            )
            box.toggled.connect(lambda _=False: self.refresh_views())
            self.cat_box_container.addWidget(box)
            self._cat_boxes.append(box)

    def selected_category_ids(self) -> list[int | None]:
        boxes = getattr(self, "_cat_boxes", [])
        return [b.property("cat_id") for b in boxes if b.isChecked()]

    def refresh_views(self) -> None:
        current = self.view_stack.currentWidget()
        if hasattr(current, "refresh"):
            current.refresh()

    def _toggle_theme(self) -> None:
        new = "dark" if get_theme(self.conn) == "light" else "light"
        set_theme(self.conn, new)
        from PySide6.QtWidgets import QApplication
        apply_theme(QApplication.instance(), new)
        self._sync_theme_button()

    def _sync_theme_button(self) -> None:
        dark = get_theme(self.conn) == "dark"
        self.btn_theme.setText("☀ 浅色" if dark else "🌙 深色")
```

- [ ] **Step 2: 写 app/main.py**

```python
from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from app.data.db import (
    app_dir, backup, connect, default_db_path, is_dir_writable,
)
from app.services.settings_service import get_theme
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme


def _install_excepthook() -> None:
    def hook(exc_type, exc, tb):
        text = "".join(traceback.format_exception(exc_type, exc, tb))
        try:
            log = app_dir() / "error.log"
            with open(log, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except OSError:
            pass
        QMessageBox.critical(
            None, "程序出错",
            "发生未预期的错误,详情已写入 error.log。\n\n" + str(exc),
        )
    sys.excepthook = hook


def run() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("工作计划")
    _install_excepthook()
    directory = app_dir()
    if not is_dir_writable(directory):
        QMessageBox.critical(
            None, "无法启动",
            "软件所在目录不可写,数据将无法保存。\n"
            "请将软件放到可写目录(不要放在 Program Files)。",
        )
        sys.exit(1)
    db_path = default_db_path()
    backup(db_path)
    conn = connect(db_path)
    apply_theme(app, get_theme(conn))
    win = MainWindow(conn)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
```

- [ ] **Step 3: 手动运行验证(macOS 开发机)**

Run: `.venv/bin/python -m app.main`
Expected 检查项:
1. 窗口出现,标题「工作计划」,工具栏显示「2026年7月」与各按钮
2. ◀ ▶ 切换月份标签正确跨年(1月←→12月);「今天」回到当月
3. 「月历」「列表」切换 QStackedWidget 占位文本
4. 侧栏出现「未分类」复选框(尚无分类)
5. 点主题按钮:深浅色即时全局切换;关闭重开程序,主题保持
6. 项目根目录生成 workplan.db 与 backups/(第二次启动后)

- [ ] **Step 4: 全量测试仍通过**

Run: `.venv/bin/pytest -q`
Expected: 全部通过(GUI 模块不被测试导入)

- [ ] **Step 5: Commit**

```bash
git add app/ui/main_window.py app/main.py
git commit -m "feat: 主窗口骨架、入口、主题切换与异常兜底"
```

---

### Task 9: 分类管理对话框 category_dialog.py

**Files:**
- Create: `app/ui/category_dialog.py`
- Modify: `app/ui/main_window.py`(挂接「管理分类」按钮)

**Interfaces:**
- Consumes: `CategoryService`(Task 4)、`MainWindow.btn_manage_cats / refresh_categories / refresh_views`(Task 8)
- Produces: `CategoryDialog(conn, parent=None)`,模态;关闭后调用方需刷新侧栏与视图

- [ ] **Step 1: 写 app/ui/category_dialog.py**

```python
from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QColorDialog, QDialog, QHBoxLayout, QInputDialog, QListWidget,
    QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout,
)

from app.services.category_service import CategoryService


class CategoryDialog(QDialog):
    def __init__(self, conn: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.svc = CategoryService(conn)
        self.setWindowTitle("管理分类")
        self.resize(360, 400)
        layout = QVBoxLayout(self)
        self.listw = QListWidget()
        layout.addWidget(self.listw)
        row = QHBoxLayout()
        for text, slot in (
            ("新增", self._add), ("重命名", self._rename),
            ("改颜色", self._recolor), ("删除", self._delete),
            ("上移", lambda: self._move(-1)),
            ("下移", lambda: self._move(1)),
        ):
            b = QPushButton(text)
            b.clicked.connect(slot)
            row.addWidget(b)
        layout.addLayout(row)
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        self._reload()

    def _reload(self) -> None:
        self.listw.clear()
        for c in self.svc.list_all():
            item = QListWidgetItem(c.name)
            pix = QPixmap(14, 14)
            pix.fill(QColor(c.color))
            item.setIcon(QIcon(pix))
            item.setData(Qt.UserRole, c)
            self.listw.addItem(item)

    def _current(self):
        item = self.listw.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _add(self) -> None:
        name, ok = QInputDialog.getText(self, "新增分类", "分类名称:")
        if not ok:
            return
        color = QColorDialog.getColor(QColor("#4A90D9"), self, "选择颜色")
        if not color.isValid():
            return
        try:
            cat = self.svc.create(name, color.name())
            cat.sort_order = self.listw.count()
            self.svc.update(cat)
        except ValueError as e:
            QMessageBox.warning(self, "无法新增", str(e))
        self._reload()

    def _rename(self) -> None:
        cat = self._current()
        if not cat:
            return
        name, ok = QInputDialog.getText(
            self, "重命名", "分类名称:", text=cat.name
        )
        if not ok:
            return
        cat.name = name
        try:
            self.svc.update(cat)
        except ValueError as e:
            QMessageBox.warning(self, "无法重命名", str(e))
        self._reload()

    def _recolor(self) -> None:
        cat = self._current()
        if not cat:
            return
        color = QColorDialog.getColor(QColor(cat.color), self, "选择颜色")
        if color.isValid():
            cat.color = color.name()
            self.svc.update(cat)
            self._reload()

    def _delete(self) -> None:
        cat = self._current()
        if not cat:
            return
        ans = QMessageBox.question(
            self, "删除分类",
            f"删除分类「{cat.name}」?\n其下的计划会变为「未分类」,不会被删除。",
        )
        if ans == QMessageBox.Yes:
            self.svc.delete(cat.id)
            self._reload()

    def _move(self, delta: int) -> None:
        row = self.listw.currentRow()
        target = row + delta
        if row < 0 or not (0 <= target < self.listw.count()):
            return
        cats = self.svc.list_all()
        cats[row], cats[target] = cats[target], cats[row]
        for i, c in enumerate(cats):
            c.sort_order = i
            self.svc.update(c)
        self._reload()
        self.listw.setCurrentRow(target)
```

- [ ] **Step 2: 在 main_window.py 挂接按钮**

在 `MainWindow.__init__` 末尾(`self._update_month_label()` 之前)加:

```python
        self.btn_manage_cats.clicked.connect(self._open_category_dialog)
```

在类中新增方法:

```python
    def _open_category_dialog(self) -> None:
        from app.ui.category_dialog import CategoryDialog
        CategoryDialog(self.conn, self).exec()
        self.refresh_categories()
        self.refresh_views()
```

- [ ] **Step 3: 手动运行验证**

Run: `.venv/bin/python -m app.main`
Expected:「管理分类」打开对话框;新增「项目A」蓝色、「日常」绿色;重命名、改颜色、上移下移生效;删除有确认提示;关闭后侧栏复选框同步出现且带颜色

- [ ] **Step 4: Commit**

```bash
git add app/ui/category_dialog.py app/ui/main_window.py
git commit -m "feat: 分类管理对话框——增删改名、颜色、排序"
```

---

### Task 10: 计划编辑对话框 plan_dialog.py(含路径绑定)

**Files:**
- Create: `app/ui/plan_dialog.py`
- Modify: `app/ui/main_window.py`(挂接「+ 新建」按钮)

**Interfaces:**
- Consumes: `PlanService`(Task 4)、`CategoryService`(Task 4)、`platform_utils.open_path/path_exists`(Task 6)、`models.STATUS_NAMES`(Task 2)
- Produces:
  - `PlanDialog(conn, plan_id: int | None = None, default_date: date | None = None, parent=None)`:`plan_id=None` 为新建;`exec()` 返回后调用方一律刷新视图
  - 内部保存/删除均已落库;`ValueError` 以警告框呈现,不崩溃

- [ ] **Step 1: 写 app/ui/plan_dialog.py**

```python
from __future__ import annotations

import sqlite3
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QButtonGroup, QComboBox, QDateEdit, QDialog, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMessageBox, QPushButton, QRadioButton,
    QTextEdit, QVBoxLayout,
)

from app import platform_utils
from app.data.models import STATUS_NAMES
from app.services.category_service import CategoryService
from app.services.plan_service import PlanService


def _to_qdate(d: date) -> QDate:
    return QDate(d.year, d.month, d.day)


class PlanDialog(QDialog):
    def __init__(self, conn: sqlite3.Connection,
                 plan_id: int | None = None,
                 default_date: date | None = None, parent=None):
        super().__init__(parent)
        self.svc = PlanService(conn)
        self.cat_svc = CategoryService(conn)
        self.plan_id = plan_id
        self.setWindowTitle("编辑计划" if plan_id else "新建计划")
        self.resize(480, 560)
        self._build_form()
        if plan_id:
            self._load(plan_id)
        else:
            d = _to_qdate(default_date or date.today())
            self.start_edit.setDate(d)
            self.end_edit.setDate(d)

    def _build_form(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.title_edit = QLineEdit()
        form.addRow("标题", self.title_edit)
        self.cat_combo = QComboBox()
        self.cat_combo.addItem("未分类", None)
        for c in self.cat_svc.list_all():
            self.cat_combo.addItem(c.name, c.id)
        form.addRow("分类", self.cat_combo)
        self.start_edit = QDateEdit(calendarPopup=True)
        self.end_edit = QDateEdit(calendarPopup=True)
        dates = QHBoxLayout()
        dates.addWidget(self.start_edit)
        dates.addWidget(QLabel("至"))
        dates.addWidget(self.end_edit)
        form.addRow("日期", dates)
        self.status_group = QButtonGroup(self)
        status_row = QHBoxLayout()
        for value, name in STATUS_NAMES.items():
            rb = QRadioButton(name)
            self.status_group.addButton(rb, value)
            status_row.addWidget(rb)
        self.status_group.button(0).setChecked(True)
        form.addRow("状态", status_row)
        self.note_edit = QTextEdit()
        self.note_edit.setFixedHeight(70)
        form.addRow("备注", self.note_edit)
        layout.addLayout(form)
        layout.addWidget(QLabel("绑定文件夹 / 文件"))
        self.links_list = QListWidget()
        layout.addWidget(self.links_list)
        btns = QHBoxLayout()
        for text, slot in (
            ("添加文件夹", self._add_folder), ("添加文件", self._add_file),
            ("打开", self._open_selected), ("移除", self._remove_selected),
        ):
            b = QPushButton(text)
            b.clicked.connect(slot)
            btns.addWidget(b)
        layout.addLayout(btns)
        footer = QHBoxLayout()
        self.btn_delete = QPushButton("删除计划")
        self.btn_delete.clicked.connect(self._delete)
        self.btn_delete.setVisible(self.plan_id is not None)
        footer.addWidget(self.btn_delete)
        footer.addStretch()
        cancel = QPushButton("取消")
        cancel.clicked.connect(self.reject)
        save = QPushButton("保存")
        save.setDefault(True)
        save.clicked.connect(self._save)
        footer.addWidget(cancel)
        footer.addWidget(save)
        layout.addLayout(footer)

    def _load(self, plan_id: int) -> None:
        plan, links = self.svc.get_with_links(plan_id)
        self.title_edit.setText(plan.title)
        idx = self.cat_combo.findData(plan.category_id)
        self.cat_combo.setCurrentIndex(max(idx, 0))
        self.start_edit.setDate(_to_qdate(plan.start_date))
        self.end_edit.setDate(_to_qdate(plan.end_date))
        self.status_group.button(plan.status).setChecked(True)
        self.note_edit.setPlainText(plan.note)
        for link in links:
            self._append_path(link.path)

    def _append_path(self, path: str) -> None:
        item = QListWidgetItem(path)
        if not platform_utils.path_exists(path):
            item.setForeground(Qt.red)
            item.setText(f"{path}  (路径不存在)")
            item.setData(Qt.UserRole, path)
        else:
            item.setData(Qt.UserRole, path)
        self.links_list.addItem(item)

    def _add_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if d:
            self._append_path(d)

    def _add_file(self) -> None:
        f, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if f:
            self._append_path(f)

    def _open_selected(self) -> None:
        item = self.links_list.currentItem()
        if not item:
            return
        err = platform_utils.open_path(item.data(Qt.UserRole))
        if err:
            QMessageBox.warning(self, "无法打开", err)

    def _remove_selected(self) -> None:
        row = self.links_list.currentRow()
        if row >= 0:
            self.links_list.takeItem(row)

    def _paths(self) -> list[str]:
        return [
            self.links_list.item(i).data(Qt.UserRole)
            for i in range(self.links_list.count())
        ]

    def _save(self) -> None:
        title = self.title_edit.text()
        start = self.start_edit.date().toPython()
        end = self.end_edit.date().toPython()
        cat_id = self.cat_combo.currentData()
        status = self.status_group.checkedId()
        note = self.note_edit.toPlainText()
        try:
            if self.plan_id is None:
                self.svc.create(
                    title, start, end, category_id=cat_id, note=note,
                    status=status, paths=tuple(self._paths()),
                )
            else:
                plan, _ = self.svc.get_with_links(self.plan_id)
                plan.title, plan.note, plan.category_id = title, note, cat_id
                plan.start_date, plan.end_date = start, end
                plan.status = status
                self.svc.update(plan, paths=self._paths())
        except ValueError as e:
            QMessageBox.warning(self, "无法保存", str(e))
            return
        self.accept()

    def _delete(self) -> None:
        ans = QMessageBox.question(
            self, "删除计划", "确定删除这条计划?绑定路径记录会一并删除。"
        )
        if ans == QMessageBox.Yes:
            self.svc.delete(self.plan_id)
            self.accept()
```

- [ ] **Step 2: 在 main_window.py 挂接「+ 新建」**

在 `MainWindow.__init__` 末尾加:

```python
        self.btn_new.clicked.connect(self._new_plan)
```

新增方法:

```python
    def _new_plan(self) -> None:
        from app.ui.plan_dialog import PlanDialog
        PlanDialog(self.conn, parent=self).exec()
        self.refresh_views()
```

- [ ] **Step 3: 手动运行验证**

Run: `.venv/bin/python -m app.main`
Expected:「+ 新建」打开对话框;空标题保存弹「标题不能为空」;结束日期早于开始日期弹「结束日期不能早于开始日期」;添加文件夹/文件后列表出现;选中一行点「打开」跳转访达(Mac 上验证);手动填一个不存在的路径进数据库后重开对话框,该行红色显示「(路径不存在)」;保存成功后重开可见数据;编辑态出现「删除计划」按钮且删除有确认

- [ ] **Step 4: Commit**

```bash
git add app/ui/plan_dialog.py app/ui/main_window.py
git commit -m "feat: 计划编辑对话框——字段校验、路径绑定与跳转"
```

---

### Task 11: 列表视图 list_view.py

**Files:**
- Create: `app/ui/list_view.py`
- Modify: `app/ui/main_window.py`(替换列表占位、新增 `_edit_plan`)

**Interfaces:**
- Consumes: `PlanService.list_filtered/get_with_links`(Task 4)、`CategoryService.list_all`(Task 4)、`MainWindow.selected_category_ids`(Task 8)、`PlanDialog`(Task 10)
- Produces:
  - `ListView(conn, sidebar_ids: Callable[[], list[int | None]])`,信号 `plan_activated(int)`(双击行)
  - `ListView.refresh() -> None`(主窗口 `refresh_views` 通过 duck-typing 调用)
  - `MainWindow._edit_plan(plan_id: int) -> None`(打开编辑对话框后刷新;Task 12/13 复用)

- [ ] **Step 1: 写 app/ui/list_view.py**

```python
from __future__ import annotations

import sqlite3
from datetime import date
from typing import Callable

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QHBoxLayout, QHeaderView,
    QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data.models import STATUS_DONE, STATUS_NAMES
from app.services.category_service import CategoryService
from app.services.plan_service import PlanService

ALL = "ALL"
COLUMNS = ["状态", "标题", "分类", "开始", "结束", "绑定"]


class ListView(QWidget):
    plan_activated = Signal(int)

    def __init__(self, conn: sqlite3.Connection,
                 sidebar_ids: Callable[[], list[int | None]]):
        super().__init__()
        self.svc = PlanService(conn)
        self.cat_svc = CategoryService(conn)
        self.sidebar_ids = sidebar_ids
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.cat_combo = QComboBox()
        self.status_combo = QComboBox()
        self.status_combo.addItem("全部状态", None)
        for value, name in STATUS_NAMES.items():
            self.status_combo.addItem(name, value)
        self.date_check = QCheckBox("按日期筛选")
        today = date.today()
        self.from_edit = QDateEdit(calendarPopup=True)
        self.from_edit.setDate(QDate(today.year, today.month, 1))
        self.to_edit = QDateEdit(calendarPopup=True)
        self.to_edit.setDate(QDate(today.year, today.month, 1).addMonths(1).addDays(-1))
        bar.addWidget(self.cat_combo)
        bar.addWidget(self.status_combo)
        bar.addWidget(self.date_check)
        bar.addWidget(self.from_edit)
        bar.addWidget(QLabel("至"))
        bar.addWidget(self.to_edit)
        bar.addStretch()
        layout.addLayout(bar)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        for w in (self.cat_combo, self.status_combo):
            w.currentIndexChanged.connect(lambda _: self.refresh())
        self.date_check.toggled.connect(lambda _: self.refresh())
        self.from_edit.dateChanged.connect(lambda _: self.refresh())
        self.to_edit.dateChanged.connect(lambda _: self.refresh())
        self.table.itemDoubleClicked.connect(self._on_double_click)
        self.refresh()

    def _rebuild_cat_combo(self) -> None:
        current = self.cat_combo.currentData()
        self.cat_combo.blockSignals(True)
        self.cat_combo.clear()
        self.cat_combo.addItem("全部分类", ALL)
        for c in self.cat_svc.list_all():
            self.cat_combo.addItem(c.name, c.id)
        self.cat_combo.addItem("未分类", None)
        idx = self.cat_combo.findData(current)
        self.cat_combo.setCurrentIndex(max(idx, 0))
        self.cat_combo.blockSignals(False)

    def _effective_category_ids(self) -> list[int | None]:
        side = self.sidebar_ids()
        chosen = self.cat_combo.currentData()
        if chosen == ALL:
            return side
        return [chosen] if chosen in side else []

    def refresh(self) -> None:
        self._rebuild_cat_combo()
        kwargs = {"category_ids": self._effective_category_ids()}
        if self.status_combo.currentData() is not None:
            kwargs["status"] = self.status_combo.currentData()
        if self.date_check.isChecked():
            kwargs["date_from"] = self.from_edit.date().toPython()
            kwargs["date_to"] = self.to_edit.date().toPython()
        plans = self.svc.list_filtered(**kwargs)
        cats = {c.id: c for c in self.cat_svc.list_all()}
        today = date.today()
        self.table.setRowCount(len(plans))
        for row, p in enumerate(plans):
            overdue = p.status != STATUS_DONE and p.end_date < today
            status_item = QTableWidgetItem(
                "逾期" if overdue else STATUS_NAMES[p.status]
            )
            if overdue:
                status_item.setForeground(QColor("#D93026"))
            title_item = QTableWidgetItem(p.title)
            if p.status == STATUS_DONE:
                f = title_item.font()
                f.setStrikeOut(True)
                title_item.setFont(f)
            cat = cats.get(p.category_id)
            cat_item = QTableWidgetItem(cat.name if cat else "未分类")
            if cat:
                cat_item.setForeground(QColor(cat.color))
            _, links = self.svc.get_with_links(p.id)
            cells = [
                status_item, title_item, cat_item,
                QTableWidgetItem(p.start_date.isoformat()),
                QTableWidgetItem(p.end_date.isoformat()),
                QTableWidgetItem(str(len(links)) if links else "—"),
            ]
            for col, item in enumerate(cells):
                item.setData(Qt.UserRole, p.id)
                self.table.setItem(row, col, item)

    def _on_double_click(self, item: QTableWidgetItem) -> None:
        self.plan_activated.emit(item.data(Qt.UserRole))
```

- [ ] **Step 2: 在 main_window.py 替换列表占位**

`_build_body` 中,将

```python
        self.view_stack.addWidget(QLabel("列表视图(Task 11 实现)",
                                         alignment=Qt.AlignCenter))
```

替换为:

```python
        from app.ui.list_view import ListView
        self.list_view = ListView(self.conn, self.selected_category_ids)
        self.list_view.plan_activated.connect(self._edit_plan)
        self.view_stack.addWidget(self.list_view)
```

新增方法:

```python
    def _edit_plan(self, plan_id: int) -> None:
        from app.ui.plan_dialog import PlanDialog
        PlanDialog(self.conn, plan_id=plan_id, parent=self).exec()
        self.refresh_views()
```

- [ ] **Step 3: 手动运行验证**

Run: `.venv/bin/python -m app.main`
Expected:切到「列表」;新建几条不同分类/状态/日期的计划;分类下拉、状态下拉、日期区间勾选后表格即时过滤;取消勾选侧栏某分类后该分类的行消失(叠加生效);已完成行标题划线;把一条未完成计划结束日期改到昨天 → 状态列显示红色「逾期」;双击行打开编辑对话框,改标题保存后表格刷新

- [ ] **Step 4: Commit**

```bash
git add app/ui/list_view.py app/ui/main_window.py
git commit -m "feat: 列表视图——筛选叠加、逾期标红、双击编辑"
```

---

### Task 12: 月历视图 calendar_view.py(自绘网格与跨天条带)

**Files:**
- Create: `app/ui/calendar_view.py`
- Modify: `app/ui/main_window.py`(替换月历占位)

**Interfaces:**
- Consumes: `PlanService.plans_for_month` / `month_grid_range`(Task 4)、`text_color_for`(Task 4)、`theme.colors`(Task 7)、`get_theme`(Task 5)、`MainWindow.selected_category_ids/_edit_plan`(Task 8/11)
- Produces:
  - `CalendarView(conn, sidebar_ids: Callable, current_month: Callable[[], tuple[int, int]])`
  - 信号:`plan_clicked(int)`、`day_clicked(object)`(参数为 `datetime.date`)、`day_double_clicked(object)`
  - `CalendarView.refresh() -> None`(重取数据并重绘;主窗口 duck-typing 调用)
  - 渲染规则:跨天连续条带、跨周断行(每周条带首格重绘标题)、已完成灰底划线、逾期红圆点、今天高亮边框、每格最多 3 条 + 「+N 更多」

- [ ] **Step 1: 写 app/ui/calendar_view.py**

```python
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Callable

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.data.models import STATUS_DONE
from app.services.category_service import CategoryService, text_color_for
from app.services.plan_service import PlanService, month_grid_range
from app.services.settings_service import get_theme
from app.ui.theme import colors

HEADER_H = 26
DAY_NUM_H = 18
BAR_H = 17
BAR_GAP = 2
MAX_LANES = 3
UNCAT_COLOR = "#888888"
WEEKDAYS = "一二三四五六日"


class CalendarView(QWidget):
    plan_clicked = Signal(int)
    day_clicked = Signal(object)
    day_double_clicked = Signal(object)

    def __init__(self, conn: sqlite3.Connection,
                 sidebar_ids: Callable[[], list[int | None]],
                 current_month: Callable[[], tuple[int, int]]):
        super().__init__()
        self.conn = conn
        self.svc = PlanService(conn)
        self.cat_svc = CategoryService(conn)
        self.sidebar_ids = sidebar_ids
        self.current_month = current_month
        self.setMinimumSize(560, 420)
        self._weeks: list[list[date]] = []
        self._plans = []
        self._cat_colors: dict[int | None, str] = {}
        self._plan_hits: list[tuple[QRect, int]] = []
        self._day_cells: list[tuple[QRect, date]] = []
        self.refresh()

    def refresh(self) -> None:
        year, month = self.current_month()
        start, end = month_grid_range(year, month)
        days = []
        d = start
        while d <= end:
            days.append(d)
            d += timedelta(days=1)
        self._weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
        allowed = set(self.sidebar_ids())
        self._plans = [
            p for p in self.svc.plans_for_month(year, month)
            if p.category_id in allowed
        ]
        self._cat_colors = {
            c.id: c.color for c in self.cat_svc.list_all()
        }
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = colors(get_theme(self.conn))
        _, month = self.current_month()
        today = date.today()
        cell_w = self.width() / 7
        rows = max(len(self._weeks), 1)
        cell_h = (self.height() - HEADER_H) / rows
        self._plan_hits = []
        self._day_cells = []
        painter.setPen(QColor(c["muted"]))
        for i, name in enumerate(WEEKDAYS):
            painter.drawText(
                QRect(int(i * cell_w), 0, int(cell_w), HEADER_H),
                Qt.AlignCenter, name,
            )
        for wi, week in enumerate(self._weeks):
            y = int(HEADER_H + wi * cell_h)
            for di, day in enumerate(week):
                x = int(di * cell_w)
                rect = QRect(x, y, int(cell_w), int(cell_h))
                self._day_cells.append((rect, day))
                painter.setPen(QColor(c["cal_grid"]))
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(rect)
                if day == today:
                    pen = QPen(QColor(c["cal_today"]))
                    pen.setWidth(2)
                    painter.setPen(pen)
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))
                in_month = day.month == month
                painter.setPen(
                    QColor(c["text"] if in_month else c["cal_out"])
                )
                painter.drawText(
                    QRect(x, y + 2, int(cell_w) - 6, DAY_NUM_H),
                    Qt.AlignRight | Qt.AlignTop, str(day.day),
                )
            self._draw_week_bars(
                painter, c, week, wi, cell_w, cell_h, today, month
            )
        painter.end()

    def _draw_week_bars(self, painter, c, week, wi, cell_w, cell_h,
                        today, month) -> None:
        week_start, week_end = week[0], week[-1]
        wplans = sorted(
            (p for p in self._plans
             if p.start_date <= week_end and p.end_date >= week_start),
            key=lambda p: (p.start_date, p.id),
        )
        lanes: list[list[tuple[int, int]]] = []
        overflow = [0] * 7
        for plan in wplans:
            c0 = max((plan.start_date - week_start).days, 0)
            c1 = min((plan.end_date - week_start).days, 6)
            lane = None
            for li, spans in enumerate(lanes):
                if all(c1 < a or b < c0 for a, b in spans):
                    lane = li
                    break
            if lane is None:
                if len(lanes) >= MAX_LANES:
                    for col in range(c0, c1 + 1):
                        overflow[col] += 1
                    continue
                lanes.append([])
                lane = len(lanes) - 1
            lanes[lane].append((c0, c1))
            y = int(HEADER_H + wi * cell_h + DAY_NUM_H + 4
                    + lane * (BAR_H + BAR_GAP))
            x = int(c0 * cell_w) + 3
            w = int((c1 - c0 + 1) * cell_w) - 6
            rect = QRect(x, y, w, BAR_H)
            color = self._cat_colors.get(plan.category_id, UNCAT_COLOR)
            done = plan.status == STATUS_DONE
            painter.setPen(Qt.NoPen)
            painter.setBrush(
                QColor(c["cal_done_bg"]) if done else QColor(color)
            )
            painter.drawRoundedRect(rect, 3, 3)
            font = painter.font()
            font.setStrikeOut(done)
            painter.setFont(font)
            painter.setPen(QColor(
                c["cal_done_text"] if done else text_color_for(color)
            ))
            text_rect = rect.adjusted(5, 0, -14, 0)
            painter.drawText(
                text_rect, Qt.AlignVCenter | Qt.AlignLeft,
                painter.fontMetrics().elidedText(
                    plan.title, Qt.ElideRight, text_rect.width()
                ),
            )
            font.setStrikeOut(False)
            painter.setFont(font)
            if not done and plan.end_date < today:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(c["cal_overdue"]))
                painter.drawEllipse(rect.right() - 10, rect.top() + 5, 7, 7)
            self._plan_hits.append((rect, plan.id))
        painter.setPen(QColor(c["muted"]))
        for col, n in enumerate(overflow):
            if n:
                painter.drawText(
                    QRect(int(col * cell_w) + 5,
                          int(HEADER_H + wi * cell_h + cell_h) - 16,
                          int(cell_w) - 10, 14),
                    Qt.AlignLeft, f"+{n} 更多",
                )

    def _hit_plan(self, pos) -> int | None:
        for rect, plan_id in self._plan_hits:
            if rect.contains(pos):
                return plan_id
        return None

    def _hit_day(self, pos) -> date | None:
        for rect, day in self._day_cells:
            if rect.contains(pos):
                return day
        return None

    def mousePressEvent(self, event) -> None:
        pos = event.position().toPoint()
        plan_id = self._hit_plan(pos)
        if plan_id is not None:
            self.plan_clicked.emit(plan_id)
            return
        day = self._hit_day(pos)
        if day is not None:
            self.day_clicked.emit(day)

    def mouseDoubleClickEvent(self, event) -> None:
        pos = event.position().toPoint()
        if self._hit_plan(pos) is None:
            day = self._hit_day(pos)
            if day is not None:
                self.day_double_clicked.emit(day)
```

- [ ] **Step 2: 在 main_window.py 替换月历占位**

`_build_body` 中,将

```python
        self.view_stack.addWidget(QLabel("月历视图(Task 12 实现)",
                                         alignment=Qt.AlignCenter))
```

替换为:

```python
        from app.ui.calendar_view import CalendarView
        self.calendar_view = CalendarView(
            self.conn, self.selected_category_ids,
            lambda: (self.current_year, self.current_month),
        )
        self.calendar_view.plan_clicked.connect(self._edit_plan)
        self.calendar_view.day_double_clicked.connect(self._new_plan_on)
        self.view_stack.addWidget(self.calendar_view)
```

(`day_clicked` 在 Task 13 接当日面板。)

新增方法:

```python
    def _new_plan_on(self, day: date) -> None:
        from app.ui.plan_dialog import PlanDialog
        PlanDialog(self.conn, default_date=day, parent=self).exec()
        self.refresh_views()
```

并在文件顶部确认已有 `from datetime import date`。

- [ ] **Step 3: 手动运行验证**

Run: `.venv/bin/python -m app.main`
Expected 检查项:
1. 月历显示当月网格,周一起始,今天有高亮边框,月外日期灰显
2. 新建单日计划 → 当天出现分类色条;新建跨 4 天计划 → 连续条带横跨 4 格
3. 新建跨周计划(如周五到下周二)→ 两段条带,第二周首格重新显示标题
4. 同一天塞 4 条计划 → 只显示 3 条 + 「+1 更多」
5. 标记一条为已完成 → 灰底划线;把一条未完成的结束日期改到昨天 → 条带右端出现红点
6. 双击空白格 → 新建对话框日期预填该天;单击计划条 → 打开编辑
7. 取消勾选侧栏分类 → 对应条带消失;切换深色主题 → 网格/文字/条带全部适配
8. ◀ ▶ 翻月、「今天」跳回,渲染正确

- [ ] **Step 4: Commit**

```bash
git add app/ui/calendar_view.py app/ui/main_window.py
git commit -m "feat: 自绘月历视图——跨天条带、跨周断行、逾期红点、更多折叠"
```

---

### Task 13: 当日面板、启动提醒与最终接线

**Files:**
- Create: `app/ui/day_panel.py`, `app/ui/reminder_dialog.py`
- Modify: `app/ui/main_window.py`(接 `day_clicked`)、`app/main.py`(启动提醒)

**Interfaces:**
- Consumes: `PlanService`(Task 4)、`get_reminders`(Task 5)、`STATUS_NAMES/STATUS_DONE`(Task 2)、`CalendarView.day_clicked`(Task 12)、`MainWindow._edit_plan/_new_plan_on`(Task 11/12)
- Produces:
  - `DayPanel(conn, day: date, parent)`:非模态小窗,列当日全部计划;信号 `plan_activated(int)`、`new_plan_requested(object)`
  - `ReminderDialog(conn, overdue: list[Plan], due_today: list[Plan], parent=None)`:模态;信号 `plan_activated(int)`

- [ ] **Step 1: 写 app/ui/day_panel.py**

```python
from __future__ import annotations

import sqlite3
from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton,
    QVBoxLayout,
)

from app.data.models import STATUS_NAMES
from app.services.plan_service import PlanService


class DayPanel(QDialog):
    plan_activated = Signal(int)
    new_plan_requested = Signal(object)

    def __init__(self, conn: sqlite3.Connection, day: date, parent=None):
        super().__init__(parent)
        self.svc = PlanService(conn)
        self.day = day
        self.setWindowTitle(f"{day.year}年{day.month}月{day.day}日 的计划")
        self.setModal(False)
        self.resize(340, 300)
        layout = QVBoxLayout(self)
        self.listw = QListWidget()
        layout.addWidget(self.listw)
        row = QHBoxLayout()
        btn_new = QPushButton("+ 在这天新建")
        btn_new.clicked.connect(
            lambda: self.new_plan_requested.emit(self.day)
        )
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        row.addWidget(btn_new)
        row.addStretch()
        row.addWidget(btn_close)
        layout.addLayout(row)
        self.listw.itemDoubleClicked.connect(
            lambda item: self.plan_activated.emit(item.data(Qt.UserRole))
        )
        self.reload()

    def reload(self) -> None:
        self.listw.clear()
        plans = self.svc.plans.list_overlapping(self.day, self.day)
        if not plans:
            self.listw.addItem("这一天还没有计划")
            return
        for p in plans:
            item = QListWidgetItem(
                f"[{STATUS_NAMES[p.status]}] {p.title}"
            )
            item.setData(Qt.UserRole, p.id)
            self.listw.addItem(item)
```

- [ ] **Step 2: 写 app/ui/reminder_dialog.py**

```python
from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QVBoxLayout,
)

from app.data.models import Plan


class ReminderDialog(QDialog):
    plan_activated = Signal(int)

    def __init__(self, conn: sqlite3.Connection, overdue: list[Plan],
                 due_today: list[Plan], parent=None):
        super().__init__(parent)
        self.setWindowTitle("待办提醒")
        self.resize(380, 340)
        layout = QVBoxLayout(self)
        self.listw = QListWidget()
        layout.addWidget(QLabel("双击条目可直接打开编辑"))
        layout.addWidget(self.listw)
        self._add_group(f"已逾期({len(overdue)})", overdue, "#D93026")
        self._add_group(f"今日到期({len(due_today)})", due_today,
                        "#BA7517")
        btn = QPushButton("知道了")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)
        self.listw.itemDoubleClicked.connect(self._on_double_click)

    def _add_group(self, title: str, plans: list[Plan],
                   color: str) -> None:
        if not plans:
            return
        header = QListWidgetItem(title)
        header.setFlags(Qt.ItemIsEnabled)
        header.setForeground(QColor(color))
        self.listw.addItem(header)
        for p in plans:
            item = QListWidgetItem(
                f"    {p.title}({p.end_date.isoformat()} 到期)"
            )
            item.setData(Qt.UserRole, p.id)
            self.listw.addItem(item)

    def _on_double_click(self, item: QListWidgetItem) -> None:
        plan_id = item.data(Qt.UserRole)
        if plan_id is not None:
            self.plan_activated.emit(plan_id)
```

- [ ] **Step 3: main_window.py 接当日面板**

Task 12 的 CalendarView 接线处补一行:

```python
        self.calendar_view.day_clicked.connect(self._show_day_panel)
```

新增方法:

```python
    def _show_day_panel(self, day: date) -> None:
        from app.ui.day_panel import DayPanel
        panel = DayPanel(self.conn, day, self)
        panel.plan_activated.connect(self._edit_plan)
        panel.plan_activated.connect(panel.reload)
        panel.new_plan_requested.connect(self._new_plan_on)
        panel.new_plan_requested.connect(lambda _: panel.reload())
        panel.show()
```

- [ ] **Step 4: main.py 接启动提醒**

`run()` 中 `win.show()` 之后、`sys.exit(app.exec())` 之前加:

```python
    from datetime import date as _date
    from app.services.reminder_service import get_reminders
    from app.ui.reminder_dialog import ReminderDialog
    overdue, due_today = get_reminders(conn, _date.today())
    if overdue or due_today:
        dlg = ReminderDialog(conn, overdue, due_today, win)
        dlg.plan_activated.connect(win._edit_plan)
        dlg.exec()
        win.refresh_views()
```

- [ ] **Step 5: 手动运行验证**

Run: `.venv/bin/python -m app.main`
Expected:
1. 单击月历某天 → 非模态小窗列出当天计划(含跨天覆盖当天的);双击条目打开编辑;「+ 在这天新建」预填该日
2. 制造一条逾期、一条今日到期 → 重启程序弹「待办提醒」,分组显示、数量正确、已完成不出现;双击条目直接打开编辑;无到期时不弹窗

- [ ] **Step 6: 全量回归 + Commit**

Run: `.venv/bin/pytest -q`
Expected: 全部通过

```bash
git add app/ui/day_panel.py app/ui/reminder_dialog.py app/ui/main_window.py app/main.py
git commit -m "feat: 当日计划面板与启动待办提醒"
```

---

### Task 14: Windows 打包与交付

**Files:**
- Create: `run.py`, `build.bat`, `.github/workflows/build.yml`, `README.md`

**Interfaces:**
- Consumes: `app.main.run`(Task 8)
- Produces: 双击 `build.bat`(Windows)得到 `dist\工作计划.exe`;推 `v*` tag 时 GitHub Actions 自动产出同名 artifact

- [ ] **Step 1: 写 run.py(PyInstaller 入口)**

```python
from app.main import run

if __name__ == "__main__":
    run()
```

- [ ] **Step 2: 写 build.bat**

```bat
@echo off
chcp 65001 >nul
echo === 工作计划 打包脚本(需要 Windows + Python 3.11+)===
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if exist app.ico (
    set ICON=--icon app.ico
) else (
    set ICON=
)
pyinstaller --noconfirm --onefile --windowed --name 工作计划 %ICON% run.py
echo.
echo 打包完成:dist\工作计划.exe
pause
```

- [ ] **Step 3: 写 .github/workflows/build.yml**

```yaml
name: build-windows-exe
on:
  push:
    tags: ["v*"]
  workflow_dispatch:
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest -q
      - run: pyinstaller --noconfirm --onefile --windowed --name 工作计划 run.py
      - uses: actions/upload-artifact@v4
        with:
          name: 工作计划-windows-exe
          path: dist/工作计划.exe
```

- [ ] **Step 4: 写 README.md**

内容(完整照写):

````markdown
# 工作计划

本地便携版工作计划管理软件:分类管理、月历/列表视图、文件夹绑定一键跳转、
启动待办提醒、浅色/深色主题。数据存在软件同目录的 `workplan.db`,
整个文件夹拷走即可迁移。

## 开发(macOS / Windows / Linux)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # Windows: .venv\Scripts\pip
.venv/bin/python -m app.main                # 运行
.venv/bin/pytest -q                         # 测试
```

## 打包成 Windows exe

PyInstaller 不支持跨平台打包,必须在 Windows 上执行(二选一):

1. **本机打包**:把仓库拷到 Windows 电脑,双击 `build.bat`,
   产物在 `dist\工作计划.exe`。
2. **GitHub Actions**:推送 `v*` tag(或手动触发 workflow),
   在 Actions 页面下载 artifact「工作计划-windows-exe」。

首次启动约 2-4 秒(onefile 解压),属正常现象。
不要把 exe 放进 `Program Files`(目录不可写会拒绝启动并提示)。

可选:仓库根目录放一个 `app.ico`,build.bat 会自动作为程序图标。

## 冒烟测试清单(打包后在 Windows 上过一遍)

1. 新建分类并配色 → 月历上颜色正确
2. 新建单日计划、跨天计划 → 月历显示正确,跨周条带断行正常
3. 绑定文件夹和文件 → 点击「打开」资源管理器跳转正确
4. 移走绑定的文件夹 → 对话框中该行标红「路径不存在」
5. 标记完成 → 灰色划线;制造逾期 → 红点 + 重启弹提醒
6. 列表视图筛选、双击编辑
7. 关闭软件,拷贝整个目录到别处再运行 → 数据完整随行
8. 切换深色主题 → 全部界面变色无遗漏;重启后仍是深色
````

- [ ] **Step 5: 提交并验证 pytest 全绿**

Run: `.venv/bin/pytest -q`
Expected: 全部通过

```bash
git add run.py build.bat .github README.md
git commit -m "feat: Windows 打包脚本、CI 自动构建与使用说明"
```

- [ ] **Step 6: (需要用户参与)Windows 实机打包与冒烟**

在用户的 Windows 电脑上执行 `build.bat`,按 README 冒烟清单逐项验证。
此步无法在 macOS 开发机完成,标记为交付前的人工步骤。

---

## Self-Review 记录

- 规格覆盖:分类(Task 9)、月历(Task 12)、列表(Task 11)、路径绑定与跳转(Task 6/10)、启动提醒(Task 13)、主题(Task 7/8)、便携存储与备份(Task 2/8)、错误处理(Task 6/8/10)、打包(Task 14)—— spec 全部条目均有对应任务
- 类型一致性:`selected_category_ids() -> list[int | None]` 贯穿 Task 8/11/12;`refresh()` duck-typing 约定贯穿 Task 8/11/12;`STATUS_*` 常量单一来源 Task 2
- 自审已修:QSizePolicy 用法、QIcon 显式转换、复选框选中态样式、`selected_category_ids` 初始化容错、占位标签任务号与 Task 11/12 替换代码对齐、移除未用 import
