from __future__ import annotations

import sqlite3
from datetime import date

from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.services.category_service import CategoryService
from app.services.plan_service import PlanService
from app.services.settings_service import get_theme, set_theme
from app.ui.icons import app_icon, set_button_icon
from app.ui.theme import apply_theme

UNCATEGORIZED = None


class MainWindow(QMainWindow):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn
        self.cat_svc = CategoryService(conn)
        self.plan_svc = PlanService(conn)
        today = date.today()
        self.current_year, self.current_month = today.year, today.month
        self.setWindowTitle("工作计划")
        self.setWindowIcon(app_icon())
        self.resize(1000, 680)
        self._day_panels = []
        self._build_toolbar()
        self._build_body()
        self.refresh_categories()
        self._update_month_label()
        self.refresh_views()
        self.btn_manage_cats.clicked.connect(self._open_category_dialog)
        self.btn_new.clicked.connect(self._new_plan)

    def _build_toolbar(self) -> None:
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self.btn_prev = QPushButton("‹")
        self.btn_next = QPushButton("›")
        for b in (self.btn_prev, self.btn_next):
            b.setObjectName("navButton")
        self.btn_today = QPushButton("今天")
        self.btn_today.setObjectName("subtleButton")
        self.month_label = QLabel()
        self.month_label.setObjectName("monthTitle")
        self.btn_cal = QPushButton("月历")
        self.btn_list = QPushButton("列表")
        self.btn_year = QPushButton("年")
        for b in (self.btn_cal, self.btn_list, self.btn_year):
            b.setCheckable(True)
            b.setObjectName("segmentButton")
        self.btn_cal.setChecked(True)
        self.btn_new = QPushButton("新建计划")
        self.btn_new.setObjectName("primaryButton")
        self.btn_theme = QPushButton()
        self.btn_theme.setObjectName("quietButton")
        self.toolbar.addWidget(self.btn_prev)
        self.toolbar.addWidget(self.month_label)
        self.toolbar.addWidget(self.btn_next)
        self.toolbar.addWidget(self.btn_today)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(self.btn_cal)
        self.toolbar.addWidget(self.btn_list)
        self.toolbar.addWidget(self.btn_year)
        self.toolbar.addWidget(self.btn_new)
        self.toolbar.addWidget(self.btn_theme)
        set_button_icon(self.btn_today, "calendar")
        set_button_icon(self.btn_cal, "calendar")
        set_button_icon(self.btn_list, "list")
        set_button_icon(self.btn_year, "year")
        set_button_icon(self.btn_new, "plus", color="#FFFFFF")
        self.btn_prev.clicked.connect(lambda: self._shift_month(-1))
        self.btn_next.clicked.connect(lambda: self._shift_month(1))
        self.btn_today.clicked.connect(self._goto_today)
        self.btn_cal.clicked.connect(lambda: self._switch_view(0))
        self.btn_list.clicked.connect(lambda: self._switch_view(1))
        self.btn_year.clicked.connect(lambda: self._switch_view(2))
        self.btn_theme.clicked.connect(self._toggle_theme)
        self._sync_theme_button()

    def _build_body(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 10, 10)
        layout.setSpacing(10)
        side = QWidget()
        side.setObjectName("sidePanel")
        side.setFixedWidth(190)
        self.side_layout = QVBoxLayout(side)
        self.side_layout.setContentsMargins(16, 18, 16, 16)
        self.side_layout.setSpacing(10)
        cap = QLabel("分类筛选")
        cap.setObjectName("mutedLabel")
        self.side_layout.addWidget(cap)
        self.cat_box_container = QVBoxLayout()
        self.side_layout.addLayout(self.cat_box_container)
        self.side_layout.addStretch()
        self.btn_manage_cats = QPushButton("管理分类")
        self.btn_manage_cats.setObjectName("sidebarButton")
        set_button_icon(self.btn_manage_cats, "tag")
        self.side_layout.addWidget(self.btn_manage_cats)
        self.view_stack = QStackedWidget()
        from app.ui.calendar_view import CalendarView
        from app.ui.list_view import ListView
        from app.ui.year_view import YearView

        self.calendar_view = CalendarView(
            self.conn,
            self.selected_category_ids,
            lambda: (self.current_year, self.current_month),
        )
        self.calendar_view.plan_clicked.connect(self._edit_plan)
        self.calendar_view.day_clicked.connect(self._show_day_panel)
        self.calendar_view.day_double_clicked.connect(self._new_plan_on)
        self.view_stack.addWidget(self.calendar_view)
        self.list_view = ListView(self.conn, self.selected_category_ids)
        self.list_view.plan_activated.connect(self._edit_plan)
        self.view_stack.addWidget(self.list_view)
        self.year_view = YearView(
            self.conn,
            self.selected_category_ids,
            lambda: self.current_year,
        )
        self.year_view.day_clicked.connect(self._show_day_panel)
        self.year_view.day_double_clicked.connect(self._new_plan_on)
        self.view_stack.addWidget(self.year_view)
        layout.addWidget(side)
        layout.addWidget(self.view_stack, stretch=1)
        self.setCentralWidget(root)

    def _switch_view(self, index: int) -> None:
        self.btn_cal.setChecked(index == 0)
        self.btn_list.setChecked(index == 1)
        self.btn_year.setChecked(index == 2)
        self.view_stack.setCurrentIndex(index)
        self._update_month_label()
        self.refresh_views()

    def _shift_month(self, delta: int) -> None:
        if self._current_view_index() == 2:
            self.current_year += delta
            self._update_month_label()
            self.refresh_views()
            return
        m = self.current_month + delta
        if m == 0:
            self.current_year, self.current_month = self.current_year - 1, 12
        elif m == 13:
            self.current_year, self.current_month = self.current_year + 1, 1
        else:
            self.current_month = m
        self._update_month_label()
        self.refresh_views()

    def _goto_today(self) -> None:
        today = date.today()
        self.current_year, self.current_month = today.year, today.month
        self._update_month_label()
        self.refresh_views()

    def _update_month_label(self) -> None:
        if self._current_view_index() == 2:
            self.month_label.setText(f"{self.current_year}年")
        else:
            self.month_label.setText(f"{self.current_year}年{self.current_month}月")

    def _current_view_index(self) -> int:
        stack = getattr(self, "view_stack", None)
        return stack.currentIndex() if stack is not None else 0

    def refresh_categories(self) -> None:
        checked = {}
        while self.cat_box_container.count():
            item = self.cat_box_container.takeAt(0)
            w = item.widget()
            if w is not None:
                checked[w.property("cat_id")] = w.isChecked()
                w.deleteLater()
        self._cat_boxes: list[QCheckBox] = []
        entries = [(c.id, c.name, c.color) for c in self.cat_svc.list_all()]
        entries.append((UNCATEGORIZED, "未分类", "#888888"))
        for cid, name, color in entries:
            box = QCheckBox(name)
            box.setObjectName("categoryChip")
            box.setProperty("cat_id", cid)
            box.setChecked(checked.get(cid, True))
            box.setStyleSheet(
                f"QCheckBox::indicator {{ width: 12px; height: 12px;"
                f" border: 1px solid {color}; border-radius: 3px; }}"
                f"QCheckBox::indicator:checked {{ background: {color}; }}"
            )
            box.toggled.connect(lambda _=False: self.refresh_views())
            self.cat_box_container.addWidget(box)
            self._cat_boxes.append(box)

    def selected_category_ids(self) -> list[int | None]:
        boxes = getattr(self, "_cat_boxes", [])
        return [b.property("cat_id") for b in boxes if b.isChecked()]

    def refresh_views(self) -> None:
        views = (
            getattr(self, "calendar_view", None),
            getattr(self, "list_view", None),
            getattr(self, "year_view", None),
        )
        for view in views:
            if hasattr(view, "refresh"):
                view.refresh()
        for panel in list(self._day_panels):
            if panel.isVisible():
                panel.reload()
            else:
                self._day_panels.remove(panel)

    def _toggle_theme(self) -> None:
        new = "dark" if get_theme(self.conn) == "light" else "light"
        set_theme(self.conn, new)
        from PySide6.QtWidgets import QApplication

        apply_theme(QApplication.instance(), new)
        self._sync_theme_button()
        self.refresh_views()

    def _sync_theme_button(self) -> None:
        dark = get_theme(self.conn) == "dark"
        self.btn_theme.setText("浅色" if dark else "深色")
        set_button_icon(self.btn_theme, "sun" if dark else "moon")

    def _open_category_dialog(self) -> None:
        from app.ui.category_dialog import CategoryDialog

        CategoryDialog(self.conn, self).exec()
        self.refresh_categories()
        self.refresh_views()

    def _new_plan(self) -> None:
        from app.ui.plan_dialog import PlanDialog

        PlanDialog(self.conn, parent=self).exec()
        self.refresh_views()

    def _new_plan_on(self, day: date) -> None:
        from app.ui.plan_dialog import PlanDialog

        PlanDialog(self.conn, default_date=day, parent=self).exec()
        self.refresh_views()

    def _edit_plan(self, plan_id: int) -> None:
        from app.ui.plan_dialog import PlanDialog

        PlanDialog(self.conn, plan_id=plan_id, parent=self).exec()
        self.refresh_views()

    def _show_day_panel(self, day: date) -> None:
        from app.ui.day_panel import DayPanel

        panel = DayPanel(self.conn, day, self)
        panel.plan_activated.connect(self._edit_plan)
        panel.plan_activated.connect(panel.reload)
        panel.new_plan_requested.connect(self._new_plan_on)
        panel.new_plan_requested.connect(lambda _: panel.reload())
        panel.show()
        self._day_panels.append(panel)
