from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from app.data.models import Plan
from app.services.china_holidays import HolidayReminder


class ReminderDialog(QDialog):
    plan_activated = Signal(int)

    def __init__(
        self,
        conn: sqlite3.Connection,
        overdue: list[Plan],
        due_today: list[Plan],
        parent=None,
        holiday_reminders: list[HolidayReminder] | None = None,
    ):
        super().__init__(parent)
        holiday_reminders = holiday_reminders or []
        self.setWindowTitle("待办提醒")
        self.resize(380, 340)
        layout = QVBoxLayout(self)
        self.listw = QListWidget()
        if overdue or due_today:
            layout.addWidget(QLabel("双击计划条目可直接打开编辑"))
        else:
            layout.addWidget(QLabel("系统内置提醒"))
        layout.addWidget(self.listw)
        self._add_holiday_group(
            f"中国大陆节假日({len(holiday_reminders)})",
            holiday_reminders,
        )
        self._add_group(f"已逾期({len(overdue)})", overdue, "#D93026")
        self._add_group(f"今日到期({len(due_today)})", due_today, "#BA7517")
        btn = QPushButton("知道了")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)
        self.listw.itemDoubleClicked.connect(self._on_double_click)

    def _add_group(self, title: str, plans: list[Plan], color: str) -> None:
        if not plans:
            return
        header = QListWidgetItem(title)
        header.setFlags(Qt.ItemIsEnabled)
        header.setForeground(QColor(color))
        self.listw.addItem(header)
        for p in plans:
            item = QListWidgetItem(f"    {p.title}({p.end_date.isoformat()} 到期)")
            item.setData(Qt.UserRole, p.id)
            self.listw.addItem(item)

    def _on_double_click(self, item: QListWidgetItem) -> None:
        plan_id = item.data(Qt.UserRole)
        if plan_id is not None:
            self.plan_activated.emit(plan_id)

    def _add_holiday_group(
        self, title: str, holiday_reminders: list[HolidayReminder]
    ) -> None:
        if not holiday_reminders:
            return
        header = QListWidgetItem(title)
        header.setFlags(Qt.ItemIsEnabled)
        header.setForeground(QColor("#C6473A"))
        self.listw.addItem(header)
        for holiday in holiday_reminders:
            item = QListWidgetItem(
                f"    {holiday.title}({holiday.day.isoformat()})"
            )
            item.setFlags(Qt.ItemIsEnabled)
            item.setForeground(QColor("#C6473A"))
            self.listw.addItem(item)
