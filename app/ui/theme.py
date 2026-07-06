from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

COLORS = {
    "light": {
        "window": "#F3F6F2",
        "surface": "#FFFFFF",
        "base": "#FBFEFA",
        "paper": "#F7FBF4",
        "paper_alt": "#EEF7EF",
        "sidebar": "#24443F",
        "sidebar_text": "#F6FBF4",
        "sidebar_muted": "#BFD6CA",
        "text": "#21312D",
        "muted": "#6B7D74",
        "border": "#D5E1DA",
        "border_strong": "#AFC8BC",
        "accent": "#167168",
        "accent_deep": "#0D5A55",
        "accent_soft": "#DCEFEB",
        "accent_faint": "#F0F8F5",
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
        "holiday_text": "#B6473B",
        "solar_term_bg": "#DDEFE8",
        "solar_term_text": "#12675F",
        "danger": "#C65345",
        "danger_soft": "#F8E5E1",
        "warning": "#BA7517",
    },
    "dark": {
        "window": "#111B1B",
        "surface": "#182625",
        "base": "#1B2928",
        "paper": "#172423",
        "paper_alt": "#1D302E",
        "sidebar": "#0C1717",
        "sidebar_text": "#EDF7F2",
        "sidebar_muted": "#94B7AA",
        "text": "#EAF4EF",
        "muted": "#9DB5AC",
        "border": "#2F4B47",
        "border_strong": "#4C7069",
        "accent": "#73D0C1",
        "accent_deep": "#9BE4D8",
        "accent_soft": "#1F3D39",
        "accent_faint": "#182F2C",
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
        "holiday_text": "#F09A90",
        "solar_term_bg": "#203D38",
        "solar_term_text": "#8FE0D1",
        "danger": "#ED8377",
        "danger_soft": "#3B2523",
        "warning": "#E0A34C",
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
    border: none;
    spacing: 8px;
    padding: 12px 14px;
}}
QLabel#monthTitle {{
    color: {text};
    font-size: 26px;
    font-weight: 800;
    padding: 0 14px;
}}
QPushButton {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 7px 14px;
    min-height: 28px;
    outline: none;
}}
QPushButton:hover {{
    background: {hover};
    border-color: {border_strong};
}}
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
QPushButton#primaryButton:hover {{
    background: {accent_deep};
    border-color: {accent_deep};
}}
QPushButton#quietButton {{
    background: transparent;
    color: {muted};
    border-color: transparent;
}}
QPushButton#subtleButton {{
    background: {accent_faint};
    color: {accent_deep};
    border-color: transparent;
    font-weight: 700;
}}
QPushButton#dangerButton {{
    background: {danger_soft};
    color: {danger};
    border-color: transparent;
    font-weight: 700;
}}
QPushButton#navButton {{
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    border-radius: 17px;
    padding: 0;
    font-size: 22px;
    font-weight: 600;
}}
QPushButton#segmentButton {{
    background: transparent;
    border-color: transparent;
    border-radius: 10px;
    color: {muted};
    font-weight: 700;
    padding: 7px 16px;
}}
QPushButton#segmentButton:hover {{
    background: {hover};
    color: {text};
}}
QPushButton#segmentButton:checked {{
    background: {accent};
    border-color: {accent};
    color: #FFFFFF;
}}
QPushButton#statusPill {{
    background: {accent_faint};
    border-color: transparent;
    color: {muted};
    border-radius: 12px;
    padding: 7px 14px;
    font-weight: 700;
}}
QPushButton#statusPill:checked {{
    background: {accent};
    border-color: {accent};
    color: #FFFFFF;
}}
QPushButton#sidebarButton {{
    background: rgba(255, 255, 255, 0.12);
    color: {sidebar_text};
    border-color: rgba(255, 255, 255, 0.18);
    font-weight: 700;
}}
QWidget#filterBar {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 12px;
}}
QLabel#fieldLabel {{
    color: {muted};
    font-size: 12px;
    font-weight: 800;
    padding-left: 2px;
}}
QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 6px 10px;
    min-height: 26px;
    selection-background-color: {accent_soft};
    selection-color: {text};
    outline: none;
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border: 1px solid {accent};
    background: {surface};
}}
QComboBox {{
    padding-right: 30px;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid {border};
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    background: {accent_faint};
}}
QComboBox::down-arrow {{
    image: none;
    width: 0;
    height: 0;
}}
QComboBox QAbstractItemView {{
    background: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 4px;
    outline: none;
    selection-background-color: {accent_soft};
    selection-color: {text};
}}
QDateEdit::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid {border};
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    background: {accent_faint};
}}
QDateEdit::down-arrow {{
    image: none;
    width: 0;
    height: 0;
}}
QCalendarWidget QWidget {{
    background: {surface};
    alternate-background-color: {paper_alt};
}}
QCalendarWidget QWidget#qt_calendar_navigationbar {{
    background: {surface};
    border: none;
}}
QCalendarWidget QToolButton {{
    background: {accent_faint};
    color: {accent_deep};
    border: 1px solid transparent;
    border-radius: 9px;
    margin: 4px 2px;
    padding: 5px 10px;
    font-weight: 800;
    outline: none;
}}
QCalendarWidget QToolButton:hover {{
    background: {hover};
    border-color: {border_strong};
}}
QCalendarWidget QMenu {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 8px;
}}
QCalendarWidget QSpinBox {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 4px 7px;
}}
QCalendarWidget QAbstractItemView {{
    background: {surface};
    color: {text};
    selection-background-color: {accent_soft};
    selection-color: {text};
    border: none;
    outline: none;
}}
QCalendarWidget QAbstractItemView::item:hover {{
    background: {hover};
}}
QCalendarWidget QAbstractItemView::item:selected {{
    background: {accent};
    color: #FFFFFF;
    border: none;
    outline: none;
}}
QTableWidget {{
    background: {surface};
    alternate-background-color: {paper_alt};
    gridline-color: transparent;
    border: 1px solid {border};
    border-radius: 12px;
    selection-background-color: {accent_soft};
    selection-color: {text};
    outline: none;
}}
QTableWidget::item:selected {{
    background: {accent_soft};
    color: {text};
}}
QHeaderView::section {{
    background: {surface};
    color: {muted};
    border: none;
    border-bottom: 1px solid {border};
    padding: 8px 6px;
    font-weight: 800;
}}
QCheckBox {{
    spacing: 7px;
    outline: none;
}}
QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {border_strong};
    border-radius: 5px;
    background: {surface};
}}
QCheckBox::indicator:checked {{
    background: {accent};
    border-color: {accent};
}}
QCheckBox#dateFilterPill {{
    background: {accent_faint};
    border: 1px solid transparent;
    border-radius: 12px;
    color: {muted};
    padding: 7px 12px;
    font-weight: 700;
}}
QCheckBox#dateFilterPill:checked {{
    background: {accent_soft};
    color: {accent_deep};
    border-color: {accent};
}}
QCheckBox#dateFilterPill::indicator {{
    width: 0;
    height: 0;
    border: none;
}}
QListWidget {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 12px;
    padding: 4px;
    outline: none;
    selection-background-color: {accent_soft};
    selection-color: {text};
}}
QListWidget::item {{
    border-radius: 8px;
    padding: 6px 8px;
}}
QListWidget::item:hover {{
    background: {hover};
}}
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
QWidget#sidePanel QCheckBox {{
    color: {sidebar_text};
    padding: 5px 2px;
}}
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
