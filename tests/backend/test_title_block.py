from pathlib import Path

from backend.title_block import export_title_block


def test_export_title_block_writes_svg(tmp_path: Path):
    meta = {
        "project_name": "Test Project",
        "client": "ACME",
        "sheet_name": "Cover",
        "author": "CI",
        "date": "2025-10-25",
        "product": "AlarmForge",
        "version": "0.1.0",
    }
    out = export_title_block(tmp_path, meta)
    svg = Path(out.get("svg"))
    assert svg.exists()
    txt = svg.read_text(encoding="utf-8")
    assert "Test Project" in txt
    assert "AlarmForge" in txt
