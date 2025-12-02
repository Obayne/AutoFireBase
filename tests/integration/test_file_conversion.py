"""
Integration tests for file format conversion.

Tests round-trip conversions:
- DXF → AutoFire → DXF
- DWG → DXF → AutoFire (if ODA available)
- Batch conversions
"""

import json

import pytest

from backend.file_converter import (
    ConversionError,
    FileConverter,
    FileFormatError,
    convert_file,
    detect_format,
)


class TestFormatDetection:
    """Test file format detection."""

    def test_detect_dxf(self, tmp_path):
        """Test DXF detection."""
        dxf_file = tmp_path / "test.dxf"
        dxf_file.write_text("dummy dxf content")

        assert detect_format(dxf_file) == ".dxf"

    def test_detect_dwg(self, tmp_path):
        """Test DWG detection."""
        dwg_file = tmp_path / "test.dwg"
        dwg_file.write_text("dummy dwg content")

        assert detect_format(dwg_file) == ".dwg"

    def test_detect_autofire_json(self, tmp_path):
        """Test AutoFire JSON detection."""
        autofire_file = tmp_path / "test.json"
        autofire_file.write_text(json.dumps({"version": "0.4.7", "devices": []}))

        assert detect_format(autofire_file) == ".autofire"

    def test_detect_generic_json(self, tmp_path):
        """Test generic JSON stays as .json."""
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps({"foo": "bar"}))

        assert detect_format(json_file) == ".json"

    def test_detect_unsupported(self, tmp_path):
        """Test unsupported format raises error."""
        bad_file = tmp_path / "test.xyz"
        bad_file.write_text("dummy")

        with pytest.raises(FileFormatError):
            detect_format(bad_file)


class TestFileConverter:
    """Test FileConverter class."""

    def test_converter_init(self):
        """Test converter initialization."""
        converter = FileConverter()
        assert isinstance(converter, FileConverter)
        # ODA path may or may not be found
        assert isinstance(converter.has_dwg_support, bool)

    def test_supported_formats(self):
        """Test supported formats lists."""
        converter = FileConverter()

        assert ".dxf" in converter.SUPPORTED_FORMATS["input"]
        assert ".dwg" in converter.SUPPORTED_FORMATS["input"]
        assert ".autofire" in converter.SUPPORTED_FORMATS["input"]

        assert ".dxf" in converter.SUPPORTED_FORMATS["output"]
        assert ".autofire" in converter.SUPPORTED_FORMATS["output"]

    def test_convert_same_format_copies(self, tmp_path):
        """Test converting to same format just copies file."""
        src = tmp_path / "input.dxf"
        src.write_text("dummy dxf")

        dst = tmp_path / "output.dxf"

        converter = FileConverter()
        result = converter.convert(src, dst)

        assert result == dst
        assert dst.exists()
        assert dst.read_text() == "dummy dxf"


