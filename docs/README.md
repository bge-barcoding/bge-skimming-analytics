# Documentation

This directory contains detailed documentation for the BGE skimming analytics project.

## Getting Started

- **[DATA_PROCESSING.md](DATA_PROCESSING.md)** - Complete guide to the data processing pipeline, including processing order, best practices, and overview of all transformations

## Data Processing Documentation

Individual documentation files describe specific fixes and transformations applied to the data:

### Column Standardization
- **[PROCESS_ID_FIX.md](PROCESS_ID_FIX.md)** - Renaming/removing `process_id` columns to use the standard `group_id` column name
- **[N_ALIGNED_FIX.md](N_ALIGNED_FIX.md)** - Renaming `n_aligned` to the standard `n_reads_aligned` column name

### Structured Data Parsing
- **[SEQUENCE_ID_PARSING.md](SEQUENCE_ID_PARSING.md)** - Parsing structured `sequence_id` values to extract `group_id`, `r`, and `s` columns
- **[MGE_PARAMS_PARSING.md](MGE_PARAMS_PARSING.md)** - Parsing `mge_params` values to extract `r` and `s` columns
- **[FCLEANER_MERGE_COLUMNS.md](FCLEANER_MERGE_COLUMNS.md)** - Adding boolean columns for `fcleaner` and `merge` data processing flags

### Redundant Column Removal
- **[FILENAME_FIX.md](FILENAME_FIX.md)** - Identifying and removing redundant `Filename` columns

### Data Merging
- **[1step_6p_merge_report.md](1step_6p_merge_report.md)** - Report on merging TSV validation files with CSV assembly metrics for the 6p dataset

### Analysis and Quality Control
- **[TSV_COVERAGE_ANALYSIS.md](TSV_COVERAGE_ANALYSIS.md)** - Analyzing header coverage patterns across all TSV files

## Document Structure

Each documentation file typically includes:

- **Problem Statement**: Description of the issue being addressed
- **Solution**: Approach and implementation details
- **Usage**: How to run the associated script
- **Results**: Outcomes and statistics from applying the fix
- **Examples**: Before/after comparisons
- **Tests**: Information about unit tests
- **Related Documentation**: Links to related docs

## Contributing

When creating new documentation:

1. Follow the established structure (Problem → Solution → Usage → Results → Examples → Tests)
2. Include concrete before/after examples
3. Link to related documentation
4. Update this README.md with an entry for the new document
5. Add a reference to the document in DATA_PROCESSING.md if it's part of the standard pipeline

## Quick Reference

### For New Users
Start with [DATA_PROCESSING.md](DATA_PROCESSING.md) to understand the overall workflow.

### For Script Usage
See the specific documentation file for the script you want to run, or consult [scripts/README.md](../scripts/README.md) for a list of all available scripts.

### For Understanding Past Changes
Each fix documentation describes why and how specific transformations were applied to the data.

### For Contributing
Follow existing patterns and ensure comprehensive documentation for any new processing scripts.
