from backend.workspace import Workspace, disabled_tool_kinds, policy_for


def test_policy_modelspace_allows_modeling_and_layout():
    p = policy_for(Workspace.MODEL)
    assert p.modeling_enabled is True
    assert p.layout_enabled is True
    assert p.export_enabled is True
    assert disabled_tool_kinds(Workspace.MODEL) == frozenset()


def test_policy_paperspace_disables_modeling_enables_layout_export():
    p = policy_for(Workspace.PAPER)
    assert p.modeling_enabled is False
    assert p.layout_enabled is True
    assert p.export_enabled is True
    disabled = disabled_tool_kinds(Workspace.PAPER)
    # A representative sample must be disabled
    assert {"draw/line", "modify/trim"}.issubset(disabled)
