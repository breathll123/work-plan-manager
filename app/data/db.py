from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import time
from collections.abc import Callable
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

Migration = Callable[[sqlite3.Connection], None]


def _migrate_to_1(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


MIGRATIONS: dict[int, Migration] = {
    1: _migrate_to_1,
}


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
    db_existed = db_path.exists()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        migrate_database(conn, db_path, db_existed=db_existed)
    except Exception:
        conn.close()
        raise
    return conn


def schema_version(conn: sqlite3.Connection) -> int:
    return int(conn.execute("PRAGMA user_version").fetchone()[0])


def migrate_database(
    conn: sqlite3.Connection, db_path: Path, db_existed: bool = True
) -> None:
    current = schema_version(conn)
    if current > SCHEMA_VERSION:
        raise RuntimeError(
            f"数据库版本 {current} 高于当前程序支持的版本 {SCHEMA_VERSION},"
            "请使用更新版本的程序打开。"
        )
    if current == SCHEMA_VERSION:
        return

    if db_existed:
        backup(
            db_path,
            keep=10,
            label=f"before-upgrade-v{current}-to-v{SCHEMA_VERSION}",
        )

    for version in range(current + 1, SCHEMA_VERSION + 1):
        migration = MIGRATIONS.get(version)
        if migration is None:
            raise RuntimeError(f"缺少数据库迁移脚本: v{version}")
        migration(conn)
        conn.execute(f"PRAGMA user_version = {version}")
        conn.commit()


def _backup_target(db_path: Path, label: str | None) -> Path:
    bdir = db_path.parent / "backups"
    bdir.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    safe_label = ""
    if label:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in label)
        safe_label = f"-{safe.strip('-')}" if safe.strip("-") else ""
    target = bdir / f"workplan-{stamp}{safe_label}.db"
    n = 1
    while target.exists():
        target = bdir / f"workplan-{stamp}{safe_label}-{n}.db"
        n += 1
    return target


def backup(db_path: Path, keep: int = 5, label: str | None = None) -> None:
    if not db_path.exists():
        return
    target = _backup_target(db_path, label)
    try:
        src = sqlite3.connect(str(db_path))
        dst = sqlite3.connect(str(target))
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
    except sqlite3.DatabaseError:
        if target.exists():
            target.unlink()
        shutil.copy2(db_path, target)
    bdir = db_path.parent / "backups"
    old = sorted(bdir.glob("workplan-*.db"), key=os.path.getmtime)
    for f in old[:-keep]:
        f.unlink()
