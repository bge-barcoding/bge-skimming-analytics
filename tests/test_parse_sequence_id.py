#!/usr/bin/env python3
"""
Unit tests for the parse_sequence_id_columns script.
"""

import csv
import pytest
from pathlib import Path

from scripts.parse_sequence_id_columns import (
    parse_sequence_id,
    find_tsv_files_to_fix,
    analyze_file,
    fix_file
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path


def test_parse_sequence_id_valid():
    """Test parsing a valid sequence_id."""
    seq_id = "UNIFI571-24_r_1_s_50"
    result = parse_sequence_id(seq_id)
    assert result is not None
    group_id, r, s = result
    assert group_id == "UNIFI571-24"
    assert r == "1"
    assert s == "50"


def test_parse_sequence_id_valid_with_float():
    """Test parsing a sequence_id with float r value."""
    seq_id = "BBIOP1901-24_r_1.5_s_100"
    result = parse_sequence_id(seq_id)
    assert result is not None
    group_id, r, s = result
    assert group_id == "BBIOP1901-24"
    assert r == "1.5"
    assert s == "100"


def test_parse_sequence_id_valid_complex_process_id():
    """Test parsing with a more complex process ID."""
    seq_id = "MUSBA3474-25_r_1.3_s_75"
    result = parse_sequence_id(seq_id)
    assert result is not None
    group_id, r, s = result
    assert group_id == "MUSBA3474-25"
    assert r == "1.3"
    assert s == "75"


def test_parse_sequence_id_invalid_no_pattern():
    """Test parsing an invalid sequence_id without pattern."""
    seq_id = "INVALID_ID"
    result = parse_sequence_id(seq_id)
    assert result is None


def test_parse_sequence_id_invalid_missing_r():
    """Test parsing sequence_id missing r value."""
    seq_id = "UNIFI571-24_s_50"
    result = parse_sequence_id(seq_id)
    assert result is None


def test_parse_sequence_id_invalid_missing_s():
    """Test parsing sequence_id missing s value."""
    seq_id = "UNIFI571-24_r_1"
    result = parse_sequence_id(seq_id)
    assert result is None


def test_find_tsv_files_to_fix(temp_dir):
    """Test finding TSV files that need fixing."""
    # Create a file that needs fixing (missing all three columns)
    test_file1 = temp_dir / "needs_fixing.tsv"
    with open(test_file1, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error', 'identification'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'None', 'Test'])
    
    # Create a file that needs fixing (has group_id but missing r and s)
    test_file2 = temp_dir / "has_group_id.tsv"
    with open(test_file2, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'UNIFI571-24', 'None'])
    
    # Create a file that doesn't need fixing (has r and s)
    test_file3 = temp_dir / "has_r_s.tsv"
    with open(test_file3, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'r', 's', 'error'])
        writer.writerow(['UNIFI571-24_r_1_s_50', '1', '50', 'None'])
    
    # Create a file without the pattern
    test_file4 = temp_dir / "no_pattern.tsv"
    with open(test_file4, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['INVALID_ID', 'None'])
    
    files = find_tsv_files_to_fix(temp_dir)
    assert len(files) == 2
    assert test_file1 in files
    assert test_file2 in files


def test_analyze_file_all_parseable(temp_dir):
    """Test analyzing a file where all rows are parseable."""
    test_file = temp_dir / "all_parseable.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'None'])
        writer.writerow(['BBIOP1901-24_r_1.5_s_100', 'None'])
    
    status, message, count = analyze_file(test_file)
    assert status == 'fix'
    assert count == 2
    assert 'All 2 rows can be parsed' in message


def test_analyze_file_partial(temp_dir):
    """Test analyzing a file with some unparseable rows."""
    test_file = temp_dir / "partial.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'None'])
        writer.writerow(['INVALID_ID', 'None'])
    
    status, message, count = analyze_file(test_file)
    assert status == 'partial'
    assert count == 1
    assert '1/2 rows parseable' in message


def test_analyze_file_no_parseable(temp_dir):
    """Test analyzing a file with no parseable rows."""
    test_file = temp_dir / "no_parseable.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['INVALID_ID1', 'None'])
        writer.writerow(['INVALID_ID2', 'None'])
    
    status, message, count = analyze_file(test_file)
    assert status == 'error'
    assert count == 0
    assert 'No rows can be parsed' in message


