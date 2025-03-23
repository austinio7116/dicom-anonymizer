"""
Configuration Validator Module

This module provides validation for the DICOM anonymizer configuration.
It ensures that all required fields are present and have valid values.
"""

import logging
from pathlib import Path


class ConfigValidator:
    """Validator for DICOM anonymizer configuration."""
    
    # Valid anonymization methods
    VALID_METHODS = ['fixed', 'random', 'hash', 'remove', 'date_shift']
    
    @staticmethod
    def validate(config):
        """
        Validate the configuration.
        
        Args:
            config (dict): The configuration to validate.
            
        Returns:
            dict: The validated configuration.
            
        Raises:
            ValueError: If the configuration is invalid.
        """
        ConfigValidator._validate_input_section(config)
        ConfigValidator._validate_output_section(config)
        ConfigValidator._validate_logging_section(config)
        ConfigValidator._validate_anonymization_section(config)
        
        return config
    
    @staticmethod
    def _validate_input_section(config):
        """Validate the input section of the configuration."""
        if 'input' not in config:
            raise ValueError("Input section is required in configuration")
        
        input_config = config['input']
        if not isinstance(input_config, dict):
            raise ValueError("Input section must be a dictionary")
        
        if 'directory' not in input_config:
            raise ValueError("Input directory is required in input section")
        
        input_dir = Path(input_config['directory'])
        if not input_dir.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        if not input_dir.is_dir():
            raise ValueError(f"Input path is not a directory: {input_dir}")
        
        if 'recursive' in input_config and not isinstance(input_config['recursive'], bool):
            raise ValueError("Input recursive flag must be a boolean")
    
    @staticmethod
    def _validate_output_section(config):
        """Validate the output section of the configuration."""
        if 'output' not in config:
            raise ValueError("Output section is required in configuration")
        
        output_config = config['output']
        if not isinstance(output_config, dict):
            raise ValueError("Output section must be a dictionary")
        
        if 'directory' not in output_config:
            raise ValueError("Output directory is required in output section")
        
        # Output directory will be created if it doesn't exist, so we don't check existence
        
        if 'preserve_structure' in output_config and not isinstance(output_config['preserve_structure'], bool):
            raise ValueError("Output preserve_structure flag must be a boolean")
    
    @staticmethod
    def _validate_logging_section(config):
        """Validate the logging section of the configuration."""
        if 'logging' not in config:
            config['logging'] = {}
        
        logging_config = config['logging']
        if not isinstance(logging_config, dict):
            raise ValueError("Logging section must be a dictionary")
        
        if 'level' in logging_config:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if logging_config['level'] not in valid_levels:
                raise ValueError(f"Invalid logging level: {logging_config['level']}. Must be one of {valid_levels}")
        
        if 'file' in logging_config:
            log_file = Path(logging_config['file'])
            log_dir = log_file.parent
            
            if not log_dir.exists():
                logging.warning(f"Log directory does not exist: {log_dir}. It will be created.")
    
    @staticmethod
    def _validate_anonymization_section(config):
        """Validate the anonymization section of the configuration."""
        if 'anonymization' not in config:
            raise ValueError("Anonymization section is required in configuration")
        
        anon_config = config['anonymization']
        if not isinstance(anon_config, dict):
            raise ValueError("Anonymization section must be a dictionary")
        
        if not any(key in anon_config for key in ['standard_tags', 'tag_groups', 'private_tags']):
            raise ValueError("At least one type of tag (standard_tags, tag_groups, or private_tags) must be specified for anonymization")
        
        # Validate standard tags
        if 'standard_tags' in anon_config:
            ConfigValidator._validate_standard_tags(anon_config['standard_tags'])
        
        # Validate tag groups
        if 'tag_groups' in anon_config:
            ConfigValidator._validate_tag_groups(anon_config['tag_groups'])
        
        # Validate private tags
        if 'private_tags' in anon_config:
            ConfigValidator._validate_private_tags(anon_config['private_tags'])
    
    @staticmethod
    def _validate_standard_tags(standard_tags):
        """Validate standard tags configuration."""
        if not isinstance(standard_tags, list):
            raise ValueError("Standard tags must be a list")
        
        for tag_config in standard_tags:
            if not isinstance(tag_config, dict):
                raise ValueError("Each standard tag configuration must be a dictionary")
            
            if 'tag' not in tag_config:
                raise ValueError("Tag identifier is required for standard tags")
            
            if 'method' not in tag_config:
                raise ValueError(f"Anonymization method is required for tag {tag_config['tag']}")
            
            if tag_config['method'] not in ConfigValidator.VALID_METHODS:
                raise ValueError(f"Invalid anonymization method for tag {tag_config['tag']}: {tag_config['method']}. Must be one of {ConfigValidator.VALID_METHODS}")
            
            # Check for required parameters based on method
            if tag_config['method'] == 'fixed' and 'value' not in tag_config:
                raise ValueError(f"Fixed value is required for tag {tag_config['tag']} with fixed method")
            
            if tag_config['method'] == 'hash' and 'salt' not in tag_config:
                logging.warning(f"No salt specified for tag {tag_config['tag']} with hash method. Using default salt.")
    
    @staticmethod
    def _validate_tag_groups(tag_groups):
        """Validate tag groups configuration."""
        if not isinstance(tag_groups, list):
            raise ValueError("Tag groups must be a list")
        
        for group_config in tag_groups:
            if not isinstance(group_config, dict):
                raise ValueError("Each tag group configuration must be a dictionary")
            
            if 'group' not in group_config:
                raise ValueError("Group identifier is required for tag groups")
            
            if 'method' not in group_config:
                raise ValueError(f"Anonymization method is required for group {group_config['group']}")
            
            if group_config['method'] not in ConfigValidator.VALID_METHODS:
                raise ValueError(f"Invalid anonymization method for group {group_config['group']}: {group_config['method']}. Must be one of {ConfigValidator.VALID_METHODS}")
            
            # Check for required parameters based on method
            if group_config['method'] == 'fixed' and 'value' not in group_config:
                raise ValueError(f"Fixed value is required for group {group_config['group']} with fixed method")
            
            if group_config['method'] == 'hash' and 'salt' not in group_config:
                logging.warning(f"No salt specified for group {group_config['group']} with hash method. Using default salt.")
            
            # Validate exceptions if present
            if 'exceptions' in group_config and not isinstance(group_config['exceptions'], list):
                raise ValueError(f"Exceptions for group {group_config['group']} must be a list")
    
    @staticmethod
    def _validate_private_tags(private_tags):
        """Validate private tags configuration."""
        if not isinstance(private_tags, list):
            raise ValueError("Private tags must be a list")
        
        for tag_config in private_tags:
            if not isinstance(tag_config, dict):
                raise ValueError("Each private tag configuration must be a dictionary")
            
            if 'group' not in tag_config:
                raise ValueError("Group identifier is required for private tags")
            
            # Creator is optional for private tags
            
            if 'method' not in tag_config:
                raise ValueError(f"Anonymization method is required for private tag group {tag_config['group']}")
            
            if tag_config['method'] not in ConfigValidator.VALID_METHODS:
                raise ValueError(f"Invalid anonymization method for private tag group {tag_config['group']}: {tag_config['method']}. Must be one of {ConfigValidator.VALID_METHODS}")
            
            # Check for required parameters based on method
            if tag_config['method'] == 'fixed' and 'value' not in tag_config:
                raise ValueError(f"Fixed value is required for private tag group {tag_config['group']} with fixed method")
            
            if tag_config['method'] == 'hash' and 'salt' not in tag_config:
                logging.warning(f"No salt specified for private tag group {tag_config['group']} with hash method. Using default salt.")