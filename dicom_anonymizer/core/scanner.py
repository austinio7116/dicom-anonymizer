"""
Directory Scanner Module

This module provides functionality for scanning directories to find DICOM files.
"""

import logging
import os
from pathlib import Path

try:
    import pydicom
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False


class DicomScanner:
    """Scanner for finding DICOM files in directories."""
    
    def __init__(self, input_dir, recursive=True):
        """
        Initialize the DICOM scanner.
        
        Args:
            input_dir (str or Path): The input directory to scan.
            recursive (bool): Whether to scan subdirectories recursively.
        """
        self.input_dir = Path(input_dir)
        self.recursive = recursive
        
        if not PYDICOM_AVAILABLE:
            logging.warning("pydicom is not installed. DICOM validation will be limited to file extension checks.")
    
    def scan(self):
        """
        Scan the input directory for DICOM files.
        
        Returns:
            list: A list of Path objects representing the found DICOM files.
        """
        logging.info(f"Scanning for DICOM files in {self.input_dir}")
        logging.info(f"Recursive scanning: {self.recursive}")
        
        dicom_files = []
        
        # Check if input directory exists
        if not self.input_dir.exists():
            logging.error(f"Input directory does not exist: {self.input_dir}")
            return dicom_files
        
        # Walk through the directory
        for root, dirs, files in os.walk(self.input_dir):
            root_path = Path(root)
            
            # Process files in current directory
            for file in files:
                file_path = root_path / file
                
                # Check if file is a DICOM file
                if self._is_dicom_file(file_path):
                    dicom_files.append(file_path)
            
            # If not recursive, break after first iteration
            if not self.recursive:
                break
        
        logging.info(f"Found {len(dicom_files)} DICOM files")
        return dicom_files
    
    def _is_dicom_file(self, file_path):
        """
        Check if a file is a DICOM file.
        
        Args:
            file_path (Path): The path to the file to check.
            
        Returns:
            bool: True if the file is a DICOM file, False otherwise.
        """
        # Check file extension first (quick check)
        if file_path.suffix.lower() in ['.dcm', '.dicom', '.dic']:
            return True
        
        # If pydicom is available, try to read the file as DICOM
        if PYDICOM_AVAILABLE:
            try:
                # Try to read the file header only
                pydicom.dcmread(str(file_path), stop_before_pixels=True)
                return True
            except Exception:
                return False
        
        # If pydicom is not available, check for DICOM magic number
        try:
            with open(file_path, 'rb') as f:
                # Skip preamble (128 bytes) and check for DICM marker
                f.seek(128)
                return f.read(4) == b'DICM'
        except Exception:
            return False


class DicomFileInfo:
    """Class for storing information about a DICOM file."""
    
    def __init__(self, file_path, relative_path=None):
        """
        Initialize the DICOM file information.
        
        Args:
            file_path (Path): The absolute path to the DICOM file.
            relative_path (Path, optional): The path relative to the input directory.
        """
        self.file_path = file_path
        self.relative_path = relative_path or file_path.name
        self.size = file_path.stat().st_size
        self.is_valid = True
        self.error_message = None
    
    def validate(self):
        """
        Validate that the file is a valid DICOM file.
        
        Returns:
            bool: True if the file is a valid DICOM file, False otherwise.
        """
        if not PYDICOM_AVAILABLE:
            # Can't validate without pydicom
            return True
        
        try:
            # Try to read the file
            pydicom.dcmread(str(self.file_path))
            return True
        except Exception as e:
            self.is_valid = False
            self.error_message = str(e)
            return False
    
    def __str__(self):
        """Return a string representation of the DICOM file information."""
        return f"DicomFileInfo(path={self.file_path}, size={self.size} bytes, valid={self.is_valid})"


def scan_directory(input_dir, recursive=True, validate=False):
    """
    Scan a directory for DICOM files.
    
    Args:
        input_dir (str or Path): The input directory to scan.
        recursive (bool): Whether to scan subdirectories recursively.
        validate (bool): Whether to validate that the files are valid DICOM files.
        
    Returns:
        list: A list of DicomFileInfo objects representing the found DICOM files.
    """
    scanner = DicomScanner(input_dir, recursive)
    file_paths = scanner.scan()
    
    # Convert to DicomFileInfo objects
    input_dir_path = Path(input_dir)
    file_infos = []
    
    for file_path in file_paths:
        try:
            # Calculate relative path
            relative_path = file_path.relative_to(input_dir_path)
            
            # Create file info
            file_info = DicomFileInfo(file_path, relative_path)
            
            # Validate if requested
            if validate:
                file_info.validate()
            
            file_infos.append(file_info)
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")
    
    return file_infos