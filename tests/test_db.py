import sqlite3

import pytest

from app.data.db import backup, is_dir_writable


def test_connect_creates_tables(conn):
    names = {
        r["name"]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert {"categories", "plans", "plan_links", "settings"} <= names


def test_foreign_keys_enabled(conn):
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_schema_version_set(conn):
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 1


def test_end_date_check_constraint(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO plans (title, start_date, end_date, status, "
            "created_at, updated_at) "
            "VALUES ('x', '2026-07-10', '2026-07-09', 0, '', '')"
        )


def test_backup_rotates_keep_5(tmp_path):
    from app.data.db import connect

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
