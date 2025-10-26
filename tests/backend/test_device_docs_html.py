from pathlib import Path

from backend.device_docs import export_device_docs_html
from backend.reports import export_html_submittal


class Dev:
    def __init__(self, manufacturer="Acme", part_number="P2R", name="Horn Strobe"):
        self.manufacturer = manufacturer
        self.part_number = part_number
        self.name = name


def test_export_device_docs_html(tmp_path):
    items = [Dev(), Dev(part_number="SD-355", name="Smoke Detector"), Dev(part_number="BG-12LX")]
    out = tmp_path / "docs.html"
    p = export_device_docs_html(items, str(out))
    html = Path(p).read_text(encoding="utf-8")
    # Should include at least one anchor
    assert "<a href=" in html


def test_docs_in_submittal_index(tmp_path):
    items = [Dev()]
    out = export_html_submittal(items, [], str(tmp_path))
    idx = Path(out["index_path"]).read_text(encoding="utf-8")
    # Link to device documents should be present
    assert "Device Documents" in idx
