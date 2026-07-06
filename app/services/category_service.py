from __future__ import annotations

import sqlite3

from app.data.models import Category
from app.data.repositories import CategoryRepo


def text_color_for(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#000000" if luminance > 150 else "#FFFFFF"


class CategoryService:
    def __init__(self, conn: sqlite3.Connection):
        self.repo = CategoryRepo(conn)

    def create(self, name: str, color: str) -> Category:
        name = name.strip()
        if not name:
            raise ValueError("分类名称不能为空")
        try:
            return self.repo.add(name, color)
        except sqlite3.IntegrityError:
            raise ValueError(f"分类「{name}」已存在") from None

    def update(self, cat: Category) -> None:
        cat.name = cat.name.strip()
        if not cat.name:
            raise ValueError("分类名称不能为空")
        try:
            self.repo.update(cat)
        except sqlite3.IntegrityError:
            raise ValueError(f"分类「{cat.name}」已存在") from None

    def delete(self, cat_id: int) -> None:
        self.repo.delete(cat_id)

    def list_all(self) -> list[Category]:
        return self.repo.list_all()
