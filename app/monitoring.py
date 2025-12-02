"""
Sentry error tracking integration for AutoFire.

Provides automatic error reporting and performance monitoring.
Free tier: 5,000 events/month - perfect for development and small teams.

Usage:
    from app.monitoring import init_sentry

    init_sentry()  # In production
    init_sentry(enable=False)  # Disable in development
"""

import os
import sys

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


def get_version() -> str:
    """Get AutoFire version from VERSION.txt."""
    try:
        version_file = os.path.join(os.path.dirname(__file__), "..", "VERSION.txt")
        with open(version_file) as f:
            return f.read().strip()
    except Exception:
        return "unknown"


def init_sentry(
    dsn: str | None = None,
    enable: bool | None = None,
    environment: str | None = None,
    sample_rate: float = 1.0,
    traces_sample_rate: float = 0.1,
) -> bool:
    """
    Initialize Sentry error tracking.

    Args:
        dsn: Sentry DSN (Data Source Name). If None, reads from SENTRY_DSN env var.
        enable: Force enable/disable. If None, auto-detects based on DSN availability.
        environment: Environment name (e.g., "production", "development").
                    If None, auto-detects from AUTOFIRE_ENV or defaults to "production".
        sample_rate: Error sampling rate (0.0-1.0). 1.0 = report all errors.
        traces_sample_rate: Performance trace sampling (0.0-1.0). 0.1 = 10% of transactions.

    Returns:
        bool: True if Sentry was initialized, False otherwise.

    Example:
        # Production (with DSN in environment)
        init_sentry()

        # Development (disabled)
        init_sentry(enable=False)

        # Custom DSN
        init_sentry(dsn="https://your-key@sentry.io/your-project")
    """
    if not SENTRY_AVAILABLE:
        print("Sentry SDK not installed - error tracking disabled", file=sys.stderr)
        return False

    # Check if explicitly disabled
    if enable is False:
        print("Sentry disabled by configuration")
        return False

    # Get DSN
    if dsn is None:
        dsn = os.getenv("SENTRY_DSN")

    # Auto-detect enable based on DSN
    if enable is None:
        enable = bool(dsn)

    if not enable or not dsn:
        print("Sentry not initialized (no DSN provided)")
        return False

    # Auto-detect environment
    if environment is None:
        environment = os.getenv("AUTOFIRE_ENV", "production")

    # Get version
    version = get_version()

    # Configure logging integration
    logging_integration = LoggingIntegration(
        level=None,  # Capture everything from logging
        event_level="ERROR",  # Send errors as Sentry events
    )

    # Initialize Sentry
    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=f"autofire@{version}",
            # Integrations
            integrations=[
                logging_integration,
                # PySide6 integration automatically included via sentry-sdk[pyside6]
            ],
            # Sampling
            sample_rate=sample_rate,
            traces_sample_rate=traces_sample_rate,
            # Additional context
            send_default_pii=False,  # Don't send personally identifiable info
            attach_stacktrace=True,
            # Performance
            _experiments={
                "profiles_sample_rate": 0.1,  # Profile 10% of transactions
            },
        )

        # Set additional context
        sentry_sdk.set_context(
            "app",
            {
                "name": "AutoFire",
                "version": version,
                "platform": sys.platform,
                "python_version": (
                    f"{sys.version_info.major}.{sys.version_info.minor}."
                    f"{sys.version_info.micro}"
                ),
            },
        )

        print(f"✓ Sentry initialized (env: {environment}, version: {version})")
        return True

    except Exception as e:
        print(f"Failed to initialize Sentry: {e}", file=sys.stderr)
        return False


def capture_exception(exception: Exception, **kwargs) -> str | None:
    """
    Manually capture an exception to Sentry.

    Args:
        exception: The exception to capture.
        **kwargs: Additional context (e.g., level="warning", tags={"key": "value"})

    Returns:
        str: Event ID if captured, None otherwise.

    Example:
        try:
            risky_operation()
        except Exception as e:
            event_id = capture_exception(e, level="warning", tags={"operation": "import"})
    """
    if not SENTRY_AVAILABLE:
        return None

    try:
        return sentry_sdk.capture_exception(exception, **kwargs)
    except Exception:
        return None


def capture_message(message: str, level: str = "info", **kwargs) -> str | None:
    """
    Capture a message to Sentry.

    Args:
        message: The message to capture.
        level: Severity level ("debug", "info", "warning", "error", "fatal").
        **kwargs: Additional context.

    Returns:
        str: Event ID if captured, None otherwise.

    Example:
        capture_message("User performed unusual operation", level="warning")
    """
    if not SENTRY_AVAILABLE:
        return None

    try:
        return sentry_sdk.capture_message(message, level=level, **kwargs)
    except Exception:
        return None


def set_user(user_id: str | None = None, email: str | None = None, **kwargs):
    """
    Set user context for error tracking.

    Args:
        user_id: Unique user identifier.
        email: User email address.
        **kwargs: Additional user data.

    Example:
        set_user(user_id="12345", username="john_doe")
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        user_data = {}
        if user_id:
            user_data["id"] = user_id
        if email:
            user_data["email"] = email
        user_data.update(kwargs)

        sentry_sdk.set_user(user_data)
    except Exception:
        pass


def add_breadcrumb(message: str, category: str = "default", level: str = "info", **data):
    """
    Add a breadcrumb (event trail) for debugging.

    Args:
        message: Breadcrumb message.
        category: Category (e.g., "navigation", "network", "ui").
        level: Severity level.
        **data: Additional data.

    Example:
        add_breadcrumb("User opened DXF file", category="file", data={"filename": "plan.dxf"})
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data,
        )
    except Exception:
        pass


def configure_scope(callback):
    """
    Configure Sentry scope for custom context.

    Args:
        callback: Function that receives scope as argument.

    Example:
        def set_context(scope):
            scope.set_tag("feature", "import")
            scope.set_extra("file_size", 1024)

        configure_scope(set_context)
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        sentry_sdk.configure_scope(callback)
    except Exception:
        pass
