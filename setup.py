#!/usr/bin/env python
"""
Setup script for the DICOM Anonymizer package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dicom-anonymizer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A configurable Python tool for anonymizing DICOM files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dicom-anonymizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydicom>=2.3.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "progress": ["tqdm>=4.64.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "isort>=5.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dicom-anonymizer=dicom_anonymizer.__main__:main",
        ],
    },
)