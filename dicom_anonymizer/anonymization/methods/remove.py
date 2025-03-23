"""
Remove Tag Anonymization Method Module

This module provides functionality for removing DICOM tags during anonymization.
"""

import logging


class RemoveTagAnonymizer:
    """Anonymizer for removing DICOM tags."""
    
    def __init__(self):
        """Initialize the remove tag anonymizer."""
        pass
    
    def anonymize(self, tag, value_config, original_value=None):
        """
        Anonymize a DICOM tag by removing it.
        
        Args:
            tag (str): The DICOM tag name or keyword.
            value_config (dict): The value configuration (not used for removal).
            original_value: The original value of the tag (not used for removal).
            
        Returns:
            None: Indicates that the tag should be removed.
        """
        logging.debug(f"Removing tag {tag}")
        return None


def apply_remove_tag(tag, value_config, original_value=None):
    """
    Apply tag removal to a DICOM tag.
    
    Args:
        tag (str): The DICOM tag name or keyword.
        value_config (dict): The value configuration (not used for removal).
        original_value: The original value of the tag (not used for removal).
        
    Returns:
        None: Indicates that the tag should be removed.
    """
    logging.debug(f"Removing tag {tag}")
    return None


def remove_tags(dataset, tags):
    """
    Remove multiple tags from a DICOM dataset.
    
    Args:
        dataset (pydicom.Dataset): The DICOM dataset to modify.
        tags (list): A list of tag names or keywords to remove.
        
    Returns:
        pydicom.Dataset: The modified dataset.
    """
    for tag in tags:
        if tag in dataset:
            del dataset[tag]
            logging.debug(f"Removed tag {tag}")
        else:
            logging.debug(f"Tag {tag} not found in dataset")
    
    return dataset


def remove_tag_groups(dataset, groups):
    """
    Remove groups of tags from a DICOM dataset.
    
    Args:
        dataset (pydicom.Dataset): The DICOM dataset to modify.
        groups (list): A list of group names to remove.
        
    Returns:
        pydicom.Dataset: The modified dataset.
    """
    import re
    
    for group in groups:
        # Handle special group names
        if group.lower() == 'patient':
            # Find all Patient-related tags
            pattern = re.compile(r'^Patient', re.IGNORECASE)
            tags_to_remove = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group.lower() == 'study':
            # Find all Study-related tags
            pattern = re.compile(r'^Study', re.IGNORECASE)
            tags_to_remove = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group.lower() == 'series':
            # Find all Series-related tags
            pattern = re.compile(r'^Series', re.IGNORECASE)
            tags_to_remove = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group.lower() == 'institution':
            # Find all Institution-related tags
            pattern = re.compile(r'^Institution', re.IGNORECASE)
            tags_to_remove = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        elif group.lower() == 'physician':
            # Find all Physician-related tags
            pattern = re.compile(r'^Physician|^Referring|^Requesting|^Operator', re.IGNORECASE)
            tags_to_remove = [tag for tag in dataset.dir() if pattern.match(tag)]
        
        else:
            # For custom group names, use a regex pattern
            try:
                pattern = re.compile(group, re.IGNORECASE)
                tags_to_remove = [tag for tag in dataset.dir() if pattern.match(tag)]
            except re.error:
                logging.warning(f"Invalid regex pattern for group: {group}")
                continue
        
        # Remove the tags
        for tag in tags_to_remove:
            if tag in dataset:
                del dataset[tag]
                logging.debug(f"Removed tag {tag} from group {group}")
    
    return dataset


def remove_private_tags(dataset):
    """
    Remove all private tags from a DICOM dataset.
    
    Args:
        dataset (pydicom.Dataset): The DICOM dataset to modify.
        
    Returns:
        pydicom.Dataset: The modified dataset.
    """
    # Get a list of all private tags
    private_tags = []
    for tag in dataset:
        # Private groups have odd group numbers
        if tag.group % 2 == 1:
            private_tags.append(tag)
    
    # Remove the private tags
    for tag in private_tags:
        del dataset[tag]
        logging.debug(f"Removed private tag {tag}")
    
    return dataset