"""Tests for frontend bootstrap functionality."""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow

from frontend.bootstrap import (
    log_startup_error,
    create_fallback_window,
    bootstrap_application,
    enhanced_bootstrap,
    main_bootstrap
)


class TestLogStartupError:
    """Test startup error logging."""
    
    def test_log_startup_error_creates_file(self):
        """Test that error logging creates a file."""
        with patch('os.path.expanduser') as mock_expanduser, \
             patch('os.makedirs') as mock_makedirs, \
             patch('builtins.open', create=True) as mock_open:
            
            mock_expanduser.return_value = "/home/user"
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = log_startup_error("Test error message")
            
            # Should have created directories
            mock_makedirs.assert_called_once()
            
            # Should have opened file for writing
            mock_open.assert_called_once()
            
            # Should have written error message
            mock_file.write.assert_called_once()
            args = mock_file.write.call_args[0]
            assert "Test error message" in args[0]
            assert "Frontend bootstrap startup error" in args[0]
            
            # Should return a path
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_log_startup_error_handles_exceptions(self):
        """Test that error logging handles exceptions gracefully."""
        with patch('os.path.expanduser', side_effect=Exception("Mock error")):
            result = log_startup_error("Test error")
            
            # Should return empty string on error
            assert result == ""


class TestCreateFallbackWindow:
    """Test fallback window creation."""
    
    def test_create_fallback_window(self):
        """Test that fallback window is created correctly."""
        # Need QApplication for widget creation
        app = QApplication.instance() or QApplication([])
        
        window = create_fallback_window()
        
        assert isinstance(window, QWidget)
        assert "Auto-Fire" in window.windowTitle()
        assert "Frontend Bootstrap Fallback" in window.windowTitle()
        assert window.width() == 600
        assert window.height() == 320
        
        # Should have a label with error message
        layout = window.layout()
        assert layout is not None
        assert layout.count() > 0


class MockMainWindow:
    """Mock main window for testing."""
    
    def __init__(self):
        self.shown = False
    
    def show(self):
        self.shown = True


class TestBootstrapApplication:
    """Test application bootstrap functionality."""
    
    @patch('frontend.bootstrap.QtWidgets.QApplication')
    def test_bootstrap_application_success(self, mock_app_class):
        """Test successful application bootstrap."""
        # Setup mocks
        mock_app = Mock()
        mock_app_class.instance.return_value = None
        mock_app_class.return_value = mock_app
        
        # Create mock window factory
        mock_window = MockMainWindow()
        def window_factory():
            return mock_window
        
        # Bootstrap should complete without error
        bootstrap_application(window_factory)
        
        # Verify QApplication was created and window was shown
        mock_app_class.assert_called_once_with([])
        assert mock_window.shown
        mock_app.exec.assert_called_once()
    
    @patch('frontend.bootstrap.QtWidgets.QApplication')
    @patch('frontend.bootstrap.log_startup_error')
    @patch('frontend.bootstrap.create_fallback_window')
    def test_bootstrap_application_window_error(self, mock_fallback, mock_log, mock_app_class):
        """Test bootstrap with window creation error."""
        # Setup mocks
        mock_app = Mock()
        mock_app_class.instance.return_value = None
        mock_app_class.return_value = mock_app
        
        mock_fallback_window = Mock()
        mock_fallback.return_value = mock_fallback_window
        mock_log.return_value = "/path/to/log"
        
        # Create failing window factory
        def failing_factory():
            raise Exception("Window creation failed")
        
        # Bootstrap should handle error gracefully
        bootstrap_application(failing_factory)
        
        # Should have logged error and shown fallback
        mock_log.assert_called_once()
        mock_fallback.assert_called_once()
        mock_fallback_window.show.assert_called_once()
        mock_app.exec.assert_called_once()


class TestEnhancedBootstrap:
    """Test enhanced bootstrap with tool integration."""
    
    @patch('frontend.bootstrap.QtWidgets.QApplication')
    def test_enhanced_bootstrap_without_tools(self, mock_app_class):
        """Test enhanced bootstrap without tool integration."""
        # Setup mocks
        mock_app = Mock()
        mock_app_class.instance.return_value = None
        mock_app_class.return_value = mock_app
        
        mock_window = MockMainWindow()
        def window_factory():
            return mock_window
        
        # Bootstrap without tool integration
        enhanced_bootstrap(window_factory, tool_integration=False)
        
        # Should work like regular bootstrap
        assert mock_window.shown
        mock_app.exec.assert_called_once()
    
    @patch('frontend.bootstrap.QtWidgets.QApplication')
    def test_enhanced_bootstrap_with_tools(self, mock_app_class):
        """Test enhanced bootstrap with tool integration."""
        # Setup mocks
        mock_app = Mock()
        mock_app_class.instance.return_value = None
        mock_app_class.return_value = mock_app
        
        mock_window = MockMainWindow()
        def window_factory():
            return mock_window
        
        # Mock the integration functions at module level
        with patch('frontend.integration.integrate_tool_registry') as mock_integrate, \
             patch('frontend.integration.add_registry_command_support') as mock_cmd_support:
            
            # Bootstrap with tool integration
            enhanced_bootstrap(window_factory, tool_integration=True)
            
            # Should have integrated tools
            mock_integrate.assert_called_once_with(mock_window)
            mock_cmd_support.assert_called_once_with(mock_window)
            assert mock_window.shown
            mock_app.exec.assert_called_once()


class TestMainBootstrap:
    """Test legacy compatibility bootstrap."""
    
    @patch('frontend.bootstrap.bootstrap_application')
    def test_main_bootstrap_delegates(self, mock_bootstrap):
        """Test that main_bootstrap delegates to bootstrap_application."""
        def dummy_factory():
            return MockMainWindow()
        
        main_bootstrap(dummy_factory)
        
        # Should have called bootstrap_application
        mock_bootstrap.assert_called_once_with(dummy_factory)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])