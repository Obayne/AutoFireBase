import sys


def test_frontend_dev_hook_registers_tools(monkeypatch):
    # Ensure a clean import of the package root
    sys.modules.pop("frontend", None)
    # Enable dev tools via environment
    monkeypatch.setenv("FRONTEND_OPS_TOOLS", "1")
    import frontend  # noqa: F401  # triggers _maybe_activate_dev_hooks
    from frontend.tool_registry import get

    spec = get("ops.extend_to_circle")
    assert spec is not None and callable(spec.factory)
