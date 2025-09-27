import logging
from pathlib import Path


def get_logger(name="autofire"):
    base = Path.home() / "AutoFire" / "logs"
    base.mkdir(parents=True, exist_ok=True)
    log_path = base / "autofire.log"
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(str(log_path), encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger
