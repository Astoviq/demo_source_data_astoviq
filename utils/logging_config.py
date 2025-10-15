# EuroStyle Fashion - Centralized Logging Configuration
# =====================================================
# Configures structured logging for data generation and loading operations
# Following WARP.md Rule: "dont hard code, always use guidelines and framework principles"

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import sys


class EuroStyleLogger:
    """Centralized logging configuration for EuroStyle Fashion platform."""
    
    def __init__(self, name: str, log_level: str = "INFO"):
        """
        Initialize logger for specific component.
        
        Args:
            name: Logger name (e.g., 'data_generation', 'incremental', 'loading')
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger with file and console handlers."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)-20s | %(levelname)-8s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s | %(name)s | %(message)s'
        )
        
        # File handler - detailed logs
        log_file = self.logs_dir / f"eurostyle_{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler - clean output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Error file handler - errors only
        error_file = self.logs_dir / f"eurostyle_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(error_handler)
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """Get configured logger instance."""
        return self.logger
    
    def log_operation_start(self, operation: str, **kwargs):
        """Log start of major operation."""
        details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.info(f"🚀 STARTING: {operation}" + (f" | {details}" if details else ""))
    
    def log_operation_complete(self, operation: str, duration: float = None, **kwargs):
        """Log completion of major operation."""
        details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        duration_str = f" | Duration: {duration:.2f}s" if duration else ""
        self.logger.info(f"✅ COMPLETED: {operation}" + (f" | {details}" if details else "") + duration_str)
    
    def log_operation_failed(self, operation: str, error: Exception, **kwargs):
        """Log failed operation."""
        details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.error(f"❌ FAILED: {operation}" + (f" | {details}" if details else ""))
        self.logger.error(f"Error details: {type(error).__name__}: {str(error)}")
    
    def log_data_summary(self, table: str, records: int, operation: str = "generated"):
        """Log data generation/loading summary."""
        self.logger.info(f"📊 {operation.upper()}: {table} | Records: {records:,}")
    
    def log_consistency_check(self, check_name: str, status: str, details: str = ""):
        """Log consistency check results."""
        status_emoji = "✅" if status.upper() == "PASSED" else "❌"
        self.logger.info(f"{status_emoji} CONSISTENCY: {check_name} | Status: {status}" + (f" | {details}" if details else ""))


def get_logger(component_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Quick function to get a configured logger for any component.
    
    Args:
        component_name: Name of the component (data_generation, loading, etc.)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    return EuroStyleLogger(component_name, log_level).get_logger()


def setup_data_generation_logging():
    """Setup logging specifically for data generation processes."""
    return EuroStyleLogger("data_generation", "INFO")


def setup_data_loading_logging():
    """Setup logging specifically for data loading processes."""
    return EuroStyleLogger("data_loading", "INFO")


def setup_incremental_logging():
    """Setup logging specifically for incremental data generation."""
    return EuroStyleLogger("incremental", "INFO")


# Performance monitoring decorator
def log_performance(logger: logging.Logger):
    """Decorator to log function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"PERFORMANCE: {func.__name__} completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"PERFORMANCE: {func.__name__} failed after {duration:.2f}s - {e}")
                raise
        return wrapper
    return decorator