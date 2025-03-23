"""
Fixed Value Anonymization Method Module

This module provides functionality for anonymizing DICOM tags with fixed values.
"""

import logging


def apply_fixed_value(tag, value_config, original_value=None):
    """
    Apply a fixed value to a DICOM tag.
    
    Args:
        tag (str): The DICOM tag name or keyword.
        value_config (dict): The value configuration.
        original_value: The original value of the tag (not used for fixed value).
        
    Returns:
        The fixed value to set.
    """
    if 'value' not in value_config:
        raise ValueError(f"Fixed value not specified for tag {tag}")
    
    fixed_value = value_config['value']
    logging.debug(f"Applying fixed value '{fixed_value}' to tag {tag}")
    
    return fixed_value


class FixedValueAnonymizer:
    """Anonymizer for applying fixed values to DICOM tags."""
    
    def __init__(self, default_value="ANONYMOUS"):
        """
        Initialize the fixed value anonymizer.
        
        Args:
            default_value (str): The default value to use if no value is specified.
        """
        self.default_value = default_value
    
    def anonymize(self, tag, value_config, original_value=None):
        """
        Anonymize a DICOM tag with a fixed value.
        
        Args:
            tag (str): The DICOM tag name or keyword.
            value_config (dict): The value configuration.
            original_value: The original value of the tag (not used for fixed value).
            
        Returns:
            The fixed value to set.
        """
        # Get the fixed value from the configuration, or use the default
        fixed_value = value_config.get('value', self.default_value)
        
        logging.debug(f"Anonymizing tag {tag} with fixed value '{fixed_value}'")
        
        return fixed_value