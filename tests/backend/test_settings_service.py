from pathlib import Path

from backend.settings.service import (
    AppSettings,
    add_recent_project,
    load_settings,
    save_settings,
)


def test_defaults_when_file_missing(tmp_path: Path):
    cfg = tmp_path / "missing.json"
    s = load_settings(cfg)
    assert isinstance(s, AppSettings)
    assert s.version == 1 and s.theme in {"light", "dark"}


def test_round_trip_save_and_load(tmp_path: Path):
    cfg = tmp_path / "settings.json"
    s = AppSettings(theme="dark", db_path="db/test.sqlite3")
    s = add_recent_project(s, "/proj/a")
    save_settings(s, cfg)

    reloaded = load_settings(cfg)
    assert reloaded.theme == "dark"
    assert reloaded.db_path.endswith("test.sqlite3")
    assert reloaded.recent_projects and reloaded.recent_projects[0] == "/proj/a"


def test_recent_projects_dedup_and_trim(tmp_path: Path):
    s = AppSettings()
    for i in range(15):
        s = add_recent_project(s, f"/p/{i%5}")
    assert len(s.recent_projects) <= 10
    # Most recent is last inserted (i=14 -> '/p/4')
    assert s.recent_projects[0] == "/p/4"

