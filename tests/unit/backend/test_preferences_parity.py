import os

from backend import preferences as legacy
from lv_cad.backend import preferences as migrated


def test_preferences_load_and_update_parity(tmp_path, monkeypatch):
    # Force both modules to use the same user dir by monkeypatching expanduser
    test_home = tmp_path / "home"
    test_home.mkdir()

    def _expanduser(p: str) -> str:
        return str(test_home) if p == "~" else os.path.expanduser(p)

    monkeypatch.setattr(os.path, "expanduser", _expanduser)

    # Initially, no prefs file -> both should return the same defaults
    a = legacy.load_preferences()
    b = migrated.load_preferences()
    assert a == b

    # Update via migrated module and ensure legacy sees the change
    new = a.copy()
    new["px_per_ft"] = 42.0
    ok = migrated.update_preferences(new)
    assert ok
    a2 = legacy.load_preferences()
    assert a2["px_per_ft"] == 42.0
