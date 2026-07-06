from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Callable

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.data.models import STATUS_DONE
from app.services.category_service import CategoryService, text_color_for
from app.services.china_holidays import china_mainland_holiday, holiday_reminder_for
from app.services.plan_service import PlanService, month_grid_range
from app.services.settings_service import get_theme
from app.ui.theme import colors

OUTER_PAD = 14
HEADER_H = 38
DAY_NUM_H = 28
BAR_H = 17
BAR_GAP = 2
MAX_LANES = 4
UNCAT_COLOR = "#888888"
WEEKDAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")


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
        page = self.rect().adjusted(OUTER_PAD, OUTER_PAD, -OUTER_PAD, -OUTER_PAD)
        painter.setPen(QColor(c["border"]))
        painter.setBrush(QColor(c["paper"]))
        painter.drawRoundedRect(page, 10, 10)
        cell_w = page.width() / 7
        rows = max(len(self._weeks), 1)
        cell_h = (page.height() - HEADER_H) / rows
        left = page.left()
        header_top = page.top()
        grid_top = page.top() + HEADER_H
        self._plan_hits = []
        self._day_cells = []
        header_font = painter.font()
        header_font.setBold(True)
        original_point_size = header_font.pointSize()
        if original_point_size > 0:
            header_font.setPointSize(original_point_size + 1)
        painter.setFont(header_font)
        painter.setPen(QColor(c["muted"]))
        for i, name in enumerate(WEEKDAYS):
            if i >= 5:
                painter.setPen(QColor(c["cal_overdue"]))
            else:
                painter.setPen(QColor(c["muted"]))
            painter.drawText(
                QRect(int(left + i * cell_w), header_top, int(cell_w), HEADER_H),
                Qt.AlignCenter,
                name,
            )
        header_font.setBold(False)
        if original_point_size > 0:
            header_font.setPointSize(original_point_size)
        painter.setFont(header_font)
        for wi, week in enumerate(self._weeks):
            y = int(grid_top + wi * cell_h)
            for di, day in enumerate(week):
                x = int(left + di * cell_w)
                rect = QRect(x, y, int(cell_w), int(cell_h))
                self._day_cells.append((rect, day))
                if di >= 5:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(c["cal_weekend_bg"]))
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))
                elif (wi + di) % 2 == 0:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(c["paper_alt"]))
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))
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
                holiday = china_mainland_holiday(day)
                if holiday is not None:
                    label_rect = QRect(x + 6, y + 6, int(cell_w) - 42, 18)
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(c["holiday_bg"]))
                    painter.drawRoundedRect(label_rect, 7, 7)
                    painter.setPen(QColor(c["cal_overdue"]))
                    painter.drawText(
                        label_rect.adjusted(6, 0, -6, 0),
                        Qt.AlignCenter,
                        painter.fontMetrics().elidedText(
                            holiday.name, Qt.ElideRight, label_rect.width()
                        ),
                    )
            self._draw_week_bars(
                painter, c, week, wi, left, grid_top, cell_w, cell_h, today
            )
        painter.end()

    def _draw_week_bars(
        self, painter, c, week, wi, left, grid_top, cell_w, cell_h, today
    ) -> None:
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
        holiday_spans = self._holiday_spans(week)
        if holiday_spans:
            lanes.append([])
            for c0, c1, name in holiday_spans:
                lanes[0].append((c0, c1))
                self._draw_holiday_bar(
                    painter, c, wi, left, grid_top, cell_w, cell_h, c0, c1, name
                )
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
            y = int(grid_top + wi * cell_h + DAY_NUM_H + 6 + lane * (BAR_H + BAR_GAP))
            x = int(left + c0 * cell_w) + 4
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
                        int(left + col * cell_w) + 5,
                        int(grid_top + wi * cell_h + cell_h) - 16,
                        int(cell_w) - 10,
                        14,
                    ),
                    Qt.AlignLeft,
                    f"+{n} 更多",
                )

    def _holiday_spans(self, week: list[date]) -> list[tuple[int, int, str]]:
        spans: list[tuple[int, int, str]] = []
        i = 0
        while i < len(week):
            holiday = holiday_reminder_for(week[i])
            if holiday is None:
                i += 1
                continue
            start = i
            name = holiday.name
            while i + 1 < len(week):
                next_holiday = holiday_reminder_for(week[i + 1])
                if next_holiday is None or next_holiday.name != name:
                    break
                i += 1
            spans.append((start, i, name))
            i += 1
        return spans

    def _draw_holiday_bar(
        self, painter, c, wi, left, grid_top, cell_w, cell_h, c0, c1, name
    ) -> None:
        y = int(grid_top + wi * cell_h + DAY_NUM_H + 6)
        x = int(left + c0 * cell_w) + 4
        w = int((c1 - c0 + 1) * cell_w) - 6
        rect = QRect(x, y, w, BAR_H)
        painter.setPen(QColor(c["cal_overdue"]))
        painter.setBrush(QColor(c["holiday_bg"]))
        painter.drawRoundedRect(rect, 3, 3)
        painter.setPen(QColor(c["cal_overdue"]))
        text_rect = rect.adjusted(6, 0, -6, 0)
        painter.drawText(
            text_rect,
            Qt.AlignVCenter | Qt.AlignLeft,
            painter.fontMetrics().elidedText(
                f"节假日 · {name}", Qt.ElideRight, text_rect.width()
            ),
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
