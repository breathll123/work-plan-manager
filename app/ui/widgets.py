from __future__ import annotations

from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtWidgets import QCalendarWidget, QDateEdit, QToolButton, QWidget

DATE_DISPLAY_FORMAT = "yyyy年M月d日"


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
