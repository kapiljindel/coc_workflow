"""
Logger Module
Structured logging with both console and file output
"""

import logging
import os
from datetime import datetime
from config.constants import LOGS_PATH, LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE

# Ensure logs directory exists
os.makedirs(LOGS_PATH, exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging() -> logging.Logger:
    """
    Set up logging with both console and file handlers
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('coc_bot')
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL_CONSOLE)
    console_formatter = ColoredFormatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG level)
    log_file = os.path.join(LOGS_PATH, f"bot_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(LOG_LEVEL_FILE)
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = 'coc_bot') -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.hasHandlers():
        setup_logging()
    
    return logger
