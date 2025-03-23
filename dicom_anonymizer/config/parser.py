"""
Configuration Parser Module

This module handles loading and parsing configuration files for the DICOM anonymizer.
It supports both YAML and JSON formats.
"""

import json
import logging
import os
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigParser:
    """Parser for configuration files in YAML or JSON format."""
    
    def __init__(self, config_path):
        """
        Initialize the configuration parser.
        
        Args:
            config_path (str): Path to the configuration file.
        """
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        self.file_extension = self.config_path.suffix.lower()
    
    def parse(self):
        """
        Parse the configuration file.
        
        Returns:
            dict: The parsed configuration.
        
        Raises:
            ValueError: If the file format is not supported or if parsing fails.
        """
        logging.info(f"Loading configuration from {self.config_path}")
        
        if self.file_extension in ['.yaml', '.yml']:
            return self._parse_yaml()
        elif self.file_extension == '.json':
            return self._parse_json()
        else:
            raise ValueError(f"Unsupported configuration file format: {self.file_extension}")
    
    def _parse_yaml(self):
        """Parse YAML configuration file."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML configuration files. Install it with 'pip install pyyaml'.")
        
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            return self._validate_and_set_defaults(config)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {str(e)}")
    
    def _parse_json(self):
        """Parse JSON configuration file."""
        try:
            with open(self.config_path, 'r') as file:
                config = json.load(file)
            return self._validate_and_set_defaults(config)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON configuration: {str(e)}")
    
    def _validate_and_set_defaults(self, config):
        """
        Validate the configuration and set default values for missing fields.
        
        Args:
            config (dict): The parsed configuration.
            
        Returns:
            dict: The validated configuration with defaults applied.
        """
        # Ensure required sections exist
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Set defaults for input section
        if 'input' not in config:
            config['input'] = {}
        if 'directory' not in config['input']:
            raise ValueError("Input directory must be specified in configuration")
        if 'recursive' not in config['input']:
            config['input']['recursive'] = True
        
        # Set defaults for output section
        if 'output' not in config:
            config['output'] = {}
        if 'directory' not in config['output']:
            raise ValueError("Output directory must be specified in configuration")
        if 'preserve_structure' not in config['output']:
            config['output']['preserve_structure'] = True
        
        # Set defaults for logging section
        if 'logging' not in config:
            config['logging'] = {}
        if 'level' not in config['logging']:
            config['logging']['level'] = "INFO"
        
        # Ensure anonymization section exists
        if 'anonymization' not in config:
            raise ValueError("Anonymization section must be specified in configuration")
        
        # Validate anonymization rules
        anon_config = config['anonymization']
        if not any(key in anon_config for key in ['standard_tags', 'tag_groups', 'private_tags']):
            raise ValueError("At least one type of tag (standard_tags, tag_groups, or private_tags) must be specified for anonymization")
        
        return config