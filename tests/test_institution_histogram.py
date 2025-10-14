#!/usr/bin/env python3
"""
Unit test for institution histogram visualization.

This test verifies that the institution distribution histogram
includes both registered specimens and valid output counts.
"""

import re
from pathlib import Path
import pytest


def test_institution_histogram_shows_both_metrics():
    """Test that the institution histogram shows both registered and valid specimens."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "bold_metadata_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the institution-distribution section
    assert 'institution-distribution' in content, "Could not find institution-distribution section"
    
    # Extract the section between this chunk and the next
    start_idx = content.find('```{r institution-distribution')
    assert start_idx > 0, "Could not find institution-distribution code chunk"
    
    end_idx = content.find('```', start_idx + 3)
    institution_code = content[start_idx:end_idx]
    
    # Check that it calculates both registered and valid counts
    assert 'Registered' in institution_code, "Histogram must calculate Registered count"
    assert 'Valid' in institution_code, "Histogram must calculate Valid count"
    assert 'validation_success' in institution_code, "Histogram must use validation_success"
    
    # Check for grouped/dodged bar chart
    assert 'position = "dodge"' in institution_code or 'position="dodge"' in institution_code, \
        "Histogram must use dodged bars (position='dodge')"
    
    # Check that it uses pivot_longer for reshaping
    assert 'pivot_longer' in institution_code, "Histogram must use pivot_longer to reshape data"
    
    # Check for proper ordering by registered count
    assert 'arrange(desc(Registered))' in institution_code, \
        "Histogram must sort institutions by Registered count (descending)"
    
    # Check for fill aesthetic (different colors for registered vs valid)
    assert 'fill = Type' in institution_code or 'fill=Type' in institution_code, \
        "Histogram must use fill aesthetic for Type"
    
    # Check for scale_fill_manual (custom colors)
    assert 'scale_fill_manual' in institution_code, \
        "Histogram must use scale_fill_manual for custom colors"
    
    # Check for legend
    assert 'legend' in institution_code.lower(), "Histogram must have legend configuration"


def test_institution_histogram_has_descriptive_labels():
    """Test that the histogram has descriptive labels."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "bold_metadata_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the institution-distribution section
    assert 'institution-distribution' in content, "Could not find institution-distribution section"
    
    # Extract the section between this chunk and the next
    start_idx = content.find('```{r institution-distribution')
    assert start_idx > 0, "Could not find institution-distribution code chunk"
    
    end_idx = content.find('```', start_idx + 3)
    institution_code = content[start_idx:end_idx]
    
    # Check for descriptive labels
    assert 'Registered Specimens' in institution_code or 'registered' in institution_code.lower(), \
        "Histogram must have label for registered specimens"
    assert 'Valid Output' in institution_code or 'valid' in institution_code.lower(), \
        "Histogram must have label for valid output"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
