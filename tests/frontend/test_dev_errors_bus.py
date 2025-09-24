import logging

from frontend.dev_errors import bus, install


def test_error_bus_captures_logging_error():
    install()
    logger = logging.getLogger("test.bus")
    logger.error("hello error")
    assert any("hello error" in m for m in bus.snapshot())
