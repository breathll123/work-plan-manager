from app.ui.theme import COLORS, QSS, colors, resolve_theme
from app.ui.widgets import DATE_DISPLAY_FORMAT


def test_theme_qss_formats_for_light_and_dark():
    assert QSS.format(**colors("light"))
    assert QSS.format(**colors("dark"))


def test_light_and_dark_define_same_tokens():
    assert set(COLORS["light"]) == set(COLORS["dark"])


def test_resolve_theme_passthrough():
    assert resolve_theme("light") == "light"
    assert resolve_theme("dark") == "dark"


def test_resolve_theme_system_falls_back_without_app():
    assert resolve_theme("system") in {"light", "dark"}


def test_colors_accepts_system():
    assert colors("system") in (COLORS["light"], COLORS["dark"])


def test_date_display_format_uses_chinese_year_month_day_order():
    assert DATE_DISPLAY_FORMAT == "yyyy年M月d日"
