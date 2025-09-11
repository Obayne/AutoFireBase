import os, logging, logging.handlers, pathlib

APP_DIR = os.path.join(os.path.expanduser("~"), "AutoFire")
LOG_DIR = os.path.join(APP_DIR, "logs")
pathlib.Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

def get_logger(name="autofire"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    log_path = os.path.join(LOG_DIR, f"{name}.log")
    handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger