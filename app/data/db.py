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
    """Return the exe directory when frozen, otherwise the project root."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def data_dir() -> Path:
    return app_dir() / "data"


def _migrate_legacy_db(target: Path) -> None:
    legacy = app_dir() / "workplan.db"
    if not legacy.exists() or target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(legacy), str(target))
    for suffix in ("-wal", "-shm"):
        sidecar = legacy.with_name(legacy.name + suffix)
        if sidecar.exists():
            shutil.move(str(sidecar), str(target.with_name(target.name + suffix)))


def default_db_path() -> Path:
    path = data_dir() / "workplan.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    _migrate_legacy_db(path)
    return path


def is_dir_writable(d: Path) -> bool:
    probe = d / ".write_probe"
    try:
        d.mkdir(parents=True, exist_ok=True)
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
