from typing import cast

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

DEFAULT_GRID_SIZE = 24  # pixels between minor lines


class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, grid_size=DEFAULT_GRID_SIZE, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_size = max(2, int(grid_size))
        self.show_grid = True
        self.snap_enabled = True
        self.snap_step_px = 0.0  # if >0, overrides grid intersections

        # Style (preferences can override via setters)
        self.grid_opacity = 0.35  # 0..1
        self.grid_width = 0.0  # 0 = hairline; otherwise widthF in px
        self.major_every = 5

        # Base colors (dark theme)
        self.col_minor_rgb = QtGui.QColor(120, 130, 145)  # we apply alpha every frame
        self.col_major_rgb = QtGui.QColor(160, 170, 185)
        self.col_axis_rgb = QtGui.QColor(180, 190, 205)

    def set_grid_style(
        self,
        opacity: float | None = None,
        width: float | None = None,
        major_every: int | None = None,
    ):
        if opacity is not None:
            self.grid_opacity = max(0.05, min(1.0, float(opacity)))
        if width is not None:
            self.grid_width = max(0.0, float(width))
        if major_every is not None:
            self.major_every = max(2, int(major_every))
        self.update()

    # simple grid snap
    def snap(self, pt: QtCore.QPointF) -> QtCore.QPointF:
        if not self.snap_enabled:
            return pt
        if self.snap_step_px and self.snap_step_px > 0:
            s = self.snap_step_px
            x = round(pt.x() / s) * s
            y = round(pt.y() / s) * s
            return QtCore.QPointF(x, y)
        # snap to grid intersections
        g = self.grid_size
        x = round(pt.x() / g) * g
        y = round(pt.y() / g) * g
        return QtCore.QPointF(x, y)

    def _pen(self, base_rgb: QtGui.QColor):
        c = QtGui.QColor(base_rgb)
        c.setAlphaF(self.grid_opacity)
        pen = QtGui.QPen(c)
        pen.setCosmetic(True)
        if self.grid_width > 0.0:
            pen.setWidthF(self.grid_width)
        return pen

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawBackground(painter, rect)
        if not self.show_grid or self.grid_size <= 0:
            return

        g = self.grid_size
        left = int(rect.left()) - (int(rect.left()) % g)
        top = int(rect.top()) - (int(rect.top()) % g)

        pen_minor = self._pen(self.col_minor_rgb)
        pen_major = self._pen(self.col_major_rgb)
        major_every = self.major_every

        painter.save()
        # verticals
        x = left
        idx = 0
        while x < rect.right():
            painter.setPen(pen_major if (idx % major_every == 0) else pen_minor)
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += g
            idx += 1
        # horizontals
        y = top
        idy = 0
        while y < rect.bottom():
            painter.setPen(pen_major if (idy % major_every == 0) else pen_minor)
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += g
            idy += 1

        # axes cross at (0,0)
        axis_pen = self._pen(self.col_axis_rgb)
        painter.setPen(axis_pen)
        painter.drawLine(0, int(rect.top()), 0, int(rect.bottom()))
        painter.drawLine(int(rect.left()), 0, int(rect.right()), 0)
        painter.restore()


