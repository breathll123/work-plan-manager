import pytest

from app.services.settings_service import get_setting, get_theme, set_setting, set_theme


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


def test_theme_rejects_unknown(conn):
    with pytest.raises(ValueError):
        set_theme(conn, "blue")
