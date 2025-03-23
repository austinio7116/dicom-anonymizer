"""
Random Value Anonymization Method Module

This module provides functionality for anonymizing DICOM tags with random values.
"""

import logging
import random
import string
from datetime import datetime, timedelta


class RandomValueAnonymizer:
    """Anonymizer for applying random values to DICOM tags."""
    
    def __init__(self):
        """Initialize the random value anonymizer."""
        # Cache for consistent anonymization
        self.value_cache = {}
    
    def anonymize(self, tag, value_config, original_value=None):
        """
        Anonymize a DICOM tag with a random value.
        
        Args:
            tag (str): The DICOM tag name or keyword.
            value_config (dict): The value configuration.
            original_value: The original value of the tag.
            
        Returns:
            The random value to set.
        """
        # Check if we've already generated a random value for this tag
        cache_key = f"random_{tag}"
        if cache_key in self.value_cache:
            return self.value_cache[cache_key]
        
        # Get the type of random value to generate
        random_type = value_config.get('type', 'string')
        
        # Generate the random value based on the type
        if random_type == 'string':
            random_value = self._generate_random_string(value_config)
        elif random_type == 'number':
            random_value = self._generate_random_number(value_config)
        elif random_type == 'date':
            random_value = self._generate_random_date(value_config)
        elif random_type == 'uid':
            random_value = self._generate_random_uid(value_config)
        else:
            logging.warning(f"Unknown random type '{random_type}' for tag {tag}, using string")
            random_value = self._generate_random_string(value_config)
        
        # Cache the random value for consistency
        self.value_cache[cache_key] = random_value
        
        logging.debug(f"Anonymizing tag {tag} with random value '{random_value}'")
        
        return random_value
    
    def _generate_random_string(self, value_config):
        """
        Generate a random string.
        
        Args:
            value_config (dict): The value configuration.
            
        Returns:
            str: A random string.
        """
        length = value_config.get('length', 10)
        charset = value_config.get('charset', 'alphanumeric')
        
        if charset == 'alphanumeric':
            chars = string.ascii_letters + string.digits
        elif charset == 'alpha':
            chars = string.ascii_letters
        elif charset == 'numeric':
            chars = string.digits
        elif charset == 'hex':
            chars = string.hexdigits
        elif charset == 'ascii':
            chars = string.printable
        else:
            logging.warning(f"Unknown charset '{charset}', using alphanumeric")
            chars = string.ascii_letters + string.digits
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _generate_random_number(self, value_config):
        """
        Generate a random number.
        
        Args:
            value_config (dict): The value configuration.
            
        Returns:
            int or float: A random number.
        """
        min_val = value_config.get('min', 0)
        max_val = value_config.get('max', 1000)
        is_float = value_config.get('float', False)
        
        if is_float:
            return random.uniform(min_val, max_val)
        else:
            return random.randint(min_val, max_val)
    
    def _generate_random_date(self, value_config):
        """
        Generate a random date.
        
        Args:
            value_config (dict): The value configuration.
            
        Returns:
            str: A random date in DICOM format (YYYYMMDD).
        """
        start_date = value_config.get('start_date', '1900-01-01')
        end_date = value_config.get('end_date', '2000-01-01')
        
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            delta = end_dt - start_dt
            random_days = random.randint(0, delta.days)
            random_date = start_dt + timedelta(days=random_days)
            
            return random_date.strftime('%Y%m%d')
        
        except ValueError as e:
            logging.warning(f"Error parsing date range: {str(e)}, using default")
            return '19000101'
    
    def _generate_random_uid(self, value_config):
        """
        Generate a random DICOM UID.
        
        Args:
            value_config (dict): The value configuration.
            
        Returns:
            str: A random DICOM UID.
        """
        prefix = value_config.get('prefix', '9.9.')
        length = value_config.get('length', 16)
        
        # Ensure prefix ends with a dot
        if not prefix.endswith('.'):
            prefix += '.'
        
        # Generate random digits for the UID
        uid_digits = ''.join(random.choice(string.digits) for _ in range(length))
        
        return prefix + uid_digits


def apply_random_value(tag, value_config, original_value=None):
    """
    Apply a random value to a DICOM tag.
    
    Args:
        tag (str): The DICOM tag name or keyword.
        value_config (dict): The value configuration.
        original_value: The original value of the tag.
        
    Returns:
        The random value to set.
    """
    # Create a new anonymizer for each call
    # This means values won't be cached between calls
    anonymizer = RandomValueAnonymizer()
    return anonymizer.anonymize(tag, value_config, original_value)