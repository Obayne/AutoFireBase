"""Compatibility shim: prefer migrated `lv_cad` commands when available.

This module re-exports `CADCommand` and `CADCommandStack`. During the
strangler migration we try to use the implementations from
`lv_cad.cad_core.commands_clean` when present, falling back to the
legacy `cad_core.commands_clean` otherwise.
"""

import importlib
import logging

_logger = logging.getLogger(__name__)

_lv = None
try:
    _lv = importlib.import_module("lv_cad.cad_core.commands_clean")
    CADCommand = _lv.CADCommand
    CADCommandStack = _lv.CADCommandStack
    _logger.info("Using lv_cad.cad_core.commands_clean for command stack")
except Exception:
    from .commands_clean import CADCommand, CADCommandStack

__all__ = ["CADCommand", "CADCommandStack"]
