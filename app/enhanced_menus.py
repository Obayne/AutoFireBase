"""
This file contains enhanced menu and settings functionality for AutoFire.
"""

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt


def enhance_menus(main_window):
    """
    Enhance the menu system of the main window.
    """
    # Get the existing menu bar
    menubar = main_window.menuBar()

    # Add missing menu items to existing menus
    for action in menubar.actions():
        menu = action.menu()
        if menu and action.text() == "&File":
            _enhance_file_menu(menu, main_window)
        elif menu and action.text() == "&Edit":
            _enhance_edit_menu(menu, main_window)
        elif menu and action.text() == "&View":
            _enhance_view_menu(menu, main_window)
        elif menu and action.text() == "&Tools":
            _enhance_tools_menu(menu, main_window)
        elif menu and action.text() == "&Help":
            _enhance_help_menu(menu, main_window)


def _enhance_file_menu(file_menu, main_window):
    """Enhance the File menu with additional options."""
    # Add separator before quit
    actions = file_menu.actions()
    if actions:
        file_menu.insertSeparator(actions[-1])  # Before Quit

        # Add settings submenu
        settings_menu = file_menu.insertMenu(actions[-1], "Settings")
        settings_menu.addAction("Open Settings...", main_window.open_settings)

        theme_menu = settings_menu.addMenu("Theme")
        theme_menu.addAction("Dark", lambda: main_window.set_theme("dark"))
        theme_menu.addAction("Light", lambda: main_window.set_theme("light"))
        theme_menu.addAction("High Contrast (Dark)", lambda: main_window.set_theme("high_contrast"))


def _enhance_edit_menu(edit_menu, main_window):
    """Enhance the Edit menu with additional options."""
    # Add find/replace options if they don't exist
    has_find = any(action.text() == "Find..." for action in edit_menu.actions())
    if not has_find:
        edit_menu.addSeparator()
        edit_menu.addAction("Find...", main_window.find_items, QtGui.QKeySequence("Ctrl+F"))
        edit_menu.addAction(
            "Find and Replace...", main_window.replace_items, QtGui.QKeySequence("Ctrl+H")
        )


def _enhance_view_menu(view_menu, main_window):
    """Enhance the View menu with additional options."""
    # Add view submenus
    view_menu.addSeparator()

    layers_menu = view_menu.addMenu("Layers")
    layers_menu.addAction("Layer Manager...", main_window.open_layer_manager)
    # Note: Layer toggle actions need to be connected after UI initialization

    display_menu = view_menu.addMenu("Display")
    display_menu.addAction("Grid Style...", main_window.grid_style_dialog)
    display_menu.addAction("Show Crosshair", main_window.toggle_crosshair_view)
    display_menu.addAction("Show Coverage", main_window.toggle_coverage_view)


def _enhance_tools_menu(tools_menu, main_window):
    """Enhance the Tools menu with additional options."""
    # Add analysis tools submenu if it doesn't exist
    has_analysis = any(action.text() == "Analysis Tools" for action in tools_menu.actions())
    if not has_analysis:
        analysis_menu = tools_menu.addMenu("Analysis Tools")
        analysis_menu.addAction("Generate Riser Diagram", main_window.generate_riser_diagram)
        analysis_menu.addAction("Show Calculations", main_window.show_calculations)
        analysis_menu.addAction("Circuit Properties", main_window.show_circuit_properties)

    # Add utilities submenu if it doesn't exist
    has_utilities = any(action.text() == "Utilities" for action in tools_menu.actions())
    if not has_utilities:
        utilities_menu = tools_menu.addMenu("Utilities")
        utilities_menu.addAction("Grid Style...", main_window.grid_style_dialog)
        utilities_menu.addAction(
            "Underlay Scale (Reference)...", main_window.start_underlay_scale_ref
        )
        utilities_menu.addAction("Underlay Scale (Drag)...", main_window.start_underlay_scale_drag)
        utilities_menu.addAction("Underlay Scale (Factor)...", main_window.underlay_scale_factor)
        utilities_menu.addAction("Center Underlay in View", main_window.center_underlay_in_view)
        utilities_menu.addAction("Move Underlay to Origin", main_window.move_underlay_to_origin)
        utilities_menu.addAction("Reset Underlay Transform", main_window.reset_underlay_transform)
        utilities_menu.addSeparator()
        utilities_menu.addAction("Offset Selected...", main_window.offset_selected_dialog)
        utilities_menu.addAction("Wire Spool...", main_window.open_wire_spool)


def _enhance_help_menu(help_menu, main_window):
    """Enhance the Help menu with additional options."""
    # Add separator and additional help options
    help_menu.addSeparator()
    help_menu.addAction("Documentation", main_window.show_user_guide)
    help_menu.addAction("Tutorials", lambda: None)  # Placeholder
    help_menu.addAction("Support", lambda: None)  # Placeholder


