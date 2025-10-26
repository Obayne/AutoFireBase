from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QFont, QImage, QPainter, QPen

from backend import branding


def _draw_title_block(p: QPainter, w: int, h: int, meta: dict[str, Any]) -> None:
    p.save()
    # Background
    p.fillRect(0, 0, w, h, Qt.GlobalColor.white)
    pen = QPen(Qt.GlobalColor.black)
    pen.setWidth(4)
    p.setPen(pen)
    # Border
    p.drawRect(20, 20, w - 40, h - 40)

    # Title block area (bottom 2 inches approx if 300 DPI; assume 2550x3300 => 600px height)
    tb_h = int(h * 0.18)
    tb_rect = QRectF(40, h - tb_h - 40, w - 80, tb_h)
    p.drawRect(tb_rect)

    # Headings/fonts
    title_font = QFont("Segoe UI", 28, QFont.Weight.Bold)
    body_font = QFont("Segoe UI", 16)
    small_font = QFont("Segoe UI", 12)

    # Product header (top-left)
    p.setFont(title_font)
    p.drawText(60, 100, f"{branding.PRODUCT_NAME}")
    p.setFont(small_font)
    p.drawText(60, 135, f"{branding.full_product_label()}")

    # Project info inside title block
    p.setFont(body_font)
    project_name = str(meta.get("project_name", "Project Name"))
    project_address = str(meta.get("project_address", "Address"))
    designer = str(meta.get("designer", "Designer"))
    sheet_title = str(meta.get("sheet_title", "Fire Alarm Design Sheet"))
    date_str = str(meta.get("date", datetime.today().strftime("%Y-%m-%d")))

    margin = 20
    x = int(tb_rect.left()) + margin
    y = int(tb_rect.top()) + 40
    line = 30
    p.drawText(x, y, f"Sheet: {sheet_title}")
    y += line
    p.drawText(x, y, f"Project: {project_name}")
    y += line
    p.drawText(x, y, f"Address: {project_address}")
    y += line
    p.drawText(x, y, f"Designer: {designer}")
    y += line
    p.drawText(x, y, f"Date: {date_str}")

    # Company box (bottom-right of title block)
    box_w = 520
    box_h = 140
    box_x = int(tb_rect.right()) - box_w - margin
    box_y = int(tb_rect.bottom()) - box_h - margin
    p.drawRect(box_x, box_y, box_w, box_h)
    p.setFont(body_font)
    p.drawText(box_x + 16, box_y + 40, "Company:")
    p.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
    p.drawText(box_x + 16, box_y + 80, meta.get("company", "AlarmForge"))
    p.setFont(small_font)
    p.drawText(box_x + 16, box_y + 110, meta.get("company_contact", "info@example.com"))

    p.restore()


def export_title_block_png(path: str, meta: dict[str, Any] | None = None, size: tuple[int, int] = (2550, 3300)) -> str:
    meta = meta or {}
    w, h = size
    img = QImage(w, h, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.white)
    painter = QPainter(img)
    try:
        _draw_title_block(painter, w, h, meta)
    finally:
        painter.end()
    img.save(path)
    return path


def export_title_block_pdf(path: str, meta: dict[str, Any] | None = None, size: tuple[int, int] = (2550, 3300)) -> str:
    # Render onto an image and embed into a simple PDF via QPdfWriter
    from PySide6.QtGui import QPdfWriter

    meta = meta or {}
    w, h = size
    pdf = QPdfWriter(path)
    # Set resolution to 300 DPI for good print quality
    pdf.setResolution(300)
    # Page size: Letter portrait in points via page layout is more involved; draw by pixels directly
    painter = QPainter(pdf)
    try:
        _draw_title_block(painter, w, h, meta)
    finally:
        painter.end()
    return path