def test_fix_file(temp_dir):
    """Test fixing a TSV file by adding r, s, and group_id columns."""
    test_file = temp_dir / "test_fix.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error', 'identification'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'None', 'Test1'])
        writer.writerow(['BBIOP1901-24_r_1.5_s_100', 'None', 'Test2'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        rows = list(reader)
    
    # Check headers
    assert 'group_id' in headers
    assert 'r' in headers
    assert 's' in headers
    assert headers.index('group_id') > headers.index('sequence_id')
    assert headers.index('r') > headers.index('sequence_id')
    assert headers.index('s') > headers.index('sequence_id')
    
    # Check row 1
    assert rows[0]['sequence_id'] == 'UNIFI571-24_r_1_s_50'
    assert rows[0]['group_id'] == 'UNIFI571-24'
    assert rows[0]['r'] == '1'
    assert rows[0]['s'] == '50'
    assert rows[0]['identification'] == 'Test1'
    
    # Check row 2
    assert rows[1]['sequence_id'] == 'BBIOP1901-24_r_1.5_s_100'
    assert rows[1]['group_id'] == 'BBIOP1901-24'
    assert rows[1]['r'] == '1.5'
    assert rows[1]['s'] == '100'
    assert rows[1]['identification'] == 'Test2'


def test_fix_file_dry_run(temp_dir):
    """Test that dry_run mode doesn't modify files."""
    test_file = temp_dir / "test_dry_run.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'None'])
    
    # Read original content
    with open(test_file, 'r') as f:
        original_content = f.read()
    
    # Fix in dry-run mode
    result = fix_file(test_file, dry_run=True)
    assert result is True
    
    # Verify file wasn't changed
    with open(test_file, 'r') as f:
        new_content = f.read()
    
    assert original_content == new_content


def test_fix_file_preserves_other_data(temp_dir):
    """Test that fixing preserves all other data correctly."""
    test_file = temp_dir / "test_preserve.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['ambig_basecount', 'sequence_id', 'error', 'species'])
        writer.writerow(['2', 'UNIFI571-24_r_1_s_50', 'None', 'Test species'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    # Check that original data is preserved
    assert rows[0]['ambig_basecount'] == '2'
    assert rows[0]['sequence_id'] == 'UNIFI571-24_r_1_s_50'
    assert rows[0]['error'] == 'None'
    assert rows[0]['species'] == 'Test species'
    
    # Check that new columns were added
    assert rows[0]['group_id'] == 'UNIFI571-24'
    assert rows[0]['r'] == '1'
    assert rows[0]['s'] == '50'


def test_fix_file_handles_unparseable_rows(temp_dir):
    """Test that fixing handles unparseable rows gracefully."""
    test_file = temp_dir / "test_unparseable.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'error'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'None'])
        writer.writerow(['INVALID_ID', 'None'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    # First row should be parsed correctly
    assert rows[0]['group_id'] == 'UNIFI571-24'
    assert rows[0]['r'] == '1'
    assert rows[0]['s'] == '50'
    
    # Second row should have empty values
    assert rows[1]['group_id'] == ''
    assert rows[1]['r'] == ''
    assert rows[1]['s'] == ''


def test_parse_sequence_id_with_underscore_in_process_id():
    """Test parsing sequence_id with underscore in the process ID part."""
    # This might happen if process IDs have underscores
    seq_id = "BGE_TEST001-24_r_1.5_s_50"
    result = parse_sequence_id(seq_id)
    assert result is not None
    group_id, r, s = result
    assert group_id == "BGE_TEST001-24"
    assert r == "1.5"
    assert s == "50"


def test_parse_sequence_id_with_repeated_process_id():
    """Test parsing sequence_id with repeated process ID (no suffix)."""
    seq_id = "MUSBA3189-25_r_1_s_50_MUSBA3189-25"
    result = parse_sequence_id(seq_id)
    assert result is not None
    group_id, r, s = result
    assert group_id == "MUSBA3189-25"
    assert r == "1"
    assert s == "50"


def test_parse_sequence_id_with_merge_suffix():
    """Test parsing sequence_id with _merge suffix."""
    seq_id = "MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge"
    result = parse_sequence_id(seq_id)
    assert result is not None
    group_id, r, s = result
    assert group_id == "MUSBA3189-25"
    assert r == "1"
    assert s == "50"


def test_parse_sequence_id_with_fcleaner_suffix():
    """Test parsing sequence_id with _fcleaner suffix."""
    seq_id = "BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner"
    result = parse_sequence_id(seq_id)
    assert result is not None
    group_id, r, s = result
    assert group_id == "BSCRO1521-25"
    assert r == "1.3"
    assert s == "100"


def test_parse_sequence_id_with_fcleaner_merge_suffix():
    """Test parsing sequence_id with _fcleaner_merge suffix."""
    seq_id = "BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge"
    result = parse_sequence_id(seq_id)
    assert result is not None
    group_id, r, s = result
    assert group_id == "BSCRO1521-25"
    assert r == "1.3"
    assert s == "100"


def test_parse_sequence_id_with_merge_only_no_repeated_id():
    """Test parsing sequence_id with _merge but no repeated process ID."""
    # Edge case: _merge directly after _s_<int>
    # The regex allows this pattern even though it may not appear in actual data
    seq_id = "MUSBA3189-25_r_1_s_50_merge"
    result = parse_sequence_id(seq_id)
    # This SHOULD match - the repeated process_id is optional
    assert result is not None
    group_id, r, s = result
    assert group_id == "MUSBA3189-25"
    assert r == "1"
    assert s == "50"


def test_parse_sequence_id_with_fcleaner_only_no_repeated_id():
    """Test parsing sequence_id with _fcleaner but no repeated process ID."""
    # Edge case: _fcleaner directly after _s_<int>
    # The regex allows this pattern even though it may not appear in actual data
    seq_id = "BSCRO1521-25_r_1.3_s_100_fcleaner"
    result = parse_sequence_id(seq_id)
    # This SHOULD match - the repeated process_id is optional
    assert result is not None
    group_id, r, s = result
    assert group_id == "BSCRO1521-25"
    assert r == "1.3"
    assert s == "100"


def test_fix_file_with_existing_group_id(temp_dir):
    """Test fixing a TSV file that has group_id but missing r and s columns."""
    test_file = temp_dir / "test_with_group_id.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error', 'identification'])
        writer.writerow(['UNIFI571-24_r_1_s_50', 'UNIFI571-24', 'None', 'Test1'])
        writer.writerow(['BBIOP1901-24_r_1.5_s_100', 'BBIOP1901-24', 'None', 'Test2'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        rows = list(reader)
    
    # Check headers - group_id should still be there, r and s should be added
    assert 'group_id' in headers
    assert 'r' in headers
    assert 's' in headers
    # group_id should be before r and s in the header order
    assert headers.index('group_id') < headers.index('r')
    assert headers.index('r') < headers.index('s')
    
    # Check row 1
    assert rows[0]['sequence_id'] == 'UNIFI571-24_r_1_s_50'
    assert rows[0]['group_id'] == 'UNIFI571-24'
    assert rows[0]['r'] == '1'
    assert rows[0]['s'] == '50'
    assert rows[0]['identification'] == 'Test1'
    
    # Check row 2
    assert rows[1]['sequence_id'] == 'BBIOP1901-24_r_1.5_s_100'
    assert rows[1]['group_id'] == 'BBIOP1901-24'
    assert rows[1]['r'] == '1.5'
    assert rows[1]['s'] == '100'
    assert rows[1]['identification'] == 'Test2'


def test_fix_file_with_merge_suffix(temp_dir):
    """Test fixing a TSV file with sequence_id containing _merge suffix."""
    test_file = temp_dir / "test_with_merge.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge', 'MUSBA3189-25', 'None'])
        writer.writerow(['MUSBA3189-25_r_1.3_s_100_MUSBA3189-25_merge', 'MUSBA3189-25', 'None'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    # Check row 1
    assert rows[0]['sequence_id'] == 'MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge'
    assert rows[0]['group_id'] == 'MUSBA3189-25'
    assert rows[0]['r'] == '1'
    assert rows[0]['s'] == '50'
    
    # Check row 2
    assert rows[1]['sequence_id'] == 'MUSBA3189-25_r_1.3_s_100_MUSBA3189-25_merge'
    assert rows[1]['group_id'] == 'MUSBA3189-25'
    assert rows[1]['r'] == '1.3'
    assert rows[1]['s'] == '100'


def test_fix_file_with_fcleaner_merge_suffix(temp_dir):
    """Test fixing a TSV file with sequence_id containing _fcleaner_merge suffix."""
    test_file = temp_dir / "test_with_fcleaner_merge.tsv"
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['sequence_id', 'group_id', 'error'])
        writer.writerow(['BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge', 'BSCRO1521-25', 'None'])
        writer.writerow(['BSCRO1521-25_r_1.5_s_50_BSCRO1521-25_fcleaner', 'BSCRO1521-25', 'None'])
    
    # Fix the file
    result = fix_file(test_file, dry_run=False)
    assert result is True
    
    # Verify the result
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    # Check row 1
    assert rows[0]['sequence_id'] == 'BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge'
    assert rows[0]['group_id'] == 'BSCRO1521-25'
    assert rows[0]['r'] == '1.3'
    assert rows[0]['s'] == '100'
    
    # Check row 2
    assert rows[1]['sequence_id'] == 'BSCRO1521-25_r_1.5_s_50_BSCRO1521-25_fcleaner'
    assert rows[1]['group_id'] == 'BSCRO1521-25'
    assert rows[1]['r'] == '1.5'
    assert rows[1]['s'] == '50'
