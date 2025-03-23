"""
Anonymization Engine Module

This module provides the core functionality for anonymizing DICOM datasets.
It applies anonymization rules to DICOM tags based on the configuration.
"""

import logging
import hashlib
import random
import string
from datetime import datetime, timedelta

try:
    import pydicom
    from pydicom.dataset import Dataset
    from pydicom.sequence import Sequence
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False


class AnonymizationEngine:
    """
    Engine for anonymizing DICOM datasets.
    
    This class applies anonymization rules to DICOM datasets based on the configuration.
    """
    
    def __init__(self, anonymization_config):
        """
        Initialize the anonymization engine.
        
        Args:
            anonymization_config (dict): The anonymization configuration.
        """
        self.config = anonymization_config
        
        # Check if pydicom is available
        if not PYDICOM_AVAILABLE:
            raise ImportError("pydicom is required for DICOM anonymization. Install it with 'pip install pydicom'.")
        
        # Initialize method handlers
        self.method_handlers = {
            'fixed': self._apply_fixed_value,
            'random': self._apply_random_value,
            'hash': self._apply_hash_value,
            'remove': self._apply_remove_tag,
            'date_shift': self._apply_date_shift
        }
        
        # Initialize tag handlers
        from dicom_anonymizer.anonymization.handlers.standard import StandardTagHandler
        from dicom_anonymizer.anonymization.handlers.group import GroupTagHandler
        from dicom_anonymizer.anonymization.handlers.private import PrivateTagHandler
        
        self.tag_handlers = {
            'standard_tags': StandardTagHandler(),
            'tag_groups': GroupTagHandler(),
            'private_tags': PrivateTagHandler()
        }
        
        # Cache for consistent anonymization
        self.value_cache = {}
    
    def anonymize(self, dataset):
        """
        Anonymize a DICOM dataset.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to anonymize.
            
        Returns:
            pydicom.Dataset: The anonymized DICOM dataset.
        """
        # Create a copy of the dataset to avoid modifying the original
        anonymized_dataset = dataset.copy()
        
        # Apply anonymization rules
        for tag_type, handler in self.tag_handlers.items():
            if tag_type in self.config:
                handler.anonymize(anonymized_dataset, self.config[tag_type], self.method_handlers)
        
        # Handle sequences (recursively anonymize nested datasets)
        self._anonymize_sequences(anonymized_dataset)
        
        return anonymized_dataset
    
    def _anonymize_sequences(self, dataset):
        """
        Recursively anonymize sequences in a DICOM dataset.
        
        Args:
            dataset (pydicom.Dataset): The DICOM dataset to anonymize.
        """
        for elem in dataset.values():
            if isinstance(elem, Sequence):
                for item in elem:
                    if isinstance(item, Dataset):
                        # Apply anonymization rules to each item in the sequence
                        for tag_type, handler in self.tag_handlers.items():
                            if tag_type in self.config:
                                handler.anonymize(item, self.config[tag_type], self.method_handlers)
                        
                        # Recursively anonymize nested sequences
                        self._anonymize_sequences(item)
    
    def _apply_fixed_value(self, tag, value_config, original_value=None):
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
        
        return value_config['value']
    
    def _apply_random_value(self, tag, value_config, original_value=None):
        """
        Apply a random value to a DICOM tag.
        
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
        length = value_config.get('length', 10)
        
        if random_type == 'string':
            # Generate a random string
            chars = string.ascii_letters + string.digits
            random_value = ''.join(random.choice(chars) for _ in range(length))
        
        elif random_type == 'number':
            # Generate a random number
            min_val = value_config.get('min', 0)
            max_val = value_config.get('max', 1000)
            random_value = random.randint(min_val, max_val)
        
        elif random_type == 'date':
            # Generate a random date
            from datetime import datetime, timedelta
            
            start_date = value_config.get('start_date', '1900-01-01')
            end_date = value_config.get('end_date', '2000-01-01')
            
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            delta = end_dt - start_dt
            random_days = random.randint(0, delta.days)
            random_date = start_dt + timedelta(days=random_days)
            
            random_value = random_date.strftime('%Y%m%d')
        
        else:
            raise ValueError(f"Invalid random type for tag {tag}: {random_type}")
        
        # Cache the random value for consistency
        self.value_cache[cache_key] = random_value
        
        return random_value
    
    def _apply_hash_value(self, tag, value_config, original_value=None):
        """
        Apply a hash value to a DICOM tag.
        
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
        
        # Get the salt for hashing
        salt = value_config.get('salt', 'default_salt')
        
        # Convert original value to string if it's not already
        if not isinstance(original_value, str):
            original_value = str(original_value)
        
        # Create a hash of the original value with the salt
        hash_input = f"{original_value}{salt}"
        hash_obj = hashlib.sha256(hash_input.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Truncate the hash if needed
        max_length = value_config.get('max_length', None)
        if max_length and len(hash_hex) > max_length:
            hash_hex = hash_hex[:max_length]
        
        return hash_hex
    
    def _apply_remove_tag(self, tag, value_config, original_value=None):
        """
        Remove a DICOM tag.
        
        Args:
            tag (str): The DICOM tag name or keyword.
            value_config (dict): The value configuration.
            original_value: The original value of the tag (not used for removal).
            
        Returns:
            None to indicate the tag should be removed.
        """
        return None
    
    def _apply_date_shift(self, tag, value_config, original_value=None):
        """
        Apply a date shift to a DICOM tag.
        
        Args:
            tag (str): The DICOM tag name or keyword.
            value_config (dict): The value configuration.
            original_value: The original value of the tag.
            
        Returns:
            The shifted date value to set.
        """
        if original_value is None or not isinstance(original_value, str):
            # If there's no original value or it's not a string, return a fixed date
            return "19000101"
        
        # Check if we've already calculated the date shift
        if 'date_shift_days' not in self.value_cache:
            # Get the shift parameters
            shift_min = value_config.get('min_days', -365)
            shift_max = value_config.get('max_days', 365)
            
            # Generate a random shift within the specified range
            shift_days = random.randint(shift_min, shift_max)
            
            # Cache the shift for consistency across all dates
            self.value_cache['date_shift_days'] = shift_days
        else:
            shift_days = self.value_cache['date_shift_days']
        
        try:
            # Parse the original date
            # DICOM dates are typically in format YYYYMMDD
            if len(original_value) == 8:
                original_date = datetime.strptime(original_value, '%Y%m%d')
                
                # Apply the shift
                shifted_date = original_date + timedelta(days=shift_days)
                
                # Format the shifted date
                return shifted_date.strftime('%Y%m%d')
            
            # Handle other date formats (e.g., YYYY.MM.DD)
            elif '.' in original_value:
                original_date = datetime.strptime(original_value, '%Y.%m.%d')
                shifted_date = original_date + timedelta(days=shift_days)
                return shifted_date.strftime('%Y.%m.%d')
            
            else:
                logging.warning(f"Unrecognized date format for tag {tag}: {original_value}")
                return "19000101"
        
        except Exception as e:
            logging.error(f"Error shifting date for tag {tag}: {str(e)}")
            return "19000101"