from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import platform_utils
from app.data.models import Plan, PlanLink, STATUS_NAMES
from app.services.plan_service import PlanService
from app.services.settings_service import get_theme
from app.services.system_reminders import (
    SystemReminder,
    system_reminder_kind,
    system_reminders_for_day,
)
from app.ui.icons import set_button_icon
from app.ui.theme import colors

ROLE_PLAN_ID = Qt.UserRole
ROLE_ITEM_KIND = Qt.UserRole + 1
ROLE_REMINDER_TITLE = Qt.UserRole + 2
ROLE_REMINDER_TYPE = Qt.UserRole + 3


def _format_day(day: date) -> str:
    return f"{day.year}年{day.month}月{day.day}日"


def _format_range(plan: Plan) -> str:
    if plan.start_date == plan.end_date:
        return _format_day(plan.start_date)
    return f"{_format_day(plan.start_date)} 至 {_format_day(plan.end_date)}"


class DayDetailPanel(QWidget):
    plan_activated = Signal(int)
    new_plan_requested = Signal(object)
    closed = Signal()

    def __init__(self, conn: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.svc = PlanService(conn)
        self.day: date | None = None
        self._selected_plan_id: int | None = None
        self.setObjectName("detailPanel")
        self.setMinimumWidth(330)
        self.setMaximumWidth(390)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(8)
        self.title_label = QLabel("选择日期")
        self.title_label.setObjectName("detailTitle")
        self.title_label.setWordWrap(True)
        header.addWidget(self.title_label, stretch=1)
        self.btn_close = QPushButton()
        self.btn_close.setObjectName("navButton")
        self.btn_close.setToolTip("关闭详情")
        set_button_icon(self.btn_close, "close")
        self.btn_close.clicked.connect(self._close_panel)
        header.addWidget(self.btn_close)
        outer.addLayout(header)

        self.summary_label = QLabel("点击日历中的日期查看当天计划")
        self.summary_label.setObjectName("mutedLabel")
        self.summary_label.setWordWrap(True)
        outer.addWidget(self.summary_label)

        list_label = QLabel("当天计划")
        list_label.setObjectName("detailSection")
        outer.addWidget(list_label)
        self.listw = QListWidget()
        self.listw.setObjectName("dayPlanList")
        self.listw.setMinimumHeight(138)
        self.listw.setMaximumHeight(210)
        self.listw.currentItemChanged.connect(self._render_current_detail)
        self.listw.itemDoubleClicked.connect(self._edit_item)
        outer.addWidget(self.listw)

        self.btn_new = QPushButton("在这天新建")
        self.btn_new.setObjectName("primaryButton")
        set_button_icon(self.btn_new, "plus", color="#FFFFFF")
        self.btn_new.clicked.connect(self._request_new_plan)
        outer.addWidget(self.btn_new)

        detail_label = QLabel("计划详情")
        detail_label.setObjectName("detailSection")
        outer.addWidget(detail_label)
        self.detail_scroll = QScrollArea()
        self.detail_scroll.setObjectName("detailScroll")
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setFrameShape(QFrame.NoFrame)
        self.detail_body = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_body)
        self.detail_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_layout.setSpacing(10)
        self.detail_scroll.setWidget(self.detail_body)
        outer.addWidget(self.detail_scroll, stretch=1)
        self._render_empty("选择一条计划查看详情和绑定文件")

    def show_day(self, day: date) -> None:
        self.day = day
        self.title_label.setText(_format_day(day))
        self.setVisible(True)
        self.reload()
        self.raise_()

    def reload(self) -> None:
        if self.day is None:
            return
        previous_plan_id = self._selected_plan_id
        current = self.listw.currentItem()
        if current is not None and current.data(ROLE_PLAN_ID) is not None:
            previous_plan_id = current.data(ROLE_PLAN_ID)

        self.listw.blockSignals(True)
        self.listw.clear()
        reminders = system_reminders_for_day(self.day)
        plans = self.svc.plans.list_overlapping(self.day, self.day)
        self.summary_label.setText(
            f"{len(plans)} 条计划，{len(reminders)} 条系统提醒"
        )

        theme_colors = colors(get_theme(self.conn))
        for reminder in reminders:
            self._add_reminder_item(reminder, theme_colors)
        for plan in plans:
            self._add_plan_item(plan)
        if not reminders and not plans:
            item = QListWidgetItem("这一天还没有计划")
            item.setFlags(Qt.ItemIsEnabled)
            item.setData(ROLE_ITEM_KIND, "empty")
            self.listw.addItem(item)

        target_row = self._find_plan_row(previous_plan_id)
        if target_row < 0 and self.listw.count():
            target_row = 0
        self.listw.blockSignals(False)

        if target_row >= 0:
            self.listw.setCurrentRow(target_row)
            self._render_current_detail(self.listw.currentItem(), None)
        else:
            self._render_empty("选择一条计划查看详情和绑定文件")

    def _add_reminder_item(
        self, reminder: SystemReminder, theme_colors: dict[str, str]
    ) -> None:
        kind = system_reminder_kind(reminder)
        item = QListWidgetItem(f"系统提醒 · {reminder.title}")
        item.setData(ROLE_ITEM_KIND, "system")
        item.setData(ROLE_REMINDER_TITLE, reminder.title)
        item.setData(ROLE_REMINDER_TYPE, kind)
        item.setForeground(
            QColor(
                theme_colors["holiday_text"]
                if kind == "holiday"
                else theme_colors["solar_term_text"]
            )
        )
        self.listw.addItem(item)

    def _add_plan_item(self, plan: Plan) -> None:
        if plan.id is None:
            return
        item = QListWidgetItem(f"{STATUS_NAMES[plan.status]} · {plan.title}")
        item.setData(ROLE_PLAN_ID, plan.id)
        item.setData(ROLE_ITEM_KIND, "plan")
        self.listw.addItem(item)

    def _find_plan_row(self, plan_id: int | None) -> int:
        if plan_id is None:
            return -1
        for row in range(self.listw.count()):
            if self.listw.item(row).data(ROLE_PLAN_ID) == plan_id:
                return row
        return -1

    def _clear_detail(self) -> None:
        while self.detail_layout.count():
            item = self.detail_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _render_current_detail(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if current is None:
            self._selected_plan_id = None
            self._render_empty("选择一条计划查看详情和绑定文件")
            return
        kind = current.data(ROLE_ITEM_KIND)
        if kind == "plan":
            plan_id = current.data(ROLE_PLAN_ID)
            self._selected_plan_id = plan_id
            self._render_plan(plan_id)
        elif kind == "system":
            self._selected_plan_id = None
            self._render_system(
                current.data(ROLE_REMINDER_TITLE),
                current.data(ROLE_REMINDER_TYPE),
            )
        else:
            self._selected_plan_id = None
            self._render_empty("这一天还没有计划")

    def _render_empty(self, text: str) -> None:
        self._clear_detail()
        card = self._new_card()
        layout = card.layout()
        label = QLabel(text)
        label.setObjectName("emptyDetail")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.detail_layout.addWidget(card)
        self.detail_layout.addStretch()

    def _render_system(self, title: str, kind: str) -> None:
        self._clear_detail()
        card = self._new_card()
        layout = card.layout()
        badge = QLabel("节假日提醒" if kind == "holiday" else "节气提醒")
        badge.setObjectName("detailBadge")
        title_label = QLabel(title)
        title_label.setObjectName("detailPlanTitle")
        title_label.setWordWrap(True)
        body = QLabel("系统默认提醒，当天早上 8 点弹窗。")
        body.setObjectName("mutedLabel")
        body.setWordWrap(True)
        layout.addWidget(badge)
        layout.addWidget(title_label)
        layout.addWidget(body)
        self.detail_layout.addWidget(card)
        self.detail_layout.addStretch()

    def _render_plan(self, plan_id: int) -> None:
        self._clear_detail()
        try:
            plan, links = self.svc.get_with_links(plan_id)
        except ValueError as exc:
            self._render_empty(str(exc))
            return

        card = self._new_card()
        layout = card.layout()
        top = QHBoxLayout()
        status = QLabel(STATUS_NAMES[plan.status])
        status.setObjectName("detailBadge")
        top.addWidget(status)
        top.addStretch()
        edit = QPushButton("编辑")
        edit.setObjectName("linkButton")
        set_button_icon(edit, "open")
        edit.clicked.connect(
            lambda _=False, pid=plan_id: self.plan_activated.emit(pid)
        )
        top.addWidget(edit)
        title = QLabel(plan.title)
        title.setObjectName("detailPlanTitle")
        title.setWordWrap(True)
        date_label = QLabel(_format_range(plan))
        date_label.setObjectName("mutedLabel")
        date_label.setWordWrap(True)
        layout.addLayout(top)
        layout.addWidget(title)
        layout.addWidget(date_label)
        if plan.note.strip():
            note = QLabel(plan.note.strip())
            note.setObjectName("detailNote")
            note.setWordWrap(True)
            layout.addWidget(note)
        self.detail_layout.addWidget(card)

        files_title = QLabel("绑定文件")
        files_title.setObjectName("detailSection")
        self.detail_layout.addWidget(files_title)
        if links:
            for link in links:
                self.detail_layout.addWidget(self._link_row(link))
        else:
            empty = QLabel("这条计划还没有绑定文件或文件夹")
            empty.setObjectName("emptyDetail")
            empty.setWordWrap(True)
            self.detail_layout.addWidget(empty)
        self.detail_layout.addStretch()

    def _new_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("detailCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)
        return card

    def _link_row(self, link: PlanLink) -> QFrame:
        row = QFrame()
        row.setObjectName("linkRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 9, 10, 9)
        layout.setSpacing(8)
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        name = Path(link.path).name or link.path
        title = QLabel(name)
        title.setObjectName("linkTitle")
        title.setWordWrap(True)
        path = QLabel(link.path)
        path.setObjectName("linkPath")
        path.setWordWrap(True)
        text_col.addWidget(title)
        text_col.addWidget(path)
        layout.addLayout(text_col, stretch=1)
        open_btn = QPushButton("打开")
        open_btn.setObjectName("linkButton")
        set_button_icon(open_btn, "open")
        exists = platform_utils.path_exists(link.path)
        open_btn.setEnabled(exists)
        open_btn.clicked.connect(lambda _=False, p=link.path: self._open_path(p))
        if not exists:
            path.setText(f"{link.path}  (路径不存在)")
            path.setObjectName("pathMissing")
            open_btn.setToolTip("路径不存在，无法打开")
        layout.addWidget(open_btn)
        return row

    def _open_path(self, path: str) -> None:
        err = platform_utils.open_path(path)
        if err:
            QMessageBox.warning(self, "无法打开", err)

    def _edit_item(self, item: QListWidgetItem) -> None:
        plan_id = item.data(ROLE_PLAN_ID)
        if plan_id is not None:
            self.plan_activated.emit(plan_id)

    def _request_new_plan(self) -> None:
        if self.day is not None:
            self.new_plan_requested.emit(self.day)

    def _close_panel(self) -> None:
        self.hide()
        self.closed.emit()
