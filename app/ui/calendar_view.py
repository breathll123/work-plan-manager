from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Callable

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.data.models import STATUS_DONE
from app.services.category_service import CategoryService, text_color_for
from app.services.plan_service import PlanService, month_grid_range
from app.services.settings_service import get_theme
from app.ui.theme import colors

HEADER_H = 26
DAY_NUM_H = 18
BAR_H = 17
BAR_GAP = 2
MAX_LANES = 3
UNCAT_COLOR = "#888888"
WEEKDAYS = "一二三四五六日"


class CalendarView(QWidget):
    plan_clicked = Signal(int)
    day_clicked = Signal(object)
    day_double_clicked = Signal(object)

    def __init__(
        self,
        conn: sqlite3.Connection,
        sidebar_ids: Callable[[], list[int | None]],
        current_month: Callable[[], tuple[int, int]],
    ):
        super().__init__()
        self.conn = conn
        self.svc = PlanService(conn)
        self.cat_svc = CategoryService(conn)
        self.sidebar_ids = sidebar_ids
        self.current_month = current_month
        self.setMinimumSize(560, 420)
        self._weeks: list[list[date]] = []
        self._plans = []
        self._cat_colors: dict[int | None, str] = {}
        self._plan_hits: list[tuple[QRect, int]] = []
        self._day_cells: list[tuple[QRect, date]] = []
        self.refresh()

    def refresh(self) -> None:
        year, month = self.current_month()
        start, end = month_grid_range(year, month)
        days = []
        d = start
        while d <= end:
            days.append(d)
            d += timedelta(days=1)
        self._weeks = [days[i : i + 7] for i in range(0, len(days), 7)]
        allowed = set(self.sidebar_ids())
        self._plans = [
            p for p in self.svc.plans_for_month(year, month) if p.category_id in allowed
        ]
        self._cat_colors = {c.id: c.color for c in self.cat_svc.list_all()}
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = colors(get_theme(self.conn))
        _, month = self.current_month()
        today = date.today()
        cell_w = self.width() / 7
        rows = max(len(self._weeks), 1)
        cell_h = (self.height() - HEADER_H) / rows
        self._plan_hits = []
        self._day_cells = []
        painter.setPen(QColor(c["muted"]))
        for i, name in enumerate(WEEKDAYS):
            painter.drawText(
                QRect(int(i * cell_w), 0, int(cell_w), HEADER_H),
                Qt.AlignCenter,
                name,
            )
        for wi, week in enumerate(self._weeks):
            y = int(HEADER_H + wi * cell_h)
            for di, day in enumerate(week):
                x = int(di * cell_w)
                rect = QRect(x, y, int(cell_w), int(cell_h))
                self._day_cells.append((rect, day))
                painter.setPen(QColor(c["cal_grid"]))
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(rect)
                if day == today:
                    pen = QPen(QColor(c["cal_today"]))
                    pen.setWidth(2)
                    painter.setPen(pen)
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))
                in_month = day.month == month
                painter.setPen(QColor(c["text"] if in_month else c["cal_out"]))
                painter.drawText(
                    QRect(x, y + 2, int(cell_w) - 6, DAY_NUM_H),
                    Qt.AlignRight | Qt.AlignTop,
                    str(day.day),
                )
            self._draw_week_bars(painter, c, week, wi, cell_w, cell_h, today)
        painter.end()

    def _draw_week_bars(self, painter, c, week, wi, cell_w, cell_h, today) -> None:
        week_start, week_end = week[0], week[-1]
        wplans = sorted(
            (
                p
                for p in self._plans
                if p.start_date <= week_end and p.end_date >= week_start
            ),
            key=lambda p: (p.start_date, p.id),
        )
        lanes: list[list[tuple[int, int]]] = []
        overflow = [0] * 7
        for plan in wplans:
            c0 = max((plan.start_date - week_start).days, 0)
            c1 = min((plan.end_date - week_start).days, 6)
            lane = None
            for li, spans in enumerate(lanes):
                if all(c1 < a or b < c0 for a, b in spans):
                    lane = li
                    break
            if lane is None:
                if len(lanes) >= MAX_LANES:
                    for col in range(c0, c1 + 1):
                        overflow[col] += 1
                    continue
                lanes.append([])
                lane = len(lanes) - 1
            lanes[lane].append((c0, c1))
            y = int(HEADER_H + wi * cell_h + DAY_NUM_H + 4 + lane * (BAR_H + BAR_GAP))
            x = int(c0 * cell_w) + 3
            w = int((c1 - c0 + 1) * cell_w) - 6
            rect = QRect(x, y, w, BAR_H)
            color = self._cat_colors.get(plan.category_id, UNCAT_COLOR)
            done = plan.status == STATUS_DONE
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(c["cal_done_bg"]) if done else QColor(color))
            painter.drawRoundedRect(rect, 3, 3)
            font = painter.font()
            font.setStrikeOut(done)
            painter.setFont(font)
            painter.setPen(
                QColor(c["cal_done_text"] if done else text_color_for(color))
            )
            text_rect = rect.adjusted(5, 0, -14, 0)
            painter.drawText(
                text_rect,
                Qt.AlignVCenter | Qt.AlignLeft,
                painter.fontMetrics().elidedText(
                    plan.title, Qt.ElideRight, text_rect.width()
                ),
            )
            font.setStrikeOut(False)
            painter.setFont(font)
            if not done and plan.end_date < today:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(c["cal_overdue"]))
                painter.drawEllipse(rect.right() - 10, rect.top() + 5, 7, 7)
            self._plan_hits.append((rect, plan.id))
        painter.setPen(QColor(c["muted"]))
        for col, n in enumerate(overflow):
            if n:
                painter.drawText(
                    QRect(
                        int(col * cell_w) + 5,
                        int(HEADER_H + wi * cell_h + cell_h) - 16,
                        int(cell_w) - 10,
                        14,
                    ),
                    Qt.AlignLeft,
                    f"+{n} 更多",
                )

    def _hit_plan(self, pos) -> int | None:
        for rect, plan_id in self._plan_hits:
            if rect.contains(pos):
                return plan_id
        return None

    def _hit_day(self, pos) -> date | None:
        for rect, day in self._day_cells:
            if rect.contains(pos):
                return day
        return None

    def mousePressEvent(self, event) -> None:
        pos = event.position().toPoint()
        plan_id = self._hit_plan(pos)
        if plan_id is not None:
            self.plan_clicked.emit(plan_id)
            return
        day = self._hit_day(pos)
        if day is not None:
            self.day_clicked.emit(day)

    def mouseDoubleClickEvent(self, event) -> None:
        pos = event.position().toPoint()
        if self._hit_plan(pos) is None:
            day = self._hit_day(pos)
            if day is not None:
                self.day_double_clicked.emit(day)
