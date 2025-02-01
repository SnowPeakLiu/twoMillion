"""
Logger Configuration Module
"""
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from ..config import settings

def setup_logger(
    log_file: Optional[Path] = None,
    rotation: str = "500 MB",
    retention: str = "10 days"
) -> None:
    """Configure logger
    
    Args:
        log_file: Log file path, defaults to None (only console output)
        rotation: Log file rotation size
        retention: Log retention time
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=settings.app.log_level,
        backtrace=settings.app.debug_mode,
        diagnose=settings.app.debug_mode
    )
    
    # If log file specified, add file handler
    if log_file:
        logger.add(
            log_file,
            rotation=rotation,
            retention=retention,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{name}:{function}:{line} | "
                "{message}"
            ),
            level=settings.app.log_level,
            backtrace=settings.app.debug_mode,
            diagnose=settings.app.debug_mode
        )

def get_logger(name: str):
    """Get logger with context
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        loguru.Logger: Configured logger
    """
    return logger.bind(name=name)

# Example usage
if __name__ == "__main__":
    # Set up logger
    setup_logger(Path("logs/app.log"))
    
    # Get logger
    log = get_logger(__name__)
    
    # Test various log levels
    log.debug("This is a debug log")
    log.info("This is an info log")
    log.warning("This is a warning log")
    log.error("This is an error log")
    log.critical("This is a critical error log") 