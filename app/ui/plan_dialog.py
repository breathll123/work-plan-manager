from __future__ import annotations

import sqlite3
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app import platform_utils
from app.data.models import STATUS_NAMES
from app.services.category_service import CategoryService
from app.services.plan_service import PlanService
from app.ui.widgets import ModernDateEdit


def _to_qdate(d: date) -> QDate:
    return QDate(d.year, d.month, d.day)


class PlanDialog(QDialog):
    def __init__(
        self,
        conn: sqlite3.Connection,
        plan_id: int | None = None,
        default_date: date | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.svc = PlanService(conn)
        self.cat_svc = CategoryService(conn)
        self.plan_id = plan_id
        self.setWindowTitle("编辑计划" if plan_id else "新建计划")
        self.resize(480, 560)
        self._build_form()
        if plan_id:
            self._load(plan_id)
        else:
            d = _to_qdate(default_date or date.today())
            self.start_edit.setDate(d)
            self.end_edit.setDate(d)

    def _build_form(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.title_edit = QLineEdit()
        form.addRow("标题", self.title_edit)
        self.cat_combo = QComboBox()
        self.cat_combo.addItem("未分类", None)
        for c in self.cat_svc.list_all():
            self.cat_combo.addItem(c.name, c.id)
        form.addRow("分类", self.cat_combo)
        self.start_edit = ModernDateEdit()
        self.end_edit = ModernDateEdit()
        dates = QHBoxLayout()
        dates.setSpacing(8)
        dates.addWidget(self.start_edit)
        dates.addWidget(QLabel("至"))
        dates.addWidget(self.end_edit)
        form.addRow("日期", dates)
        self.status_group = QButtonGroup(self)
        self.status_group.setExclusive(True)
        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        for value, name in STATUS_NAMES.items():
            rb = QPushButton(name)
            rb.setCheckable(True)
            rb.setObjectName("statusPill")
            self.status_group.addButton(rb, value)
            status_row.addWidget(rb)
        self.status_group.button(0).setChecked(True)
        form.addRow("状态", status_row)
        self.note_edit = QTextEdit()
        self.note_edit.setFixedHeight(70)
        form.addRow("备注", self.note_edit)
        layout.addLayout(form)
        layout.addWidget(QLabel("绑定文件夹 / 文件"))
        self.links_list = QListWidget()
        layout.addWidget(self.links_list)
        btns = QHBoxLayout()
        for text, slot in (
            ("添加文件夹", self._add_folder),
            ("添加文件", self._add_file),
            ("打开", self._open_selected),
            ("移除", self._remove_selected),
        ):
            b = QPushButton(text)
            b.clicked.connect(slot)
            btns.addWidget(b)
        layout.addLayout(btns)
        footer = QHBoxLayout()
        self.btn_delete = QPushButton("删除计划")
        self.btn_delete.setObjectName("dangerButton")
        self.btn_delete.clicked.connect(self._delete)
        self.btn_delete.setVisible(self.plan_id is not None)
        footer.addWidget(self.btn_delete)
        footer.addStretch()
        cancel = QPushButton("取消")
        cancel.setObjectName("quietButton")
        cancel.clicked.connect(self.reject)
        save = QPushButton("保存")
        save.setObjectName("primaryButton")
        save.setDefault(True)
        save.clicked.connect(self._save)
        footer.addWidget(cancel)
        footer.addWidget(save)
        layout.addLayout(footer)

    def _load(self, plan_id: int) -> None:
        plan, links = self.svc.get_with_links(plan_id)
        self.title_edit.setText(plan.title)
        idx = self.cat_combo.findData(plan.category_id)
        self.cat_combo.setCurrentIndex(max(idx, 0))
        self.start_edit.setDate(_to_qdate(plan.start_date))
        self.end_edit.setDate(_to_qdate(plan.end_date))
        self.status_group.button(plan.status).setChecked(True)
        self.note_edit.setPlainText(plan.note)
        for link in links:
            self._append_path(link.path)

    def _append_path(self, path: str) -> None:
        item = QListWidgetItem(path)
        item.setData(Qt.UserRole, path)
        if not platform_utils.path_exists(path):
            item.setForeground(QColor("#D93026"))
            item.setText(f"{path}  (路径不存在)")
        self.links_list.addItem(item)

    def _add_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if d:
            self._append_path(d)

    def _add_file(self) -> None:
        f, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if f:
            self._append_path(f)

    def _open_selected(self) -> None:
        item = self.links_list.currentItem()
        if not item:
            return
        err = platform_utils.open_path(item.data(Qt.UserRole))
        if err:
            QMessageBox.warning(self, "无法打开", err)

    def _remove_selected(self) -> None:
        row = self.links_list.currentRow()
        if row >= 0:
            self.links_list.takeItem(row)

    def _paths(self) -> list[str]:
        return [
            self.links_list.item(i).data(Qt.UserRole)
            for i in range(self.links_list.count())
        ]

    def _save(self) -> None:
        title = self.title_edit.text()
        start = self.start_edit.date().toPython()
        end = self.end_edit.date().toPython()
        cat_id = self.cat_combo.currentData()
        status = self.status_group.checkedId()
        note = self.note_edit.toPlainText()
        try:
            if self.plan_id is None:
                self.svc.create(
                    title,
                    start,
                    end,
                    category_id=cat_id,
                    note=note,
                    status=status,
                    paths=tuple(self._paths()),
                )
            else:
                plan, _ = self.svc.get_with_links(self.plan_id)
                plan.title, plan.note, plan.category_id = title, note, cat_id
                plan.start_date, plan.end_date = start, end
                plan.status = status
                self.svc.update(plan, paths=self._paths())
        except ValueError as e:
            QMessageBox.warning(self, "无法保存", str(e))
            return
        self.accept()

    def _delete(self) -> None:
        ans = QMessageBox.question(
            self, "删除计划", "确定删除这条计划?绑定路径记录会一并删除。"
        )
        if ans == QMessageBox.Yes:
            self.svc.delete(self.plan_id)
            self.accept()
