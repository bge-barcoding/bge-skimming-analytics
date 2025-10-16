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
    required_libraries = ['readr', 'dplyr', 'ggplot2', 'knitr']
    
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


def test_assembly_parameter_analysis_rmd_exists():
    """Test that the assembly parameter analysis RMarkdown file exists."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    assert rmd_file.exists(), f"RMarkdown file not found: {rmd_file}"


def test_assembly_parameter_analysis_has_yaml_header():
    """Test that the RMarkdown file has a valid YAML header."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    
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


def test_assembly_parameter_analysis_references_correct_files():
    """Test that the RMarkdown file references the correct data files."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for references to required data files
    assert '../data/bge-skimming-analytics.tsv.gz' in content, "RMarkdown must reference main data file"


def test_assembly_parameter_analysis_has_required_libraries():
    """Test that the RMarkdown file loads required R libraries."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required libraries
    required_libraries = ['readr', 'dplyr', 'ggplot2', 'knitr', 'tidyr']
    
    for lib in required_libraries:
        pattern = f'library\\({lib}\\)'
        assert re.search(pattern, content), f"RMarkdown must load library({lib})"


def test_assembly_parameter_analysis_has_independent_variables():
    """Test that the RMarkdown file analyzes all independent variables."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for independent variables
    independent_vars = ['r', 's', 'fcleaner', 'merge']
    
    for var in independent_vars:
        # Check for mention in variable selection or grouping
        assert var in content, f"RMarkdown must analyze independent variable: {var}"


def test_assembly_parameter_analysis_has_dependent_variables():
    """Test that the RMarkdown file analyzes all dependent variables."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for dependent variables
    dependent_vars = ['nuc_full_basecount', 'ambig_full_basecount', 'stop_codons']
    
    for var in dependent_vars:
        assert var in content, f"RMarkdown must analyze dependent variable: {var}"


def test_assembly_parameter_analysis_has_statistical_tests():
    """Test that the RMarkdown file includes statistical tests."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for statistical tests
    assert 'aov' in content or 'ANOVA' in content, "RMarkdown must include ANOVA tests"
    assert 't.test' in content or 'T-test' in content, "RMarkdown must include t-tests"


def test_assembly_parameter_analysis_has_visualizations():
    """Test that the RMarkdown file includes visualizations."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for visualizations
    assert 'ggplot' in content, "RMarkdown must include ggplot visualizations"
    assert 'geom_boxplot' in content, "RMarkdown must include boxplots"


def test_assembly_parameter_analysis_has_interaction_analysis():
    """Test that the RMarkdown file includes interaction analysis."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "assembly_parameter_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for interaction analysis
    assert 'Interaction' in content or 'interaction' in content, "RMarkdown must include interaction analysis"


def test_specimen_age_analysis_rmd_exists():
    """Test that the specimen age analysis RMarkdown file exists."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    assert rmd_file.exists(), f"RMarkdown file not found: {rmd_file}"


def test_specimen_age_analysis_has_yaml_header():
    """Test that the RMarkdown file has a valid YAML header."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    
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


def test_specimen_age_analysis_references_correct_files():
    """Test that the RMarkdown file references the correct data files."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for references to required data files
    required_files = [
        '../data/bge-skimming-analytics.tsv.gz',
        '../metadata/bold/lab.tsv',
        '../metadata/bold/collection_data.tsv'
    ]
    
    for file_path in required_files:
        assert file_path in content, f"RMarkdown must reference {file_path}"


def test_specimen_age_analysis_has_required_libraries():
    """Test that the RMarkdown file loads required R libraries."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required libraries
    required_libraries = ['readr', 'dplyr', 'ggplot2', 'knitr', 'lubridate']
    
    for lib in required_libraries:
        pattern = f'library\\({lib}\\)'
        assert re.search(pattern, content), f"RMarkdown must load library({lib})"


def test_specimen_age_analysis_uses_n_reads_aligned():
    """Test that the RMarkdown file analyzes n_reads_aligned."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for n_reads_aligned
    assert 'n_reads_aligned' in content, "RMarkdown must analyze n_reads_aligned"


def test_specimen_age_analysis_calculates_specimen_age():
    """Test that the RMarkdown file calculates specimen age."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for specimen age calculation
    assert 'Specimen_Age' in content or 'specimen_age' in content or 'Collection_Year' in content, \
        "RMarkdown must calculate specimen age"
    assert 'Collection Date' in content, "RMarkdown must use Collection Date"


def test_specimen_age_analysis_aggregates_by_specimen():
    """Test that the RMarkdown file aggregates data at specimen level."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for aggregation at specimen level (group_id)
    assert 'group_by(group_id)' in content, "RMarkdown must aggregate by group_id"
    # Check for selecting highest n_reads_aligned
    assert 'slice_max' in content or 'arrange' in content, \
        "RMarkdown must select highest n_reads_aligned per specimen"


