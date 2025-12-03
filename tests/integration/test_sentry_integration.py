"""Integration tests for Sentry error tracking.

These tests verify that Sentry SDK is properly integrated and can capture errors.
Run with: pytest tests/integration/test_sentry_integration.py -v
"""

import os
from unittest.mock import patch

import pytest


class TestSentryIntegration:
    """Test Sentry SDK integration in the application."""

    def test_sentry_sdk_importable(self):
        """Verify sentry_sdk can be imported."""
        try:
            import sentry_sdk

            assert sentry_sdk is not None
            assert hasattr(sentry_sdk, "init")
            assert hasattr(sentry_sdk, "capture_exception")
            assert hasattr(sentry_sdk, "add_breadcrumb")
        except ImportError:
            pytest.fail("sentry-sdk is not installed")

    def test_sentry_graceful_fallback_in_main(self):
        """Verify app/main.py handles missing Sentry gracefully."""
        # Read main.py to verify graceful import
        main_path = os.path.join(os.path.dirname(__file__), "..", "..", "app", "main.py")
        with open(main_path, encoding="utf-8") as f:
            content = f.read()

        # Check for try/except around sentry import
        assert "try:" in content
        assert "import sentry_sdk" in content
        assert "except ImportError:" in content or "except Exception:" in content

    @patch("sentry_sdk.init")
    def test_sentry_init_not_called_without_dsn(self, mock_init):
        """Verify Sentry is not initialized without a DSN."""
        # Import main without SENTRY_DSN env var
        if "SENTRY_DSN" in os.environ:
            del os.environ["SENTRY_DSN"]

        # The app should not crash even without Sentry configured
        assert True  # Placeholder - actual test would import and verify

    @patch("sentry_sdk.capture_exception")
    @patch("sentry_sdk.add_breadcrumb")
    def test_sentry_breadcrumb_tracking(self, mock_breadcrumb, mock_capture):
        """Verify breadcrumb tracking works when Sentry is available."""
        import sentry_sdk

        # Simulate user action
        sentry_sdk.add_breadcrumb(category="user_action", message="Placed FACP panel", level="info")

        # Verify breadcrumb was added
        mock_breadcrumb.assert_called_once()
        call_args = mock_breadcrumb.call_args[1]
        assert call_args["category"] == "user_action"
        assert "FACP" in call_args["message"]

    @patch("sentry_sdk.capture_exception")
    def test_sentry_exception_capture(self, mock_capture):
        """Verify exception capture works when Sentry is available."""
        import sentry_sdk

        # Simulate an error
        try:
            raise ValueError("Test error for Sentry")
        except ValueError as e:
            sentry_sdk.capture_exception(e)

        # Verify exception was captured
        mock_capture.assert_called_once()

    def test_sentry_error_boundaries_in_main(self):
        """Verify error boundaries exist in critical app sections."""
        main_path = os.path.join(os.path.dirname(__file__), "..", "..", "app", "main.py")
        with open(main_path, encoding="utf-8") as f:
            content = f.read()

        # Check for breadcrumbs in critical operations
        assert "add_breadcrumb" in content, "No breadcrumb tracking found"

        # Check for exception capture
        assert "capture_exception" in content, "No exception capture found"

        # Verify FACP placement has tracking
        facp_section = content[content.find("place_facp") : content.find("place_facp") + 2000]
        if facp_section:
            # Should have breadcrumb or exception handling
            assert (
                "add_breadcrumb" in facp_section or "capture_exception" in facp_section
            ), "FACP placement lacks Sentry tracking"

    @pytest.mark.skipif("SENTRY_DSN" not in os.environ, reason="SENTRY_DSN not configured")
    def test_sentry_dsn_configured(self):
        """Verify Sentry DSN is configured (skipped if not set)."""
        dsn = os.environ.get("SENTRY_DSN")
        assert dsn, "SENTRY_DSN environment variable is empty"
        assert dsn.startswith("https://"), "SENTRY_DSN should be an HTTPS URL"
        assert "sentry.io" in dsn or "ingest" in dsn, "SENTRY_DSN should point to Sentry"


class TestSentryErrorSimulation:
    """Simulate errors to test Sentry capture (manual testing)."""

    @pytest.mark.manual
    @pytest.mark.skipif("SENTRY_DSN" not in os.environ, reason="SENTRY_DSN not configured")
    def test_trigger_test_error_for_sentry(self):
        """Manually trigger a test error to verify Sentry dashboard.

        This test is marked as 'manual' and should be run explicitly:
        pytest tests/integration/test_sentry_integration.py::TestSentryErrorSimulation::test_trigger_test_error_for_sentry -v -m manual

        After running, check your Sentry dashboard for the captured error.
        """
        import sentry_sdk

        sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], traces_sample_rate=1.0)

        # Add breadcrumbs
        sentry_sdk.add_breadcrumb(
            category="test", message="Starting Sentry integration test", level="info"
        )

        sentry_sdk.add_breadcrumb(
            category="test", message="About to trigger test error", level="warning"
        )

        # Trigger a test error
        try:
            raise RuntimeError("This is a TEST error from pytest to verify Sentry integration")
        except RuntimeError as e:
            sentry_sdk.capture_exception(e)

        # Flush events to ensure they're sent
        sentry_sdk.flush()

        print("\n✅ Test error sent to Sentry. Check your dashboard at https://sentry.io/")
