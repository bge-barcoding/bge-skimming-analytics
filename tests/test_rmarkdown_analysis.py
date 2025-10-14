#!/usr/bin/env python3
"""
Unit tests for RMarkdown analysis files.

This test verifies that RMarkdown files exist and have valid structure.
"""

import re
from pathlib import Path
import pytest


def test_bold_metadata_analysis_rmd_exists():
    """Test that the BOLD metadata analysis RMarkdown file exists."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "bold_metadata_analysis.Rmd"
    assert rmd_file.exists(), f"RMarkdown file not found: {rmd_file}"


def test_bold_metadata_analysis_has_yaml_header():
    """Test that the RMarkdown file has a valid YAML header."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "bold_metadata_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for YAML header (starts with --- and ends with ---)
    assert content.startswith('---'), "RMarkdown file must start with YAML header (---)"
    
    # Find the end of YAML header
    yaml_end = content.find('---', 3)
    assert yaml_end > 0, "YAML header must end with ---"
    
    yaml_header = content[3:yaml_end]
    
    # Check for required YAML fields
    assert 'title:' in yaml_header, "YAML header must include title"
    assert 'output:' in yaml_header, "YAML header must include output"


def test_bold_metadata_analysis_references_correct_files():
    """Test that the RMarkdown file references the correct data files."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "bold_metadata_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for references to required data files
    required_files = [
        '../data/bge-skimming-analytics.tsv.gz',
        '../metadata/bold/lab.tsv',
        '../metadata/bold/collection_data.tsv',
        '../metadata/bold/voucher.tsv',
        '../metadata/bold/taxonomy.tsv'
    ]
    
    for file_path in required_files:
        assert file_path in content, f"RMarkdown must reference {file_path}"


def test_bold_metadata_analysis_has_join_operations():
    """Test that the RMarkdown file includes join operations."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "bold_metadata_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for join operations
    assert 'left_join' in content, "RMarkdown must include left_join operations"
    
    # Check for join with group_id and Process ID
    assert 'group_id' in content, "RMarkdown must reference group_id column"
    assert 'Process ID' in content, "RMarkdown must reference Process ID column"
    assert 'Sample ID' in content, "RMarkdown must reference Sample ID column"


def test_bold_metadata_analysis_has_required_libraries():
    """Test that the RMarkdown file loads required R libraries."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "bold_metadata_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required libraries
    required_libraries = ['readr', 'dplyr', 'tidyr', 'ggplot2', 'knitr']
    
    for lib in required_libraries:
        pattern = f'library\\({lib}\\)'
        assert re.search(pattern, content), f"RMarkdown must load library({lib})"


def test_analysis_readme_exists():
    """Test that the analysis README exists."""
    repo_root = Path(__file__).parent.parent
    readme_file = repo_root / "analysis" / "README.md"
    assert readme_file.exists(), f"Analysis README not found: {readme_file}"


def test_analysis_readme_documents_rmd():
    """Test that the analysis README documents the RMarkdown file."""
    repo_root = Path(__file__).parent.parent
    readme_file = repo_root / "analysis" / "README.md"
    
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for documentation of the RMarkdown file
    assert 'bold_metadata_analysis.Rmd' in content, "README must document the RMarkdown file"
    assert 'BOLD metadata' in content, "README must explain BOLD metadata joining"
    
    # Check for usage instructions
    assert 'Usage' in content or 'usage' in content, "README must include usage instructions"


def test_bold_metadata_analysis_has_validation_section():
    """Test that the RMarkdown file includes a barcode validation section."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "bold_metadata_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for validation section header
    assert 'Barcode Validation Success' in content, "RMarkdown must have a 'Barcode Validation Success' section"
    
    # Check for structural validity checks
    assert 'structural_valid' in content, "RMarkdown must calculate structural_valid"
    assert 'valid_length' in content, "RMarkdown must check valid_length (nuc_basecount >= 500)"
    assert 'valid_ambig' in content, "RMarkdown must check valid_ambig (ambig_basecount == 0)"
    assert 'valid_stops' in content, "RMarkdown must check valid_stops (stop_codons == 0)"
    
    # Check for taxonomic validity checks
    assert 'taxonomic_valid' in content, "RMarkdown must calculate taxonomic_valid"
    assert 'identification' in content, "RMarkdown must reference identification column"
    assert 'obs_taxon' in content, "RMarkdown must reference obs_taxon column"
    
    # Check for overall validation success
    assert 'validation_success' in content, "RMarkdown must calculate overall validation_success"
    
    # Check for documentation of assembly-level factors
    assembly_factors = ['r', 's', 'fcleaner', 'merge', 'validation_steps', 'assembly_params']
    for factor in assembly_factors:
        assert factor in content, f"RMarkdown must mention assembly factor: {factor}"
    
    # Check for documentation of specimen-level factors
    assert 'Collection Date' in content or 'Collection_Year' in content, "RMarkdown must mention specimen age/date"
    assert 'Phylum' in content or 'taxonomic' in content.lower(), "RMarkdown must mention taxonomic classification"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
