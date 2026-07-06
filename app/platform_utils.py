from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def path_exists(path: str) -> bool:
    return Path(path).exists()


def _launch(path: str) -> None:
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=True)
    else:
        subprocess.run(["xdg-open", path], check=True)


def open_path(path: str) -> str | None:
    if not path_exists(path):
        return f"路径不存在:{path}"
    try:
        _launch(path)
        return None
    except (OSError, subprocess.SubprocessError):
        return f"无法打开:{path}"
