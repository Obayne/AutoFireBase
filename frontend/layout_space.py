from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class LayoutSpaceState:
    """Headless state for the Layout Space (formerly Paper Space).

    This avoids any Qt dependency so it can be tested in CI easily.
    UI widgets can bind to this state and subscribe to events.
    """

    sheets_visible: bool = False
    selected_layout: Optional[str] = None
    locked: bool = False
    layouts: List[str] = field(default_factory=lambda: ["Layout 1"])  # default seed

    # simple event hooks (name -> list of callbacks)
    _listeners: Dict[str, List[Callable[..., None]]] = field(
        default_factory=lambda: {"toggle_sheets": [], "select_layout": [], "lock": [], "command": []},
        init=False,
        repr=False,
    )

    def on(self, event: str, cb: Callable[..., None]) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(cb)

    def _emit(self, event: str, *args, **kwargs) -> None:
        for cb in self._listeners.get(event, []):
            cb(*args, **kwargs)

    # Actions the UI can wire to buttons/menu items
    def toggle_sheets_dock(self) -> None:
        self.sheets_visible = not self.sheets_visible
        self._emit("toggle_sheets", self.sheets_visible)

    def select_layout(self, name: str) -> None:
        if name not in self.layouts:
            self.layouts.append(name)
        self.selected_layout = name
        self._emit("select_layout", name)

    def set_lock(self, locked: bool) -> None:
        self.locked = bool(locked)
        self._emit("lock", self.locked)

    # Command bar integration (headless)
    def submit_command(self, text: str) -> None:
        self._emit("command", text)


__all__ = ["LayoutSpaceState"]

