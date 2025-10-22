import logging

from app.logging_config import setup_logging

from db import loader

setup_logging()
logger = logging.getLogger(__name__)

con = loader.connect()
loader.ensure_schema(con)
loader.seed_demo(con)
devs = loader.fetch_devices(con)
logger.info("devices: %s", len(devs))
for d in devs[:10]:
    logger.info("%s", d)
con.close()
