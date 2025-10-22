from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    """Lightweight specification for a frontend tool.

    Keep this free of Qt types so it can be safely imported in headless
    environments and unit tests.
    """

    name: str
    command: str
    shortcut: str | None = None
    description: str | None = None


_registry: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    """Register or update a tool specification by its command key."""

    _registry[spec.command] = spec


def get(command: str) -> ToolSpec | None:
    """Retrieve a tool specification by command, if present."""

    return _registry.get(command)


def all_tools() -> dict[str, ToolSpec]:
    """Return the full registry mapping (command -> ToolSpec)."""

    return _registry