class CanvasView(QtWidgets.QGraphicsView):
    """Graphics view for CAD canvas with device and layer management."""

    def __init__(self, scene, devices_group, wires_group, sketch_group, overlay_group, window_ref):
        super().__init__(scene)
        self.setRenderHints(
            QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing
        )
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
        self.setMouseTracking(True)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Store references to groups and window
        self.devices_group = devices_group
        self.wires_group = wires_group
        self.sketch_group = sketch_group
        self.overlay_group = overlay_group
        self.win = window_ref

        # Zoom and pan state
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0

        # Enable scroll wheel zooming
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+wheel
            zoom_factor = 1.15
            if event.angleDelta().y() < 0:
                zoom_factor = 1.0 / zoom_factor

            self.zoom_by_factor(zoom_factor, event.position())
            event.accept()
        else:
            # Default scroll behavior
            super().wheelEvent(event)

    def zoom_by_factor(self, factor, center=None):
        """Zoom by a factor, optionally centered on a point."""
        new_zoom = self.zoom_factor * factor
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        if abs(new_zoom - self.zoom_factor) < 0.01:
            return  # No significant change

        self.zoom_factor = new_zoom

        if center is None:
            center = self.viewport().rect().center()

        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.scale(factor, factor)

        # Update status if window has status bar
        if hasattr(self.win, "statusBar"):
            self.win.statusBar().showMessage(f"Zoom: {self.zoom_factor:.1%}")

        # Update zoom label if it exists
        if hasattr(self.win, "zoom_label"):
            self.win.zoom_label.setText(f"Zoom: {self.zoom_factor:.0%}")

    def zoom_in(self):
        """Zoom in by 25%."""
        self.zoom_by_factor(1.25)

    def zoom_out(self):
        """Zoom out by 25%."""
        self.zoom_by_factor(0.8)

    def zoom_fit(self):
        """Fit the entire scene in view."""
        if self.scene():
            rect = self.scene().itemsBoundingRect()
            if not rect.isEmpty():
                self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                # Update zoom factor based on current transform
                self.zoom_factor = self.transform().m11()  # Horizontal scale factor
                if hasattr(self.win, "statusBar"):
                    self.win.statusBar().showMessage(f"Zoom: {self.zoom_factor:.1%}")
                if hasattr(self.win, "zoom_label"):
                    self.win.zoom_label.setText(f"Zoom: {self.zoom_factor:.0%}")

    def zoom_to_rect(self, rect):
        """Zoom to a specific rectangle."""
        if not rect.isEmpty():
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            self.zoom_factor = self.transform().m11()
            if hasattr(self.win, "statusBar"):
                self.win.statusBar().showMessage(f"Zoom: {self.zoom_factor:.1%}")
            if hasattr(self.win, "zoom_label"):
                self.win.zoom_label.setText(f"Zoom: {self.zoom_factor:.0%}")

    def pan_to_point(self, point):
        """Pan to center on a specific point."""
        self.centerOn(point)

    def toggle_grid(self):
        """Toggle grid visibility."""
        if isinstance(self.scene(), GridScene):
            grid_scene = cast(GridScene, self.scene())
            grid_scene.show_grid = not grid_scene.show_grid
            grid_scene.update()
            status = "on" if grid_scene.show_grid else "off"
            if hasattr(self.win, "statusBar"):
                self.win.statusBar().showMessage(f"Grid: {status}")

    def toggle_snap(self):
        """Toggle snap to grid."""
        if isinstance(self.scene(), GridScene):
            grid_scene = cast(GridScene, self.scene())
            grid_scene.snap_enabled = not grid_scene.snap_enabled
            status = "on" if grid_scene.snap_enabled else "off"
            if hasattr(self.win, "statusBar"):
                self.win.statusBar().showMessage(f"Snap: {status}")

    def mousePressEvent(self, event):
        """Handle mouse press events for panning and device placement with enhanced feedback."""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Middle mouse button for panning
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
            # Create a fake left button event for dragging
            fake_event = QtGui.QMouseEvent(
                QtGui.QMouseEvent.Type.MouseButtonPress,
                event.position(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                event.modifiers(),
            )
            super().mousePressEvent(fake_event)
        elif event.button() == Qt.MouseButton.LeftButton:
            # Check if we have a selected device for placement
            if hasattr(self.win, "current_proto") and self.win.current_proto:
                # Place the device at the click position
                scene_pos = self.mapToScene(event.position().toPoint())
                success = self._place_device_at(scene_pos)

                # Provide visual feedback for successful/failed placement
                if success:
                    self._show_placement_feedback(scene_pos, success=True)
                    # Keep the prototype selected for continuous placement
                    # User can press ESC to exit placement mode
                else:
                    self._show_placement_feedback(scene_pos, success=False)

                event.accept()
                return
            # Check if we're in drawing mode
            elif hasattr(self.win, "draw") and self.win.draw.mode != 0:  # DrawMode.NONE
                scene_pos = self.mapToScene(event.position().toPoint())
                shift_ortho = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
                if self.win.draw.on_click(scene_pos, shift_ortho):
                    # Drawing completed, reset to device placement mode
                    pass
                event.accept()
                return
            else:
                # Normal left click behavior
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

        # Handle right-click for context menu
        if event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()
            return

    def _show_placement_feedback(self, scene_pos, success=True):
        """Show visual feedback for device placement attempt."""
        try:
            from PySide6 import QtCore

            # Create a temporary feedback circle
            color = QtCore.Qt.GlobalColor.green if success else QtCore.Qt.GlobalColor.red
            pen = QtGui.QPen(color, 2)
            brush = QtGui.QBrush(color, QtCore.Qt.BrushStyle.SolidPattern)

            # Create circle at placement position
            feedback_circle = self.scene().addEllipse(
                scene_pos.x() - 10, scene_pos.y() - 10, 20, 20, pen, brush
            )
            feedback_circle.setOpacity(0.7)

            # Remove feedback after short delay
            QtCore.QTimer.singleShot(500, lambda: self.scene().removeItem(feedback_circle))
        except Exception:
            # Fallback if visual feedback fails
            pass

    def mouseMoveEvent(self, event):
        """Handle mouse move events for ghost device positioning with enhanced preview."""
        super().mouseMoveEvent(event)

        # Update ghost device position if one exists
        if hasattr(self.win, "ghost") and self.win.ghost:
            scene_pos = self.mapToScene(event.position().toPoint())

            # Snap ghost to grid if enabled
            if isinstance(self.scene(), GridScene):
                grid_scene = cast(GridScene, self.scene())
                if grid_scene.snap_enabled:
                    scene_pos = grid_scene.snap(scene_pos)

            self.win.ghost.setPos(scene_pos)

            # Update ghost appearance based on placement validity
            if hasattr(self.win, "current_proto") and self.win.current_proto:
                device_data = self._extract_device_data(self.win.current_proto)
                is_valid = self._validate_placement_location(scene_pos, device_data)

                # Change ghost color based on validity
                if hasattr(self.win.ghost, "setOpacity"):
                    self.win.ghost.setOpacity(0.7 if is_valid else 0.4)

        # Update drawing preview if in drawing mode
        if hasattr(self.win, "draw") and self.win.draw.mode != 0:  # DrawMode.NONE
            scene_pos = self.mapToScene(event.position().toPoint())
            shift_ortho = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            self.win.draw.on_mouse_move(scene_pos, shift_ortho)

        # Update coordinate display in status bar
        if hasattr(self.win, "coord_label"):
            scene_pos = self.mapToScene(event.position().toPoint())
            # Convert to feet for display
            px_per_ft = getattr(self.win, "px_per_ft", 12.0)
            # ft_x = scene_pos.x() / px_per_ft
            ft_y = scene_pos.y() / px_per_ft
            self.win.coord_label.setText(".2f")

    def _place_device_at(self, scene_pos):
        """Place the currently selected device prototype at the given position with enhanced validation."""
        if not hasattr(self.win, "current_proto") or not self.win.current_proto:
            self._show_status("No device selected for placement")
            return False

        # Snap to grid if enabled
        if isinstance(self.scene(), GridScene):
            grid_scene = cast(GridScene, self.scene())
            scene_pos = grid_scene.snap(scene_pos)

        # Extract device data from prototype
        device_data = self._extract_device_data(self.win.current_proto)

        # Validate placement location
        if not self._validate_placement_location(scene_pos, device_data):
            return False

        # Create device based on type
        device = self._create_device_from_data(scene_pos, device_data)
        if not device:
            self._show_status(f"Failed to create device: {device_data['name']}")
            return False

        # Execute placement with proper command system
        success = self._execute_device_placement(device, device_data)

        if success:
            self._post_placement_actions(device, device_data)
            self._show_status(
                f"Placed: {device_data['name']} at ({scene_pos.x():.0f}, {scene_pos.y():.0f})"
            )
            return True
        else:
            self._show_status(f"Failed to place: {device_data['name']}")
            return False

    def _extract_device_data(self, proto):
        """Extract and normalize device data from prototype."""
        return {
            "name": (
                proto.get("name") or proto.get("model") or proto.get("device_type") or "Unknown"
            ),
            "symbol": (proto.get("symbol") or proto.get("uid") or "?"),
            "type": proto.get("type", "other").lower(),
            "manufacturer": proto.get("manufacturer", ""),
            "part_number": proto.get("part_number", ""),
            "model": proto.get("model", ""),
            "properties": proto.get("properties", {}),
        }

    def _validate_placement_location(self, scene_pos, device_data):
        """Validate that the device can be placed at the specified location."""
        # Check for conflicts with existing devices (use larger collision box)
        collision_size = 20  # 20 pixel collision detection
        check_rect = QtCore.QRectF(
            scene_pos.x() - collision_size / 2,
            scene_pos.y() - collision_size / 2,
            collision_size,
            collision_size,
        )

        items_at_pos = self.scene().items(check_rect)
        for item in items_at_pos:
            from frontend.device import DeviceItem
            from frontend.fire_alarm_panel import FireAlarmPanel

            if isinstance(item, (DeviceItem, FireAlarmPanel)):
                self._show_status(
                    f"Device placement conflict at ({scene_pos.x():.0f}, {scene_pos.y():.0f})"
                )
                return False

        # Additional validation for fire alarm panels
        if device_data["type"] in ["panel", "fire_alarm_panel", "main_panel"]:
            # Check if we already have a main panel
            if hasattr(self.win, "circuit_manager") and self.win.circuit_manager.main_panel:
                self._show_status("Main fire alarm panel already exists")
                return False

        return True

    def _create_device_from_data(self, scene_pos, device_data):
        """Create the appropriate device object from device data."""
        try:
            # Check if this should be a fire alarm panel
            if device_data["type"] in ["panel", "fire_alarm_panel", "main_panel"]:
                from frontend.fire_alarm_panel import FireAlarmPanel

                device = FireAlarmPanel(
                    scene_pos.x(),
                    scene_pos.y(),
                    device_data["symbol"],
                    device_data["name"],
                    device_data["manufacturer"],
                    device_data["part_number"],
                )
                device.panel_type = "main"
                device.device_type = "fire_alarm_panel"
                return device
            else:
                # Create regular device
                from frontend.device import DeviceItem

                device = DeviceItem(
                    scene_pos.x(),
                    scene_pos.y(),
                    device_data["symbol"],
                    device_data["name"],
                    device_data["manufacturer"],
                    device_data["part_number"],
                )
                # Set device type from catalog data for circuit management
                device.device_type = self._map_device_type(device_data["type"])
                return device
        except Exception as e:
            print(f"Error creating device: {e}")
            return None

    def _execute_device_placement(self, device, device_data):
        """Execute device placement using command system."""
        try:
            if hasattr(self.win, "command_stack"):
                from cad_core.commands import AddDeviceCommand

                command = AddDeviceCommand(self.scene(), device, self.devices_group)
                return self.win.command_stack.execute(command)
            else:
                # Fallback if no command stack
                self.devices_group.addToGroup(device)
                return True
        except Exception as e:
            print(f"Error executing device placement: {e}")
            return False

    def _post_placement_actions(self, device, device_data):
        """Perform post-placement actions like registering with circuit manager."""
        # Register fire alarm panels with circuit manager
        if hasattr(self.win, "circuit_manager") and device_data["type"] in [
            "panel",
            "fire_alarm_panel",
            "main_panel",
        ]:
            self.win.circuit_manager.add_panel(device)

        # Update device counters in System Builder if available
        if hasattr(self.win, "system_builder"):
            self.win.system_builder.increment_placed_count(device_data["type"])

        # Auto-select the placed device for immediate property editing
        self.scene().clearSelection()
        device.setSelected(True)

        # Update inspector panel if available
        if hasattr(self.win, "_update_inspector_for_selection"):
            self.win._update_inspector_for_selection()

    def _show_status(self, message):
        """Show status message to user."""
        if hasattr(self.win, "statusBar"):
            self.win.statusBar().showMessage(message)
        else:
            print(f"STATUS: {message}")

    def _map_device_type(self, catalog_type):
        """Map catalog device type to circuit-compatible device type."""
        type_mapping = {
            "detector": "smoke_detector",  # Default detectors to smoke
            "notification": "horn_strobe",  # Default notification to horn/strobe
            "initiating": "pull_station",  # Default initiating to pull station
            "panel": "fire_alarm_panel",
        }
        return type_mapping.get(catalog_type.lower(), catalog_type.lower())

    def keyPressEvent(self, event):
        """Handle key press events with enhanced shortcuts."""
        if event.key() == Qt.Key.Key_Escape:
            # Clear device selection and ghost
            if hasattr(self.win, "current_proto"):
                self.win.current_proto = None
                self.win.current_kind = "other"
            if hasattr(self.win, "ghost") and self.win.ghost:
                self.win.scene.removeItem(self.win.ghost)
                self.win.ghost = None

            # Finish any active drawing
            if hasattr(self.win, "draw"):
                self.win.draw.finish()

            if hasattr(self.win, "statusBar"):
                self.win.statusBar().showMessage("Ready")
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            # Delete selected items
            if self._delete_selected():
                event.accept()
                return
        elif (
            event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # Ctrl+A: Select all
            self._select_all()
            event.accept()
        elif (
            event.key() == Qt.Key.Key_D and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # Ctrl+D: Deselect all
            self.scene().clearSelection()
            event.accept()
        elif event.key() == Qt.Key.Key_G:
            # G: Toggle grid
            self.toggle_grid()
            event.accept()
        elif event.key() == Qt.Key.Key_S and not (
            event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # S: Toggle snap (not Ctrl+S which is save)
            self.toggle_snap()
            event.accept()
        elif event.key() == Qt.Key.Key_F:
            # F: Fit all in view
            self.zoom_fit()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _show_context_menu(self, global_pos):
        """Show context menu at the cursor position."""
        menu = QtWidgets.QMenu()

        # Get scene position and item under cursor
        view_pos = self.mapFromGlobal(global_pos)
        scene_pos = self.mapToScene(view_pos)
        item_under = self.scene().itemAt(scene_pos, self.transform())

        # Check if we clicked on a device
        from frontend.device import DeviceItem

        if isinstance(item_under, DeviceItem):
            # Device-specific context menu
            menu.addAction("Properties...", lambda: self._edit_device_properties(item_under))
            menu.addAction("Delete Device", lambda: self._delete_device(item_under))
            menu.addSeparator()
            menu.addAction("Set Address...", lambda: self._set_device_address(item_under))
            menu.addAction("Connect to...", lambda: self._connect_device(item_under))
            menu.addSeparator()

        # General context menu actions
        selected_items = self.scene().selectedItems()

        if selected_items:
            menu.addAction(f"Delete Selected ({len(selected_items)})", self._delete_selected)
            menu.addSeparator()

        menu.addAction("Select All", self._select_all)
        menu.addAction("Clear Selection", lambda: self.scene().clearSelection())
        menu.addSeparator()

        # Grid and snap actions
        if hasattr(self, "toggle_grid"):
            menu.addAction("Toggle Grid", self.toggle_grid)
        if hasattr(self, "toggle_snap"):
            menu.addAction("Toggle Snap", self.toggle_snap)

        # Show the menu
        menu.exec(global_pos)

    def _edit_device_properties(self, device):
        """Edit device properties."""
        # TODO: Implement device properties dialog
        if hasattr(self.win, "statusBar"):
            self.win.statusBar().showMessage(f"Edit properties for {device.name}")

    def _delete_device(self, device):
        """Delete a specific device."""
        if device.scene():
            device.scene().removeItem(device)
        if hasattr(self.win, "statusBar"):
            self.win.statusBar().showMessage(f"Deleted {device.name}")

    def _set_device_address(self, device):
        """Set device address."""
        # TODO: Implement address assignment dialog
        if hasattr(self.win, "statusBar"):
            self.win.statusBar().showMessage(f"Set address for {device.name}")

    def _connect_device(self, device):
        """Connect device to another device."""
        if not hasattr(self.win, "circuit_manager"):
            if hasattr(self.win, "statusBar"):
                self.win.statusBar().showMessage("Circuit manager not available")
            return

        # Get all other devices in the scene
        other_devices = []
        for item in self.scene().items():
            if hasattr(item, "device_type") and item != device and hasattr(item, "name"):
                other_devices.append(item)

        if not other_devices:
            if hasattr(self.win, "statusBar"):
                self.win.statusBar().showMessage("No other devices to connect to")
            return

        # Show device selection dialog
        dialog = QtWidgets.QDialog(self.win if hasattr(self.win, "win") else None)
        dialog.setWindowTitle(f"Connect {device.name}")
        dialog.setModal(True)
        dialog.resize(300, 200)

        layout = QtWidgets.QVBoxLayout(dialog)

        label = QtWidgets.QLabel(f"Select device to connect {device.name} to:")
        layout.addWidget(label)

        device_list = QtWidgets.QListWidget()
        for other_device in other_devices:
            device_list.addItem(f"{other_device.name} ({other_device.device_type})")
        layout.addWidget(device_list)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            selection = device_list.currentRow()
            if selection >= 0:
                target_device = other_devices[selection]
                # TODO: Implement actual circuit connection logic
                if hasattr(self.win, "statusBar"):
                    self.win.statusBar().showMessage(
                        f"Connected {device.name} to {target_device.name}"
                    )

    def _delete_selected(self):
        """Delete all selected items."""
        selected_items = self.scene().selectedItems()
        if not selected_items:
            return False

        # Confirm deletion for multiple items
        if len(selected_items) > 1:
            reply = QtWidgets.QMessageBox.question(
                self.win if hasattr(self, "win") else None,
                "Confirm Deletion",
                f"Delete {len(selected_items)} selected items?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                return False

        # Delete items using command system if available
        if hasattr(self.win, "command_stack"):
            from cad_core.commands import DeleteItemsCommand

            command = DeleteItemsCommand(self.scene(), selected_items)
            success = self.win.command_stack.execute(command)
            if success and hasattr(self.win, "statusBar"):
                self.win.statusBar().showMessage(f"Deleted {len(selected_items)} items")
            return success
        else:
            # Fallback deletion
            for item in selected_items:
                if item.scene():
                    item.scene().removeItem(item)
            if hasattr(self.win, "statusBar"):
                self.win.statusBar().showMessage(f"Deleted {len(selected_items)} items")
            return True

    def _select_all(self):
        """Select all selectable items in the scene."""
        path = QtGui.QPainterPath()
        path.addRect(self.scene().itemsBoundingRect())
        self.scene().setSelectionArea(path)

        selected_count = len(self.scene().selectedItems())
        if hasattr(self.win, "statusBar"):
            self.win.statusBar().showMessage(f"Selected {selected_count} items")
