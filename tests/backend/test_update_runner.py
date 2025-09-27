import sys
import types


def test_run_updater_safe_when_missing(monkeypatch):
    # Ensure importing updater.auto_update fails
    monkeypatch.setitem(sys.modules, "updater", None)
    sys.modules.pop("updater.auto_update", None)

    from backend.update_runner import run_updater_safe

    assert run_updater_safe() is False


def test_run_updater_safe_when_present(monkeypatch):
    # Provide a fake updater.auto_update module
    fake_mod = types.SimpleNamespace(check_and_apply_updates=lambda: True)
    monkeypatch.setitem(sys.modules, "updater", types.ModuleType("updater"))
    monkeypatch.setitem(sys.modules, "updater.auto_update", fake_mod)

    from backend.update_runner import run_updater_safe

    assert run_updater_safe() is True
