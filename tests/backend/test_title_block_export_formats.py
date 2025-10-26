from pathlib import Path

from backend.title_block import (
    export_title_block,
    export_title_block_pdf_file,
    export_title_block_png_file,
    export_title_block_svg_file,
)


def test_export_title_block_folder(tmp_path):
    meta = {
        "project_name": "Demo Project",
        "client": "Demo Client",
        "sheet_name": "Cover",
        "author": "Unit Test",
        "date": "2025-10-25",
        "product": "AlarmForge",
        "version": "1.0.0",
    }
    out = export_title_block(tmp_path, meta)
    assert "svg" in out
    svg_path = Path(out["svg"])
    assert svg_path.exists()
    # Optional outputs
    if "png" in out:
        assert Path(out["png"]).exists()
    if "pdf" in out:
        assert Path(out["pdf"]).exists()


def test_export_title_block_file_helpers(tmp_path):
    meta = {
        "project_name": "Demo Project",
        "client": "Demo Client",
        "sheet_name": "Sheet 1",
        "author": "Unit Test",
        "date": "2025-10-25",
        "product": "AlarmForge",
        "version": "1.0.0",
    }
    svg_path = tmp_path / "out.svg"
    p = export_title_block_svg_file(svg_path, meta)
    assert Path(p).exists()

    # PNG/PDF helpers depend on optional deps; accept RuntimeError when unavailable
    png_path = tmp_path / "out.png"
    try:
        p2 = export_title_block_png_file(png_path, meta)
        assert Path(p2).exists()
    except RuntimeError:
        # No optional deps installed; acceptable
        pass

    pdf_path = tmp_path / "out.pdf"
    try:
        p3 = export_title_block_pdf_file(pdf_path, meta)
        assert Path(p3).exists()
    except RuntimeError:
        # No optional deps installed; acceptable
        pass
