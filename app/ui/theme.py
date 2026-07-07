from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

# 配色主题「宣纸墨砚」:
# 浅色 = 暖纸底 + 墨色文字 + 竹青主色;深色 = 墨炭底 + 青瓷主色。
# 语义色保持:红 = 逾期/节假日,青蓝 = 节气,琥珀 = 系统提醒。
COLORS = {
    "light": {
        "window": "#F6F2E9",
        "surface": "#FDFBF5",
        "base": "#FDFBF5",
        "paper": "#FDFBF5",
        "paper_alt": "#F0EBDD",
        "sidebar": "#FDFBF5",
        "sidebar_text": "#33312B",
        "sidebar_muted": "#8A8471",
        "sidebar_button_bg": "#F2EDDF",
        "sidebar_button_border": "#DCD4BE",
        "text": "#33312B",
        "muted": "#8A8471",
        "border": "#E1DAC6",
        "border_strong": "#C6BCA1",
        "accent": "#2E7D6B",
        "accent_deep": "#1E5D4E",
        "accent_soft": "#D5E8DF",
        "accent_faint": "#EBF3EE",
        "on_accent": "#FFFFFF",
        "hover": "#F0EADC",
        "sel_bg": "#D5E8DF",
        "cal_grid": "#DFD7C2",
        "cal_out": "#B3AC98",
        "cal_today": "#2E7D6B",
        "cal_today_bg": "#E6F1EA",
        "cal_overdue": "#C24732",
        "cal_done_bg": "#EAE3D2",
        "cal_done_text": "#9B937E",
        "cal_weekend_bg": "#F8EEDC",
        "holiday_bg": "#F6DFD3",
        "holiday_text": "#AE3A24",
        "solar_term_bg": "#DFEAEC",
        "solar_term_text": "#366F7D",
        "system_bar_bg": "#B67A1C",
        "system_bar_text": "#FFF6E2",
        "danger": "#C24732",
        "danger_soft": "#F6DFD3",
        "warning": "#9C6716",
    },
    "dark": {
        "window": "#1F2321",
        "surface": "#282D2A",
        "base": "#282D2A",
        "paper": "#252A27",
        "paper_alt": "#303632",
        "sidebar": "#282D2A",
        "sidebar_text": "#ECE7DA",
        "sidebar_muted": "#A49E8D",
        "sidebar_button_bg": "#333936",
        "sidebar_button_border": "#4A524D",
        "text": "#ECE7DA",
        "muted": "#A09A89",
        "border": "#3B423E",
        "border_strong": "#545C56",
        "accent": "#7CC3AD",
        "accent_deep": "#A6DBC7",
        "accent_soft": "#2C473F",
        "accent_faint": "#293632",
        "on_accent": "#14251F",
        "hover": "#313734",
        "sel_bg": "#2C473F",
        "cal_grid": "#3A403C",
        "cal_out": "#6F6B5E",
        "cal_today": "#7CC3AD",
        "cal_today_bg": "#263630",
        "cal_overdue": "#E4735B",
        "cal_done_bg": "#323733",
        "cal_done_text": "#8A8577",
        "cal_weekend_bg": "#2E2C24",
        "holiday_bg": "#452F29",
        "holiday_text": "#F09F8C",
        "solar_term_bg": "#283F45",
        "solar_term_text": "#8FC6D2",
        "system_bar_bg": "#6D4A13",
        "system_bar_text": "#FFC862",
        "danger": "#E4735B",
        "danger_soft": "#44302A",
        "warning": "#D8A64F",
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
    color: {on_accent};
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
    color: {on_accent};
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
    color: {on_accent};
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
QComboBox:on {{
    border-color: {accent};
    background: {accent_faint};
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
QComboBox::drop-down:hover {{
    background: {accent_soft};
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
QListView#comboPopup {{
    background: {surface};
    color: {text};
    border: 1px solid {border_strong};
    border-radius: 12px;
    padding: 6px;
    outline: none;
    selection-background-color: {accent_faint};
    selection-color: {accent_deep};
}}
QListView#comboPopup::item {{
    min-height: 30px;
    padding: 7px 10px;
    border-radius: 8px;
}}
QListView#comboPopup::item:hover {{
    background: {hover};
    color: {text};
}}
QListView#comboPopup::item:selected {{
    background: {accent_faint};
    color: {accent_deep};
    font-weight: 800;
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
    color: {on_accent};
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
QScrollBar:vertical {{
    background: transparent;
    width: 12px;
    margin: 4px 2px 4px 2px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {border_strong};
    min-height: 34px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {muted};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
    border: none;
    background: transparent;
}}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 12px;
    margin: 2px 4px 2px 4px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {border_strong};
    min-width: 34px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {muted};
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
    border: none;
    background: transparent;
}}
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background: transparent;
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


def system_color_scheme() -> str:
    """读取操作系统当前的深浅色偏好,读不到时按浅色处理。"""
    app = QApplication.instance()
    if app is None:
        return "light"
    try:
        scheme = app.styleHints().colorScheme()
    except AttributeError:
        return "light"
    return "dark" if scheme == Qt.ColorScheme.Dark else "light"


def resolve_theme(name: str) -> str:
    """把主题设置(system/light/dark)解析成实际生效的 light/dark。"""
    return system_color_scheme() if name == "system" else name


def colors(name: str) -> dict[str, str]:
    return COLORS.get(resolve_theme(name), COLORS["light"])


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
    pal.setColor(QPalette.HighlightedText, QColor(c["on_accent"]))
    app.setPalette(pal)
    app.setStyleSheet(QSS.format(**c))
