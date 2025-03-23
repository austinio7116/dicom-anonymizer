"""
Logging Utility Module

This module provides utilities for setting up logging for the DICOM anonymizer.
"""

import logging
import os
import sys
from pathlib import Path


def setup_logging(level_name="INFO", log_file=None):
    """
    Set up logging for the application.
    
    Args:
        level_name (str): The logging level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file (str, optional): Path to the log file. If None, logs will only be sent to console.
    """
    # Map level name to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    level = level_map.get(level_name.upper(), logging.INFO)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        log_path = Path(log_file)
        
        # Create directory if it doesn't exist
        log_dir = log_path.parent
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, mode='a')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logging.info(f"Logging initialized at level {level_name}")
    if log_file:
        logging.info(f"Logs will be written to {log_file}")


class ProgressLogger:
    """
    Logger for tracking progress of operations.
    
    This class provides methods for logging progress information,
    such as the number of files processed, success/failure counts, etc.
    """
    
    def __init__(self, total_files=0):
        """
        Initialize the progress logger.
        
        Args:
            total_files (int): The total number of files to process.
        """
        self.total_files = total_files
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start tracking progress."""
        import time
        self.start_time = time.time()
        logging.info(f"Starting processing of {self.total_files} files")
    
    def update(self, success=True, filename=None):
        """
        Update progress.
        
        Args:
            success (bool): Whether the operation was successful.
            filename (str, optional): The name of the file that was processed.
        """
        self.processed_files += 1
        if success:
            self.successful_files += 1
        else:
            self.failed_files += 1
        
        # Log progress every 10% or every 100 files, whichever is less
        log_interval = min(max(1, self.total_files // 10), 100)
        
        if self.processed_files % log_interval == 0 or self.processed_files == self.total_files:
            progress_pct = (self.processed_files / self.total_files) * 100 if self.total_files > 0 else 0
            logging.info(f"Progress: {self.processed_files}/{self.total_files} files ({progress_pct:.1f}%)")
            logging.info(f"Success: {self.successful_files}, Failed: {self.failed_files}")
    
    def finish(self):
        """Finish tracking progress and log summary."""
        import time
        self.end_time = time.time()
        duration = self.end_time - self.start_time if self.start_time else 0
        
        logging.info("Processing completed")
        logging.info(f"Total files: {self.total_files}")
        logging.info(f"Processed files: {self.processed_files}")
        logging.info(f"Successful files: {self.successful_files}")
        logging.info(f"Failed files: {self.failed_files}")
        logging.info(f"Duration: {duration:.2f} seconds")
        
        if self.total_files > 0:
            files_per_second = self.processed_files / duration if duration > 0 else 0
            logging.info(f"Processing rate: {files_per_second:.2f} files/second")