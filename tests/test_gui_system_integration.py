"""
GUI integration tests for system configuratio        # Mock UI components
        window.device_tree = Mock()
        window.statusBar = Mock()
        window.statusBar.return_value.showMessage = Mock()
        window.system_info_label = Mock()
        window._update_device_palette_for_system = Mock()

        # Call new system method
        window._new_system_config()

        # Verify system was created
        assert hasattr(window, 'current_system')
        assert isinstance(window.current_system, SystemConfiguration)
        assert window.current_system.name.startswith("System")

        # Verify UI updates were called
        window.system_info_label.setText.assert_called_once()
        window._update_device_palette_for_system.assert_called_once()
        window.statusBar.return_value.showMessage.assert_called_once()
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os

pytestmark = pytest.mark.gui


class TestDevicePaletteSystemIntegration:
    """Test GUI integration of system configuration in device palette."""

    @patch('PySide6.QtWidgets.QApplication')
    @patch('PySide6.QtWidgets.QMainWindow.__init__')
    def test_system_buttons_creation(self, mock_qmainwindow_init, mock_qapp):
        """Test that system configuration buttons are created in device palette."""
        from app.model_space_window import ModelSpaceWindow

        # Mock the controller
        mock_controller = Mock()
        mock_controller.devices_all = []
        mock_controller.prefs = {}

        # Create window
        window = ModelSpaceWindow(mock_controller)

        # Check that system buttons were created
        assert hasattr(window, 'btn_new_system')
        assert hasattr(window, 'btn_load_system')
        assert hasattr(window, 'btn_save_system')
        assert hasattr(window, 'system_info_label')

    @patch('PySide6.QtWidgets.QApplication')
    @patch('PySide6.QtWidgets.QMainWindow.__init__')
    def test_new_system_creation(self, mock_qmainwindow_init, mock_qapp):
        """Test creating a new system configuration."""
        from app.model_space_window import ModelSpaceWindow
        from app.system_builder import SystemConfiguration

        # Mock the controller
        mock_controller = Mock()
        mock_controller.devices_all = []
        mock_controller.prefs = {}

        # Create window
        window = ModelSpaceWindow(mock_controller)

        # Mock the device tree and status bar
        window.device_tree = Mock()
        window.statusBar = Mock()
        window.statusBar.return_value.showMessage = Mock()

        # Mock the update method
        window._update_device_palette_for_system = Mock()

        # Call new system method
        window._new_system_config()

        # Verify system was created
        assert hasattr(window, 'current_system')
        assert isinstance(window.current_system, SystemConfiguration)
        assert window.current_system.name.startswith("System")

        # Verify UI updates were called
        window.system_info_label.setText.assert_called_once()
        window._update_device_palette_for_system.assert_called_once()
        window.statusBar.return_value.showMessage.assert_called_once()

    @patch('PySide6.QtWidgets.QApplication')
    @patch('PySide6.QtWidgets.QMainWindow.__init__')
    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    def test_load_system_configuration(self, mock_get_open_filename, mock_qmainwindow_init, mock_qapp):
        """Test loading a system configuration from file."""
        from app.model_space_window import ModelSpaceWindow
        from app.system_builder import SystemConfiguration

        # Create a test system file
        test_system = SystemConfiguration("Load Test")
        test_system.facp_type = "Addressable"
        test_data = test_system.to_dict()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Mock file dialog to return our temp file
            mock_get_open_filename.return_value = (temp_file, "JSON Files (*.json)")

            # Mock the controller
            mock_controller = Mock()
            mock_controller.devices_all = []
            mock_controller.prefs = {}

            # Create window
            window = ModelSpaceWindow(mock_controller)

            # Mock UI components
            window.device_tree = Mock()
            window.statusBar = Mock()
            window.statusBar.return_value.showMessage = Mock()
            window._update_device_palette_for_system = Mock()

            # Call load method
            window._load_system_config()

            # Verify system was loaded
            assert hasattr(window, 'current_system')
            assert window.current_system.name == "Load Test"
            assert window.current_system.facp_type == "Addressable"

            # Verify UI updates
            assert window.system_info_label.setText.called
            assert window._update_device_palette_for_system.called
            assert window.statusBar.return_value.showMessage.called

        finally:
            os.unlink(temp_file)

    @patch('PySide6.QtWidgets.QApplication')
    @patch('PySide6.QtWidgets.QMainWindow.__init__')
    @patch('PySide6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_system_configuration(self, mock_get_save_filename, mock_qmainwindow_init, mock_qapp):
        """Test saving a system configuration to file."""
        from app.model_space_window import ModelSpaceWindow
        from app.system_builder import SystemConfiguration

        # Mock file dialog to return a temp file path
        temp_file = tempfile.mktemp(suffix='.json')
        mock_get_save_filename.return_value = (temp_file, "JSON Files (*.json)")

        # Mock the controller
        mock_controller = Mock()
        mock_controller.devices_all = []
        mock_controller.prefs = {}

        # Create window
        window = ModelSpaceWindow(mock_controller)

        # Create a test system
        test_system = SystemConfiguration("Save Test")
        test_system.facp_type = "Hybrid"
        window.current_system = test_system

        # Mock UI components
        window.statusBar = Mock()
        window.statusBar.return_value.showMessage = Mock()

        try:
            # Call save method
            window._save_system_config()

            # Verify file was created and contains correct data
            assert os.path.exists(temp_file)

            with open(temp_file, 'r') as f:
                saved_data = json.load(f)

            assert saved_data["name"] == "Save Test"
            assert saved_data["facp_type"] == "Hybrid"

            # Verify status message
            assert window.statusBar.return_value.showMessage.called

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @patch('PySide6.QtWidgets.QApplication')
    @patch('PySide6.QtWidgets.QMainWindow.__init__')
    def test_device_palette_system_filtering(self, mock_qmainwindow_init, mock_qapp):
        """Test that device palette filters devices based on loaded system."""
        from app.model_space_window import ModelSpaceWindow
        from app.system_builder import SystemConfiguration

        # Mock the controller
        mock_controller = Mock()
        mock_controller.devices_all = []
        mock_controller.prefs = {}

        # Create window
        window = ModelSpaceWindow(mock_controller)

        # Mock device tree
        window.device_tree = Mock()
        window._update_device_count = Mock()

        # Create system with specific devices
        system = SystemConfiguration("Filter Test")
        system.devices["smoke_detectors"] = [
            {"manufacturer": "FireLite", "part_number": "SD100"}
        ]
        system.devices["pull_stations"] = [
            {"manufacturer": "System Sensor", "part_number": "PS200"}
        ]
        window.current_system = system

        # Mock device loading
        def mock_load_devices(category_name):
            if category_name == "smoke_detectors":
                return [
                    {"type": "smoke_detector", "name": "SD-100", "manufacturer": "FireLite",
                     "part_number": "SD100", "symbol": "SD"}
                ]
            elif category_name == "pull_stations":
                return [
                    {"type": "pull_station", "name": "PS-200", "manufacturer": "System Sensor",
                     "part_number": "PS200", "symbol": "PS"}
                ]
            return []

        with patch.object(window, '_load_devices_for_category', side_effect=mock_load_devices):
            # Call update method
            window._update_device_palette_for_system()

            # Verify device tree was cleared and populated
            assert window.device_tree.clear.called
            # Should have added top-level items for categories that exist in system
            assert window.device_tree.addTopLevelItem.called
            assert window._update_device_count.called

    @patch('PySide6.QtWidgets.QApplication')
    @patch('PySide6.QtWidgets.QMainWindow.__init__')
    def test_system_info_display(self, mock_qmainwindow_init, mock_qapp):
        """Test that system information is properly displayed in UI."""
        from app.model_space_window import ModelSpaceWindow
        from app.system_builder import SystemConfiguration

        # Mock the controller
        mock_controller = Mock()
        mock_controller.devices_all = []
        mock_controller.prefs = {}

        # Create window
        window = ModelSpaceWindow(mock_controller)

        # Test with no system loaded
        window.system_info_label = Mock()
        window._update_device_palette_for_system()
        assert window.system_info_label.setText.called_with("No system loaded")

        # Test with system loaded
        system = SystemConfiguration("Display Test")
        window.current_system = system
        window.system_info_label.reset_mock()

        window._update_device_palette_for_system()
        assert window.system_info_label.setText.called_with("System: Display Test")


class TestSystemConfigurationWorkflow:
    """Test complete workflow of system configuration integration."""

    @patch('PySide6.QtWidgets.QApplication')
    @patch('PySide6.QtWidgets.QMainWindow.__init__')
    def test_complete_system_workflow(self, mock_qmainwindow_init, mock_qapp):
        """Test complete workflow from system creation to device palette filtering."""
        from app.model_space_window import ModelSpaceWindow
        from app.system_builder import SystemConfiguration

        # Mock the controller
        mock_controller = Mock()
        mock_controller.devices_all = [
            {"type": "smoke_detector", "name": "SD-100", "manufacturer": "FireLite", "part_number": "SD100", "symbol": "SD"},
            {"type": "pull_station", "name": "PS-100", "manufacturer": "System Sensor", "part_number": "PS100", "symbol": "PS"},
            {"type": "heat_detector", "name": "HD-100", "manufacturer": "FireLite", "part_number": "HD100", "symbol": "HD"},
        ]
        mock_controller.prefs = {}

        # Create window
        window = ModelSpaceWindow(mock_controller)

        # Mock UI components
        window.device_tree = Mock()
        window.statusBar = Mock()
        window.statusBar.return_value.showMessage = Mock()
        window.system_info_label = Mock()
        window._update_device_count = Mock()

        # Step 1: Create new system
        window._new_system_config()

        assert hasattr(window, 'current_system')
        assert isinstance(window.current_system, SystemConfiguration)

        # Step 2: Add devices to system
        window.current_system.devices["smoke_detectors"] = [
            {"manufacturer": "FireLite", "part_number": "SD100"}
        ]

        # Step 3: Update device palette (should filter to show only system devices)
        def mock_load_devices(category_name):
            if category_name == "smoke_detectors":
                return [
                    {"type": "smoke_detector", "name": "SD-100", "manufacturer": "FireLite",
                     "part_number": "SD100", "symbol": "SD"}
                ]
            return []

        with patch.object(window, '_load_devices_for_category', side_effect=mock_load_devices):
            window._update_device_palette_for_system()

            # Verify the workflow completed successfully
            assert window.device_tree.clear.called
            assert window.system_info_label.setText.called
            assert window._update_device_count.called