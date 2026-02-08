# src/utils/logger.py
"""Logging configuration."""
import logging
import os
from datetime import datetime


def setup_logger(name: str = "smart_farming") -> logging.Logger:
    """Configure structured logging."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_filename = f"{log_dir}/{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_filename)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
