def test_command_stack_basic_parity():
    import cad_core.commands_clean as legacy
    from lv_cad.cad_core.commands_clean import CADCommandStack as NewStack

    class _Noop(legacy.CADCommand):
        def __init__(self, description: str = ""):
            super().__init__(description)

        def execute(self) -> bool:
            return True

        def undo(self) -> bool:
            return True

    # legacy
    s_legacy = legacy.CADCommandStack()
    ok = s_legacy.execute(_Noop("one"))
    assert ok and s_legacy.can_undo()
    assert s_legacy.get_undo_description() == "one"
    assert s_legacy.undo()

    # new implementation
    s_new = NewStack()
    ok2 = s_new.execute(_Noop("one"))
    assert ok2 and s_new.can_undo()
    assert s_new.get_undo_description() == "one"
    assert s_new.undo()
