"""
Paperspace Window - Print layout workspace with sheets and viewports
"""

import os
import sys

# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
)

from app.layout import PageFrame, TitleBlock, ViewportItem
from app.logging_config import setup_logging

# Ensure logging is configured early
setup_logging()
import logging

_logger = logging.getLogger(__name__)


class PaperspaceWindow(QMainWindow):
    """
    Paperspace Window - Dedicated print layout workspace.
    Manages multiple sheets with viewports, title blocks, and print-specific tools.
    """

    def __init__(self, app_controller, model_scene, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.model_scene = model_scene  # Reference to model space scene
        self.setWindowTitle("AutoFire - Paperspace")
        self.setObjectName("PaperspaceWindow")

        # Initialize core attributes
        self.prefs = app_controller.prefs
        self.px_per_ft = float(self.prefs.get("px_per_ft", 12.0))

        # Initialize sheets
        self.sheets = []
        self.current_sheet_index = 0
        self.paper_scene = None

        # Create the main view
        self._setup_view()

        # Setup UI components
        self._setup_ui()

        # Initialize first sheet
        self._create_new_sheet()

        # Connect to app controller signals
        self._connect_signals()

        self.resize(1000, 700)

    def _setup_view(self):
        """Setup the paperspace view."""
        from app.main import CanvasView

        # Create initial empty scene (will be replaced by sheets)
        self.paper_scene = QtWidgets.QGraphicsScene()
        self.paper_scene.setBackgroundBrush(QtGui.QColor(250, 250, 250))

        # Create view
        self.view = CanvasView(
            self.paper_scene,
            None,  # No device group in paperspace
            None,  # No wires in paperspace
            None,  # No sketch in paperspace
            None,  # No overlay in paperspace
            self,  # Pass self as window reference
        )

        self.setCentralWidget(self.view)

    def _setup_ui(self):
        """Setup UI components."""
        self._setup_docks()
        self._setup_status_bar()
        self._setup_menus()

    def _setup_docks(self):
        """Setup dockable panels."""
        # Sheets manager dock
        self._setup_sheets_dock()

        # Viewport properties dock
        self._setup_viewport_dock()

    def _setup_sheets_dock(self):
        """Setup the sheets management dock."""
        dock = QtWidgets.QDockWidget("Sheets", self)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Sheets list
        self.lst_sheets = QtWidgets.QListWidget()
        self.lst_sheets.currentRowChanged.connect(self.switch_sheet)

        # Buttons
        btns = QtWidgets.QHBoxLayout()
        b_add = QtWidgets.QPushButton("Add")
        b_ren = QtWidgets.QPushButton("Rename")
        b_del = QtWidgets.QPushButton("Delete")
        b_up = QtWidgets.QPushButton("Up")
        b_dn = QtWidgets.QPushButton("Down")

        btns.addWidget(b_add)
        btns.addWidget(b_ren)
        btns.addWidget(b_del)
        btns.addWidget(b_up)
        btns.addWidget(b_dn)

        lay.addWidget(self.lst_sheets)
        lay.addLayout(btns)
        dock.setWidget(w)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # Connect buttons
        b_add.clicked.connect(self.add_sheet)
        b_ren.clicked.connect(self.rename_sheet)
        b_del.clicked.connect(self.delete_sheet)
        b_up.clicked.connect(lambda: self.move_sheet(-1))
        b_dn.clicked.connect(lambda: self.move_sheet(1))

    def _setup_viewport_dock(self):
        """Setup viewport properties dock."""
        dock = QtWidgets.QDockWidget("Viewport Properties", self)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Viewport controls will be populated when viewport is selected
        self.viewport_label = QtWidgets.QLabel("Select a viewport to edit properties")
        lay.addWidget(self.viewport_label)

        dock.setWidget(w)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _setup_status_bar(self):
        """Setup the status bar."""
        self.statusBar().showMessage("Paperspace - Ready")

        # Add sheet indicator
        self.sheet_label = QtWidgets.QLabel("Sheet 1")
        self.statusBar().addPermanentWidget(self.sheet_label)

    def _setup_menus(self):
        """Setup menus using global menu bar."""
        # Use global menu bar from app controller
        self.app_controller.create_global_menu_bar(self)

        # Add window-specific menus after global ones
        menubar = self.menuBar()

        # View menu for paperspace specific options
        view_menu = menubar.addMenu("&View")
        self.act_add_viewport = QtGui.QAction("Add Viewport", self)
        self.act_add_viewport.triggered.connect(self.add_viewport)
        view_menu.addAction(self.act_add_viewport)

        # Sheet menu
        sheet_menu = menubar.addMenu("&Sheet")
        self.act_new_sheet = QtGui.QAction("New Sheet", self)
        self.act_new_sheet.triggered.connect(self.add_sheet)
        sheet_menu.addAction(self.act_new_sheet)

    def _connect_signals(self):
        """Connect to app controller signals."""
        # Connect to app controller signals for inter-window communication
        self.app_controller.model_space_changed.connect(self.on_model_space_changed)
        self.app_controller.paperspace_changed.connect(self.on_paperspace_changed)
        self.app_controller.project_changed.connect(self.on_project_changed)

    def on_model_space_changed(self, change_data):
        """Handle model space changes - update viewports."""
        change_type = change_data.get("type", "general")
        if change_type in ["device_placed", "scene_updated"]:
            # Update all viewports to reflect model space changes
            for sheet in self.sheets:
                for item in sheet["scene"].items():
                    if hasattr(item, "update_viewport"):
                        item.update_viewport()

    def on_paperspace_changed(self, change_data):
        """Handle paperspace changes from other windows."""
        change_data.get("type", "general")
        # Handle paperspace-specific changes
        pass

    def on_project_changed(self, change_data):
        """Handle project state changes."""
        change_type = change_data.get("type", "general")
        if change_type == "new_project":
            # Reset to single sheet
            self.sheets = []
            self._create_new_sheet()
        elif change_type == "project_loaded":
            # Refresh sheet display
            self._update_sheet_list()

    def _update_sheet_list(self):
        """Update the sheet list widget to reflect current sheets."""
        self.lst_sheets.clear()
        for sheet in self.sheets:
            item = QtWidgets.QListWidgetItem(sheet["name"])
            self.lst_sheets.addItem(item)
        # Select current sheet
        if self.sheets:
            self.lst_sheets.setCurrentRow(len(self.sheets) - 1)

    def _create_new_sheet(self, name=None):
        """Create a new sheet."""
        if name is None:
            name = f"Sheet {len(self.sheets) + 1}"

        # Create new scene for the sheet
        sc = QtWidgets.QGraphicsScene()
        sc.setBackgroundBrush(QtGui.QColor(250, 250, 250))

        # Add page frame
        pf = PageFrame(
            self.px_per_ft,
            size_name=self.prefs.get("page_size", "Letter"),
            orientation=self.prefs.get("page_orient", "Landscape"),
            margin_in=self.prefs.get("page_margin_in", 0.5),
        )
        sc.addItem(pf)

        # Add title block
        tb = TitleBlock(
            self.px_per_ft,
            size_name=self.prefs.get("page_size", "Letter"),
            orientation=self.prefs.get("page_orient", "Landscape"),
            meta={
                "project": self.prefs.get("proj_project", ""),
                "address": self.prefs.get("proj_address", ""),
                "sheet": name,
                "date": self.prefs.get("proj_date", ""),
                "by": self.prefs.get("proj_by", ""),
            },
        )
        sc.addItem(tb)

        # Store sheet
        self.sheets.append({"name": name, "scene": sc})

        # Switch to new sheet
        self.switch_sheet(len(self.sheets) - 1)

        # Update sheets list
        self._refresh_sheets_list()

    def _refresh_sheets_list(self):
        """Refresh the sheets list widget."""
        if not hasattr(self, "lst_sheets"):
            return

        self.lst_sheets.clear()
        for sheet in self.sheets:
            self.lst_sheets.addItem(sheet.get("name", "Sheet"))

        # Select current sheet
        if self.current_sheet_index < self.lst_sheets.count():
            self.lst_sheets.setCurrentRow(self.current_sheet_index)

    def switch_sheet(self, index):
        """Switch to a different sheet."""
        if 0 <= index < len(self.sheets):
            self.current_sheet_index = index
            self.paper_scene = self.sheets[index]["scene"]
            self.view.setScene(self.paper_scene)

            # Update status
            sheet_name = self.sheets[index].get("name", "Sheet")
            self.sheet_label.setText(sheet_name)
            self.statusBar().showMessage(f"Switched to {sheet_name}")

    def add_sheet(self):
        """Add a new sheet."""
        name, ok = QtWidgets.QInputDialog.getText(
            self, "New Sheet", "Sheet name", text=f"Sheet {len(self.sheets) + 1}"
        )
        if ok and name:
            self._create_new_sheet(name)

    def rename_sheet(self):
        """Rename the current sheet."""
        if not self.sheets:
            return

        current_name = self.sheets[self.current_sheet_index]["name"]
        name, ok = QtWidgets.QInputDialog.getText(
            self, "Rename Sheet", "New name", text=current_name
        )
        if ok and name:
            self.sheets[self.current_sheet_index]["name"] = name
            self._refresh_sheets_list()
            self.sheet_label.setText(name)

    def delete_sheet(self):
        """Delete the current sheet."""
        if len(self.sheets) <= 1:
            QMessageBox.warning(self, "Sheets", "At least one sheet is required.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Sheet",
            f"Delete '{self.sheets[self.current_sheet_index]['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.sheets[self.current_sheet_index]
            if self.current_sheet_index >= len(self.sheets):
                self.current_sheet_index = len(self.sheets) - 1
            self.switch_sheet(self.current_sheet_index)
            self._refresh_sheets_list()

    def move_sheet(self, delta):
        """Move sheet up/down in the list."""
        new_index = self.current_sheet_index + delta
        if 0 <= new_index < len(self.sheets):
            # Swap sheets
            self.sheets[self.current_sheet_index], self.sheets[new_index] = (
                self.sheets[new_index],
                self.sheets[self.current_sheet_index],
            )
            self.current_sheet_index = new_index
            self._refresh_sheets_list()

    def add_viewport(self):
        """Add a viewport to the current sheet."""
        if not self.paper_scene:
            return

        # Calculate page bounds (simplified)
        page_rect = QtCore.QRectF(50, 50, 700, 500)  # Letter landscape approximation

        # Create viewport
        vp = ViewportItem(self.model_scene, page_rect, self)
        self.paper_scene.addItem(vp)

        self.statusBar().showMessage("Viewport added")

    def get_sheets_state(self):
        """Get sheets state for serialization."""
        # This will be implemented when we add project save/load
        return {"sheets": self.sheets.copy() if self.sheets else []}

    def load_sheets_state(self, data):
        """Load sheets state from serialized data."""
        # This will be implemented when we add project save/load
        pass

    def closeEvent(self, event):
        """Handle window close event."""
        # Notify controller about window closing
        if hasattr(self.app_controller, "on_paperspace_closed"):
            self.app_controller.on_paperspace_closed()
        event.accept()