class TestDXFAutoFireConversion:
    """Test DXF ↔ AutoFire conversion."""

    @pytest.fixture
    def sample_dxf(self, tmp_path):
        """Create a minimal DXF file using ezdxf."""
        pytest.importorskip("ezdxf")
        import ezdxf

        dxf_path = tmp_path / "sample.dxf"

        doc = ezdxf.new("R2018")
        msp = doc.modelspace()

        # Add some geometry
        doc.layers.add("SPRINKLER", color=1)
        doc.layers.add("WALLS", color=7)

        # Add devices as circles on SPRINKLER layer
        msp.add_circle(center=(10, 10), radius=0.5, dxfattribs={"layer": "SPRINKLER"})
        msp.add_circle(center=(20, 10), radius=0.5, dxfattribs={"layer": "SPRINKLER"})

        # Add walls as lines
        msp.add_line(start=(0, 0), end=(30, 0), dxfattribs={"layer": "WALLS"})
        msp.add_line(start=(30, 0), end=(30, 20), dxfattribs={"layer": "WALLS"})

        doc.saveas(str(dxf_path))
        return dxf_path

    def test_dxf_to_autofire(self, sample_dxf, tmp_path):
        """Test DXF to AutoFire conversion."""
        pytest.importorskip("ezdxf")

        autofire_path = tmp_path / "output.autofire"

        converter = FileConverter()
        result = converter.convert(sample_dxf, autofire_path)

        assert result == autofire_path
        assert autofire_path.exists()

        # Validate AutoFire JSON
        with open(autofire_path) as f:
            data = json.load(f)

        assert data["version"] == "0.4.7"
        assert "devices" in data
        assert "geometry" in data

        # Should have detected 2 sprinklers
        assert len(data["devices"]) == 2
        assert all(d["type"] == "sprinkler" for d in data["devices"])

    def test_autofire_to_dxf(self, tmp_path):
        """Test AutoFire to DXF conversion."""
        pytest.importorskip("ezdxf")

        # Create AutoFire file
        autofire_path = tmp_path / "input.autofire"
        autofire_data = {
            "version": "0.4.7",
            "devices": [
                {"type": "sprinkler", "x": 10, "y": 10, "layer": "DEVICES"},
                {"type": "alarm", "x": 20, "y": 10, "layer": "DEVICES"},
            ],
            "geometry": [{"type": "line", "start": [0, 0], "end": [30, 0], "layer": "WALLS"}],
            "units": "feet",
        }

        with open(autofire_path, "w") as f:
            json.dump(autofire_data, f)

        # Convert to DXF
        dxf_path = tmp_path / "output.dxf"

        converter = FileConverter()
        result = converter.convert(autofire_path, dxf_path)

        assert result == dxf_path
        assert dxf_path.exists()

        # Validate DXF
        import ezdxf

        doc = ezdxf.readfile(str(dxf_path))
        msp = doc.modelspace()

        # Should have created entities
        entities = list(msp)
        assert len(entities) > 0

        # Check layers were created
        assert "DEVICES" in doc.layers
        assert "WALLS" in doc.layers


class TestDWGConversion:
    """Test DWG conversion (requires ODA File Converter)."""

    def test_dwg_to_dxf_without_oda(self, tmp_path):
        """Test DWG conversion fails gracefully without ODA."""
        converter = FileConverter(oda_path=None)
        assert not converter.has_dwg_support

        dwg_path = tmp_path / "test.dwg"
        dwg_path.write_text("dummy dwg")

        dxf_path = tmp_path / "output.dxf"

        with pytest.raises(ConversionError, match="ODA File Converter"):
            converter.convert(dwg_path, dxf_path)


class TestBatchConversion:
    """Test batch conversion operations."""

    def test_batch_convert(self, tmp_path):
        """Test batch DXF to AutoFire conversion."""
        pytest.importorskip("ezdxf")
        import ezdxf

        # Create multiple DXF files
        dxf_files = []
        for i in range(3):
            dxf_path = tmp_path / f"file{i}.dxf"
            doc = ezdxf.new("R2018")
            doc.layers.add("FIRE")
            msp = doc.modelspace()
            msp.add_circle(center=(i * 10, 10), radius=0.5, dxfattribs={"layer": "FIRE"})
            doc.saveas(str(dxf_path))
            dxf_files.append(dxf_path)

        # Batch convert
        converter = FileConverter()
        results = converter.batch_convert(dxf_files, ".autofire")

        assert len(results) == 3

        for inp, out in results:
            assert inp.suffix == ".dxf"
            assert out.suffix == ".autofire"
            assert out.exists()


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_convert_file(self, tmp_path):
        """Test convert_file convenience function."""
        src = tmp_path / "input.dxf"
        src.write_text("dummy")

        dst = tmp_path / "output.dxf"

        result = convert_file(src, dst)
        assert result == dst
        assert dst.exists()


class TestErrorHandling:
    """Test error handling."""

    def test_missing_input_file(self, tmp_path):
        """Test conversion with missing input file."""
        converter = FileConverter()

        with pytest.raises(FileNotFoundError):
            converter.convert(tmp_path / "missing.dxf", tmp_path / "output.autofire")

    def test_unsupported_output_format(self, tmp_path):
        """Test conversion to unsupported format."""
        src = tmp_path / "input.dxf"
        src.write_text("dummy")

        dst = tmp_path / "output.xyz"

        converter = FileConverter()

        with pytest.raises(FileFormatError, match="Unsupported output format"):
            converter.convert(src, dst)

    def test_pdf_to_dxf_not_implemented(self, tmp_path):
        """Test PDF to DXF raises not implemented."""
        src = tmp_path / "input.pdf"
        src.write_text("dummy pdf")

        dst = tmp_path / "output.dxf"

        converter = FileConverter()

        with pytest.raises(ConversionError, match="not yet implemented"):
            converter.convert(src, dst)
