from __future__ import annotations

import logging
import sys
from collections import deque
from collections.abc import Callable


class ErrorBus:
    def __init__(self, max_items: int = 200) -> None:
        self._buf: deque[str] = deque(maxlen=max_items)
        self._subs: list[Callable[[str], None]] = []

    def subscribe(self, cb: Callable[[str], None]) -> None:
        if cb not in self._subs:
            self._subs.append(cb)

    def unsubscribe(self, cb: Callable[[str], None]) -> None:
        if cb in self._subs:
            self._subs.remove(cb)

    def emit(self, msg: str) -> None:
        self._buf.append(msg)
        for cb in list(self._subs):
            try:
                cb(msg)
            except Exception:
                # Best-effort; don't let subscribers break broadcasting
                pass

    def snapshot(self) -> list[str]:
        return list(self._buf)


class ErrorHandler(logging.Handler):
    def __init__(self, bus: ErrorBus) -> None:
        super().__init__(level=logging.ERROR)
        self.bus = bus

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:  # pragma: no cover
            msg = record.getMessage()
        self.bus.emit(msg)


bus = ErrorBus()
_installed = False


def install() -> None:
    global _installed
    if _installed:
        return
    handler = ErrorHandler(bus)
    formatter = logging.Formatter("%(levelname)s: %(name)s: %(message)s")
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.addHandler(handler)
    # Don't force level change; respect existing config

    def _excepthook(exc_type, exc, tb):
        logging.getLogger("frontend.dev_errors").error(
            "Uncaught exception", exc_info=(exc_type, exc, tb)
        )

    # Chain existing excepthook if any
    prev = sys.excepthook

    def chained_excepthook(exc_type, exc, tb):
        try:
            _excepthook(exc_type, exc, tb)
        finally:
            try:
                prev(exc_type, exc, tb)
            except Exception:
                pass

    sys.excepthook = chained_excepthook
    _installed = True


__all__ = ["bus", "install", "ErrorBus"]
