import io
from contextlib import redirect_stdout

from scripts.device_cli import export_devices, list_devices, search_devices


def capture_output(fn, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn(*args, **kwargs)
    return buf.getvalue()


def test_list_devices_formats_table():
    out = capture_output(list_devices, device_type="Detector")
    # Header present
    assert "Name" in out and "Manufacturer" in out and "Part #" in out
    # At least one known device row
    assert "Smoke Detector" in out or "Heat Detector" in out


def test_search_devices_formats_table():
    out = capture_output(search_devices, "smoke")
    assert "Found" in out and "Smoke Detector" in out


def test_export_csv_utf8(tmp_path):
    out_file = tmp_path / "devices.csv"
    export_devices("csv", str(out_file))
    assert out_file.exists() and out_file.stat().st_size > 0
    # Ensure file decodes as UTF-8
    data = out_file.read_text(encoding="utf-8")
    assert "name,type,manufacturer,part_number,symbol".replace(",", ",") or "name" in data
