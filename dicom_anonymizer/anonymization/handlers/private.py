"""
Private Tag Handler Module

This module provides functionality for anonymizing private DICOM tags.
"""

import logging

try:
    import pydicom
    from pydicom.tag import Tag
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False


class PrivateTagHandler:
    """Handler for anonymizing private DICOM tags."""
    
    def __init__(self):
        """Initialize the private tag handler."""
        # Check if pydicom is available
        if not PYDICOM_AVAILABLE:
            raise ImportError("pydicom is required for DICOM anonymization. Install it with 'pip install pydicom'.")
    
    def anonymize(self, dataset, private_configs, method_handlers):
        """
        Anonymize private tags in a DICOM dataset.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to anonymize.
            private_configs (list): List of private tag configurations.
            method_handlers (dict): Dictionary of method handler functions.
        """
        if not private_configs:
            return
        
        for private_config in private_configs:
            self._anonymize_private_group(dataset, private_config, method_handlers)
    
    def _anonymize_private_group(self, dataset, private_config, method_handlers):
        """
        Anonymize a group of private tags in a DICOM dataset.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to anonymize.
            private_config (dict): The private tag configuration.
            method_handlers (dict): Dictionary of method handler functions.
        """
        # Get group information
        group_str = private_config.get('group')
        if not group_str:
            logging.warning("Private group not specified in configuration")
            return
        
        # Get creator (optional)
        creator = private_config.get('creator')
        
        # Get anonymization method
        method = private_config.get('method')
        if not method:
            logging.warning(f"Anonymization method not specified for private group {group_str}")
            return
        
        # Check if method is supported
        if method not in method_handlers:
            logging.warning(f"Unsupported anonymization method for private group {group_str}: {method}")
            return
        
        # Get the method handler
        method_handler = method_handlers[method]
        
        try:
            # Parse group number
            if group_str.startswith('0x'):
                group = int(group_str, 16)
            else:
                try:
                    group = int(group_str)
                except ValueError:
                    logging.warning(f"Invalid private group format: {group_str}")
                    return
            
            # Find all private tags in the specified group
            private_tags = self._find_private_tags(dataset, group, creator)
            
            # Anonymize each private tag
            for tag in private_tags:
                try:
                    # Get original value
                    original_value = dataset[tag].value
                    
                    # Apply anonymization method
                    new_value = method_handler(str(tag), private_config, original_value)
                    
                    # Update or remove the tag
                    if new_value is None:
                        # Remove the tag
                        del dataset[tag]
                        logging.debug(f"Removed private tag {tag}")
                    else:
                        # Update the tag value
                        dataset[tag].value = new_value
                        logging.debug(f"Anonymized private tag {tag}")
                
                except Exception as e:
                    logging.error(f"Error anonymizing private tag {tag}: {str(e)}")
        
        except Exception as e:
            logging.error(f"Error processing private group {group_str}: {str(e)}")
    
    def _find_private_tags(self, dataset, group, creator=None):
        """
        Find all private tags in a dataset that belong to a specific group and creator.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to search.
            group (int): The group number to find.
            creator (str, optional): The private creator to filter by.
            
        Returns:
            list: A list of private tags that match the criteria.
        """
        private_tags = []
        
        # Validate group is odd (private groups are odd-numbered)
        if group % 2 == 0:
            logging.warning(f"Group {group:04x} is not a private group (not odd)")
            return private_tags
        
        # Find all private creator blocks if creator is specified
        creator_blocks = {}
        if creator:
            for tag in dataset:
                # Check if tag is a private creator
                if tag.group == group and tag.element < 0x0100 and tag.element > 0:
                    if dataset[tag].value == creator:
                        # Found a matching creator, remember its block
                        block = tag.element
                        creator_blocks[block] = creator
        
        # Find all private tags in the specified group
        for tag in dataset:
            if tag.group == group:
                # Skip private creators
                if tag.element < 0x0100:
                    continue
                
                # If creator is specified, check if tag belongs to a matching creator block
                if creator:
                    # Extract the block from the element
                    block = (tag.element >> 8) & 0xFF
                    if block not in creator_blocks:
                        continue
                
                private_tags.append(tag)
        
        logging.debug(f"Found {len(private_tags)} private tags in group {group:04x}" + 
                     (f" with creator '{creator}'" if creator else ""))
        
        return private_tags


def is_private_group(group_number):
    """
    Check if a group number is a private group.
    
    Args:
        group_number (int): The group number to check.
        
    Returns:
        bool: True if the group is a private group, False otherwise.
    """
    # Private groups have odd group numbers
    return group_number % 2 == 1


def get_private_tag(dataset, group, element, creator=None):
    """
    Get a private tag from a dataset.
    
    Args:
        dataset (pydicom.Dataset): The DICOM dataset.
        group (int): The group number.
        element (int): The element number.
        creator (str, optional): The private creator.
        
    Returns:
        pydicom.tag.Tag: The private tag, or None if not found.
    """
    if not is_private_group(group):
        logging.warning(f"Group {group:04x} is not a private group")
        return None
    
    # If creator is specified, find the creator block
    if creator:
        creator_block = None
        
        # Find the creator block
        for tag in dataset:
            if tag.group == group and tag.element < 0x0100 and tag.element > 0:
                if dataset[tag].value == creator:
                    creator_block = tag.element
                    break
        
        if creator_block is None:
            logging.warning(f"Private creator '{creator}' not found in group {group:04x}")
            return None
        
        # Construct the private tag using the creator block
        block = creator_block
        private_element = ((block & 0xFF) << 8) | (element & 0xFF)
        return Tag(group, private_element)
    
    # If no creator is specified, just return the tag
    return Tag(group, element)