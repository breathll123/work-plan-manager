import pytest

from app.services.category_service import CategoryService, text_color_for


def test_create_strips_and_returns(conn):
    c = CategoryService(conn).create("  项目A ", "#4A90D9")
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
