"""
Unified file format converter for AutoFire.

Handles conversion between:
- DXF ↔ DWG (via ezdxf + ODA File Converter if available)
- DXF → AutoFire (.autofire JSON)
- PDF → DXF (via vectorization)
- AutoFire → DXF (export)

Philosophy: Handle all CAD file formats users throw at us.
"""

import json
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class FileFormatError(Exception):
    """Raised when file format is unsupported or invalid."""

    pass


class ConversionError(Exception):
    """Raised when file conversion fails."""

    pass


class FileConverter:
    """Unified file format converter."""

    SUPPORTED_FORMATS = {
        "input": [".dxf", ".dwg", ".pdf", ".autofire", ".json"],
        "output": [".dxf", ".dwg", ".autofire", ".json", ".pdf"],
    }

    def __init__(self, oda_path: Path | None = None):
        """
        Initialize converter.

        Args:
            oda_path: Path to ODA File Converter executable (for DWG support)
        """
        self.oda_path = oda_path or self._find_oda_converter()
        self.has_dwg_support = self.oda_path is not None

    def _find_oda_converter(self) -> Path | None:
        """Try to locate ODA File Converter on system."""
        # Common install locations
        possible_paths = [
            Path("C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe"),
            Path("C:/Program Files (x86)/ODA/ODAFileConverter/ODAFileConverter.exe"),
            Path.home() / "ODA" / "ODAFileConverter.exe",
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"Found ODA File Converter at {path}")
                return path

        # Try system PATH
        oda_exe = shutil.which("ODAFileConverter")
        if oda_exe:
            logger.info(f"Found ODA File Converter in PATH: {oda_exe}")
            return Path(oda_exe)

        logger.warning("ODA File Converter not found - DWG support unavailable")
        return None

    def detect_format(self, file_path: str | Path) -> str:
        """
        Detect file format from extension and content.

        Args:
            file_path: Path to file

        Returns:
            Normalized format string (.dxf, .dwg, .pdf, .autofire)

        Raises:
            FileFormatError: If format cannot be detected
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext not in self.SUPPORTED_FORMATS["input"]:
            raise FileFormatError(f"Unsupported file format: {ext}")

        # Normalize .json to .autofire if it contains AutoFire schema
        if ext == ".json":
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    if "version" in data and "devices" in data:
                        return ".autofire"
            except Exception:
                pass

        return ext

    def convert(self, input_path: str | Path, output_path: str | Path, **options) -> Path:
        """
        Convert file from one format to another.

        Args:
            input_path: Source file path
            output_path: Destination file path
            **options: Format-specific conversion options

        Returns:
            Path to converted file

        Raises:
            FileFormatError: If formats are unsupported
            ConversionError: If conversion fails
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        input_fmt = self.detect_format(input_path)
        output_fmt = output_path.suffix.lower()

        if output_fmt not in self.SUPPORTED_FORMATS["output"]:
            raise FileFormatError(f"Unsupported output format: {output_fmt}")

        # Route to appropriate converter
        if input_fmt == output_fmt:
            # Just copy
            shutil.copy2(input_path, output_path)
            return output_path

        if input_fmt == ".dwg" and output_fmt == ".dxf":
            return self._dwg_to_dxf(input_path, output_path)

        if input_fmt == ".dxf" and output_fmt == ".dwg":
            return self._dxf_to_dwg(input_path, output_path)

        if input_fmt == ".dxf" and output_fmt in [".autofire", ".json"]:
            return self._dxf_to_autofire(input_path, output_path, **options)

        if input_fmt in [".autofire", ".json"] and output_fmt == ".dxf":
            return self._autofire_to_dxf(input_path, output_path, **options)

        if input_fmt == ".pdf" and output_fmt == ".dxf":
            return self._pdf_to_dxf(input_path, output_path, **options)

        raise ConversionError(f"Conversion not supported: {input_fmt} → {output_fmt}")

    def _dwg_to_dxf(self, dwg_path: Path, dxf_path: Path) -> Path:
        """Convert DWG to DXF using ODA File Converter."""
        if not self.has_dwg_support:
            raise ConversionError(
                "DWG conversion requires ODA File Converter. "
                "Download from https://www.opendesign.com/guestfiles/oda_file_converter"
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_out = Path(tmpdir) / "output"
            tmp_out.mkdir()

            # ODA File Converter command
            cmd = [
                str(self.oda_path),
                str(dwg_path.parent),
                str(tmp_out),
                "ACAD2018",  # Output DXF version
                "DXF",  # Output format
                "0",  # Recurse subdirectories: no
                "1",  # Audit: yes
                str(dwg_path.name),  # Filter for specific file
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
                logger.debug(f"ODA output: {result.stdout}")

                # Find converted file
                converted = list(tmp_out.glob("*.dxf"))
                if not converted:
                    raise ConversionError("ODA File Converter produced no output")

                shutil.copy2(converted[0], dxf_path)
                logger.info(f"Converted DWG → DXF: {dxf_path}")
                return dxf_path

            except subprocess.TimeoutExpired:
                raise ConversionError("DWG conversion timed out")
            except subprocess.CalledProcessError as e:
                raise ConversionError(f"DWG conversion failed: {e.stderr}")

    def _dxf_to_dwg(self, dxf_path: Path, dwg_path: Path) -> Path:
        """Convert DXF to DWG using ODA File Converter."""
        if not self.has_dwg_support:
            raise ConversionError(
                "DWG conversion requires ODA File Converter. "
                "Download from https://www.opendesign.com/guestfiles/oda_file_converter"
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_out = Path(tmpdir) / "output"
            tmp_out.mkdir()

            cmd = [
                str(self.oda_path),
                str(dxf_path.parent),
                str(tmp_out),
                "ACAD2018",  # Output DWG version
                "DWG",  # Output format
                "0",  # Recurse subdirectories: no
                "1",  # Audit: yes
                str(dxf_path.name),  # Filter for specific file
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
                logger.debug(f"ODA output: {result.stdout}")

                converted = list(tmp_out.glob("*.dwg"))
                if not converted:
                    raise ConversionError("ODA File Converter produced no output")

                shutil.copy2(converted[0], dwg_path)
                logger.info(f"Converted DXF → DWG: {dwg_path}")
                return dwg_path

            except subprocess.TimeoutExpired:
                raise ConversionError("DXF→DWG conversion timed out")
            except subprocess.CalledProcessError as e:
                raise ConversionError(f"DXF→DWG conversion failed: {e.stderr}")

    def _dxf_to_autofire(self, dxf_path: Path, autofire_path: Path, **options) -> Path:
        """
        Convert DXF to AutoFire format using Layer Intelligence.

        Args:
            dxf_path: Input DXF file
            autofire_path: Output .autofire file
            **options: layer_patterns, confidence_threshold

        Returns:
            Path to .autofire file
        """
        try:
            import ezdxf
        except ImportError:
            raise ConversionError("DXF conversion requires ezdxf: pip install ezdxf")

        try:
            # Load DXF
            doc = ezdxf.readfile(str(dxf_path))
            msp = doc.modelspace()

            # Extract geometry and layer info
            devices = []
            geometry = []

            for entity in msp:
                layer = entity.dxf.layer
                dxf_type = entity.dxftype()

                # Detect fire devices (circles on fire-related layers)
                if dxf_type == "CIRCLE":
                    center = entity.dxf.center
                    radius = entity.dxf.radius

                    # Simple heuristic: circles on FIRE/SPRINKLER/ALARM layers
                    if any(
                        kw in layer.upper()
                        for kw in ["FIRE", "SPRINKLER", "ALARM", "DEVICE", "HEAD"]
                    ):
                        devices.append(
                            {
                                "type": "sprinkler",  # Default, could enhance with AI
                                "x": center[0],
                                "y": center[1],
                                "layer": layer,
                                "source": "dxf_import",
                            }
                        )
                    else:
                        # Generic circle geometry
                        geometry.append(
                            {
                                "type": "circle",
                                "center": [center[0], center[1]],
                                "radius": radius,
                                "layer": layer,
                            }
                        )

                elif dxf_type == "LINE":
                    start = entity.dxf.start
                    end = entity.dxf.end
                    geometry.append(
                        {
                            "type": "line",
                            "start": [start[0], start[1]],
                            "end": [end[0], end[1]],
                            "layer": layer,
                        }
                    )

                elif dxf_type in ["LWPOLYLINE", "POLYLINE"]:
                    points = []
                    if dxf_type == "LWPOLYLINE":
                        points = [[v[0], v[1]] for v in entity.get_points()]
                    else:
                        points = [[v.dxf.location[0], v.dxf.location[1]] for v in entity.vertices]

                    geometry.append({"type": "polyline", "points": points, "layer": layer})

            # Create AutoFire JSON
            autofire_data = {
                "version": "0.4.7",
                "source": str(dxf_path),
                "devices": devices,
                "geometry": geometry,
                "units": "feet",  # Could detect from DXF $INSUNITS
                "metadata": {
                    "converted_from": "dxf",
                    "device_count": len(devices),
                    "geometry_count": len(geometry),
                },
            }

            # Write AutoFire JSON
            with open(autofire_path, "w", encoding="utf-8") as f:
                json.dump(autofire_data, f, indent=2)

            logger.info(
                f"Converted DXF → AutoFire: {len(devices)} devices, {len(geometry)} geometry items"
            )
            return autofire_path

        except Exception as e:
            raise ConversionError(f"DXF→AutoFire conversion failed: {e}")

    def _autofire_to_dxf(self, autofire_path: Path, dxf_path: Path, **options) -> Path:
        """
        Convert AutoFire format to DXF.

        Args:
            autofire_path: Input .autofire file
            dxf_path: Output DXF file
            **options: dxf_version (default ACAD2018)

        Returns:
            Path to DXF file
        """
        try:
            import ezdxf
        except ImportError:
            raise ConversionError("DXF export requires ezdxf: pip install ezdxf")

        try:
            # Load AutoFire JSON
            with open(autofire_path, encoding="utf-8") as f:
                data = json.load(f)

            # Create new DXF
            dxf_version = options.get("dxf_version", "R2018")
            doc = ezdxf.new(dxf_version)
            msp = doc.modelspace()

            # Create layers
            layers_created = set()

            def ensure_layer(name: str):
                if name not in layers_created:
                    doc.layers.add(name, color=7)
                    layers_created.add(name)

            # Add devices as circles
            for device in data.get("devices", []):
                layer = device.get("layer", "DEVICES")
                ensure_layer(layer)

                msp.add_circle(
                    center=(device["x"], device["y"]),
                    radius=0.5,  # Default device radius
                    dxfattribs={"layer": layer},
                )

            # Add geometry
            for geom in data.get("geometry", []):
                layer = geom.get("layer", "0")
                ensure_layer(layer)

                if geom["type"] == "line":
                    msp.add_line(
                        start=tuple(geom["start"]),
                        end=tuple(geom["end"]),
                        dxfattribs={"layer": layer},
                    )

                elif geom["type"] == "circle":
                    msp.add_circle(
                        center=tuple(geom["center"]),
                        radius=geom["radius"],
                        dxfattribs={"layer": layer},
                    )

                elif geom["type"] == "polyline":
                    points = [tuple(pt) for pt in geom["points"]]
                    msp.add_lwpolyline(points, dxfattribs={"layer": layer})

            # Save DXF
            doc.saveas(str(dxf_path))
            logger.info(f"Converted AutoFire → DXF: {dxf_path}")
            return dxf_path

        except Exception as e:
            raise ConversionError(f"AutoFire→DXF conversion failed: {e}")

    def _pdf_to_dxf(self, pdf_path: Path, dxf_path: Path, **options) -> Path:
        """
        Convert PDF to DXF via vectorization.

        Note: This is a placeholder - PDF→DXF requires complex vectorization.
        Consider external tools like Inkscape, Adobe Illustrator, or commercial converters.

        Args:
            pdf_path: Input PDF file
            dxf_path: Output DXF file
            **options: page (default 0), dpi (default 300)

        Raises:
            ConversionError: Always (not yet implemented)
        """
        raise ConversionError(
            "PDF→DXF conversion not yet implemented. "
            "Consider external tools: Inkscape (free), Adobe Illustrator, "
            "or commercial converters like Able2Extract, AutoDWG PDF to DXF."
        )

    def batch_convert(
        self, input_files: list[str | Path], output_format: str, **options
    ) -> list[tuple[Path, Path]]:
        """
        Batch convert multiple files to target format.

        Args:
            input_files: List of input file paths
            output_format: Target format (.dxf, .dwg, .autofire)
            **options: Conversion options passed to convert()

        Returns:
            List of (input_path, output_path) tuples

        Raises:
            ConversionError: If any conversion fails
        """
        results = []
        errors = []

        for input_path in input_files:
            input_path = Path(input_path)
            output_path = input_path.with_suffix(output_format)

            try:
                converted = self.convert(input_path, output_path, **options)
                results.append((input_path, converted))
                logger.info(f"✓ {input_path.name} → {converted.name}")

            except Exception as e:
                error_msg = f"✗ {input_path.name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        if errors:
            raise ConversionError(
                f"Batch conversion completed with {len(errors)} errors:\n" + "\n".join(errors)
            )

        return results


# Convenience functions
def convert_file(input_path: str | Path, output_path: str | Path, **options) -> Path:
    """
    Convenience function to convert a single file.

    Args:
        input_path: Source file
        output_path: Destination file
        **options: Conversion options

    Returns:
        Path to converted file
    """
    converter = FileConverter()
    return converter.convert(input_path, output_path, **options)


def detect_format(file_path: str | Path) -> str:
    """Detect file format from path and content."""
    converter = FileConverter()
    return converter.detect_format(file_path)
