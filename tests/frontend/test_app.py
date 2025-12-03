"""Tests for frontend app entrypoint."""

from unittest.mock import patch


def test_main_delegates_to_boot():
    """Test that main() delegates to app.boot.main."""
    with patch("app.boot.main") as mock_boot_main:
        from frontend.app import main

        main()

        mock_boot_main.assert_called_once()
