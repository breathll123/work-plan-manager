from __future__ import annotations

import sys
import traceback
from datetime import date

from PySide6.QtWidgets import QApplication, QMessageBox

from app.data.db import app_dir, backup, connect, default_db_path, is_dir_writable
from app.services.reminder_service import get_reminders
from app.services.settings_service import get_theme
from app.ui.main_window import MainWindow
from app.ui.reminder_dialog import ReminderDialog
from app.ui.theme import apply_theme


def _install_excepthook() -> None:
    def hook(exc_type, exc, tb):
        text = "".join(traceback.format_exception(exc_type, exc, tb))
        try:
            log = app_dir() / "error.log"
            with open(log, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except OSError:
            pass
        QMessageBox.critical(
            None,
            "程序出错",
            "发生未预期的错误,详情已写入 error.log。\n\n" + str(exc),
        )

    sys.excepthook = hook


def run() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("工作计划")
    _install_excepthook()
    directory = app_dir()
    if not is_dir_writable(directory):
        QMessageBox.critical(
            None,
            "无法启动",
            "软件所在目录不可写,数据将无法保存。\n"
            "请将软件放到可写目录(不要放在 Program Files)。",
        )
        sys.exit(1)
    db_path = default_db_path()
    backup(db_path)
    conn = connect(db_path)
    apply_theme(app, get_theme(conn))
    win = MainWindow(conn)
    win.show()
    overdue, due_today = get_reminders(conn, date.today())
    if overdue or due_today:
        dlg = ReminderDialog(conn, overdue, due_today, win)
        dlg.plan_activated.connect(win._edit_plan)
        dlg.exec()
        win.refresh_views()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
