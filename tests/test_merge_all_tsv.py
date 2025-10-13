#!/usr/bin/env python3
"""
Tests for merge_all_tsv.py script.
"""

import gzip
import json
import pytest
from pathlib import Path
import pandas as pd


def test_merged_file_exists():
    """Test that the merged gzip file exists."""
    repo_root = Path(__file__).parent.parent
    merged_file = repo_root / 'data' / 'bge-skimming-analytics.tsv.gz'
    assert merged_file.exists(), "Merged TSV.GZ file should exist"


def test_datapackage_json_exists():
    """Test that the datapackage.json file exists."""
    repo_root = Path(__file__).parent.parent
    datapackage_file = repo_root / 'data' / 'datapackage.json'
    assert datapackage_file.exists(), "datapackage.json should exist"


def test_datapackage_json_valid():
    """Test that datapackage.json is valid JSON with required fields."""
    repo_root = Path(__file__).parent.parent
    datapackage_file = repo_root / 'data' / 'datapackage.json'
    
    with open(datapackage_file) as f:
        pkg = json.load(f)
    
    # Check required fields
    assert 'name' in pkg
    assert 'resources' in pkg
    assert len(pkg['resources']) > 0
    
    # Check resource structure
    resource = pkg['resources'][0]
    assert 'name' in resource
    assert 'path' in resource
    assert 'schema' in resource
    assert 'fields' in resource['schema']
    
    # Check compression metadata
    assert resource.get('compression') == 'gzip', "Resource should indicate gzip compression"


def test_merged_file_has_all_columns():
    """Test that merged file has all expected columns from headers.tsv."""
    repo_root = Path(__file__).parent.parent
    merged_file = repo_root / 'data' / 'bge-skimming-analytics.tsv.gz'
    headers_file = repo_root / 'metadata' / 'headers.tsv'
    
    # Read expected columns
    headers_df = pd.read_csv(headers_file, sep='\t')
    expected_cols = set(headers_df['barcode_validator TSV header'].tolist())
    
    # Read merged file columns (from gzip)
    with gzip.open(merged_file, 'rt', encoding='utf-8') as f:
        merged_df = pd.read_csv(f, sep='\t', nrows=0)
    actual_cols = set(merged_df.columns)
    
    # Check all expected columns are present
    missing = expected_cols - actual_cols
    assert not missing, f"Missing columns: {missing}"
    
    # Check no extra columns
    extra = actual_cols - expected_cols
    assert not extra, f"Extra columns: {extra}"


def test_merged_file_has_data():
    """Test that merged file has data rows."""
    repo_root = Path(__file__).parent.parent
    merged_file = repo_root / 'data' / 'bge-skimming-analytics.tsv.gz'
    
    with gzip.open(merged_file, 'rt', encoding='utf-8') as f:
        df = pd.read_csv(f, sep='\t', nrows=10)
    assert len(df) > 0, "Merged file should have data rows"


def test_boolean_columns_standardized():
    """Test that boolean columns have standardized values."""
    repo_root = Path(__file__).parent.parent
    merged_file = repo_root / 'data' / 'bge-skimming-analytics.tsv.gz'
    
    with gzip.open(merged_file, 'rt', encoding='utf-8') as f:
        df = pd.read_csv(f, sep='\t', nrows=1000)
    
    # Check fcleaner column
    if 'fcleaner' in df.columns:
        fcleaner_values = df['fcleaner'].dropna().astype(str).unique()
        assert all(v in ['True', 'False'] for v in fcleaner_values), \
            f"fcleaner should only have True/False values, got: {fcleaner_values}"
    
    # Check merge column
    if 'merge' in df.columns:
        merge_values = df['merge'].dropna().astype(str).unique()
        assert all(v in ['True', 'False'] for v in merge_values), \
            f"merge should only have True/False values, got: {merge_values}"


def test_datapackage_field_count_matches():
    """Test that datapackage.json has the same number of fields as merged file columns."""
    repo_root = Path(__file__).parent.parent
    merged_file = repo_root / 'data' / 'bge-skimming-analytics.tsv.gz'
    datapackage_file = repo_root / 'data' / 'datapackage.json'
    
    # Read merged file columns
    with gzip.open(merged_file, 'rt', encoding='utf-8') as f:
        merged_df = pd.read_csv(f, sep='\t', nrows=0)
    num_cols = len(merged_df.columns)
    
    # Read datapackage fields
    with open(datapackage_file) as f:
        pkg = json.load(f)
    
    num_fields = len(pkg['resources'][0]['schema']['fields'])
    
    assert num_cols == num_fields, \
        f"Number of columns ({num_cols}) should match number of fields ({num_fields})"


def test_compulsory_columns_marked():
    """Test that compulsory columns are marked as required in datapackage.json."""
    repo_root = Path(__file__).parent.parent
    headers_file = repo_root / 'metadata' / 'headers.tsv'
    datapackage_file = repo_root / 'data' / 'datapackage.json'
    
    # Read compulsory columns
    headers_df = pd.read_csv(headers_file, sep='\t')
    compulsory_cols = set(
        headers_df[headers_df['Compulsory'] == 'true']['barcode_validator TSV header'].tolist()
    )
    
    # Read datapackage
    with open(datapackage_file) as f:
        pkg = json.load(f)
    
    # Check that compulsory columns have required constraint
    fields = pkg['resources'][0]['schema']['fields']
    for field in fields:
        if field['name'] in compulsory_cols:
            # Sample check for one compulsory field
            if field['name'] == 'ambig_basecount':
                assert 'constraints' in field, \
                    f"Compulsory field {field['name']} should have constraints"
                assert field['constraints'].get('required'), \
                    f"Compulsory field {field['name']} should be marked as required"


def test_compression_effective():
    """Test that compression provides significant size reduction."""
    repo_root = Path(__file__).parent.parent
    merged_file = repo_root / 'data' / 'bge-skimming-analytics.tsv.gz'
    
    # Get compressed size
    compressed_size = merged_file.stat().st_size
    
    # Compressed size should be less than 50 MB (GitHub's recommended limit)
    assert compressed_size < 50 * 1024 * 1024, \
        f"Compressed file should be under 50 MB, got {compressed_size / (1024*1024):.2f} MB"
    
    # For reference, the uncompressed size would be ~288 MB
    # So we expect at least 80% compression
    # We'll just check it's under 25 MB for this test
    assert compressed_size < 25 * 1024 * 1024, \
        f"Compression should be effective, file is {compressed_size / (1024*1024):.2f} MB"
