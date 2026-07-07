from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

COLORS = {
    "light": {
        "window": "#F5F7FA",
        "surface": "#FFFFFF",
        "base": "#FFFFFF",
        "paper": "#FFFFFF",
        "paper_alt": "#F1F4F8",
        "sidebar": "#FFFFFF",
        "sidebar_text": "#1E293B",
        "sidebar_muted": "#667085",
        "sidebar_button_bg": "#F3F6FA",
        "sidebar_button_border": "#D7DEE8",
        "text": "#1E293B",
        "muted": "#667085",
        "border": "#D8DEE8",
        "border_strong": "#B8C2D0",
        "accent": "#2563EB",
        "accent_deep": "#1D4ED8",
        "accent_soft": "#DBEAFE",
        "accent_faint": "#EFF6FF",
        "hover": "#F1F5F9",
        "sel_bg": "#DBEAFE",
        "cal_grid": "#D5DCE8",
        "cal_out": "#9AA4B2",
        "cal_today": "#2563EB",
        "cal_today_bg": "#F1F6FF",
        "cal_overdue": "#DC2626",
        "cal_done_bg": "#E5E7EB",
        "cal_done_text": "#8A94A6",
        "cal_weekend_bg": "#FFF7ED",
        "holiday_bg": "#FEE2E2",
        "holiday_text": "#B42318",
        "solar_term_bg": "#E0F2FE",
        "solar_term_text": "#0369A1",
        "system_bar_bg": "#D97706",
        "system_bar_text": "#FFF7ED",
        "danger": "#DC2626",
        "danger_soft": "#FEE2E2",
        "warning": "#B45309",
    },
    "dark": {
        "window": "#2A2724",
        "surface": "#34302C",
        "base": "#37332F",
        "paper": "#302D29",
        "paper_alt": "#393530",
        "sidebar": "#252C2A",
        "sidebar_text": "#F0ECE4",
        "sidebar_muted": "#B9C8BF",
        "sidebar_button_bg": "#33413D",
        "sidebar_button_border": "#52635E",
        "text": "#F0ECE4",
        "muted": "#B6AEA4",
        "border": "#514B45",
        "border_strong": "#6B6259",
        "accent": "#72C8B8",
        "accent_deep": "#9CE3D7",
        "accent_soft": "#2F504A",
        "accent_faint": "#303B37",
        "hover": "#3E3934",
        "sel_bg": "#2F504A",
        "cal_grid": "#504A43",
        "cal_out": "#7B736A",
        "cal_today": "#72C8B8",
        "cal_today_bg": "#243538",
        "cal_overdue": "#F07D70",
        "cal_done_bg": "#3C3934",
        "cal_done_text": "#8F897F",
        "cal_weekend_bg": "#40362F",
        "holiday_bg": "#523B35",
        "holiday_text": "#F2A197",
        "solar_term_bg": "#2B514B",
        "solar_term_text": "#9DE1D4",
        "system_bar_bg": "#74460E",
        "system_bar_text": "#FFB340",
        "danger": "#F07D70",
        "danger_soft": "#4A332E",
        "warning": "#D59A3C",
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
    border: 1px solid {border};
    border-radius: 14px;
}}
QWidget#detailPanel {{
    background: {paper};
    border: 1px solid {border};
    border-radius: 14px;
}}
QLabel#detailTitle {{
    color: {text};
    font-size: 18px;
    font-weight: 800;
}}
QLabel#detailSection {{
    color: {muted};
    font-size: 12px;
    font-weight: 800;
}}
QFrame#detailCard {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 12px;
}}
QLabel#detailPlanTitle {{
    color: {text};
    font-size: 17px;
    font-weight: 800;
}}
QLabel#detailBadge {{
    background: {accent_faint};
    color: {accent_deep};
    border: 1px solid {accent_soft};
    border-radius: 10px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 800;
}}
QLabel#detailNote {{
    background: {accent_faint};
    color: {text};
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 9px 10px;
}}
QLabel#emptyDetail {{
    color: {muted};
    background: {surface};
    border: 1px dashed {border_strong};
    border-radius: 12px;
    padding: 14px;
}}
QScrollArea#detailScroll {{
    background: transparent;
    border: none;
}}
QListWidget#dayPlanList {{
    background: {surface};
    border-color: {border};
}}
QListWidget#dayPlanList::item {{
    min-height: 28px;
    padding: 8px 10px;
}}
QFrame#linkRow {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 12px;
}}
QFrame#linkRow:hover {{
    border-color: {border_strong};
    background: {hover};
}}
QLabel#linkTitle {{
    color: {text};
    font-weight: 800;
}}
QLabel#linkPath {{
    color: {muted};
    font-size: 12px;
}}
QLabel#pathMissing {{
    color: {danger};
    font-size: 12px;
}}
QPushButton#linkButton {{
    background: {accent_faint};
    color: {accent_deep};
    border-color: transparent;
    border-radius: 10px;
    padding: 6px 10px;
    font-weight: 800;
}}
QPushButton#linkButton:hover {{
    background: {accent_soft};
    border-color: {accent};
}}
QPushButton#linkButton:disabled {{
    background: {paper_alt};
    color: {muted};
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
    background: {sidebar_button_bg};
    color: {sidebar_text};
    border-color: {sidebar_button_border};
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
QLabel#formLabel {{
    color: {muted};
    font-weight: 800;
    padding-top: 2px;
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
    background: {sidebar_button_bg};
    color: {sidebar_text};
    border-color: {sidebar_button_border};
}}
QWidget#sidePanel QPushButton:focus {{
    border-color: {accent};
}}
QWidget#sidePanel QPushButton#sidebarToggle {{
    background: transparent;
    color: {sidebar_muted};
    border: 1px solid transparent;
    border-radius: 8px;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    padding: 0;
    font-size: 16px;
    font-weight: 800;
}}
QWidget#sidePanel QPushButton#sidebarToggle:hover {{
    background: {sidebar_button_bg};
    color: {sidebar_text};
    border-color: {sidebar_button_border};
}}
QWidget#sidePanel QPushButton#sidebarToggle:focus {{
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
