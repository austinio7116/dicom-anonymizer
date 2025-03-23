"""
Progress Tracking Utility Module

This module provides utilities for tracking and displaying progress information
during the DICOM anonymization process.
"""

import logging
import sys
import time
from datetime import timedelta

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class ProgressTracker:
    """
    Tracker for monitoring and displaying progress information.
    
    This class provides methods for tracking progress of operations,
    such as the number of files processed, estimated time remaining, etc.
    It uses tqdm for progress bar display if available, otherwise falls back
    to simple console output.
    """
    
    def __init__(self, total_files=0, description="Processing", use_tqdm=True):
        """
        Initialize the progress tracker.
        
        Args:
            total_files (int): The total number of files to process.
            description (str): Description of the operation being tracked.
            use_tqdm (bool): Whether to use tqdm for progress display if available.
        """
        self.total_files = total_files
        self.description = description
        self.use_tqdm = use_tqdm and TQDM_AVAILABLE
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.start_time = None
        self.progress_bar = None
    
    def start(self):
        """Start tracking progress."""
        self.start_time = time.time()
        
        if self.use_tqdm:
            self.progress_bar = tqdm(
                total=self.total_files,
                desc=self.description,
                unit="file",
                ncols=100,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
            )
        else:
            logging.info(f"Starting {self.description} of {self.total_files} files")
    
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
        
        if self.progress_bar:
            self.progress_bar.update(1)
            # Update progress bar postfix with success/failure counts
            self.progress_bar.set_postfix(
                success=self.successful_files,
                failed=self.failed_files
            )
        else:
            # Log progress every 10% or every 100 files, whichever is less
            log_interval = min(max(1, self.total_files // 10), 100)
            
            if self.processed_files % log_interval == 0 or self.processed_files == self.total_files:
                self._log_progress()
    
    def _log_progress(self):
        """Log progress information."""
        progress_pct = (self.processed_files / self.total_files) * 100 if self.total_files > 0 else 0
        elapsed = time.time() - self.start_time
        
        # Calculate estimated time remaining
        if self.processed_files > 0:
            files_per_second = self.processed_files / elapsed
            remaining_files = self.total_files - self.processed_files
            eta_seconds = remaining_files / files_per_second if files_per_second > 0 else 0
            eta = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta = "unknown"
        
        logging.info(f"Progress: {self.processed_files}/{self.total_files} files ({progress_pct:.1f}%)")
        logging.info(f"Success: {self.successful_files}, Failed: {self.failed_files}")
        logging.info(f"Elapsed: {str(timedelta(seconds=int(elapsed)))}, ETA: {eta}")
    
    def finish(self):
        """Finish tracking progress and log summary."""
        if self.progress_bar:
            self.progress_bar.close()
        
        elapsed = time.time() - self.start_time
        
        logging.info(f"{self.description} completed")
        logging.info(f"Total files: {self.total_files}")
        logging.info(f"Processed files: {self.processed_files}")
        logging.info(f"Successful files: {self.successful_files}")
        logging.info(f"Failed files: {self.failed_files}")
        logging.info(f"Duration: {str(timedelta(seconds=int(elapsed)))}")
        
        if self.total_files > 0:
            files_per_second = self.processed_files / elapsed if elapsed > 0 else 0
            logging.info(f"Processing rate: {files_per_second:.2f} files/second")


class DummyProgressBar:
    """
    A dummy progress bar that mimics the tqdm interface but does nothing.
    
    This is used when tqdm is not available or when progress display is disabled.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the dummy progress bar."""
        pass
    
    def update(self, n=1):
        """Update the progress bar."""
        pass
    
    def close(self):
        """Close the progress bar."""
        pass
    
    def set_postfix(self, **kwargs):
        """Set the postfix of the progress bar."""
        pass


def get_progress_bar(total, description="Processing", use_tqdm=True, **kwargs):
    """
    Get a progress bar instance.
    
    Args:
        total (int): The total number of items to process.
        description (str): Description of the operation being tracked.
        use_tqdm (bool): Whether to use tqdm for progress display if available.
        **kwargs: Additional arguments to pass to tqdm.
        
    Returns:
        A progress bar instance (either tqdm or DummyProgressBar).
    """
    if use_tqdm and TQDM_AVAILABLE:
        return tqdm(
            total=total,
            desc=description,
            unit="file",
            ncols=100,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            **kwargs
        )
    else:
        return DummyProgressBar()