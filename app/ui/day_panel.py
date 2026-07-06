from __future__ import annotations

import sqlite3
from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from app.data.models import STATUS_NAMES
from app.services.china_holidays import holiday_reminder_for
from app.services.plan_service import PlanService


class DayPanel(QDialog):
    plan_activated = Signal(int)
    new_plan_requested = Signal(object)

    def __init__(self, conn: sqlite3.Connection, day: date, parent=None):
        super().__init__(parent)
        self.svc = PlanService(conn)
        self.day = day
        self.setWindowTitle(f"{day.year}年{day.month}月{day.day}日 的计划")
        self.setModal(False)
        self.resize(340, 300)
        layout = QVBoxLayout(self)
        self.listw = QListWidget()
        layout.addWidget(self.listw)
        row = QHBoxLayout()
        btn_new = QPushButton("+ 在这天新建")
        btn_new.clicked.connect(lambda: self.new_plan_requested.emit(self.day))
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        row.addWidget(btn_new)
        row.addStretch()
        row.addWidget(btn_close)
        layout.addLayout(row)
        self.listw.itemDoubleClicked.connect(self._open_item)
        self.reload()

    def reload(self) -> None:
        self.listw.clear()
        holiday = holiday_reminder_for(self.day)
        if holiday is not None:
            item = QListWidgetItem(f"[系统提醒] {holiday.title}")
            item.setFlags(Qt.ItemIsEnabled)
            item.setData(Qt.UserRole, None)
            self.listw.addItem(item)
        plans = self.svc.plans.list_overlapping(self.day, self.day)
        if not plans and holiday is None:
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
