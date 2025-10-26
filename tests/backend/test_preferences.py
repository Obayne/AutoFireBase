from __future__ import annotations

from pathlib import Path

from backend.preferences import (
    get_default_preferences,
    get_preferences_path,
    load_preferences,
    save_preferences,
    update_preferences,
)


def test_defaults_without_file(tmp_path: Path) -> None:
    pref_file = tmp_path / "prefs.json"
    prefs = load_preferences(pref_file, cwd=tmp_path)
    defaults = get_default_preferences(tmp_path)
    assert prefs["report_default_dir"] == defaults["report_default_dir"]
    assert prefs["include_device_docs_in_submittal"] is True
    assert isinstance(prefs["export_image_dpi"], int) and prefs["export_image_dpi"] == 300


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    pref_file = tmp_path / "prefs.json"
    custom = {
        "report_default_dir": str(tmp_path / "out"),
        "include_device_docs_in_submittal": False,
        "export_image_dpi": 200,
        # unknown key should round-trip as well
        "extra_key": "keep-me",
    }
    save_preferences(custom, pref_file)
    loaded = load_preferences(pref_file, cwd=tmp_path)
    assert loaded["report_default_dir"] == custom["report_default_dir"]
    assert loaded["include_device_docs_in_submittal"] is False
    assert loaded["export_image_dpi"] == 200
    assert loaded.get("extra_key") == "keep-me"


def test_partial_update_merge(tmp_path: Path) -> None:
    pref_file = tmp_path / "prefs.json"
    # seed file
    save_preferences(get_default_preferences(tmp_path), pref_file)

    merged = update_preferences({"export_image_dpi": 150}, pref_file, cwd=tmp_path)
    assert merged["export_image_dpi"] == 150
    # Ensure other keys remain
    assert "report_default_dir" in merged
    assert "include_device_docs_in_submittal" in merged


def test_get_preferences_path_overrides(tmp_path: Path, monkeypatch) -> None:
    # file override wins
    monkeypatch.setenv("AUTOFIRE_PREF_FILE", str(tmp_path / "a.json"))
    assert get_preferences_path() == tmp_path / "a.json"
    # dir override used when file unset
    monkeypatch.delenv("AUTOFIRE_PREF_FILE", raising=False)
    monkeypatch.setenv("AUTOFIRE_PREF_DIR", str(tmp_path / "cfg"))
    assert get_preferences_path().parent == tmp_path / "cfg"
