from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

ICON_COLOR = "#1D4ED8"


def icon(name: str, color: str = ICON_COLOR, size: int = 18) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor(color))
    pen.setWidthF(max(1.6, size / 12))
    pen.setStyle(Qt.SolidLine)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    s = size

    if name == "plus":
        p.drawLine(QPoint(s // 2, s // 4), QPoint(s // 2, s * 3 // 4))
        p.drawLine(QPoint(s // 4, s // 2), QPoint(s * 3 // 4, s // 2))
    elif name == "calendar":
        p.drawRoundedRect(QRectF(3, 4, s - 6, s - 7), 3, 3)
        p.drawLine(QPoint(3, 8), QPoint(s - 3, 8))
        p.drawLine(QPoint(7, 2), QPoint(7, 6))
        p.drawLine(QPoint(s - 7, 2), QPoint(s - 7, 6))
    elif name == "year":
        for row in range(3):
            for col in range(3):
                p.drawRoundedRect(QRectF(3 + col * 5, 4 + row * 5, 3, 3), 1, 1)
    elif name == "list":
        for y in (5, 9, 13):
            p.drawLine(QPoint(7, y), QPoint(s - 3, y))
            p.drawPoint(QPoint(4, y))
    elif name == "folder":
        path = QPainterPath()
        path.moveTo(3, 6)
        path.lineTo(7, 6)
        path.lineTo(9, 8)
        path.lineTo(s - 3, 8)
        path.lineTo(s - 3, s - 4)
        path.lineTo(3, s - 4)
        path.closeSubpath()
        p.drawPath(path)
    elif name == "file":
        p.drawRoundedRect(QRectF(5, 3, s - 9, s - 6), 2, 2)
        p.drawLine(QPoint(s - 7, 3), QPoint(s - 7, 7))
        p.drawLine(QPoint(s - 7, 7), QPoint(s - 4, 7))
    elif name == "open":
        p.drawRoundedRect(QRectF(4, 5, s - 8, s - 8), 2, 2)
        p.drawLine(QPoint(8, s - 8), QPoint(s - 4, 4))
        p.drawLine(QPoint(s - 9, 4), QPoint(s - 4, 4))
        p.drawLine(QPoint(s - 4, 4), QPoint(s - 4, 9))
    elif name == "trash":
        p.drawLine(QPoint(5, 6), QPoint(s - 5, 6))
        p.drawRoundedRect(QRectF(6, 7, s - 12, s - 4 - 7), 2, 2)
        p.drawLine(QPoint(8, 4), QPoint(s - 8, 4))
    elif name == "save":
        p.drawRoundedRect(QRectF(4, 3, s - 8, s - 6), 2, 2)
        p.drawLine(QPoint(7, 3), QPoint(7, 8))
        p.drawLine(QPoint(s - 7, 3), QPoint(s - 7, 8))
        p.drawLine(QPoint(7, s - 5), QPoint(s - 7, s - 5))
    elif name == "tag":
        p.drawRoundedRect(QRectF(4, 5, s - 8, s - 10), 3, 3)
        p.drawPoint(QPoint(8, 9))
    elif name == "palette":
        p.drawEllipse(QRectF(3, 4, s - 6, s - 8))
        p.drawPoint(QPoint(8, 8))
        p.drawPoint(QPoint(12, 9))
        p.drawPoint(QPoint(10, 13))
    elif name == "sun":
        p.drawEllipse(QRectF(6, 6, s - 12, s - 12))
        p.drawLine(QPoint(s // 2, 2), QPoint(s // 2, 4))
        p.drawLine(QPoint(s // 2, s - 4), QPoint(s // 2, s - 2))
        p.drawLine(QPoint(2, s // 2), QPoint(4, s // 2))
        p.drawLine(QPoint(s - 4, s // 2), QPoint(s - 2, s // 2))
    elif name == "moon":
        p.drawArc(QRectF(5, 3, s - 8, s - 6), 70 * 16, 260 * 16)
    elif name == "close":
        p.drawLine(QPoint(5, 5), QPoint(s - 5, s - 5))
        p.drawLine(QPoint(s - 5, 5), QPoint(5, s - 5))
    elif name == "up":
        p.drawLine(QPoint(5, 11), QPoint(s // 2, 6))
        p.drawLine(QPoint(s // 2, 6), QPoint(s - 5, 11))
    elif name == "down":
        p.drawLine(QPoint(5, 7), QPoint(s // 2, 12))
        p.drawLine(QPoint(s // 2, 12), QPoint(s - 5, 7))

    p.end()
    return QIcon(pix)


def app_icon(size: int = 64) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    bg = QPainterPath()
    bg.addRoundedRect(QRectF(4, 4, size - 8, size - 8), 14, 14)
    p.fillPath(bg, QColor("#2563EB"))
    pen = QPen(QColor("#FFFFFF"))
    pen.setWidth(4)
    pen.setStyle(Qt.SolidLine)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.drawRoundedRect(QRectF(18, 14, 28, 34), 5, 5)
    p.drawLine(QPoint(18, 23), QPoint(46, 23))
    p.drawLine(QPoint(25, 12), QPoint(25, 18))
    p.drawLine(QPoint(39, 12), QPoint(39, 18))
    p.drawLine(QPoint(24, 36), QPoint(30, 42))
    p.drawLine(QPoint(30, 42), QPoint(42, 30))
    p.end()
    return QIcon(pix)


def set_button_icon(button, name: str, color: str = ICON_COLOR, size: int = 18) -> None:
    button.setIcon(icon(name, color, size))
    button.setIconSize(QSize(size, size))
