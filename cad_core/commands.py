"""Compatibility shim: provide CADCommand and CADCommandStack.

The original file was corrupted; a clean implementation is available
in :mod:`cad_core.commands_clean`. Import and re-export here so other
modules importing ``cad_core.commands`` keep working.
"""

from .commands_clean import CADCommand, CADCommandStack

__all__ = ["CADCommand", "CADCommandStack"]
