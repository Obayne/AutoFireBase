"""
Frontend application entrypoint.

Phase 1 integration extracts Qt bootstrap into frontend/bootstrap module
for better organization while maintaining compatibility with existing boot logic.
"""

from __future__ import annotations


def main() -> None:
    """Main frontend entrypoint with enhanced bootstrap."""
    try:
        # Try enhanced bootstrap with tool integration
        from .bootstrap import enhanced_bootstrap
        from app.main import create_window
        
        enhanced_bootstrap(create_window, tool_integration=True)
        
    except ImportError:
        # Fallback to existing boot logic for compatibility
        from app.boot import main as _boot
        _boot()


def legacy_main() -> None:
    """Legacy compatibility entrypoint."""
    # Delegate to existing resilient boot for backwards compatibility
    from app.boot import main as _boot
    _boot()


if __name__ == "__main__":
    main()

