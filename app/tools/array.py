from PySide6 import QtCore, QtWidgets

from app.device import DeviceItem


class ArrayTool(QtCore.QObject):
    """Simple rectangular array: spacing derived from active device coverage or manual."""

    def __init__(self, window, devices_group):
        super().__init__(window)
        self.win = window
        self.layer_devices = devices_group

    def run(self):
        win = self.win
        proto = getattr(win.view, "current_proto", None)
        if not proto:
            QtWidgets.QMessageBox.information(win, "Array", "Pick a device in the palette first.")
            return

        # spacing from active "defaults" or device coverage after place; here ask user:
        spacing_ft, ok = QtWidgets.QInputDialog.getDouble(
            win,
            "Array spacing",
            "Center-to-center spacing (ft):",
            win.prefs.get("array_spacing_ft", 20.0),
            1.0,
            200.0,
            1,
        )
        if not ok:
            return
        win.prefs["array_spacing_ft"] = spacing_ft

        width_ft, ok = QtWidgets.QInputDialog.getDouble(
            win, "Area width", "Width (ft):", 60.0, 1.0, 10000.0, 1
        )
        if not ok:
            return
        height_ft, ok = QtWidgets.QInputDialog.getDouble(
            win, "Area height", "Height (ft):", 40.0, 1.0, 10000.0, 1
        )
        if not ok:
            return

        ppf = float(win.px_per_ft)
        sx = spacing_ft * ppf
        cols = max(1, int(width_ft / spacing_ft))
        rows = max(1, int(height_ft / spacing_ft))

        # place centered in the current view rect
        vis = win.view.mapToScene(win.view.viewport().rect()).boundingRect()
        cx, cy = vis.center().x(), vis.center().y()
        left = cx - (cols - 1) * sx / 2.0
        top = cy - (rows - 1) * sx / 2.0

        for r in range(rows):
            for c in range(cols):
                x = left + c * sx
                y = top + r * sx
                d = proto
                it = DeviceItem(
                    x,
                    y,
                    d["symbol"],
                    d["name"],
                    d.get("manufacturer", ""),
                    d.get("part_number", ""),
                )
                # default coverage for previewed arrays (optional: half spacing ring)
                it.set_coverage(
                    {
                        "mode": "strobe",
                        "mount": "ceiling",
                        "computed_radius_ft": spacing_ft / 2.0,
                        "px_per_ft": ppf,
                    }
                )
                it.setParentItem(self.layer_devices)

        win.push_history()
        win.statusBar().showMessage(f"Array placed: {cols}x{rows} at ~{spacing_ft:.1f} ft.")
