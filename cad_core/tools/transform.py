from app.device import DeviceItem
from PySide6 import QtCore, QtWidgets


def _clone_item(it: QtWidgets.QGraphicsItem) -> QtWidgets.QGraphicsItem | None:
    if isinstance(it, DeviceItem):
        d = it.to_json()
        clone = DeviceItem(
            float(d["x"]),
            float(d["y"]),
            d["symbol"],
            d["name"],
            d.get("manufacturer", ""),
            d.get("part_number", ""),
        )
        if d.get("coverage"):
            clone.set_coverage(d["coverage"])
        if "label_offset" in d:
            off = d["label_offset"]
            # use union types in isinstance checks per ruff UP038 recommendation
            if isinstance(off, (list | tuple)) and len(off) == 2:
                clone.set_label_offset(float(off[0]), float(off[1]))
        if "rotation" in d:
            try:
                clone.setRotation(float(d["rotation"]))
            except Exception:
                pass
        return clone
    elif isinstance(it, QtWidgets.QGraphicsPathItem):
        c = QtWidgets.QGraphicsPathItem()
        c.setPath(it.path())
        c.setPen(it.pen())
        c.setBrush(it.brush())
        c.setZValue(it.zValue())
        c.setTransform(it.transform())
        return c
    else:
        return None


def duplicate_selected(
    scene: QtWidgets.QGraphicsScene,
    parent_group: QtWidgets.QGraphicsItem,
    dx_px: float = 12.0,
    dy_px: float = 12.0,
):
    sel = scene.selectedItems()
    if not sel:
        return 0
    count = 0
    for it in sel:
        clone = _clone_item(it)
        if clone is None:
            continue
        clone.setPos(it.pos() + QtCore.QPointF(dx_px, dy_px))
        clone.setParentItem(parent_group)
        count += 1
    return count


def rotate_selected(scene: QtWidgets.QGraphicsScene, angle_deg: float):
    sel = scene.selectedItems()
    if not sel:
        return 0
    for it in sel:
        it.setRotation(it.rotation() + angle_deg)
    return len(sel)


def nudge_selected(scene: QtWidgets.QGraphicsScene, dx_px: float, dy_px: float):
    sel = scene.selectedItems()
    if not sel:
        return 0
    for it in sel:
        it.setPos(it.pos() + QtCore.QPointF(dx_px, dy_px))
    return len(sel)


def align_selected_to_grid(scene, px_per_ft: float, snap_step_px: float, grid_size: int):
    sel = scene.selectedItems()
    if not sel:
        return 0
    step = float(snap_step_px) if (snap_step_px and snap_step_px > 0) else float(grid_size)
    if step <= 0:
        step = float(grid_size) if grid_size > 0 else 12.0

    def _snap(v: float) -> float:
        return round(v / step) * step

    for it in sel:
        p = it.pos()
        it.setPos(QtCore.QPointF(_snap(p.x()), _snap(p.y())))
    return len(sel)
