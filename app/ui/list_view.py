from __future__ import annotations

import sqlite3
from datetime import date
from typing import Callable

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.data.models import STATUS_DONE, STATUS_NAMES
from app.services.category_service import CategoryService
from app.services.plan_service import PlanService
from app.ui.widgets import ModernDateEdit

ALL = "ALL"
COLUMNS = ["状态", "标题", "分类", "开始", "结束", "绑定"]
COLUMN_WIDTHS = {
    0: 82,
    2: 116,
    3: 112,
    4: 112,
    5: 72,
}


class ListView(QWidget):
    plan_activated = Signal(int)

    def __init__(
        self, conn: sqlite3.Connection, sidebar_ids: Callable[[], list[int | None]]
    ):
        super().__init__()
        self.svc = PlanService(conn)
        self.cat_svc = CategoryService(conn)
        self.sidebar_ids = sidebar_ids
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        bar_widget = QWidget()
        bar_widget.setObjectName("filterBar")
        bar = QHBoxLayout(bar_widget)
        bar.setContentsMargins(12, 10, 12, 10)
        bar.setSpacing(8)
        self.cat_combo = QComboBox()
        self.cat_combo.setMinimumWidth(128)
        self.status_combo = QComboBox()
        self.status_combo.setMinimumWidth(118)
        self.status_combo.addItem("全部状态", None)
        for value, name in STATUS_NAMES.items():
            self.status_combo.addItem(name, value)
        self.date_check = QCheckBox("按日期筛选")
        self.date_check.setObjectName("dateFilterPill")
        today = date.today()
        self.from_edit = ModernDateEdit()
        self.from_edit.setDate(QDate(today.year, today.month, 1))
        self.to_edit = ModernDateEdit()
        self.to_edit.setDate(QDate(today.year, today.month, 1).addMonths(1).addDays(-1))
        cat_label = QLabel("分类")
        cat_label.setObjectName("fieldLabel")
        status_label = QLabel("状态")
        status_label.setObjectName("fieldLabel")
        bar.addWidget(cat_label)
        bar.addWidget(self.cat_combo)
        bar.addWidget(status_label)
        bar.addWidget(self.status_combo)
        bar.addWidget(self.date_check)
        bar.addWidget(self.from_edit)
        bar.addWidget(QLabel("至"))
        bar.addWidget(self.to_edit)
        bar.addStretch()
        layout.addWidget(bar_widget)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self._configure_table_columns()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)
        for w in (self.cat_combo, self.status_combo):
            w.currentIndexChanged.connect(lambda _: self.refresh())
        self.date_check.toggled.connect(lambda _: self.refresh())
        self.from_edit.dateChanged.connect(lambda _: self.refresh())
        self.to_edit.dateChanged.connect(lambda _: self.refresh())
        self.table.itemDoubleClicked.connect(self._on_double_click)
        self.refresh()

    def _configure_table_columns(self) -> None:
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStretchLastSection(False)
        for col in range(len(COLUMNS)):
            if col == 1:
                header.setSectionResizeMode(col, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.Fixed)
                self.table.setColumnWidth(col, COLUMN_WIDTHS[col])

    def _rebuild_cat_combo(self) -> None:
        current = self.cat_combo.currentData()
        self.cat_combo.blockSignals(True)
        self.cat_combo.clear()
        self.cat_combo.addItem("全部分类", ALL)
        for c in self.cat_svc.list_all():
            self.cat_combo.addItem(c.name, c.id)
        self.cat_combo.addItem("未分类", None)
        idx = self.cat_combo.findData(current)
        self.cat_combo.setCurrentIndex(max(idx, 0))
        self.cat_combo.blockSignals(False)

    def _effective_category_ids(self) -> list[int | None]:
        side = self.sidebar_ids()
        chosen = self.cat_combo.currentData()
        if chosen == ALL:
            return side
        return [chosen] if chosen in side else []

    def refresh(self) -> None:
        self._rebuild_cat_combo()
        kwargs = {"category_ids": self._effective_category_ids()}
        if self.status_combo.currentData() is not None:
            kwargs["status"] = self.status_combo.currentData()
        if self.date_check.isChecked():
            kwargs["date_from"] = self.from_edit.date().toPython()
            kwargs["date_to"] = self.to_edit.date().toPython()
        plans = self.svc.list_filtered(**kwargs)
        cats = {c.id: c for c in self.cat_svc.list_all()}
        today = date.today()
        self.table.setRowCount(len(plans))
        for row, p in enumerate(plans):
            overdue = p.status != STATUS_DONE and p.end_date < today
            status_item = QTableWidgetItem("逾期" if overdue else STATUS_NAMES[p.status])
            if overdue:
                status_item.setForeground(QColor("#D93026"))
            title_item = QTableWidgetItem(p.title)
            if p.status == STATUS_DONE:
                f = title_item.font()
                f.setStrikeOut(True)
                title_item.setFont(f)
            cat = cats.get(p.category_id)
            cat_item = QTableWidgetItem(cat.name if cat else "未分类")
            if cat:
                cat_item.setForeground(QColor(cat.color))
            _, links = self.svc.get_with_links(p.id)
            cells = [
                status_item,
                title_item,
                cat_item,
                QTableWidgetItem(p.start_date.isoformat()),
                QTableWidgetItem(p.end_date.isoformat()),
                QTableWidgetItem(str(len(links)) if links else "-"),
            ]
            for col, item in enumerate(cells):
                item.setData(Qt.UserRole, p.id)
                if col in (3, 4, 5):
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

    def _on_double_click(self, item: QTableWidgetItem) -> None:
        self.plan_activated.emit(item.data(Qt.UserRole))
