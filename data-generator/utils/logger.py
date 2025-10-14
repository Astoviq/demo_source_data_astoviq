"""
Logger Utility
==============

Provides structured logging for the EuroStyle Fashion data generation system.
"""

import logging
import sys
from typing import Optional
from datetime import datetime

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a structured logger with consistent formatting.
    
    Args:
        name: Logger name (typically __name__ or class name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Check if logger already has handlers (avoid duplicate handlers)
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger (avoid duplicate messages)
    logger.propagate = False
    
    return logger

def setup_file_logger(name: str, filename: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger that writes to both console and file.
    
    Args:
        name: Logger name
        filename: Path to log file
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    
    # Get basic logger
    logger = setup_logger(name, level)
    
    # Add file handler
    file_handler = logging.FileHandler(filename, mode='a', encoding='utf-8')
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Create detailed formatter for file
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)-25s | %(levelname)-8s | %(funcName)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    
    return logger

class DataGenerationLogger:
    """Specialized logger for data generation with progress tracking."""
    
    def __init__(self, name: str, enable_file_logging: bool = True):
        """Initialize the data generation logger."""
        self.logger = setup_logger(name)
        
        if enable_file_logging:
            # Create log file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"logs/data_generation_{timestamp}.log"
            
            # Ensure logs directory exists
            import os
            os.makedirs("logs", exist_ok=True)
            
            # Add file handler
            self.logger = setup_file_logger(name, log_file)
        
        self.generation_start_time = None
        self.current_table = None
        self.table_start_time = None
    
    def start_generation(self, total_tables: int) -> None:
        """Log the start of data generation process."""
        self.generation_start_time = datetime.now()
        self.logger.info(f"🏪 Starting EuroStyle Fashion data generation for {total_tables} tables")
        self.logger.info(f"📅 Generation started at: {self.generation_start_time}")
    
    def start_table(self, table_name: str, expected_records: int) -> None:
        """Log the start of table generation."""
        self.current_table = table_name
        self.table_start_time = datetime.now()
        self.logger.info(f"📋 Starting generation for {table_name} ({expected_records:,} records)")
    
    def finish_table(self, table_name: str, actual_records: int) -> None:
        """Log the completion of table generation."""
        if self.table_start_time:
            duration = datetime.now() - self.table_start_time
            records_per_sec = actual_records / duration.total_seconds() if duration.total_seconds() > 0 else 0
            
            self.logger.info(
                f"✅ Completed {table_name}: {actual_records:,} records in {duration.total_seconds():.1f}s "
                f"({records_per_sec:.0f} records/sec)"
            )
        else:
            self.logger.info(f"✅ Completed {table_name}: {actual_records:,} records")
    
    def table_error(self, table_name: str, error: Exception) -> None:
        """Log table generation error."""
        self.logger.error(f"❌ Failed to generate {table_name}: {str(error)}")
        
        # Log stack trace at debug level
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Stack trace for {table_name} error:", exc_info=True)
    
    def finish_generation(self, successful_tables: int, total_tables: int) -> None:
        """Log the completion of data generation process."""
        if self.generation_start_time:
            duration = datetime.now() - self.generation_start_time
            self.logger.info(f"🏁 Data generation completed in {duration.total_seconds():.1f}s")
        
        if successful_tables == total_tables:
            self.logger.info(f"🎉 Successfully generated all {total_tables} tables")
        else:
            self.logger.warning(f"⚠️ Generated {successful_tables}/{total_tables} tables successfully")
    
    def log_progress(self, message: str, progress_percent: Optional[float] = None) -> None:
        """Log progress message with optional percentage."""
        if progress_percent is not None:
            self.logger.info(f"📈 {message} ({progress_percent:.1f}%)")
        else:
            self.logger.info(f"📈 {message}")
    
    def log_validation(self, table_name: str, validation_passed: bool, details: str = "") -> None:
        """Log validation results."""
        if validation_passed:
            self.logger.info(f"✅ Validation passed for {table_name}" + (f": {details}" if details else ""))
        else:
            self.logger.warning(f"⚠️ Validation failed for {table_name}" + (f": {details}" if details else ""))
    
    def log_business_metric(self, metric_name: str, expected: float, actual: float, tolerance: float = 0.1) -> None:
        """Log business metric validation."""
        diff_percent = abs(actual - expected) / expected * 100
        
        if diff_percent <= tolerance * 100:
            self.logger.info(f"📊 {metric_name}: Expected {expected:.2f}, Actual {actual:.2f} ✅")
        else:
            self.logger.warning(f"📊 {metric_name}: Expected {expected:.2f}, Actual {actual:.2f} ({diff_percent:.1f}% diff) ⚠️")
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)