from frontend.tool_registry import ToolSpec, all_tools, get, register


def test_register_and_get_tool():
    spec = ToolSpec(name="Trim", command="trim", shortcut="T")
    register(spec)
    got = get("trim")
    assert got is not None
    assert got.name == "Trim"
    assert all_tools()["trim"].shortcut == "T"
