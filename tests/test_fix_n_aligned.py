#!/usr/bin/env python3
"""
Unit tests for fix_n_aligned_column.py script.

This test verifies that the script correctly handles TSV files with n_aligned column.
"""

import csv
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from fix_n_aligned_column import analyze_file, fix_file


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_analyze_file_rename(temp_dir):
    """Test that files with only n_aligned are identified for rename."""
    # Create a test file
    test_file = temp_dir / "test_rename.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'n_aligned', 'error'])
        writer.writerow(['seq1', '100', ''])
        writer.writerow(['seq2', '200', ''])
    
    action, message = analyze_file(test_file)
    
    assert action == 'rename'
    assert 'n_reads_aligned column absent' in message


def test_analyze_file_skip(temp_dir):
    """Test that files with n_reads_aligned are skipped."""
    # Create a test file
    test_file = temp_dir / "test_skip.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'n_reads_aligned', 'error'])
        writer.writerow(['seq1', '100', ''])
        writer.writerow(['seq2', '200', ''])
    
    action, message = analyze_file(test_file)
    
    assert action == 'skip'
    assert 'n_aligned column not found' in message


def test_analyze_file_both_columns(temp_dir):
    """Test that files with both n_aligned and n_reads_aligned are skipped."""
    # Create a test file
    test_file = temp_dir / "test_both.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'n_aligned', 'n_reads_aligned', 'error'])
        writer.writerow(['seq1', '100', '100', ''])
        writer.writerow(['seq2', '200', '200', ''])
    
    action, message = analyze_file(test_file)
    
    assert action == 'skip'
    assert 'n_reads_aligned already exists' in message


def test_fix_file_rename(temp_dir):
    """Test that n_aligned column is correctly renamed to n_reads_aligned."""
    # Create a test file
    test_file = temp_dir / "test_rename.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'n_aligned', 'error'])
        writer.writerow(['seq1', '100', ''])
        writer.writerow(['seq2', '200', ''])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        rows = list(reader)
    
    assert 'n_aligned' not in headers
    assert 'n_reads_aligned' in headers
    assert rows[0]['n_reads_aligned'] == '100'
    assert rows[1]['n_reads_aligned'] == '200'


def test_fix_file_dry_run(temp_dir):
    """Test that dry_run mode doesn't modify files."""
    # Create a test file
    test_file = temp_dir / "test_dry_run.tsv"
    original_content = [
        ['sequence_id', 'n_aligned', 'error'],
        ['seq1', '100', ''],
        ['seq2', '200', '']
    ]
    
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(original_content)
    
    # Run in dry run mode
    result = fix_file(test_file, dry_run=True)
    assert result is True
    
    # Verify the file hasn't changed
    with open(test_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        new_content = list(reader)
    
    assert new_content == original_content


def test_fix_file_preserves_data(temp_dir):
    """Test that fixing preserves all other data correctly."""
    # Create a test file with multiple columns
    test_file = temp_dir / "test_preserve.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'species', 'n_aligned', 'error', 'stop_codons'])
        writer.writerow(['seq1', 'Species A', '100', '', '0'])
        writer.writerow(['seq2', 'Species B', '200', 'some error', '1'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        rows = list(reader)
    
    # Check headers
    assert headers == ['sequence_id', 'species', 'n_reads_aligned', 'error', 'stop_codons']
    
    # Check first row
    assert rows[0]['sequence_id'] == 'seq1'
    assert rows[0]['species'] == 'Species A'
    assert rows[0]['n_reads_aligned'] == '100'
    assert rows[0]['error'] == ''
    assert rows[0]['stop_codons'] == '0'
    
    # Check second row
    assert rows[1]['sequence_id'] == 'seq2'
    assert rows[1]['species'] == 'Species B'
    assert rows[1]['n_reads_aligned'] == '200'
    assert rows[1]['error'] == 'some error'
    assert rows[1]['stop_codons'] == '1'
