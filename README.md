# DICOM Anonymizer

A configurable Python tool for anonymizing DICOM files.

## Overview

DICOM Anonymizer is a flexible and powerful tool for anonymizing DICOM (Digital Imaging and Communications in Medicine) files. It allows you to specify which tags to anonymize and how to anonymize them through a configuration file.

Key features:
- Configurable anonymization of standard DICOM tags, tag groups, and private tags
- Multiple anonymization methods (fixed value, random value, hash, removal)
- Support for nested directory structures
- Comprehensive logging and progress tracking
- Parallel processing for improved performance

## Installation

### Prerequisites

- Python 3.8 or higher
- pydicom library
- PyYAML library (for YAML configuration files)
- tqdm library (optional, for progress bars)

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/dicom-anonymizer.git
cd dicom-anonymizer

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Usage

### Basic Usage

```bash
# Anonymize DICOM files using a configuration file
python -m dicom_anonymizer --config config.yaml

# Specify input and output directories
python -m dicom_anonymizer --config config.yaml --input /path/to/input --output /path/to/output

# Enable verbose output
python -m dicom_anonymizer --config config.yaml --verbose
```

### Configuration File

The configuration file (YAML or JSON) specifies which DICOM tags to anonymize and how to anonymize them. Here's a basic example:

```yaml
# Input directory configuration
input:
  directory: "./input"  # Path to the input directory containing DICOM files
  recursive: true       # Whether to scan subdirectories recursively

# Output directory configuration
output:
  directory: "./output"  # Path to the output directory for anonymized DICOM files
  preserve_structure: true  # Whether to preserve the directory structure of the input files

# Logging configuration
logging:
  level: "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  file: "anonymization.log"  # Path to the log file (optional)

# Anonymization configuration
anonymization:
  # Standard tags to anonymize
  standard_tags:
    # Patient name - replace with fixed value
    - tag: "PatientName"
      method: "fixed"
      value: "ANONYMOUS"
    
    # Patient ID - replace with hash of original value
    - tag: "PatientID"
      method: "hash"
      salt: "custom-salt"
    
    # Patient birth date - replace with random date
    - tag: "PatientBirthDate"
      method: "random"
      type: "date"
      start_date: "1940-01-01"
      end_date: "2000-01-01"
    
    # Patient address - remove completely
    - tag: "PatientAddress"
      method: "remove"
  
  # Tag groups to anonymize
  tag_groups:
    # All physician-related tags - replace with fixed value
    - group: "Physician"
      method: "fixed"
      value: "ANONYMOUS PHYSICIAN"
  
  # Private tags to anonymize
  private_tags:
    # All private tags in group 0x0009 - remove completely
    - group: "0x0009"
      method: "remove"
```

See the `examples` directory for more configuration examples.

## Anonymization Methods

The following anonymization methods are supported:

### Fixed Value

Replace the tag value with a fixed value.

```yaml
- tag: "PatientName"
  method: "fixed"
  value: "ANONYMOUS"
```

### Random Value

Replace the tag value with a random value.

```yaml
- tag: "PatientID"
  method: "random"
  type: "string"  # string, number, date, uid
  length: 10
  charset: "alphanumeric"  # alphanumeric, alpha, numeric, hex, ascii
```

### Hash

Replace the tag value with a hash of the original value.

```yaml
- tag: "PatientID"
  method: "hash"
  salt: "custom-salt"
  algorithm: "sha256"  # md5, sha1, sha256, sha512
  max_length: 16
```

### Remove

Remove the tag completely.

```yaml
- tag: "PatientAddress"
  method: "remove"
```

### Date Shift

Shift dates by a random number of days (consistent across all dates).

```yaml
- tag: "PatientBirthDate"
  method: "date_shift"
  min_days: -1000
  max_days: 1000
```

## Tag Groups

You can anonymize groups of tags that match a pattern:

```yaml
# All patient-related tags
- group: "Patient"
  method: "fixed"
  value: "ANONYMOUS"
  exceptions: ["PatientWeight", "PatientHeight"]  # Tags to exclude

# All tags in a specific group (by hex group number)
- group: "0x0010"
  method: "remove"
```

## Private Tags

You can anonymize private tags by group and creator:

```yaml
# All private tags in group 0x0009
- group: "0x0009"
  method: "remove"

# Private tags with specific creator
- group: "0x0011"
  creator: "GEMS_PATI_01"
  method: "fixed"
  value: "ANONYMIZED"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.