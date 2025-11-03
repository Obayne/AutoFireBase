from __future__ import annotations

from pathlib import Path

from frontend.labels_manager import (
    format_label_for_ui,
    get_hide_conduit_fill,
    set_hide_conduit_fill,
)


def test_hide_conduit_fill_pref_changes_output(tmp_path: Path):
    # Point prefs to a temp file to avoid touching user home
    import os

    os.environ["AUTOFIRE_PREF_FILE"] = str(tmp_path / "preferences.json")

    # Ensure default is False
    assert get_hide_conduit_fill() is False

    # With default (False) we include fill percent
    lbl = format_label_for_ui(conduit_kind="EMT", trade_size="3/4", wires={18: 5})
    assert isinstance(lbl, str) and lbl.endswith("% fill")

    # Toggle hide to True
    set_hide_conduit_fill(True)
    assert get_hide_conduit_fill() is True

    # Now we should only see the bundle
    lbl2 = format_label_for_ui(conduit_kind="EMT", trade_size="3/4", wires={18: 5})
    assert lbl2 == "5x18AWG"
