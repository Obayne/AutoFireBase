from __future__ import annotations

from cad_core.labels import format_wirepath_label


def test_label_hide_fill_true_returns_bundle_only():
    lbl = format_wirepath_label(
        conduit_kind="EMT", trade_size="3/4", wires={18: 10, 12: 2}, hide_fill=True
    )
    assert lbl == "10x18AWG + 2x12AWG"


def test_label_with_fill_includes_conduit_and_percent():
    lbl = format_wirepath_label(conduit_kind="EMT", trade_size="3/4", wires={18: 10})
    assert isinstance(lbl, str)
    assert lbl.startswith("3/4 EMT — 10x18AWG — ")
    assert lbl.endswith("% fill")
