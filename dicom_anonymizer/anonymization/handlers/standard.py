"""
Standard Tag Handler Module

This module provides functionality for anonymizing standard DICOM tags.
"""

import logging

try:
    import pydicom
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False


class StandardTagHandler:
    """Handler for anonymizing standard DICOM tags."""
    
    def __init__(self):
        """Initialize the standard tag handler."""
        # Check if pydicom is available
        if not PYDICOM_AVAILABLE:
            raise ImportError("pydicom is required for DICOM anonymization. Install it with 'pip install pydicom'.")
    
    def anonymize(self, dataset, tag_configs, method_handlers):
        """
        Anonymize standard tags in a DICOM dataset.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to anonymize.
            tag_configs (list): List of tag configurations.
            method_handlers (dict): Dictionary of method handler functions.
        """
        if not tag_configs:
            return
        
        for tag_config in tag_configs:
            self._anonymize_tag(dataset, tag_config, method_handlers)
    
    def _anonymize_tag(self, dataset, tag_config, method_handlers):
        """
        Anonymize a single tag in a DICOM dataset.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to anonymize.
            tag_config (dict): The tag configuration.
            method_handlers (dict): Dictionary of method handler functions.
        """
        # Get tag information
        tag_name = tag_config.get('tag')
        if not tag_name:
            logging.warning("Tag name not specified in configuration")
            return
        
        # Get anonymization method
        method = tag_config.get('method')
        if not method:
            logging.warning(f"Anonymization method not specified for tag {tag_name}")
            return
        
        # Check if method is supported
        if method not in method_handlers:
            logging.warning(f"Unsupported anonymization method for tag {tag_name}: {method}")
            return
        
        # Get the method handler
        method_handler = method_handlers[method]
        
        try:
            # Check if tag exists in dataset
            if tag_name in dataset:
                # Get original value
                original_value = dataset.get(tag_name)
                
                # Apply anonymization method
                new_value = method_handler(tag_name, tag_config, original_value)
                
                # Update or remove the tag
                if new_value is None:
                    # Remove the tag
                    del dataset[tag_name]
                    logging.debug(f"Removed tag {tag_name}")
                else:
                    # Update the tag value
                    dataset[tag_name].value = new_value
                    logging.debug(f"Anonymized tag {tag_name}")
            else:
                logging.debug(f"Tag {tag_name} not found in dataset")
        
        except Exception as e:
            logging.error(f"Error anonymizing tag {tag_name}: {str(e)}")


def get_dicom_tag(tag_name):
    """
    Get a DICOM tag from its name or keyword.
    
    Args:
        tag_name (str): The DICOM tag name or keyword.
        
    Returns:
        pydicom.tag.Tag: The DICOM tag.
    """
    try:
        # Try to get tag by keyword
        return pydicom.datadict.tag_for_keyword(tag_name)
    except:
        # Try to parse tag as a hex string (e.g., "0010,0010")
        try:
            if ',' in tag_name:
                group, element = tag_name.split(',')
                return pydicom.tag.Tag(int(group, 16), int(element, 16))
        except:
            pass
    
    # If all else fails, return None
    return None