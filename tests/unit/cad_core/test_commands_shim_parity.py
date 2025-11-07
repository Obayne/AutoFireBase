from cad_core import commands as legacy_shim
from lv_cad.cad_core import commands_clean as migrated


def test_commands_shim_reexports_same_symbols():
    # The shim should re-export the command classes from lv_cad when available
    assert hasattr(legacy_shim, "CADCommand")
    assert hasattr(legacy_shim, "CADCommandStack")
    # Ensure the legacy shim points to the migrated implementations when importable
    assert legacy_shim.CADCommand is migrated.CADCommand
    assert legacy_shim.CADCommandStack is migrated.CADCommandStack
