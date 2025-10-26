import json
from pathlib import Path

from tools.import_device_docs_csv import merge_csv_into_device_docs


def write_csv(tmp_path: Path, name: str, lines: list[str]) -> Path:
    p = tmp_path / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def test_merge_preserve_and_insert(tmp_path: Path):
    # Existing JSON with one complete and one missing field
    out_json = tmp_path / "device_docs.json"
    existing = {
        "p2r": {
            "cutsheet": "https://old.example.com/p2r_cut.pdf",
            "manual": "https://old.example.com/p2r_man.pdf",
        },
        "sd-355": {
            "manual": "https://old.example.com/sd355_man.pdf",
        },
    }
    out_json.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    # CSV with a replacement for p2r (should be ignored without overwrite),
    # a cutsheet for sd-355 (should be added), and a new device bg-12lx.
    csv_path = write_csv(
        tmp_path,
        "docs.csv",
        [
            "PN,cutsheet,manual",
            "p2r,https://new.example.com/p2r_cut.pdf,https://new.example.com/p2r_man.pdf",
            "SD-355,https://new.example.com/sd355_cut.pdf,",
            "bg-12lx,https://new.example.com/bg12lx_cut.pdf,https://new.example.com/bg12lx_man.pdf",
        ],
    )

    summary = merge_csv_into_device_docs(csv_path, out_json, overwrite=False)

    # Validate summary counts
    assert summary["inserts"] == 1
    # updates: sd-355 cutsheet + bg-12lx cutsheet + bg-12lx manual = 3
    assert summary["updates"] == 3
    assert summary["total"] == 3
    assert summary.get("skipped", 0) == 0

    data = json.loads(out_json.read_text(encoding="utf-8"))

    # p2r unchanged
    assert data["p2r"]["cutsheet"] == "https://old.example.com/p2r_cut.pdf"
    assert data["p2r"]["manual"] == "https://old.example.com/p2r_man.pdf"

    # sd-355 gets cutsheet added, manual preserved
    assert data["sd-355"]["cutsheet"] == "https://new.example.com/sd355_cut.pdf"
    assert data["sd-355"]["manual"] == "https://old.example.com/sd355_man.pdf"

    # new device present with both links
    assert data["bg-12lx"]["cutsheet"].endswith("bg12lx_cut.pdf")
    assert data["bg-12lx"]["manual"].endswith("bg12lx_man.pdf")


def test_merge_overwrite_true(tmp_path: Path):
    out_json = tmp_path / "device_docs.json"
    existing = {
        "p2r": {
            "cutsheet": "https://old/p2r_cut.pdf",
            "manual": "https://old/p2r_man.pdf",
        }
    }
    out_json.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    csv_path = write_csv(
        tmp_path,
        "docs.csv",
        [
            "part,Spec,Install",
            "P2R,https://new/p2r_cut_new.pdf,https://new/p2r_man_new.pdf",
        ],
    )

    summary = merge_csv_into_device_docs(csv_path, out_json, overwrite=True)
    assert summary["inserts"] == 0
    # Both fields should be updated
    assert summary["updates"] == 2
    assert summary.get("skipped", 0) == 0

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["p2r"]["cutsheet"] == "https://new/p2r_cut_new.pdf"
    assert data["p2r"]["manual"] == "https://new/p2r_man_new.pdf"


def test_header_aliases_and_case(tmp_path: Path):
    out_json = tmp_path / "device_docs.json"
    csv_path = write_csv(
        tmp_path,
        "docs.csv",
        [
            "Model,spec_url,INSTALL",
            "SD-355,https://x/sd355_cut.pdf,https://x/sd355_man.pdf",
        ],
    )

    summary = merge_csv_into_device_docs(csv_path, out_json, overwrite=False)
    assert summary["inserts"] == 1
    assert summary["updates"] == 2
    assert summary.get("skipped", 0) == 0


def test_importer_skips_invalid_urls(tmp_path: Path):
    out_json = tmp_path / "device_docs.json"
    csv_path = write_csv(
        tmp_path,
        "docs.csv",
        [
            "pn,cutsheet,manual",
            "P2R,notaurl,https://valid/manual.pdf",
            "SD-355,https://valid/cut.pdf,not-a-url",
        ],
    )
    summary = merge_csv_into_device_docs(csv_path, out_json, overwrite=False)
    assert summary["inserts"] == 2
    assert summary["updates"] == 2  # only the valid ones
    assert summary.get("skipped", 0) == 2

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert "sd-355" in data
    assert data["sd-355"]["cutsheet"].endswith("sd355_cut.pdf")
    assert data["sd-355"]["manual"].endswith("sd355_man.pdf")
