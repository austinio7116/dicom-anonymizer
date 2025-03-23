"""
DICOM Processor Module

This module provides the main processing functionality for anonymizing DICOM files.
It coordinates the scanning, anonymization, and output of DICOM files.
"""

import logging
import os
import concurrent.futures
from pathlib import Path

try:
    import pydicom
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False

from dicom_anonymizer.core.scanner import scan_directory
from dicom_anonymizer.core.writer import DicomWriter
from dicom_anonymizer.anonymization.engine import AnonymizationEngine
from dicom_anonymizer.utils.progress import ProgressTracker


class DicomProcessor:
    """
    Processor for anonymizing DICOM files.
    
    This class coordinates the scanning, anonymization, and output of DICOM files.
    """
    
    def __init__(self, config):
        """
        Initialize the DICOM processor.
        
        Args:
            config (dict): The configuration dictionary.
        """
        self.config = config
        self.input_dir = Path(config['input']['directory'])
        self.output_dir = Path(config['output']['directory'])
        self.recursive = config['input'].get('recursive', True)
        self.preserve_structure = config['output'].get('preserve_structure', True)
        
        # Initialize anonymization engine
        self.anonymization_engine = AnonymizationEngine(config['anonymization'])
        
        # Initialize writer
        self.writer = DicomWriter(self.output_dir, self.preserve_structure)
        
        # Check if pydicom is available
        if not PYDICOM_AVAILABLE:
            raise ImportError("pydicom is required for DICOM processing. Install it with 'pip install pydicom'.")
    
    def process(self):
        """
        Process DICOM files according to the configuration.
        
        This method scans the input directory for DICOM files, anonymizes them,
        and writes the anonymized files to the output directory.
        """
        logging.info("Starting DICOM anonymization process")
        
        # Scan for DICOM files
        logging.info(f"Scanning input directory: {self.input_dir}")
        dicom_files = scan_directory(self.input_dir, self.recursive)
        
        if not dicom_files:
            logging.warning("No DICOM files found in the input directory")
            return
        
        logging.info(f"Found {len(dicom_files)} DICOM files")
        
        # Create output directory if it doesn't exist
        if not self.output_dir.exists():
            logging.info(f"Creating output directory: {self.output_dir}")
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process files
        self._process_files(dicom_files)
    
    def _process_files(self, dicom_files):
        """
        Process a list of DICOM files.
        
        Args:
            dicom_files (list): A list of DicomFileInfo objects to process.
        """
        # Initialize progress tracker
        progress = ProgressTracker(len(dicom_files), "Anonymizing DICOM files")
        progress.start()
        
        # Determine whether to use parallel processing
        max_workers = self.config.get('max_workers', None)
        if max_workers is None:
            # Default to number of CPU cores
            import multiprocessing
            max_workers = multiprocessing.cpu_count()
        
        # Process files
        if max_workers > 1:
            self._process_files_parallel(dicom_files, progress, max_workers)
        else:
            self._process_files_sequential(dicom_files, progress)
        
        progress.finish()
    
    def _process_files_sequential(self, dicom_files, progress):
        """
        Process DICOM files sequentially.
        
        Args:
            dicom_files (list): A list of DicomFileInfo objects to process.
            progress (ProgressTracker): The progress tracker.
        """
        logging.info("Processing files sequentially")
        
        for file_info in dicom_files:
            try:
                self._process_single_file(file_info)
                progress.update(success=True, filename=str(file_info.file_path))
            except Exception as e:
                logging.error(f"Error processing file {file_info.file_path}: {str(e)}")
                progress.update(success=False, filename=str(file_info.file_path))
    
    def _process_files_parallel(self, dicom_files, progress, max_workers):
        """
        Process DICOM files in parallel.
        
        Args:
            dicom_files (list): A list of DicomFileInfo objects to process.
            progress (ProgressTracker): The progress tracker.
            max_workers (int): The maximum number of worker threads.
        """
        logging.info(f"Processing files in parallel with {max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(self._process_single_file, file_info): file_info
                for file_info in dicom_files
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    future.result()
                    progress.update(success=True, filename=str(file_info.file_path))
                except Exception as e:
                    logging.error(f"Error processing file {file_info.file_path}: {str(e)}")
                    progress.update(success=False, filename=str(file_info.file_path))
    
    def _process_single_file(self, file_info):
        """
        Process a single DICOM file.
        
        Args:
            file_info (DicomFileInfo): The DICOM file information.
            
        Returns:
            Path: The path to the anonymized file.
        """
        try:
            # Read DICOM file
            dataset = pydicom.dcmread(str(file_info.file_path))
            
            # Anonymize dataset
            anonymized_dataset = self.anonymization_engine.anonymize(dataset)
            
            # Write anonymized dataset to output directory
            output_path = self.writer.write(anonymized_dataset, file_info.relative_path)
            
            return output_path
        
        except Exception as e:
            logging.error(f"Error processing file {file_info.file_path}: {str(e)}")
            raise