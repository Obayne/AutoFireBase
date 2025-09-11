def get_app_logger():
    try:
        from core.logger import get_logger
        return get_logger("autofire_app")
    except Exception:
        import logging
        return logging.getLogger("autofire_app_fallback")