#!/usr/bin/env python
"""
DICOM Anonymizer - Command Line Interface

This module serves as the entry point for the DICOM anonymizer tool when run as a command-line application.
It parses command-line arguments and initiates the anonymization process.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dicom_anonymizer.config.parser import ConfigParser
from dicom_anonymizer.core.processor import DicomProcessor
from dicom_anonymizer.utils.logging import setup_logging


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DICOM Anonymizer - A tool for anonymizing DICOM files"
    )
    parser.add_argument(
        "-c", "--config", 
        required=True,
        help="Path to the configuration file (YAML or JSON)"
    )
    parser.add_argument(
        "-i", "--input", 
        help="Input directory containing DICOM files (overrides config file)"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output directory for anonymized DICOM files (overrides config file)"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--log-file", 
        help="Path to log file (overrides config file)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    try:
        # Load configuration
        config_parser = ConfigParser(args.config)
        config = config_parser.parse()
        
        # Override config with command line arguments if provided
        if args.input:
            config["input"]["directory"] = args.input
        if args.output:
            config["output"]["directory"] = args.output
        if args.log_file:
            config["logging"]["file"] = args.log_file
        if args.verbose:
            config["logging"]["level"] = "DEBUG"
        
        # Setup logging
        log_level = config["logging"].get("level", "INFO")
        log_file = config["logging"].get("file", None)
        setup_logging(log_level, log_file)
        
        # Validate input and output directories
        input_dir = Path(config["input"]["directory"])
        output_dir = Path(config["output"]["directory"])
        
        if not input_dir.exists():
            logging.error(f"Input directory does not exist: {input_dir}")
            sys.exit(1)
        
        # Create output directory if it doesn't exist
        if not output_dir.exists():
            logging.info(f"Creating output directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize processor and start anonymization
        processor = DicomProcessor(config)
        processor.process()
        
        logging.info("Anonymization completed successfully")
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        if args.verbose:
            logging.exception("Detailed error information:")
        sys.exit(1)


if __name__ == "__main__":
    main()