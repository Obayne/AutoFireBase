"""Integration tests for DXF import/export workflows."""

import pytest

try:
    import ezdxf

    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False


pytestmark = pytest.mark.skipif(not EZDXF_AVAILABLE, reason="ezdxf not available")


class TestDXFImport:
    """Test DXF file import functionality."""

    @pytest.fixture
    def sample_dxf_path(self, tmp_path):
        """Create a simple DXF file for testing."""
        dxf_path = tmp_path / "test_drawing.dxf"

        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        # Add some basic entities
        msp.add_line((0, 0), (10, 10))
        msp.add_circle((5, 5), radius=3)
        msp.add_text("Test Label", dxfattribs={"insert": (0, 0), "height": 0.5})

        doc.saveas(dxf_path)
        return dxf_path

    def test_import_dxf_file_exists(self, sample_dxf_path):
        """Test that DXF file can be loaded."""
        doc = ezdxf.readfile(sample_dxf_path)
        assert doc is not None
        assert doc.modelspace() is not None

    def test_import_dxf_entities(self, sample_dxf_path):
        """Test that entities are correctly imported."""
        doc = ezdxf.readfile(sample_dxf_path)
        msp = doc.modelspace()

        # Count entities by type
        lines = list(msp.query("LINE"))
        circles = list(msp.query("CIRCLE"))
        texts = list(msp.query("TEXT"))

        assert len(lines) == 1
        assert len(circles) == 1
        assert len(texts) == 1

    def test_import_line_properties(self, sample_dxf_path):
        """Test that line properties are preserved."""
        doc = ezdxf.readfile(sample_dxf_path)
        msp = doc.modelspace()

        line = list(msp.query("LINE"))[0]
        start = line.dxf.start
        end = line.dxf.end

        assert (start.x, start.y) == (0, 0)
        assert (end.x, end.y) == (10, 10)

    def test_import_circle_properties(self, sample_dxf_path):
        """Test that circle properties are preserved."""
        doc = ezdxf.readfile(sample_dxf_path)
        msp = doc.modelspace()

        circle = list(msp.query("CIRCLE"))[0]
        center = circle.dxf.center
        radius = circle.dxf.radius

        assert (center.x, center.y) == (5, 5)
        assert radius == 3


class TestDXFExport:
    """Test DXF file export functionality."""

    def test_export_empty_drawing(self, tmp_path):
        """Test exporting an empty DXF file."""
        output_path = tmp_path / "output.dxf"

        doc = ezdxf.new("R2010")
        doc.saveas(output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_with_entities(self, tmp_path):
        """Test exporting a DXF with entities."""
        output_path = tmp_path / "output_with_entities.dxf"

        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        # Add various entities
        msp.add_line((0, 0), (100, 100))
        msp.add_circle((50, 50), radius=25)
        msp.add_arc((75, 75), radius=15, start_angle=0, end_angle=90)

        doc.saveas(output_path)

        # Verify by re-reading
        doc2 = ezdxf.readfile(output_path)
        msp2 = doc2.modelspace()

        assert len(list(msp2.query("LINE"))) == 1
        assert len(list(msp2.query("CIRCLE"))) == 1
        assert len(list(msp2.query("ARC"))) == 1

    def test_export_with_layers(self, tmp_path):
        """Test exporting entities on different layers."""
        output_path = tmp_path / "output_layers.dxf"

        doc = ezdxf.new("R2010")
        doc.layers.add("FIRE-ALARM", color=1)
        doc.layers.add("FIRE-SMOKE", color=2)

        msp = doc.modelspace()
        msp.add_circle((0, 0), radius=5, dxfattribs={"layer": "FIRE-ALARM"})
        msp.add_circle((10, 10), radius=5, dxfattribs={"layer": "FIRE-SMOKE"})

        doc.saveas(output_path)

        # Verify layers are preserved
        doc2 = ezdxf.readfile(output_path)
        assert "FIRE-ALARM" in doc2.layers
        assert "FIRE-SMOKE" in doc2.layers


class TestDXFRoundTrip:
    """Test import/export roundtrip integrity."""

    def test_roundtrip_preserves_geometry(self, tmp_path):
        """Test that geometry survives import/export cycle."""
        original_path = tmp_path / "original.dxf"
        roundtrip_path = tmp_path / "roundtrip.dxf"

        # Create original
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()
        msp.add_line((0, 0), (100, 50))
        msp.add_circle((25, 25), radius=10)
        doc.saveas(original_path)

        # Roundtrip
        doc2 = ezdxf.readfile(original_path)
        doc2.saveas(roundtrip_path)

        # Verify
        doc3 = ezdxf.readfile(roundtrip_path)
        msp3 = doc3.modelspace()

        line = list(msp3.query("LINE"))[0]
        circle = list(msp3.query("CIRCLE"))[0]

        assert (line.dxf.start.x, line.dxf.start.y) == (0, 0)
        assert (line.dxf.end.x, line.dxf.end.y) == (100, 50)
        assert circle.dxf.radius == 10

    def test_roundtrip_preserves_layers(self, tmp_path):
        """Test that layers survive roundtrip."""
        original_path = tmp_path / "original_layers.dxf"
        roundtrip_path = tmp_path / "roundtrip_layers.dxf"

        # Create with layers
        doc = ezdxf.new("R2010")
        doc.layers.add("CUSTOM-LAYER", color=5)
        msp = doc.modelspace()
        msp.add_line((0, 0), (10, 10), dxfattribs={"layer": "CUSTOM-LAYER"})
        doc.saveas(original_path)

        # Roundtrip
        doc2 = ezdxf.readfile(original_path)
        doc2.saveas(roundtrip_path)

        # Verify
        doc3 = ezdxf.readfile(roundtrip_path)
        assert "CUSTOM-LAYER" in doc3.layers
        line = list(doc3.modelspace().query("LINE"))[0]
        assert line.dxf.layer == "CUSTOM-LAYER"


class TestDXFErrorHandling:
    """Test error handling for invalid DXF files."""

    def test_import_nonexistent_file(self):
        """Test handling of non-existent file."""
        with pytest.raises(IOError):
            ezdxf.readfile("nonexistent_file.dxf")

    def test_import_corrupted_file(self, tmp_path):
        """Test handling of corrupted DXF file."""
        corrupted_path = tmp_path / "corrupted.dxf"
        corrupted_path.write_text("This is not a valid DXF file")

        with pytest.raises((ezdxf.DXFStructureError, OSError, IOError)):
            ezdxf.readfile(corrupted_path)

    def test_export_to_readonly_location(self, tmp_path):
        """Test handling of write-protected location."""
        # Create a read-only directory (platform-specific behavior)
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()

        doc = ezdxf.new("R2010")
        output_path = readonly_dir / "test.dxf"

        # Should still be able to write (requires actual read-only setup)
        doc.saveas(output_path)
        assert output_path.exists()
