#!/usr/bin/env python3
"""
Unit tests for fix_filename_column.py script.

This test verifies that the script correctly handles TSV files with Filename column.
"""

import csv
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from fix_filename_column import analyze_file, fix_file


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_analyze_file_remove(temp_dir):
    """Test that files matching Pattern 1 are identified for removal."""
    # Create a test file where Filename matches sequence_id (Pattern 1)
    test_file = temp_dir / "test_remove.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'Filename', 'error'])
        writer.writerow(['seq1_r_1_s_50', 'seq1_r_1_s_50', ''])
        writer.writerow(['seq2_r_1_s_100', 'seq2_r_1_s_100', ''])
    
    action, message = analyze_file(test_file)
    assert action == 'remove'
    assert 'pattern 1' in message.lower()


def test_analyze_file_remove_with_merge_suffix(temp_dir):
    """Test that files where sequence_id = Filename + '_merge' are identified for removal (Pattern 1)."""
    # Create a test file with the _merge pattern
    test_file = temp_dir / "test_remove_merge.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'Filename', 'error'])
        writer.writerow(['seq1_r_1_s_50', 'seq1_r_1_s_50', ''])
        writer.writerow(['seq2_r_1_s_100_merge', 'seq2_r_1_s_100', ''])  # Pattern 1: has _merge suffix
        writer.writerow(['seq3_r_1_s_50', 'seq3_r_1_s_50', ''])
    
    action, message = analyze_file(test_file)
    assert action == 'remove'
    assert 'pattern 1' in message.lower()


def test_analyze_file_keep_no_sequence_id(temp_dir):
    """Test that files without sequence_id are flagged to keep."""
    # Create a test file with only Filename
    test_file = temp_dir / "test_keep.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Filename', 'error'])
        writer.writerow(['seq1_r_1_s_50', ''])
        writer.writerow(['seq2_r_1_s_100', ''])
    
    action, message = analyze_file(test_file)
    assert action == 'keep'
    assert 'absent' in message.lower()


def test_analyze_file_keep_different_values(temp_dir):
    """Test that files not matching Pattern 1 are flagged to keep."""
    # Create a test file where values don't match Pattern 1 (e.g., Pattern 2 with trailing process ID)
    test_file = temp_dir / "test_keep_diff.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'Filename', 'error'])
        writer.writerow(['seq1_r_1_s_50', 'seq1_r_1_s_50_PROC123', ''])  # Filename has extra suffix
        writer.writerow(['seq2_r_1_s_100', 'seq2_r_1_s_100_PROC456', ''])  # Filename has extra suffix
    
    action, message = analyze_file(test_file)
    assert action == 'keep'
    assert 'pattern 1' in message.lower()


def test_fix_file_remove(temp_dir):
    """Test that Filename column is correctly removed."""
    # Create a test file
    test_file = temp_dir / "test_remove.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'Filename', 'error'])
        writer.writerow(['seq1_r_1_s_50', 'seq1_r_1_s_50', ''])
        writer.writerow(['seq2_r_1_s_100', 'seq2_r_1_s_100', ''])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        rows = list(reader)
    
    assert 'Filename' not in headers
    assert 'sequence_id' in headers
    assert rows[0]['sequence_id'] == 'seq1_r_1_s_50'
    assert rows[1]['sequence_id'] == 'seq2_r_1_s_100'


def test_fix_file_dry_run(temp_dir):
    """Test that dry_run mode doesn't modify files."""
    # Create a test file
    test_file = temp_dir / "test_dry_run.tsv"
    original_content = [
        ['sequence_id', 'Filename', 'error'],
        ['seq1', 'seq1', '']
    ]
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(original_content)
    
    # Read original content
    with open(test_file, 'r') as f:
        original = f.read()
    
    # Fix in dry_run mode
    result = fix_file(test_file, dry_run=True)
    assert result is True
    
    # Verify file is unchanged
    with open(test_file, 'r') as f:
        after = f.read()
    
    assert original == after


def test_fix_file_preserves_data(temp_dir):
    """Test that fixing preserves all other data correctly."""
    # Create a test file with multiple columns
    test_file = temp_dir / "test_preserve.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'Filename', 'error', 'species', 'stop_codons'])
        writer.writerow(['seq1_r_1_s_50', 'seq1_r_1_s_50', '', 'Homo sapiens', '0'])
        writer.writerow(['seq2_r_1_s_100', 'seq2_r_1_s_100', 'some error', 'Mus musculus', '2'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify all data is preserved
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]['sequence_id'] == 'seq1_r_1_s_50'
    assert rows[0]['error'] == ''
    assert rows[0]['species'] == 'Homo sapiens'
    assert rows[0]['stop_codons'] == '0'
    
    assert rows[1]['sequence_id'] == 'seq2_r_1_s_100'
    assert rows[1]['error'] == 'some error'
    assert rows[1]['species'] == 'Mus musculus'
    assert rows[1]['stop_codons'] == '2'


def test_fix_file_preserves_column_order(temp_dir):
    """Test that fixing preserves column order (except for removed Filename)."""
    # Create a test file with specific column order
    test_file = temp_dir / "test_order.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['ambig_basecount', 'Filename', 'error', 'sequence_id', 'species'])
        writer.writerow(['2', 'seq1', '', 'seq1', 'Species1'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify column order
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = list(reader.fieldnames)
    
    # Filename should be removed, but order of others preserved
    assert headers == ['ambig_basecount', 'error', 'sequence_id', 'species']
