from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

COLORS = {
    "light": {
        "window": "#EDE7DC",
        "base": "#FFFDF7",
        "paper": "#FFF9EC",
        "paper_alt": "#FAF0DF",
        "sidebar": "#2F4054",
        "sidebar_text": "#F8F1E4",
        "sidebar_muted": "#D5C8B5",
        "text": "#1E252D",
        "muted": "#746A5E",
        "border": "#D8C7AA",
        "accent": "#1D5C7A",
        "accent_soft": "#E0EEF1",
        "hover": "#F2E6D2",
        "sel_bg": "#D8E7EB",
        "cal_grid": "#D8C7AA",
        "cal_out": "#A99B8A",
        "cal_today": "#1D5C7A",
        "cal_overdue": "#C6473A",
        "cal_done_bg": "#E5DED2",
        "cal_done_text": "#9C9285",
        "cal_weekend_bg": "#F8ECDC",
        "holiday_bg": "#F8DDD8",
    },
    "dark": {
        "window": "#171A1E",
        "base": "#22272D",
        "paper": "#20262D",
        "paper_alt": "#252C33",
        "sidebar": "#111820",
        "sidebar_text": "#EDE6D8",
        "sidebar_muted": "#A99D8B",
        "text": "#EFE8DC",
        "muted": "#A99D8B",
        "border": "#3B4650",
        "accent": "#76B8D8",
        "accent_soft": "#263C46",
        "hover": "#2C343C",
        "sel_bg": "#294251",
        "cal_grid": "#3B4650",
        "cal_out": "#68727B",
        "cal_today": "#76B8D8",
        "cal_overdue": "#E06B61",
        "cal_done_bg": "#30353B",
        "cal_done_text": "#777F87",
        "cal_weekend_bg": "#252A2F",
        "holiday_bg": "#3D2B2D",
    },
}

QSS = """
QMainWindow, QDialog {{ background: {window}; }}
QWidget {{
    color: {text};
    font-family: "LXGW WenKai", "Source Han Sans SC", "Microsoft YaHei UI", "PingFang SC";
    font-size: 13px;
}}
QWidget#appRoot {{ background: {window}; }}
QWidget#sidePanel {{
    background: {sidebar};
    border-right: 1px solid {border};
}}
QToolBar {{
    background: {window};
    border-bottom: 1px solid {border};
    spacing: 8px;
    padding: 8px 10px;
}}
QPushButton {{
    background: {base};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 6px 13px;
}}
QPushButton:hover {{ background: {hover}; }}
QPushButton:checked {{ background: {accent_soft}; border-color: {accent}; color: {accent}; }}
QPushButton#primaryButton {{
    background: {accent};
    color: #FFFFFF;
    border-color: {accent};
    font-weight: 700;
}}
QPushButton#quietButton {{
    background: transparent;
    color: {muted};
}}
QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {{
    background: {base}; border: 1px solid {border};
    border-radius: 6px; padding: 4px 7px; }}
QTableWidget {{ background: {base}; gridline-color: {cal_grid};
    border: 1px solid {border}; }}
QHeaderView::section {{ background: {window}; color: {muted};
    border: none; border-bottom: 1px solid {border}; padding: 4px; }}
QCheckBox {{ spacing: 6px; }}
QListWidget {{ background: {base}; border: 1px solid {border};
    border-radius: 6px; }}
QLabel#mutedLabel {{ color: {muted}; }}
QWidget#sidePanel QLabel#mutedLabel {{
    color: {sidebar_muted};
    font-weight: 700;
    letter-spacing: 1px;
}}
QWidget#sidePanel QCheckBox {{ color: {sidebar_text}; }}
QWidget#sidePanel QPushButton {{
    background: rgba(255, 255, 255, 0.08);
    color: {sidebar_text};
    border-color: rgba(255, 255, 255, 0.18);
}}
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
