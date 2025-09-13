from frontend.layout_space import LayoutSpaceState


def test_layout_space_default_state():
    ls = LayoutSpaceState()
    assert ls.sheets_visible is False
    assert ls.selected_layout is None
    assert ls.locked is False
    assert ls.layouts and ls.layouts[0] == "Layout 1"


def test_toggle_and_select_and_lock():
    ls = LayoutSpaceState()
    seen = {"toggle": None, "select": None, "lock": None, "cmd": None}

    ls.on("toggle_sheets", lambda v: seen.__setitem__("toggle", v))
    ls.on("select_layout", lambda n: seen.__setitem__("select", n))
    ls.on("lock", lambda v: seen.__setitem__("lock", v))
    ls.on("command", lambda t: seen.__setitem__("cmd", t))

    ls.toggle_sheets_dock()
    assert ls.sheets_visible is True and seen["toggle"] is True

    ls.select_layout("Detail A")
    assert ls.selected_layout == "Detail A" and seen["select"] == "Detail A"
    assert "Detail A" in ls.layouts

    ls.set_lock(True)
    assert ls.locked is True and seen["lock"] is True

    ls.submit_command("regen")
    assert seen["cmd"] == "regen"

