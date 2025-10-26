from pathlib import Path

from backend.reports_cli import run_cli


def test_reports_cli_demo_folder(tmp_path: Path):
    out_dir = tmp_path / "reports"
    code = run_cli(["--out", str(out_dir), "--demo"])  # returns 0 on success
    assert code == 0
    # Expect index.html and CSVs to exist
    assert (out_dir / "index.html").exists()
    assert (out_dir / "bom.csv").exists()
    assert (out_dir / "cable_schedule.csv").exists()
    assert (out_dir / "riser.csv").exists()
    assert (out_dir / "compliance_summary.csv").exists()


def test_reports_cli_demo_zip(tmp_path: Path):
    zip_path = tmp_path / "bundle.zip"
    code = run_cli(["--zip", str(zip_path), "--demo"])  # returns 0 on success
    assert code == 0
    assert zip_path.exists()
