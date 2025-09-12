from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass(frozen=True)
class ToolSpec:
    name: str
    command: str
    shortcut: Optional[str] = None
    icon: Optional[str] = None
    factory: Optional[Callable[..., object]] = None  # UI-level construction


_REGISTRY: Dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    _REGISTRY[spec.command] = spec


def get(command: str) -> Optional[ToolSpec]:
    return _REGISTRY.get(command)


def all_tools() -> Dict[str, ToolSpec]:
    return dict(_REGISTRY)


__all__ = ["ToolSpec", "register", "get", "all_tools"]

