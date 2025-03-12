import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger('flask_logger')
    logger.setLevel(LOG_LEVEL)

    fh = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=5 * 1024 * 1024, backupCount=5)
    fh.setLevel(LOG_LEVEL)

    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
