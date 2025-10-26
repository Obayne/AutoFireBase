"""Frontend package

This package contains UI-adjacent interfaces that are safe to import in
headless/test environments. Keep Qt imports out of module top-levels to
avoid side effects during testing.
"""

__all__ = [
    "tool_registry",
]