# Additional methods for the main window
def add_main_window_methods(main_window_class):
    """
    Add additional methods to the main window class.
    """

    def show_circuit_properties(self):
        """Open the circuit properties dialog."""
        # Try to import the dialog, fallback if not available
        try:
            from app.dialogs.circuit_properties import CircuitPropertiesDialog

            dialog = CircuitPropertiesDialog(self)
            dialog.exec()
        except ImportError:
            QtWidgets.QMessageBox.information(
                self, "Circuit Properties", "Circuit properties dialog not available."
            )

    def find_items(self):
        """Open find dialog."""
        QtWidgets.QMessageBox.information(
            self, "Find", "Find functionality is not yet implemented."
        )

    def replace_items(self):
        """Open replace dialog."""
        QtWidgets.QMessageBox.information(
            self, "Replace", "Replace functionality is not yet implemented."
        )

    def cut_selection(self):
        """Cut selected items."""
        QtWidgets.QMessageBox.information(self, "Cut", "Cut functionality is not yet implemented.")

    def copy_selection(self):
        """Copy selected items."""
        QtWidgets.QMessageBox.information(
            self, "Copy", "Copy functionality is not yet implemented."
        )

    def paste_selection(self):
        """Paste items."""
        QtWidgets.QMessageBox.information(
            self, "Paste", "Paste functionality is not yet implemented."
        )

    def select_all_items(self):
        """Select all items."""
        # Try to import DeviceItem, fallback if not available
        try:
            from app.device import DeviceItem

            # Select all items in the current scene
            for item in self.scene.items():
                if isinstance(item, (DeviceItem, QtWidgets.QGraphicsItem)):
                    item.setSelected(True)
        except ImportError:
            # Fallback: select all QGraphicsItems
            for item in self.scene.items():
                if isinstance(item, QtWidgets.QGraphicsItem):
                    item.setSelected(True)

    def clear_selection(self):
        """Clear selection."""
        self.scene.clearSelection()

    def zoom_in(self):
        """Zoom in."""
        self.view.scale(1.15, 1.15)

    def zoom_out(self):
        """Zoom out."""
        self.view.scale(1 / 1.15, 1 / 1.15)

    def zoom_to_selection(self):
        """Zoom to selected items."""
        # Get bounding rect of selected items
        bounds = QtCore.QRectF()
        for item in self.scene.selectedItems():
            bounds = bounds.united(item.sceneBoundingRect())

        if not bounds.isEmpty():
            # Add some margin
            margin = 50
            bounds.adjust(-margin, -margin, margin, margin)
            self.view.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
            self.statusBar().showMessage("Zoomed to selection")
        else:
            self.statusBar().showMessage("No selection to zoom to")

    def pan_view(self):
        """Pan the view."""
        # For now, just show a message about panning
        self.statusBar().showMessage("Hold SPACE and drag to pan the view")

    def toggle_grid_view(self):
        """Toggle grid visibility."""
        self.scene.show_grid = not self.scene.show_grid
        self.scene.update()
        self.statusBar().showMessage(f"Grid {'enabled' if self.scene.show_grid else 'disabled'}")

    def toggle_snap_view(self):
        """Toggle snap functionality."""
        self.scene.snap_enabled = not self.scene.snap_enabled
        self.statusBar().showMessage(f"Snap {'enabled' if self.scene.snap_enabled else 'disabled'}")

    def toggle_crosshair_view(self):
        """Toggle crosshair visibility."""
        self.view.show_crosshair = not self.view.show_crosshair
        self.statusBar().showMessage(
            f"Crosshair {'enabled' if self.view.show_crosshair else 'disabled'}"
        )

    def toggle_coverage_view(self):
        """Toggle coverage visibility."""
        self.show_coverage = not self.show_coverage
        # Try to import DeviceItem, fallback if not available
        try:
            from app.device import DeviceItem

            for it in self.layer_devices.childItems():
                if isinstance(it, DeviceItem):
                    try:
                        it.set_coverage_enabled(self.show_coverage)
                    except Exception:
                        pass
        except ImportError:
            # Fallback: do nothing
            pass
        self.prefs["show_coverage"] = self.show_coverage
        # Assuming save_prefs is available in the scope
        # save_prefs(self.prefs)
        self.statusBar().showMessage(f"Coverage {'enabled' if self.show_coverage else 'disabled'}")

    def print_document(self):
        """Print the document."""
        QtWidgets.QMessageBox.information(
            self, "Print", "Print functionality is not yet implemented."
        )

    def print_preview(self):
        """Show print preview."""
        QtWidgets.QMessageBox.information(
            self, "Print Preview", "Print preview functionality is not yet implemented."
        )

    def toggle_underlay_layer(self):
        """Toggle underlay layer visibility."""
        if hasattr(self, "chk_underlay"):
            self.chk_underlay.toggle()

    def toggle_sketch_layer(self):
        """Toggle sketch layer visibility."""
        if hasattr(self, "chk_sketch"):
            self.chk_sketch.toggle()

    def toggle_wires_layer(self):
        """Toggle wires layer visibility."""
        if hasattr(self, "chk_wires"):
            self.chk_wires.toggle()

    def toggle_devices_layer(self):
        """Toggle devices layer visibility."""
        if hasattr(self, "chk_devices"):
            self.chk_devices.toggle()

    # Add methods to the class
    main_window_class.show_circuit_properties = show_circuit_properties
    main_window_class.find_items = find_items
    main_window_class.replace_items = replace_items
    main_window_class.cut_selection = cut_selection
    main_window_class.copy_selection = copy_selection
    main_window_class.paste_selection = paste_selection
    main_window_class.select_all_items = select_all_items
    main_window_class.clear_selection = clear_selection
    main_window_class.zoom_in = zoom_in
    main_window_class.zoom_out = zoom_out
    main_window_class.zoom_to_selection = zoom_to_selection
    main_window_class.pan_view = pan_view
    main_window_class.toggle_grid_view = toggle_grid_view
    main_window_class.toggle_snap_view = toggle_snap_view
    main_window_class.toggle_crosshair_view = toggle_crosshair_view
    main_window_class.toggle_coverage_view = toggle_coverage_view
    main_window_class.print_document = print_document
    main_window_class.print_preview = print_preview
    main_window_class.toggle_underlay_layer = toggle_underlay_layer
    main_window_class.toggle_sketch_layer = toggle_sketch_layer
    main_window_class.toggle_wires_layer = toggle_wires_layer
    main_window_class.toggle_devices_layer = toggle_devices_layer
