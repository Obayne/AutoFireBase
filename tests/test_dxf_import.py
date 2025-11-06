import os
from unittest.mock import Mock, patch

import pytest
from PySide6 import QtCore

import app.dxf_import as dxf_import


class TestDXFImport:
    """Test DXF import functionality."""

    def test_aci_to_qcolor(self):
        """Test AutoCAD Color Index to QColor conversion."""
        # Test known colors
        assert dxf_import._aci_to_qcolor(1).name() == "#ff0000"  # Red
        assert dxf_import._aci_to_qcolor(2).name() == "#ffff00"  # Yellow
        assert dxf_import._aci_to_qcolor(7).name() == "#ffffff"  # White

        # Test default/fallback
        assert dxf_import._aci_to_qcolor(999).name() == "#cccccc"  # Gray fallback
        assert dxf_import._aci_to_qcolor(0).name() == "#ffffff"  # Zero -> 7 (white)

    def test_insunits_to_feet(self):
        """Test INSUNITS conversion to feet per unit."""
        # Test common units
        assert dxf_import._insunits_to_feet(0) == 1.0  # Unitless -> feet
        assert dxf_import._insunits_to_feet(1) == 1.0 / 12.0  # Inches
        assert dxf_import._insunits_to_feet(2) == 1.0  # Feet
        assert dxf_import._insunits_to_feet(3) == pytest.approx(0.003280839895)  # mm
        assert dxf_import._insunits_to_feet(4) == pytest.approx(0.03280839895)  # cm
        assert dxf_import._insunits_to_feet(5) == pytest.approx(3.280839895)  # m

        # Test default/fallback
        assert dxf_import._insunits_to_feet(999) == 1.0

    @patch("ezdxf.readfile")
    def test_build_paths_basic(self, mock_readfile):
        """Test basic path building from DXF document."""
        # Create mock DXF document
        mock_doc = Mock()
        _mock_msp = Mock()
        mock_doc.modelspace.return_value = []
        mock_doc.header = {}
        mock_readfile.return_value = mock_doc

        # Test with empty document
        result = dxf_import._build_paths(mock_doc, 96.0)  # 96 px/ft
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_import_dxf_into_group_missing_ezdxf(self):
        """Test that import fails gracefully when ezdxf is not available."""
        with patch.dict("sys.modules", {"ezdxf": None}):
            with pytest.raises(RuntimeError, match="DXF support not available"):
                dxf_import.import_dxf_into_group("dummy.dxf", Mock(), 96.0)

    def test_import_dxf_into_group_with_sample_file(self):
        """Test importing the sample DXF file if ezdxf is available."""
        sample_file = "c:\\Dev\\Autofire\\Projects\\Star-Wars-Logo.dxf"

        if not os.path.exists(sample_file):
            pytest.skip("Sample DXF file not found")

        # Skip this test if running in headless environment without Qt
        try:
            from PySide6 import QtWidgets

            app = QtWidgets.QApplication.instance()
            if app is None:
                app = QtWidgets.QApplication([])
        except Exception:
            pytest.skip("Qt not available in test environment")

        try:
            # Create a real graphics group for testing
            group = QtWidgets.QGraphicsItemGroup()
            bounds, layer_groups = dxf_import.import_dxf_into_group(sample_file, group, 96.0)

            # Should return a valid bounds rect and layer groups dict
            assert isinstance(bounds, QtCore.QRectF)
            assert isinstance(layer_groups, dict)

            # Should have created some layer groups if the DXF has content
            # (We don't assert specific content since it depends on the DXF file)

        except RuntimeError as e:
            if "DXF support not available" in str(e):
                pytest.skip("ezdxf not available in test environment")
            else:
                raise
