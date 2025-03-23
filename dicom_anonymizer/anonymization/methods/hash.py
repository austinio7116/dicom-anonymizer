"""
Hash Value Anonymization Method Module

This module provides functionality for anonymizing DICOM tags with hash values.
"""

import logging
import hashlib


class HashValueAnonymizer:
    """Anonymizer for applying hash values to DICOM tags."""
    
    def __init__(self, default_salt="dicom_anonymizer"):
        """
        Initialize the hash value anonymizer.
        
        Args:
            default_salt (str): The default salt to use if no salt is specified.
        """
        self.default_salt = default_salt
        # Cache for consistent anonymization
        self.value_cache = {}
    
    def anonymize(self, tag, value_config, original_value=None):
        """
        Anonymize a DICOM tag with a hash value.
        
        Args:
            tag (str): The DICOM tag name or keyword.
            value_config (dict): The value configuration.
            original_value: The original value of the tag.
            
        Returns:
            The hashed value to set.
        """
        if original_value is None:
            # If there's no original value, return a fixed string
            return "ANONYMIZED"
        
        # Check if we've already hashed this value
        cache_key = f"hash_{tag}_{original_value}"
        if cache_key in self.value_cache:
            return self.value_cache[cache_key]
        
        # Get the salt for hashing
        salt = value_config.get('salt', self.default_salt)
        
        # Get the hash algorithm
        algorithm = value_config.get('algorithm', 'sha256')
        
        # Convert original value to string if it's not already
        if not isinstance(original_value, str):
            original_value = str(original_value)
        
        # Create a hash of the original value with the salt
        hash_value = self._create_hash(original_value, salt, algorithm)
        
        # Truncate the hash if needed
        max_length = value_config.get('max_length', None)
        if max_length and len(hash_value) > max_length:
            hash_value = hash_value[:max_length]
        
        # Cache the hash value for consistency
        self.value_cache[cache_key] = hash_value
        
        logging.debug(f"Anonymizing tag {tag} with hash value")
        
        return hash_value
    
    def _create_hash(self, value, salt, algorithm):
        """
        Create a hash of a value with a salt.
        
        Args:
            value (str): The value to hash.
            salt (str): The salt to use.
            algorithm (str): The hash algorithm to use.
            
        Returns:
            str: The hashed value.
        """
        # Create the hash input
        hash_input = f"{value}{salt}"
        
        # Create the hash
        if algorithm == 'md5':
            hash_obj = hashlib.md5(hash_input.encode())
        elif algorithm == 'sha1':
            hash_obj = hashlib.sha1(hash_input.encode())
        elif algorithm == 'sha256':
            hash_obj = hashlib.sha256(hash_input.encode())
        elif algorithm == 'sha512':
            hash_obj = hashlib.sha512(hash_input.encode())
        else:
            logging.warning(f"Unknown hash algorithm '{algorithm}', using sha256")
            hash_obj = hashlib.sha256(hash_input.encode())
        
        # Return the hash as a hexadecimal string
        return hash_obj.hexdigest()


def apply_hash_value(tag, value_config, original_value=None):
    """
    Apply a hash value to a DICOM tag.
    
    Args:
        tag (str): The DICOM tag name or keyword.
        value_config (dict): The value configuration.
        original_value: The original value of the tag.
        
    Returns:
        The hashed value to set.
    """
    # Create a new anonymizer for each call
    # This means values won't be cached between calls
    anonymizer = HashValueAnonymizer()
    return anonymizer.anonymize(tag, value_config, original_value)


def consistent_hash(value, salt="dicom_anonymizer", algorithm="sha256", max_length=None):
    """
    Create a consistent hash of a value.
    
    This function can be used to create consistent hash values for DICOM tags
    outside of the anonymization process.
    
    Args:
        value (str): The value to hash.
        salt (str): The salt to use.
        algorithm (str): The hash algorithm to use.
        max_length (int, optional): The maximum length of the hash.
        
    Returns:
        str: The hashed value.
    """
    # Create a new anonymizer
    anonymizer = HashValueAnonymizer(default_salt=salt)
    
    # Create the hash
    value_config = {
        'salt': salt,
        'algorithm': algorithm,
        'max_length': max_length
    }
    
    return anonymizer.anonymize("custom", value_config, value)