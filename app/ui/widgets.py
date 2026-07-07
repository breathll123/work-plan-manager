from __future__ import annotations

from PySide6.QtCore import QDate, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCalendarWidget,
    QComboBox,
    QDateEdit,
    QListView,
    QToolButton,
    QWidget,
)

DATE_DISPLAY_FORMAT = "yyyy年M月d日"


class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(34)
        self.setMaxVisibleItems(10)
        popup = QListView(self)
        popup.setObjectName("comboPopup")
        popup.setUniformItemSizes(True)
        popup.setMouseTracking(True)
        popup.setSpacing(2)
        self.setView(popup)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        self._draw_arrow()

    def _draw_arrow(self) -> None:
        rect = self.rect()
        center_x = rect.right() - 15
        center_y = rect.center().y() + 1
        color = self.palette().highlight().color()
        if not self.isEnabled():
            color = QColor("#9AA4B2")

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(color)
        pen.setWidthF(1.8)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(center_x - 4, center_y - 2, center_x, center_y + 2)
        painter.drawLine(center_x, center_y + 2, center_x + 4, center_y - 2)
        painter.end()


class ModernCalendarWidget(QCalendarWidget):
    """Calendar popup with Chinese year-month order in the navigation header."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFirstDayOfWeek(Qt.Monday)
        self.setGridVisible(False)
        self.currentPageChanged.connect(self._sync_header)
        QTimer.singleShot(0, self._sync_header)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._sync_header()

    def _sync_header(self, *_args) -> None:
        nav = self.findChild(QWidget, "qt_calendar_navigationbar")
        month = self.findChild(QToolButton, "qt_calendar_monthbutton")
        year = self.findChild(QToolButton, "qt_calendar_yearbutton")
        if month is None or year is None:
            return

        month.setText(f"{self.monthShown()}月")
        year.setText(f"{self.yearShown()}年")

        layout = nav.layout() if nav is not None else None
        if layout is None:
            return
        widgets = [
            layout.itemAt(i).widget()
            for i in range(layout.count())
            if layout.itemAt(i).widget() is not None
        ]
        if (
            year in widgets
            and month in widgets
            and widgets.index(year) > widgets.index(month)
        ):
            layout.removeWidget(year)
            widgets = [
                layout.itemAt(i).widget()
                for i in range(layout.count())
                if layout.itemAt(i).widget() is not None
            ]
            layout.insertWidget(widgets.index(month), year)


class ModernDateEdit(QDateEdit):
    def __init__(self, date: QDate | None = None, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDisplayFormat(DATE_DISPLAY_FORMAT)
        self.setMinimumWidth(132)
        self.setMinimumHeight(34)
        self.setCalendarWidget(ModernCalendarWidget(self))
        if date is not None:
            self.setDate(date)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        self._draw_calendar_icon()

    def _draw_calendar_icon(self) -> None:
        rect = self.rect()
        icon_rect = QRect(rect.right() - 23, rect.center().y() - 7, 14, 14)
        if not icon_rect.isValid():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = self.palette().highlight().color()
        if not self.isEnabled():
            color = QColor("#9AA4B2")
        pen = QPen(color)
        pen.setWidthF(1.4)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(icon_rect.adjusted(1, 2, -1, -1), 2, 2)
        painter.drawLine(
            icon_rect.left() + 1,
            icon_rect.top() + 6,
            icon_rect.right() - 1,
            icon_rect.top() + 6,
        )
        painter.drawLine(
            icon_rect.left() + 4,
            icon_rect.top() + 1,
            icon_rect.left() + 4,
            icon_rect.top() + 4,
        )
        painter.drawLine(
            icon_rect.right() - 4,
            icon_rect.top() + 1,
            icon_rect.right() - 4,
            icon_rect.top() + 4,
        )
        painter.end()
