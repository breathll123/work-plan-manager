from app.ui.theme import QSS, colors
from app.ui.widgets import DATE_DISPLAY_FORMAT


def test_theme_qss_formats_for_light_and_dark():
    assert QSS.format(**colors("light"))
    assert QSS.format(**colors("dark"))


def test_date_display_format_uses_chinese_year_month_day_order():
    assert DATE_DISPLAY_FORMAT == "yyyy年M月d日"
