import logging
import os
from logging.handlers import RotatingFileHandler
from backend.config import Config

# Ensure log directory exists
log_dir = os.path.dirname(Config.LOG_FILE)
os.makedirs(log_dir, exist_ok=True)

def get_logger(name: str):
    """Create and return a configured logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)

    # Prevent duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler (rotating)
        file_handler = RotatingFileHandler(
            Config.LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler (optional for local debugging)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
