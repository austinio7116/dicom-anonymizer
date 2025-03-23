"""
Anonymization Methods Package

This package provides various methods for anonymizing DICOM tags.
"""

from dicom_anonymizer.anonymization.methods.fixed import apply_fixed_value, FixedValueAnonymizer
from dicom_anonymizer.anonymization.methods.random import apply_random_value, RandomValueAnonymizer
from dicom_anonymizer.anonymization.methods.hash import apply_hash_value, HashValueAnonymizer, consistent_hash
from dicom_anonymizer.anonymization.methods.remove import apply_remove_tag, RemoveTagAnonymizer, remove_tags, remove_tag_groups, remove_private_tags


# Dictionary of method handler functions
METHOD_HANDLERS = {
    'fixed': apply_fixed_value,
    'random': apply_random_value,
    'hash': apply_hash_value,
    'remove': apply_remove_tag
}


# Dictionary of anonymizer classes
ANONYMIZER_CLASSES = {
    'fixed': FixedValueAnonymizer,
    'random': RandomValueAnonymizer,
    'hash': HashValueAnonymizer,
    'remove': RemoveTagAnonymizer
}


def get_method_handler(method_name):
    """
    Get a method handler function by name.
    
    Args:
        method_name (str): The name of the method.
        
    Returns:
        function: The method handler function.
        
    Raises:
        ValueError: If the method is not supported.
    """
    if method_name not in METHOD_HANDLERS:
        raise ValueError(f"Unsupported anonymization method: {method_name}")
    
    return METHOD_HANDLERS[method_name]


def get_anonymizer(method_name, **kwargs):
    """
    Get an anonymizer instance by method name.
    
    Args:
        method_name (str): The name of the method.
        **kwargs: Additional arguments to pass to the anonymizer constructor.
        
    Returns:
        object: An instance of the anonymizer class.
        
    Raises:
        ValueError: If the method is not supported.
    """
    if method_name not in ANONYMIZER_CLASSES:
        raise ValueError(f"Unsupported anonymization method: {method_name}")
    
    return ANONYMIZER_CLASSES[method_name](**kwargs)