def test_specimen_age_analysis_has_visualizations():
    """Test that the RMarkdown file includes visualizations."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for visualizations
    assert 'ggplot' in content, "RMarkdown must include ggplot visualizations"
    # Check for multiple plot types
    plot_types = ['geom_point', 'geom_boxplot', 'geom_col', 'geom_histogram', 'geom_hex']
    found_plot_types = [pt for pt in plot_types if pt in content]
    assert len(found_plot_types) >= 3, "RMarkdown must include at least 3 types of plots"


def test_specimen_age_analysis_has_statistical_tests():
    """Test that the RMarkdown file includes statistical tests."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "specimen_age_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for statistical tests
    assert 'cor.test' in content, "RMarkdown must include correlation test"
    assert 'lm' in content or 'linear' in content.lower(), "RMarkdown must include linear regression"
    assert 'aov' in content or 'ANOVA' in content, "RMarkdown must include ANOVA"


def test_analysis_readme_documents_specimen_age():
    """Test that the analysis README documents the specimen age analysis."""
    repo_root = Path(__file__).parent.parent
    readme_file = repo_root / "analysis" / "README.md"
    
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for documentation of the specimen age analysis
    assert 'specimen_age_analysis.Rmd' in content, "README must document specimen_age_analysis.Rmd"
    assert 'n_reads_aligned' in content, "README must mention n_reads_aligned metric"


def test_taxonomic_validation_analysis_rmd_exists():
    """Test that the taxonomic validation analysis RMarkdown file exists."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    assert rmd_file.exists(), f"RMarkdown file not found: {rmd_file}"


def test_taxonomic_validation_analysis_has_yaml_header():
    """Test that the RMarkdown file has a valid YAML header."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
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
    assert 'Taxonomic Validation' in yaml_header, \
        "Title must reference taxonomic validation"


def test_taxonomic_validation_analysis_references_correct_files():
    """Test that the RMarkdown file references the correct data files."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for references to required data files
    assert 'bge-skimming-analytics.tsv.gz' in content, \
        "RMarkdown must reference main analytics data file"
    assert 'metadata/bold/lab.tsv' in content or 'lab.tsv' in content, \
        "RMarkdown must reference BOLD lab metadata"
    assert 'metadata/bold/taxonomy.tsv' in content or 'taxonomy.tsv' in content, \
        "RMarkdown must reference BOLD taxonomy metadata"


def test_taxonomic_validation_analysis_has_required_libraries():
    """Test that the RMarkdown file loads required libraries."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required R libraries
    required_libs = ['readr', 'dplyr', 'ggplot2', 'knitr']
    for lib in required_libs:
        assert f'library({lib})' in content, f"RMarkdown must load {lib} library"


def test_taxonomic_validation_analysis_uses_taxonomic_validation():
    """Test that the analysis uses taxonomic validation criteria."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for taxonomic validation logic
    assert 'identification' in content, "RMarkdown must reference identification column"
    assert 'obs_taxon' in content, "RMarkdown must reference obs_taxon column"
    # Check for either grepl or strsplit approach for matching
    assert 'grepl' in content or 'strsplit' in content, \
        "RMarkdown must use grepl or strsplit to check if identification is in obs_taxon"
    assert 'taxonomic_valid' in content, "RMarkdown must calculate taxonomic_valid"


def test_taxonomic_validation_analysis_aggregates_by_specimen():
    """Test that the analysis aggregates by specimen (group_id)."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for aggregation by group_id
    assert 'group_by(group_id' in content, "RMarkdown must aggregate by group_id"
    # Check for either any_success or taxonomic_valid to determine specimen success
    assert 'any_success' in content or 'taxonomic_valid' in content, \
        "RMarkdown must check if specimen was successful"


def test_taxonomic_validation_analysis_filters_by_order():
    """Test that the analysis filters to Orders with at least 5 specimens."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Order filtering
    assert 'Order' in content, "RMarkdown must reference taxonomic Order"
    assert 'n_specimens >= 5' in content or '>= 5' in content, \
        "RMarkdown must filter to Orders with at least 5 specimens"


def test_taxonomic_validation_analysis_filters_empty_values():
    """Test that the analysis filters out records with empty identification or obs_taxon."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for filtering of empty values
    # Accept either analytics_data_filtered or analytics_with_match as valid names
    assert 'analytics_data_filtered' in content or 'analytics_with_match' in content, \
        "RMarkdown must create filtered dataset"
    assert 'filter(!is.na(identification)' in content or 'filter(!is.na(obs_taxon)' in content, \
        "RMarkdown must filter out records with NA identification or obs_taxon"
    # Check that some form of filtered data is used
    assert 'analytics_data_filtered %>%' in content or 'analytics_with_match %>%' in content, \
        "RMarkdown must use filtered analytics data"


def test_taxonomic_validation_analysis_has_statistical_tests():
    """Test that the RMarkdown file includes statistical tests."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for statistical tests
    assert 'chisq.test' in content, "RMarkdown must include chi-square test"
    assert 'cramers_v' in content or "Cramér's V" in content, \
        "RMarkdown must calculate Cramér's V effect size"


def test_taxonomic_validation_analysis_has_visualizations():
    """Test that the RMarkdown file includes visualizations."""
    repo_root = Path(__file__).parent.parent
    rmd_file = repo_root / "analysis" / "taxonomic_validation_analysis.Rmd"
    
    with open(rmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for visualizations
    assert 'ggplot' in content, "RMarkdown must include ggplot visualizations"
    # Check for multiple plot types
    plot_types = ['geom_col', 'geom_histogram', 'geom_point']
    found_plot_types = [pt for pt in plot_types if pt in content]
    assert len(found_plot_types) >= 2, "RMarkdown must include at least 2 types of plots"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
