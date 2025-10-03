import logging
from contextlib import contextmanager


@contextmanager
def preserve_root_logging():
    """Temporarily preserve and restore root logger configuration."""
    root = logging.getLogger()
    old_level = root.level
    old_handlers = list(root.handlers)
    try:
        yield root
    finally:
        # Restore original handlers and level
        for h in list(root.handlers):
            root.removeHandler(h)
        for h in old_handlers:
            root.addHandler(h)
        root.setLevel(old_level)


def test_setup_logging_idempotent_handlers():
    from app.logging_config import setup_logging

    with preserve_root_logging() as root:
        # Start from a clean state
        for h in list(root.handlers):
            root.removeHandler(h)

        setup_logging()
        first_count = len(root.handlers)
        # Call again should not add more handlers
        setup_logging()
        second_count = len(root.handlers)

        assert first_count == 1
        assert second_count == first_count


def test_setup_logging_custom_level_and_format():
    from app.logging_config import setup_logging

    with preserve_root_logging() as root:
        # Ensure no pre-existing handlers so custom format is applied
        for h in list(root.handlers):
            root.removeHandler(h)

        fmt = "X:%(levelname)s:%(name)s:%(message)s"
        setup_logging(level=logging.DEBUG, fmt=fmt)

        assert len(root.handlers) == 1
        handler = root.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.formatter is not None
        # Inspect the formatter string
        assert getattr(handler.formatter, "_fmt", None) == fmt
        # Level should be set as requested
        assert root.level == logging.DEBUG


def test_emission_after_setup_writes_records(caplog):
    from app.logging_config import setup_logging

    with preserve_root_logging():
        setup_logging(level=logging.INFO)
        logger = logging.getLogger("app.test.logger")
        with caplog.at_level(logging.INFO):
            logger.info("hello world")
        # Ensure a record was emitted at INFO level from our logger
        assert any(
            rec.name == "app.test.logger" and rec.levelno == logging.INFO for rec in caplog.records
        )
