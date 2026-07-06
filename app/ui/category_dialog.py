from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.services.category_service import CategoryService


class CategoryDialog(QDialog):
    def __init__(self, conn: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.svc = CategoryService(conn)
        self.setWindowTitle("管理分类")
        self.resize(360, 400)
        layout = QVBoxLayout(self)
        self.listw = QListWidget()
        layout.addWidget(self.listw)
        row = QHBoxLayout()
        for text, slot in (
            ("新增", self._add),
            ("重命名", self._rename),
            ("改颜色", self._recolor),
            ("删除", self._delete),
            ("上移", lambda: self._move(-1)),
            ("下移", lambda: self._move(1)),
        ):
            b = QPushButton(text)
            b.clicked.connect(slot)
            row.addWidget(b)
        layout.addLayout(row)
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        self._reload()

    def _reload(self) -> None:
        self.listw.clear()
        for c in self.svc.list_all():
            item = QListWidgetItem(c.name)
            pix = QPixmap(14, 14)
            pix.fill(QColor(c.color))
            item.setIcon(QIcon(pix))
            item.setData(Qt.UserRole, c)
            self.listw.addItem(item)

    def _current(self):
        item = self.listw.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _add(self) -> None:
        name, ok = QInputDialog.getText(self, "新增分类", "分类名称:")
        if not ok:
            return
        color = QColorDialog.getColor(QColor("#4A90D9"), self, "选择颜色")
        if not color.isValid():
            return
        try:
            cat = self.svc.create(name, color.name())
            cat.sort_order = self.listw.count()
            self.svc.update(cat)
        except ValueError as e:
            QMessageBox.warning(self, "无法新增", str(e))
        self._reload()

    def _rename(self) -> None:
        cat = self._current()
        if not cat:
            return
        name, ok = QInputDialog.getText(
            self, "重命名", "分类名称:", text=cat.name
        )
        if not ok:
            return
        cat.name = name
        try:
            self.svc.update(cat)
        except ValueError as e:
            QMessageBox.warning(self, "无法重命名", str(e))
        self._reload()

    def _recolor(self) -> None:
        cat = self._current()
        if not cat:
            return
        color = QColorDialog.getColor(QColor(cat.color), self, "选择颜色")
        if color.isValid():
            cat.color = color.name()
            self.svc.update(cat)
            self._reload()

    def _delete(self) -> None:
        cat = self._current()
        if not cat:
            return
        ans = QMessageBox.question(
            self,
            "删除分类",
            f"删除分类「{cat.name}」?\n其下的计划会变为「未分类」,不会被删除。",
        )
        if ans == QMessageBox.Yes:
            self.svc.delete(cat.id)
            self._reload()

    def _move(self, delta: int) -> None:
        row = self.listw.currentRow()
        target = row + delta
        if row < 0 or not (0 <= target < self.listw.count()):
            return
        cats = self.svc.list_all()
        cats[row], cats[target] = cats[target], cats[row]
        for i, c in enumerate(cats):
            c.sort_order = i
            self.svc.update(c)
        self._reload()
        self.listw.setCurrentRow(target)
