#!/usr/bin/env python3
"""
Unit tests for assess_collection_dates.py script.

This test verifies that the script correctly identifies implausible collection dates.
"""

import csv
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from assess_collection_dates import (
    parse_collection_date,
    assess_collection_dates,
    write_report
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_parse_collection_date_valid():
    """Test parsing valid collection dates."""
    assert parse_collection_date("23-Aug-1983") == 1983
    assert parse_collection_date("01-Jan-2020") == 2020
    assert parse_collection_date("15-Feb-0198") == 198
    assert parse_collection_date("30-Jun-1817") == 1817


def test_parse_collection_date_empty():
    """Test parsing empty or None dates."""
    assert parse_collection_date("") is None
    assert parse_collection_date("   ") is None
    assert parse_collection_date(None) is None


def test_parse_collection_date_invalid():
    """Test parsing invalid date formats."""
    assert parse_collection_date("invalid") is None
    # Note: "123" would parse to year 123, which would be caught as implausible later


def test_assess_collection_dates_no_issues(temp_dir):
    """Test that valid dates are not flagged."""
    # Create a test file with valid dates
    test_file = temp_dir / "collection_data.tsv"
    with open(test_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Sample ID', 'Collection Date', 'Country/Ocean'])
        writer.writerow(['SAMPLE001', '23-Aug-1983', 'Netherlands'])
        writer.writerow(['SAMPLE002', '15-Jun-2020', 'France'])
        writer.writerow(['SAMPLE003', '01-Jan-2000', 'Germany'])
    
    results = assess_collection_dates(test_file, 1825, 2025)
    
    assert len(results) == 0


def test_assess_collection_dates_too_old(temp_dir):
    """Test that dates before min_year are flagged."""
    # Create a test file with old dates
    test_file = temp_dir / "collection_data.tsv"
    with open(test_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Sample ID', 'Collection Date', 'Country/Ocean'])
        writer.writerow(['SAMPLE001', '15-Feb-0198', 'Italy'])
        writer.writerow(['SAMPLE002', '30-Jun-1817', 'Austria'])
        writer.writerow(['SAMPLE003', '01-Jul-1824', 'Spain'])
    
    results = assess_collection_dates(test_file, 1825, 2025)
    
    assert len(results) == 3
    
    # Check that all are flagged as too old
    for _, _, year, reason in results:
        assert "too old" in reason
        assert year < 1825


def test_assess_collection_dates_future(temp_dir):
    """Test that dates after max_year are flagged."""
    # Create a test file with future dates
    test_file = temp_dir / "collection_data.tsv"
    with open(test_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Sample ID', 'Collection Date', 'Country/Ocean'])
        writer.writerow(['SAMPLE001', '20-Jun-2029', 'Greece'])
        writer.writerow(['SAMPLE002', '21-May-2026', 'Bulgaria'])
    
    results = assess_collection_dates(test_file, 1825, 2025)
    
    assert len(results) == 2
    
    # Check that all are flagged as future
    for _, _, year, reason in results:
        assert "future" in reason
        assert year > 2025


def test_assess_collection_dates_mixed(temp_dir):
    """Test file with mix of valid and invalid dates."""
    # Create a test file with mixed dates
    test_file = temp_dir / "collection_data.tsv"
    with open(test_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Sample ID', 'Collection Date', 'Country/Ocean'])
        writer.writerow(['SAMPLE001', '23-Aug-1983', 'Netherlands'])  # Valid
        writer.writerow(['SAMPLE002', '15-Feb-0198', 'Italy'])  # Too old
        writer.writerow(['SAMPLE003', '15-Jun-2020', 'France'])  # Valid
        writer.writerow(['SAMPLE004', '20-Jun-2029', 'Greece'])  # Future
        writer.writerow(['SAMPLE005', '', 'Germany'])  # Empty date
    
    results = assess_collection_dates(test_file, 1825, 2025)
    
    assert len(results) == 2
    
    # Check that we got one too old and one future
    sample_ids = [sample_id for sample_id, _, _, _ in results]
    assert 'SAMPLE002' in sample_ids
    assert 'SAMPLE004' in sample_ids


def test_assess_collection_dates_empty_file(temp_dir):
    """Test with file containing only headers."""
    test_file = temp_dir / "collection_data.tsv"
    with open(test_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Sample ID', 'Collection Date', 'Country/Ocean'])
    
    results = assess_collection_dates(test_file, 1825, 2025)
    
    assert len(results) == 0


def test_write_report_to_file(temp_dir):
    """Test writing report to a file."""
    output_file = temp_dir / "report.txt"
    
    implausible_dates = [
        ('SAMPLE001', '15-Feb-0198', 198, 'too old (before 1825)'),
        ('SAMPLE002', '20-Jun-2029', 2029, 'in the future (after 2025)')
    ]
    
    write_report(implausible_dates, output_file, 1825, 2025)
    
    assert output_file.exists()
    
    content = output_file.read_text()
    assert "BOLD Collection Date Assessment Report" in content
    assert "Total implausible dates found: 2" in content
    assert "SAMPLE001" in content
    assert "SAMPLE002" in content
    assert "198" in content
    assert "2029" in content


def test_write_report_no_issues(temp_dir):
    """Test writing report when no issues found."""
    output_file = temp_dir / "report.txt"
    
    write_report([], output_file, 1825, 2025)
    
    assert output_file.exists()
    
    content = output_file.read_text()
    assert "No implausible dates found" in content
    assert "Total implausible dates found: 0" in content
