from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Callable

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.data.models import STATUS_DONE
from app.services.category_service import CategoryService
from app.services.plan_service import PlanService
from app.services.settings_service import get_theme
from app.ui.theme import colors

MONTH_NAMES = (
    "一月",
    "二月",
    "三月",
    "四月",
    "五月",
    "六月",
    "七月",
    "八月",
    "九月",
    "十月",
    "十一月",
    "十二月",
)
WEEKDAYS = ("日", "一", "二", "三", "四", "五", "六")
UNCAT_COLOR = "#888888"


class YearView(QWidget):
    day_clicked = Signal(object)
    day_double_clicked = Signal(object)

    def __init__(
        self,
        conn: sqlite3.Connection,
        sidebar_ids: Callable[[], list[int | None]],
        current_year: Callable[[], int],
    ):
        super().__init__()
        self.conn = conn
        self.svc = PlanService(conn)
        self.cat_svc = CategoryService(conn)
        self.sidebar_ids = sidebar_ids
        self.current_year = current_year
        self._day_marks: dict[date, list[str]] = {}
        self._day_cells: list[tuple[QRect, date]] = []
        self.setMinimumSize(760, 520)
        self.refresh()

    def refresh(self) -> None:
        year = self.current_year()
        allowed = set(self.sidebar_ids())
        plans = self.svc.list_filtered(
            category_ids=list(allowed),
            date_from=date(year, 1, 1),
            date_to=date(year, 12, 31),
        )
        cat_colors = {c.id: c.color for c in self.cat_svc.list_all()}
        marks: dict[date, list[str]] = {}
        start_year = date(year, 1, 1)
        end_year = date(year, 12, 31)
        for plan in plans:
            if plan.status == STATUS_DONE:
                color = colors(get_theme(self.conn))["cal_done_text"]
            else:
                color = cat_colors.get(plan.category_id, UNCAT_COLOR)
            current = max(plan.start_date, start_year)
            end = min(plan.end_date, end_year)
            while current <= end:
                day_colors = marks.setdefault(current, [])
                if color not in day_colors:
                    day_colors.append(color)
                current += timedelta(days=1)
        self._day_marks = marks
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = colors(get_theme(self.conn))
        self._day_cells = []
        page = self.rect().adjusted(0, 0, -1, -1)
        painter.setPen(QColor(c["border"]))
        painter.setBrush(QColor(c["paper"]))
        painter.drawRoundedRect(page, 14, 14)

        gap_x = 24
        gap_y = 26
        month_w = (page.width() - gap_x * 3) / 4
        month_h = (page.height() - gap_y * 2) / 3
        year = self.current_year()
        for month in range(1, 13):
            row = (month - 1) // 4
            col = (month - 1) % 4
            rect = QRect(
                int(page.left() + col * (month_w + gap_x)),
                int(page.top() + row * (month_h + gap_y)),
                int(month_w),
                int(month_h),
            )
            self._draw_month(painter, c, year, month, rect)
        painter.end()

    def _draw_month(
        self, painter: QPainter, c: dict[str, str], year: int, month: int, rect: QRect
    ) -> None:
        title_font = QFont(painter.font())
        title_font.setBold(True)
        title_font.setPointSize(max(title_font.pointSize() + 3, 14))
        painter.setFont(title_font)
        painter.setPen(QColor(c["accent_deep"]))
        painter.drawText(
            rect.left(),
            rect.top(),
            rect.width(),
            28,
            Qt.AlignLeft,
            MONTH_NAMES[month - 1],
        )

        body_font = QFont(painter.font())
        body_font.setBold(True)
        body_font.setPointSize(max(body_font.pointSize() - 3, 9))
        painter.setFont(body_font)
        header_y = rect.top() + 40
        grid_top = header_y + 22
        cell_w = rect.width() / 7
        cell_h = max((rect.height() - 62) / 6, 16)

        painter.setPen(QColor(c["muted"]))
        for i, name in enumerate(WEEKDAYS):
            painter.setPen(QColor(c["warning"] if i in (0, 6) else c["muted"]))
            painter.drawText(
                QRect(int(rect.left() + i * cell_w), header_y, int(cell_w), 18),
                Qt.AlignCenter,
                name,
            )

        today = date.today()
        first = date(year, month, 1)
        start = first - timedelta(days=(first.weekday() + 1) % 7)
        for index in range(42):
            day = start + timedelta(days=index)
            row = index // 7
            col = index % 7
            cell = QRect(
                int(rect.left() + col * cell_w),
                int(grid_top + row * cell_h),
                int(cell_w),
                int(cell_h),
            )
            self._day_cells.append((cell, day))
            in_month = day.month == month
            is_weekend = col in (0, 6)
            is_today = day == today and in_month
            if is_weekend:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(c["cal_weekend_bg"]))
                painter.drawRoundedRect(cell.adjusted(1, 1, -1, -1), 4, 4)
            if is_today:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(c["cal_today_bg"]))
                today_rect = cell.adjusted(1, 0, -1, 0)
                painter.drawRoundedRect(today_rect, 6, 6)
                pen = QPen(QColor(c["cal_today"]))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(today_rect, 6, 6)
                painter.setPen(QColor(c["accent_deep"]))
            else:
                painter.setPen(QColor(c["text"] if in_month else c["cal_out"]))
            painter.drawText(
                cell.adjusted(0, 0, 0, -5),
                Qt.AlignCenter,
                str(day.day),
            )

            marks = self._day_marks.get(day, [])
            if in_month and marks:
                line_count = min(len(marks), 3)
                total_w = min(cell.width() - 6, 18)
                line_w = total_w / line_count
                y = cell.bottom() - 4
                for i, color in enumerate(marks[:3]):
                    x1 = int(cell.center().x() - total_w / 2 + i * line_w)
                    x2 = int(x1 + line_w - 2)
                    painter.setPen(QPen(QColor(color), 2, Qt.SolidLine, Qt.RoundCap))
                    painter.drawLine(x1, y, x2, y)

    def _hit_day(self, pos) -> date | None:
        for rect, day in self._day_cells:
            if rect.contains(pos):
                return day
        return None

    def mousePressEvent(self, event) -> None:
        day = self._hit_day(event.position().toPoint())
        if day is not None:
            self.day_clicked.emit(day)

    def mouseDoubleClickEvent(self, event) -> None:
        day = self._hit_day(event.position().toPoint())
        if day is not None:
            self.day_double_clicked.emit(day)
