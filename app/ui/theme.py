from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

COLORS = {
    "light": {
        "window": "#F5F5F5",
        "base": "#FFFFFF",
        "text": "#1C1C1C",
        "muted": "#767676",
        "border": "#D5D5D5",
        "accent": "#3574F0",
        "hover": "#EAEAEA",
        "sel_bg": "#D6E4FF",
        "cal_grid": "#DCDCDC",
        "cal_out": "#B5B5B5",
        "cal_today": "#3574F0",
        "cal_overdue": "#D93026",
        "cal_done_bg": "#E6E6E6",
        "cal_done_text": "#9A9A9A",
    },
    "dark": {
        "window": "#2B2B2B",
        "base": "#1F1F1F",
        "text": "#E8E8E8",
        "muted": "#9A9A9A",
        "border": "#454545",
        "accent": "#5B8DEF",
        "hover": "#3A3A3A",
        "sel_bg": "#2F4468",
        "cal_grid": "#404040",
        "cal_out": "#666666",
        "cal_today": "#5B8DEF",
        "cal_overdue": "#E5534B",
        "cal_done_bg": "#3A3A3A",
        "cal_done_text": "#808080",
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
