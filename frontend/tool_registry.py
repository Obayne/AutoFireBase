from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    command: str
    shortcut: str | None = None
    icon: str | None = None
    factory: Callable[..., object] | None = None  # UI-level construction


_REGISTRY: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    _REGISTRY[spec.command] = spec


def get(command: str) -> ToolSpec | None:
    return _REGISTRY.get(command)


def all_tools() -> dict[str, ToolSpec]:
    return dict(_REGISTRY)


__all__ = ["ToolSpec", "register", "get", "all_tools"]
