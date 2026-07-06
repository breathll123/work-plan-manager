from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

COLORS = {
    "light": {
        "window": "#EAF1EC",
        "base": "#FBFEFA",
        "paper": "#F7FBF4",
        "paper_alt": "#EEF7EF",
        "sidebar": "#24443F",
        "sidebar_text": "#F6FBF4",
        "sidebar_muted": "#BFD6CA",
        "text": "#21312D",
        "muted": "#6B7D74",
        "border": "#C7DAD0",
        "accent": "#167168",
        "accent_soft": "#DCEFEB",
        "hover": "#EEF7F3",
        "sel_bg": "#DCEFEB",
        "cal_grid": "#CBDED3",
        "cal_out": "#9BAEA5",
        "cal_today": "#167168",
        "cal_overdue": "#C65345",
        "cal_done_bg": "#E1EAE4",
        "cal_done_text": "#8FA098",
        "cal_weekend_bg": "#EDF6F1",
        "holiday_bg": "#F6DDD8",
    },
    "dark": {
        "window": "#111B1B",
        "base": "#1B2928",
        "paper": "#172423",
        "paper_alt": "#1D302E",
        "sidebar": "#0C1717",
        "sidebar_text": "#EDF7F2",
        "sidebar_muted": "#94B7AA",
        "text": "#EAF4EF",
        "muted": "#9DB5AC",
        "border": "#2F4B47",
        "accent": "#73D0C1",
        "accent_soft": "#1F3D39",
        "hover": "#223532",
        "sel_bg": "#1F3D39",
        "cal_grid": "#31504B",
        "cal_out": "#67827A",
        "cal_today": "#73D0C1",
        "cal_overdue": "#ED8377",
        "cal_done_bg": "#243331",
        "cal_done_text": "#748A84",
        "cal_weekend_bg": "#1B2B29",
        "holiday_bg": "#42302E",
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
    outline: none;
}}
QPushButton:hover {{ background: {hover}; }}
QPushButton:focus {{ border: 1px solid {accent}; }}
QPushButton:checked {{
    background: {accent_soft};
    border: 1px solid {accent};
    color: {accent};
    font-weight: 700;
}}
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
    border-radius: 6px; padding: 4px 7px; outline: none; }}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border: 1px solid {accent};
    background: {base};
}}
QTableWidget {{ background: {base}; gridline-color: {cal_grid};
    border: 1px solid {border};
    selection-background-color: {accent_soft};
    selection-color: {text};
    outline: none; }}
QTableWidget::item:selected {{
    background: {accent_soft};
    color: {text};
}}
QHeaderView::section {{ background: {window}; color: {muted};
    border: none; border-bottom: 1px solid {border}; padding: 4px; }}
QCheckBox {{ spacing: 6px; outline: none; }}
QListWidget {{ background: {base}; border: 1px solid {border};
    border-radius: 6px; outline: none;
    selection-background-color: {accent_soft};
    selection-color: {text}; }}
QListWidget::item:selected {{
    background: {accent_soft};
    color: {text};
}}
QLabel#mutedLabel {{ color: {muted}; }}
QWidget#sidePanel QLabel#mutedLabel {{
    color: {sidebar_muted};
    font-weight: 700;
    letter-spacing: 1px;
}}
QWidget#sidePanel QCheckBox {{ color: {sidebar_text}; }}
QWidget#sidePanel QPushButton {{
    background: rgba(255, 255, 255, 0.10);
    color: {sidebar_text};
    border-color: rgba(255, 255, 255, 0.20);
}}
QWidget#sidePanel QPushButton:focus {{
    border-color: {accent};
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
