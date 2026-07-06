from __future__ import annotations

import sqlite3
from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from app.data.models import STATUS_NAMES
from app.services.plan_service import PlanService
from app.services.settings_service import get_theme
from app.services.system_reminders import (
    system_reminder_kind,
    system_reminders_for_day,
)
from app.ui.icons import set_button_icon
from app.ui.theme import colors


class DayPanel(QDialog):
    plan_activated = Signal(int)
    new_plan_requested = Signal(object)

    def __init__(self, conn: sqlite3.Connection, day: date, parent=None):
        super().__init__(parent)
        self.svc = PlanService(conn)
        self.conn = conn
        self.day = day
        self.setWindowTitle(f"{day.year}年{day.month}月{day.day}日 的计划")
        self.setModal(False)
        self.resize(340, 300)
        layout = QVBoxLayout(self)
        self.listw = QListWidget()
        layout.addWidget(self.listw)
        row = QHBoxLayout()
        btn_new = QPushButton("在这天新建")
        set_button_icon(btn_new, "plus")
        btn_new.clicked.connect(lambda: self.new_plan_requested.emit(self.day))
        btn_close = QPushButton("关闭")
        set_button_icon(btn_close, "close")
        btn_close.clicked.connect(self.close)
        row.addWidget(btn_new)
        row.addStretch()
        row.addWidget(btn_close)
        layout.addLayout(row)
        self.listw.itemDoubleClicked.connect(self._open_item)
        self.reload()

    def reload(self) -> None:
        self.listw.clear()
        system_reminders = system_reminders_for_day(self.day)
        theme_colors = colors(get_theme(self.conn))
        for reminder in system_reminders:
            item = QListWidgetItem(f"[系统提醒] {reminder.title}")
            item.setFlags(Qt.ItemIsEnabled)
            item.setData(Qt.UserRole, None)
            item.setForeground(
                QColor(
                    theme_colors["holiday_text"]
                    if system_reminder_kind(reminder) == "holiday"
                    else theme_colors["solar_term_text"]
                )
            )
            self.listw.addItem(item)
        plans = self.svc.plans.list_overlapping(self.day, self.day)
        if not plans and not system_reminders:
            self.listw.addItem("这一天还没有计划")
            return
        for p in plans:
            item = QListWidgetItem(f"[{STATUS_NAMES[p.status]}] {p.title}")
            item.setData(Qt.UserRole, p.id)
            self.listw.addItem(item)

    def _open_item(self, item: QListWidgetItem) -> None:
        plan_id = item.data(Qt.UserRole)
        if plan_id is not None:
            self.plan_activated.emit(plan_id)
