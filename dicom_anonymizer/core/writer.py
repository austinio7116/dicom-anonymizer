"""
DICOM Writer Module

This module provides functionality for writing anonymized DICOM files to the output directory.
"""

import logging
import os
from pathlib import Path

try:
    import pydicom
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False


class DicomWriter:
    """Writer for saving anonymized DICOM files."""
    
    def __init__(self, output_dir, preserve_structure=True):
        """
        Initialize the DICOM writer.
        
        Args:
            output_dir (str or Path): The output directory to write files to.
            preserve_structure (bool): Whether to preserve the directory structure
                                      of the input files in the output directory.
        """
        self.output_dir = Path(output_dir)
        self.preserve_structure = preserve_structure
        
        # Check if pydicom is available
        if not PYDICOM_AVAILABLE:
            raise ImportError("pydicom is required for DICOM writing. Install it with 'pip install pydicom'.")
    
    def write(self, dataset, relative_path=None):
        """
        Write a DICOM dataset to the output directory.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to write.
            relative_path (str or Path, optional): The path relative to the input directory.
                                                 If None, the file will be written directly to the output directory.
        
        Returns:
            Path: The path to the written file.
        """
        # Determine output path
        if self.preserve_structure and relative_path:
            output_path = self.output_dir / relative_path
        else:
            # Use SOPInstanceUID as filename if available, otherwise use a timestamp
            if hasattr(dataset, 'SOPInstanceUID'):
                filename = f"{dataset.SOPInstanceUID}.dcm"
            else:
                import time
                filename = f"anonymized_{int(time.time())}.dcm"
            
            output_path = self.output_dir / filename
        
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the dataset to the output path
        try:
            dataset.save_as(str(output_path))
            logging.debug(f"Wrote anonymized DICOM file to {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error writing DICOM file to {output_path}: {str(e)}")
            raise
    
    def write_batch(self, datasets_and_paths):
        """
        Write multiple DICOM datasets to the output directory.
        
        Args:
            datasets_and_paths (list): A list of tuples (dataset, relative_path) to write.
        
        Returns:
            list: A list of paths to the written files.
        """
        output_paths = []
        
        for dataset, relative_path in datasets_and_paths:
            try:
                output_path = self.write(dataset, relative_path)
                output_paths.append(output_path)
            except Exception as e:
                logging.error(f"Error writing DICOM file: {str(e)}")
        
        return output_paths


def ensure_output_directory(output_dir):
    """
    Ensure that the output directory exists.
    
    Args:
        output_dir (str or Path): The output directory to check.
        
    Returns:
        Path: The output directory path.
    """
    output_path = Path(output_dir)
    
    if not output_path.exists():
        logging.info(f"Creating output directory: {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
    elif not output_path.is_dir():
        raise ValueError(f"Output path exists but is not a directory: {output_path}")
    
    return output_path


def check_disk_space(output_dir, required_bytes):
    """
    Check if there is enough disk space available in the output directory.
    
    Args:
        output_dir (str or Path): The output directory to check.
        required_bytes (int): The number of bytes required.
        
    Returns:
        bool: True if there is enough disk space, False otherwise.
    """
    try:
        import shutil
        
        output_path = Path(output_dir)
        
        # Create the directory if it doesn't exist
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Get disk usage statistics
        disk_usage = shutil.disk_usage(output_path)
        
        # Check if there is enough free space
        if disk_usage.free < required_bytes:
            logging.warning(
                f"Not enough disk space in {output_path}. "
                f"Required: {required_bytes / (1024*1024):.2f} MB, "
                f"Available: {disk_usage.free / (1024*1024):.2f} MB"
            )
            return False
        
        return True
    
    except Exception as e:
        logging.warning(f"Error checking disk space: {str(e)}")
        # If we can't check disk space, assume there is enough
        return True