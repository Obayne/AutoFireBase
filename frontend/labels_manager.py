"""
Labels Manager - UI formatting and conduit fill utilities
"""

# Global state for conduit fill hiding
_hide_conduit_fill = False


def format_label_for_ui(label_text: str) -> str:
    """Format a label for display in the UI."""
    if not label_text:
        return ""

    # Clean up the label text
    formatted = label_text.strip()

    # Handle special cases
    if formatted.upper() in ["N/A", "NONE", "NULL"]:
        return ""

    # Return formatted text
    return formatted


def get_hide_conduit_fill() -> bool:
    """Get the current state of conduit fill hiding."""
    return _hide_conduit_fill


def set_hide_conduit_fill(hide: bool) -> None:
    """Set the state of conduit fill hiding."""
    global _hide_conduit_fill
    _hide_conduit_fill = hide
