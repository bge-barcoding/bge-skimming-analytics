#!/usr/bin/env python3
"""
Unit tests for TSV file header validation.

This test verifies that all TSV files in the data folder and subfolders
have headers that match the definitions in metadata/headers.tsv.
"""

import csv
from pathlib import Path
import pytest


def get_expected_headers():
    """
    Read expected headers from metadata/headers.tsv.
    
    Returns:
        set: Set of expected column names from the barcode_validator TSV header
    """
    repo_root = Path(__file__).parent.parent
    headers_file = repo_root / "metadata" / "headers.tsv"
    
    expected_headers = set()
    with open(headers_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip the header row
        for row in reader:
            if row:  # Skip empty rows
                header_name = row[0].strip()
                expected_headers.add(header_name)
    
    return expected_headers


def get_tsv_files():
    """
    Find all TSV files in the data directory and subdirectories.
    
    Returns:
        list: List of Path objects for all TSV files
    """
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data"
    
    # Find all .tsv files recursively
    tsv_files = list(data_dir.glob("**/*.tsv"))
    
    return tsv_files


@pytest.mark.parametrize("tsv_file", get_tsv_files())
def test_tsv_headers(tsv_file):
    """
    Test that each TSV file has headers that are a subset of the expected headers.
    
    The test verifies that all headers in each TSV file are defined in 
    metadata/headers.tsv. TSV files may have a subset of the defined headers.
    """
    expected_headers = get_expected_headers()
    
    # Read the first line (headers) from the TSV file
    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        actual_headers = set(next(reader))
    
    # Check that all actual headers are in the expected headers
    unexpected_headers = actual_headers - expected_headers
    
    assert not unexpected_headers, (
        f"File '{tsv_file.relative_to(Path(__file__).parent.parent)}' contains "
        f"unexpected headers: {sorted(unexpected_headers)}. "
        f"All headers must be defined in metadata/headers.tsv"
    )


def test_expected_headers_exist():
    """
    Sanity check to ensure metadata/headers.tsv can be read and contains headers.
    """
    expected_headers = get_expected_headers()
    assert len(expected_headers) > 0, "No headers found in metadata/headers.tsv"


def test_tsv_files_exist():
    """
    Sanity check to ensure there are TSV files to test.
    """
    tsv_files = get_tsv_files()
    assert len(tsv_files) > 0, "No TSV files found in data directory"
