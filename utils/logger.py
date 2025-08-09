"""
Logging utilities for Lumi-Setup v2.0
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logging(log_level=logging.INFO):
    """Setup application logging"""
    
    # Create logs directory
    log_dir = Path.home() / ".lumi-setup" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"lumi-setup_{timestamp}.log"
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # Console output
        ]
    )
    
    # Create application logger
    logger = logging.getLogger("lumi-setup")
    logger.info(f"Logging initialized - Log file: {log_file}")
    
    return logger

def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(f"lumi-setup.{name}")
