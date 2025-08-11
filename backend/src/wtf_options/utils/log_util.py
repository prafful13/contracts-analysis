import logging
import sys
from .. import config

def setup_logging():
    """
    Configures the root logger for the application.
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Create a file handler
    # file_handler = logging.FileHandler('backend.log')
    # file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    # file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    # logger.addHandler(file_handler)

    # Special handling for yfinance to reduce noise
    logging.getLogger('yfinance').setLevel(logging.INFO)

    return logger

# Create and configure the logger when the module is imported
log = setup_logging()
