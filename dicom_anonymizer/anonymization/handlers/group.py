"""
Group Tag Handler Module

This module provides functionality for anonymizing groups of DICOM tags.
"""

import logging
import re

try:
    import pydicom
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False


class GroupTagHandler:
    """Handler for anonymizing groups of DICOM tags."""
    
    def __init__(self):
        """Initialize the group tag handler."""
        # Check if pydicom is available
        if not PYDICOM_AVAILABLE:
            raise ImportError("pydicom is required for DICOM anonymization. Install it with 'pip install pydicom'.")
    
    def anonymize(self, dataset, group_configs, method_handlers):
        """
        Anonymize tag groups in a DICOM dataset.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to anonymize.
            group_configs (list): List of group configurations.
            method_handlers (dict): Dictionary of method handler functions.
        """
        if not group_configs:
            return
        
        for group_config in group_configs:
            self._anonymize_group(dataset, group_config, method_handlers)
    
    def _anonymize_group(self, dataset, group_config, method_handlers):
        """
        Anonymize a group of tags in a DICOM dataset.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to anonymize.
            group_config (dict): The group configuration.
            method_handlers (dict): Dictionary of method handler functions.
        """
        # Get group information
        group_name = group_config.get('group')
        if not group_name:
            logging.warning("Group name not specified in configuration")
            return
        
        # Get anonymization method
        method = group_config.get('method')
        if not method:
            logging.warning(f"Anonymization method not specified for group {group_name}")
            return
        
        # Check if method is supported
        if method not in method_handlers:
            logging.warning(f"Unsupported anonymization method for group {group_name}: {method}")
            return
        
        # Get the method handler
        method_handler = method_handlers[method]
        
        # Get exceptions (tags to exclude from anonymization)
        exceptions = group_config.get('exceptions', [])
        
        # Find all tags in the dataset that belong to the group
        group_tags = self._find_group_tags(dataset, group_name)
        
        # Anonymize each tag in the group
        for tag_name in group_tags:
            # Skip exceptions
            if tag_name in exceptions:
                logging.debug(f"Skipping exception tag {tag_name} in group {group_name}")
                continue
            
            try:
                # Get original value
                original_value = dataset.get(tag_name)
                
                # Apply anonymization method
                new_value = method_handler(tag_name, group_config, original_value)
                
                # Update or remove the tag
                if new_value is None:
                    # Remove the tag
                    del dataset[tag_name]
                    logging.debug(f"Removed tag {tag_name} from group {group_name}")
                else:
                    # Update the tag value
                    dataset[tag_name].value = new_value
                    logging.debug(f"Anonymized tag {tag_name} from group {group_name}")
            
            except Exception as e:
                logging.error(f"Error anonymizing tag {tag_name} from group {group_name}: {str(e)}")
    
    def _find_group_tags(self, dataset, group_name):
        """
        Find all tags in a dataset that belong to a specific group.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to search.
            group_name (str): The name of the group to find.
            
        Returns:
            list: A list of tag names that belong to the group.
        """
        group_tags = []
        
        # Handle special group names
        if group_name.lower() == 'patient':
            # Find all Patient-related tags
            pattern = re.compile(r'^Patient', re.IGNORECASE)
            group_tags = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group_name.lower() == 'study':
            # Find all Study-related tags
            pattern = re.compile(r'^Study', re.IGNORECASE)
            group_tags = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group_name.lower() == 'series':
            # Find all Series-related tags
            pattern = re.compile(r'^Series', re.IGNORECASE)
            group_tags = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group_name.lower() == 'institution':
            # Find all Institution-related tags
            pattern = re.compile(r'^Institution', re.IGNORECASE)
            group_tags = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group_name.lower() == 'physician':
            # Find all Physician-related tags
            pattern = re.compile(r'^Physician|^Referring|^Requesting|^Operator', re.IGNORECASE)
            group_tags = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group_name.lower() == 'device':
            # Find all Device-related tags
            pattern = re.compile(r'^Device|^Detector|^Generator', re.IGNORECASE)
            group_tags = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group_name.startswith('0x'):
            # Handle group specified as a hex group number (e.g., "0x0010")
            try:
                group_number = int(group_name, 16)
                
                # Find all tags with the specified group number
                for tag in dataset:
                    if tag.group == group_number:
                        tag_name = pydicom.datadict.keyword_for_tag(tag)
                        if tag_name:
                            group_tags.append(tag_name)
                        else:
                            # For private tags or tags without keywords, use the tag string
                            group_tags.append(str(tag))
            
            except ValueError:
                logging.warning(f"Invalid group number format: {group_name}")
        
        else:
            # For custom group names, use a regex pattern
            try:
                pattern = re.compile(group_name, re.IGNORECASE)
                group_tags = [tag for tag in dataset.dir() if pattern.match(tag)]
            except re.error:
                logging.warning(f"Invalid regex pattern for group: {group_name}")
        
        logging.debug(f"Found {len(group_tags)} tags in group {group_name}")
        return group_tags