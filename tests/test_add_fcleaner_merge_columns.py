#!/usr/bin/env python3
"""
Unit tests for the add_fcleaner_merge_columns script.
"""

import csv
import pytest
from pathlib import Path

from scripts.add_fcleaner_merge_columns import (
    check_suffixes,
    find_tsv_files,
    add_columns_to_file
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path


def test_check_suffixes_no_suffix():
    """Test checking suffixes when neither fcleaner nor merge are present."""
    seq_id = "UNIFI571-24_r_1_s_50"
    has_fcleaner, has_merge = check_suffixes(seq_id)
    assert has_fcleaner is False
    assert has_merge is False


def test_check_suffixes_merge_only():
    """Test checking suffixes when only merge is present."""
    seq_id = "MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge"
    has_fcleaner, has_merge = check_suffixes(seq_id)
    assert has_fcleaner is False
    assert has_merge is True


def test_check_suffixes_fcleaner_only():
    """Test checking suffixes when only fcleaner is present."""
    seq_id = "BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner"
    has_fcleaner, has_merge = check_suffixes(seq_id)
    assert has_fcleaner is True
    assert has_merge is False


def test_check_suffixes_both():
    """Test checking suffixes when both fcleaner and merge are present."""
    seq_id = "BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge"
    has_fcleaner, has_merge = check_suffixes(seq_id)
    assert has_fcleaner is True
    assert has_merge is True


def test_find_tsv_files(temp_dir):
    """Test finding TSV files in a directory."""
    # Create some test files
    (temp_dir / "file1.tsv").touch()
    (temp_dir / "file2.tsv").touch()
    (temp_dir / "file3.txt").touch()
    
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "file4.tsv").touch()
    
    tsv_files = find_tsv_files(temp_dir)
    assert len(tsv_files) == 3
    assert all(f.suffix == '.tsv' for f in tsv_files)


def test_add_columns_to_file_no_suffix(temp_dir):
    """Test adding columns to a file with no suffixes."""
    test_file = temp_dir / "test_no_suffix.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'UNIFI571-24', 'None'])
        writer.writerow(['UNIFI571-24_r_1_s_100', 'UNIFI571-24', 'None'])
    
    result = add_columns_to_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert 'fcleaner' in rows[0]
    assert 'merge' in rows[0]
    assert rows[0]['fcleaner'] == 'False'
    assert rows[0]['merge'] == 'False'
    assert rows[1]['fcleaner'] == 'False'
    assert rows[1]['merge'] == 'False'


def test_add_columns_to_file_with_merge(temp_dir):
    """Test adding columns to a file with merge suffix."""
    test_file = temp_dir / "test_with_merge.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge', 'MUSBA3189-25', 'None'])
    
    result = add_columns_to_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert rows[0]['fcleaner'] == 'False'
    assert rows[0]['merge'] == 'True'


def test_add_columns_to_file_with_fcleaner(temp_dir):
    """Test adding columns to a file with fcleaner suffix."""
    test_file = temp_dir / "test_with_fcleaner.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner', 'BSCRO1521-25', 'None'])
    
    result = add_columns_to_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert rows[0]['fcleaner'] == 'True'
    assert rows[0]['merge'] == 'False'


def test_add_columns_to_file_with_both(temp_dir):
    """Test adding columns to a file with both suffixes."""
    test_file = temp_dir / "test_with_both.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge', 'BSCRO1521-25', 'None'])
    
    result = add_columns_to_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert rows[0]['fcleaner'] == 'True'
    assert rows[0]['merge'] == 'True'


def test_add_columns_to_file_mixed_rows(temp_dir):
    """Test adding columns to a file with mixed suffix patterns."""
    test_file = temp_dir / "test_mixed.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'UNIFI571-24', 'None'])
        writer.writerow(['MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge', 'MUSBA3189-25', 'None'])
        writer.writerow(['BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner', 'BSCRO1521-25', 'None'])
        writer.writerow(['BSCRO1521-25_r_1.5_s_50_BSCRO1521-25_fcleaner_merge', 'BSCRO1521-25', 'None'])
    
    result = add_columns_to_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert rows[0]['fcleaner'] == 'False' and rows[0]['merge'] == 'False'
    assert rows[1]['fcleaner'] == 'False' and rows[1]['merge'] == 'True'
    assert rows[2]['fcleaner'] == 'True' and rows[2]['merge'] == 'False'
    assert rows[3]['fcleaner'] == 'True' and rows[3]['merge'] == 'True'


def test_add_columns_to_file_already_has_columns(temp_dir):
    """Test adding columns to a file that already has them (should skip)."""
    test_file = temp_dir / "test_already_has.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'fcleaner', 'merge'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'False', 'False'])
    
    result = add_columns_to_file(test_file, dry_run=False)
    assert result is True
    
    # Verify file wasn't changed
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert len(rows) == 1
    assert rows[0]['fcleaner'] == 'False'
    assert rows[0]['merge'] == 'False'


def test_add_columns_to_file_no_sequence_id(temp_dir):
    """Test adding columns to a file without sequence_id column (should skip)."""
    test_file = temp_dir / "test_no_seq_id.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['group_id', 'error'])
        writer.writerow(['UNIFI571-24', 'None'])
    
    result = add_columns_to_file(test_file, dry_run=False)
    assert result is True  # Should succeed but not modify
    
    # Verify no columns were added
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
    
    assert 'fcleaner' not in headers
    assert 'merge' not in headers


def test_add_columns_to_file_dry_run(temp_dir):
    """Test dry run mode doesn't modify the file."""
    test_file = temp_dir / "test_dry_run.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'UNIFI571-24'])
    
    result = add_columns_to_file(test_file, dry_run=True)
    assert result is True
    
    # Verify file wasn't modified
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
    
    assert 'fcleaner' not in headers
    assert 'merge' not in headers


def test_add_columns_preserves_other_data(temp_dir):
    """Test that adding columns preserves all other data in the file."""
    test_file = temp_dir / "test_preserve.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'r', 's', 'error', 'identification'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'UNIFI571-24', '1', '50', 'None', 'Test1'])
        writer.writerow(['MUSBA3189-25_r_1_s_100_MUSBA3189-25_merge', 'MUSBA3189-25', '1', '100', 'None', 'Test2'])
    
    result = add_columns_to_file(test_file, dry_run=False)
    assert result is True
    
    # Verify all data is preserved
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    assert rows[0]['sequence_id'] == 'UNIFI571-24_r_1_s_50'
    assert rows[0]['group_id'] == 'UNIFI571-24'
    assert rows[0]['r'] == '1'
    assert rows[0]['s'] == '50'
    assert rows[0]['error'] == 'None'
    assert rows[0]['identification'] == 'Test1'
    assert rows[0]['fcleaner'] == 'False'
    assert rows[0]['merge'] == 'False'
    
    assert rows[1]['sequence_id'] == 'MUSBA3189-25_r_1_s_100_MUSBA3189-25_merge'
    assert rows[1]['fcleaner'] == 'False'
    assert rows[1]['merge'] == 'True'
