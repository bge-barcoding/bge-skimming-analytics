#!/usr/bin/env python3
"""
Unit tests for fix_process_id_column.py script.

This test verifies that the script correctly handles TSV files with process_id column.
"""

import csv
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from fix_process_id_column import analyze_file, fix_file


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_analyze_file_remove(temp_dir):
    """Test that files with matching process_id and group_id are identified for removal."""
    # Create a test file where process_id matches group_id
    test_file = temp_dir / "test_remove.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'process_id', 'group_id', 'error'])
        writer.writerow(['seq1', 'BGE001', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE002', 'BGE002', ''])
    
    action, message = analyze_file(test_file)
    assert action == 'remove'
    assert 'values match' in message.lower()


def test_analyze_file_rename(temp_dir):
    """Test that files with only process_id are identified for rename."""
    # Create a test file with only process_id
    test_file = temp_dir / "test_rename.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'process_id', 'error'])
        writer.writerow(['seq1', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE002', ''])
    
    action, message = analyze_file(test_file)
    assert action == 'rename'
    assert 'absent' in message.lower()


def test_analyze_file_conflict(temp_dir):
    """Test that files with mismatched process_id and group_id are flagged as conflict."""
    # Create a test file where values don't match
    test_file = temp_dir / "test_conflict.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'process_id', 'group_id', 'error'])
        writer.writerow(['seq1', 'BGE001', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE002', 'BGE999', ''])  # Mismatch
    
    action, message = analyze_file(test_file)
    assert action == 'conflict'
    assert "don't match" in message.lower()


def test_fix_file_remove(temp_dir):
    """Test that process_id column is correctly removed."""
    # Create a test file
    test_file = temp_dir / "test_remove.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'process_id', 'group_id', 'error'])
        writer.writerow(['seq1', 'BGE001', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE002', 'BGE002', ''])
    
    # Fix the file
    result = fix_file(test_file, 'remove', dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        rows = list(reader)
    
    assert 'process_id' not in headers
    assert 'group_id' in headers
    assert rows[0]['group_id'] == 'BGE001'
    assert rows[1]['group_id'] == 'BGE002'


def test_fix_file_rename(temp_dir):
    """Test that process_id column is correctly renamed to group_id."""
    # Create a test file
    test_file = temp_dir / "test_rename.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'process_id', 'error'])
        writer.writerow(['seq1', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE002', ''])
    
    # Fix the file
    result = fix_file(test_file, 'rename', dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        rows = list(reader)
    
    assert 'process_id' not in headers
    assert 'group_id' in headers
    assert rows[0]['group_id'] == 'BGE001'
    assert rows[1]['group_id'] == 'BGE002'


def test_fix_file_dry_run(temp_dir):
    """Test that dry_run mode doesn't modify files."""
    # Create a test file
    test_file = temp_dir / "test_dry_run.tsv"
    original_content = [
        ['sequence_id', 'process_id', 'error'],
        ['seq1', 'BGE001', '']
    ]
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(original_content)
    
    # Read original content
    with open(test_file, 'r') as f:
        original = f.read()
    
    # Fix in dry_run mode
    result = fix_file(test_file, 'rename', dry_run=True)
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
        writer.writerow(['sequence_id', 'process_id', 'group_id', 'error', 'species', 'stop_codons'])
        writer.writerow(['seq1', 'BGE001', 'BGE001', '', 'Homo sapiens', '0'])
        writer.writerow(['seq2', 'BGE002', 'BGE002', 'some error', 'Mus musculus', '2'])
    
    # Fix the file
    result = fix_file(test_file, 'remove', dry_run=False)
    assert result is True
    
    # Verify all data is preserved
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]['sequence_id'] == 'seq1'
    assert rows[0]['group_id'] == 'BGE001'
    assert rows[0]['error'] == ''
    assert rows[0]['species'] == 'Homo sapiens'
    assert rows[0]['stop_codons'] == '0'
    
    assert rows[1]['sequence_id'] == 'seq2'
    assert rows[1]['group_id'] == 'BGE002'
    assert rows[1]['error'] == 'some error'
    assert rows[1]['species'] == 'Mus musculus'
    assert rows[1]['stop_codons'] == '2'
