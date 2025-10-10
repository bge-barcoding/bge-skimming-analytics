"""
Tests for remove_negative_controls.py
"""

import csv
import tempfile
from pathlib import Path

import pytest

# Import functions from the script
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from remove_negative_controls import (
    find_tsv_files_with_negative_controls,
    analyze_file,
    clean_file
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_find_files_with_group_id_nc(temp_dir):
    """Test that files with group_id ending in -NC are detected."""
    # Create a test file with group_id ending in -NC
    test_file = temp_dir / "test_group_id_nc.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['seq1', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE001-NC', ''])
    
    files = find_tsv_files_with_negative_controls(temp_dir)
    assert len(files) == 1
    assert files[0] == test_file


def test_find_files_with_error_not_in_bold(temp_dir):
    """Test that files with '<something>-NC not in BOLD' error are detected."""
    # Create a test file with error message
    test_file = temp_dir / "test_error_nc.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['seq1', ''])
        writer.writerow(['seq2', 'BGE001-NC not in BOLD'])
    
    files = find_tsv_files_with_negative_controls(temp_dir)
    assert len(files) == 1
    assert files[0] == test_file


def test_find_files_no_negative_controls(temp_dir):
    """Test that files without negative controls are not detected."""
    # Create a test file without negative controls
    test_file = temp_dir / "test_no_nc.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['seq1', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE002', 'some other error'])
    
    files = find_tsv_files_with_negative_controls(temp_dir)
    assert len(files) == 0


def test_analyze_file_group_id_nc(temp_dir):
    """Test analyzing a file with group_id negative controls."""
    test_file = temp_dir / "test_analyze_group.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['seq1', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE001-NC', ''])
        writer.writerow(['seq3', 'BGE001-NC', ''])
        writer.writerow(['seq4', 'BGE002', ''])
    
    total_rows, nc_rows, message = analyze_file(test_file)
    assert total_rows == 4
    assert nc_rows == 2
    assert '2 negative control row(s)' in message


def test_analyze_file_error_not_in_bold(temp_dir):
    """Test analyzing a file with error message negative controls."""
    test_file = temp_dir / "test_analyze_error.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['seq1', ''])
        writer.writerow(['seq2', 'BGE001-NC not in BOLD'])
        writer.writerow(['seq3', 'some other error'])
    
    total_rows, nc_rows, message = analyze_file(test_file)
    assert total_rows == 3
    assert nc_rows == 1
    assert '1 negative control row(s)' in message


def test_clean_file_group_id_nc(temp_dir):
    """Test cleaning a file with group_id negative controls."""
    test_file = temp_dir / "test_clean_group.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['seq1', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE001-NC', 'some error'])
        writer.writerow(['seq3', 'BGE002', ''])
    
    # Clean the file
    result = clean_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]['sequence_id'] == 'seq1'
    assert rows[0]['group_id'] == 'BGE001'
    assert rows[1]['sequence_id'] == 'seq3'
    assert rows[1]['group_id'] == 'BGE002'


def test_clean_file_error_not_in_bold(temp_dir):
    """Test cleaning a file with error message negative controls."""
    test_file = temp_dir / "test_clean_error.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['seq1', ''])
        writer.writerow(['seq2', 'BGE001-NC not in BOLD'])
        writer.writerow(['seq3', 'some other error'])
    
    # Clean the file
    result = clean_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]['sequence_id'] == 'seq1'
    assert rows[0]['error'] == ''
    assert rows[1]['sequence_id'] == 'seq3'
    assert rows[1]['error'] == 'some other error'


def test_clean_file_both_types(temp_dir):
    """Test cleaning a file with both types of negative controls."""
    test_file = temp_dir / "test_clean_both.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['seq1', 'BGE001', ''])
        writer.writerow(['seq2', 'BGE001-NC', 'Could not find nodes for ID BGE001-NC'])
        writer.writerow(['seq3', 'BGE002', 'BGE002-NC not in BOLD'])
        writer.writerow(['seq4', 'BGE003', ''])
    
    # Clean the file
    result = clean_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]['sequence_id'] == 'seq1'
    assert rows[1]['sequence_id'] == 'seq4'


def test_clean_file_dry_run(temp_dir):
    """Test that dry_run mode doesn't modify files."""
    test_file = temp_dir / "test_dry_run.tsv"
    original_content = [
        ['sequence_id', 'group_id', 'error'],
        ['seq1', 'BGE001', ''],
        ['seq2', 'BGE001-NC', '']
    ]
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(original_content)
    
    # Read original content
    with open(test_file, 'r') as f:
        original = f.read()
    
    # Clean in dry_run mode
    result = clean_file(test_file, dry_run=True)
    assert result is True
    
    # Verify file is unchanged
    with open(test_file, 'r') as f:
        after = f.read()
    
    assert original == after


def test_clean_file_preserves_other_data(temp_dir):
    """Test that cleaning preserves all other data correctly."""
    test_file = temp_dir / "test_preserve.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error', 'species', 'stop_codons'])
        writer.writerow(['seq1', 'BGE001', '', 'Homo sapiens', '0'])
        writer.writerow(['seq2', 'BGE001-NC', 'some error', 'Unknown', '0'])
        writer.writerow(['seq3', 'BGE002', 'some error', 'Mus musculus', '2'])
    
    # Clean the file
    result = clean_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]['sequence_id'] == 'seq1'
    assert rows[0]['group_id'] == 'BGE001'
    assert rows[0]['error'] == ''
    assert rows[0]['species'] == 'Homo sapiens'
    assert rows[0]['stop_codons'] == '0'
    
    assert rows[1]['sequence_id'] == 'seq3'
    assert rows[1]['group_id'] == 'BGE002'
    assert rows[1]['error'] == 'some error'
    assert rows[1]['species'] == 'Mus musculus'
    assert rows[1]['stop_codons'] == '2'
