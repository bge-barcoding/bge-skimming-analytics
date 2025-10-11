# Header Cleanup Summary

## Overview

This document describes the cleanup of `metadata/headers.tsv` to remove headers that do not occur in any TSV files in the `data/` directory.

## Analysis Results

### Headers Removed (0 occurrences in 168 TSV files)

The following 10 headers were removed from `metadata/headers.tsv` because they did not appear in any TSV file:

1. `cleaned` - Boolean denoting whether the barcode consensus sequence was generated pre- or post-cleaning
2. `family` - Taxonomic family identification
3. `fasta_file` - Source FASTA file path
4. `genes` - Genes identified in sequence
5. `output_dir` - Output directory path
6. `protein_reference_file` - Path to protein reference file
7. `r` - MGE parameter r value
8. `run_name` - Name of the sequencing/analysis run
9. `s` - MGE parameter s value
10. `samples_file` - Path to samples file

### Statistics

- **Before cleanup:** 53 headers (54 lines including header row)
- **After cleanup:** 43 headers (44 lines including header row)
- **Headers removed:** 10
- **Headers kept:** 43
- **TSV files analyzed:** 168

### Header Occurrence Counts

The table below shows all remaining headers and the number of TSV files in which they occur (ordered in increasing order):

| Header | Occurrences | Percentage |
|--------|-------------|------------|
| length | 11 | 6.5% |
| n_aligned | 11 | 6.5% |
| n_reads | 11 | 6.5% |
| skipped_reads_low_rel | 11 | 6.5% |
| cleaning_ambig_bases | 44 | 26.2% |
| cleaning_cov_percent | 44 | 26.2% |
| cleaning_removed_at | 44 | 26.2% |
| cleaning_removed_human | 44 | 26.2% |
| cleaning_removed_outlier | 44 | 26.2% |
| cleaning_removed_reference | 44 | 26.2% |
| fasta_header | 44 | 26.2% |
| mge_params | 44 | 26.2% |
| n_reads_aligned | 44 | 26.2% |
| n_reads_in | 44 | 26.2% |
| n_reads_skipped | 44 | 26.2% |
| ref_accession | 44 | 26.2% |
| ref_length | 44 | 26.2% |
| ref_rank | 44 | 26.2% |
| sample_taxid | 44 | 26.2% |
| BOLD_submission | 55 | 32.7% |
| Filename | 55 | 32.7% |
| ambig_original | 55 | 32.7% |
| cov_avg | 55 | 32.7% |
| cov_max | 55 | 32.7% |
| cov_med | 55 | 32.7% |
| cov_min | 55 | 32.7% |
| reading_frame | 59 | 35.1% |
| group_id | 60 | 35.7% |
| sequence | 60 | 35.7% |
| ambig_basecount | 168 | 100.0% |
| ambig_full_basecount | 168 | 100.0% |
| dataset | 168 | 100.0% |
| error | 168 | 100.0% |
| identification | 168 | 100.0% |
| identification_method | 168 | 100.0% |
| identification_rank | 168 | 100.0% |
| marker_code | 168 | 100.0% |
| nuc_basecount | 168 | 100.0% |
| nuc_full_basecount | 168 | 100.0% |
| obs_taxon | 168 | 100.0% |
| sequence_id | 168 | 100.0% |
| species | 168 | 100.0% |
| stop_codons | 168 | 100.0% |

### Key Insights

1. **Universal headers (100% occurrence):** 13 headers appear in all 168 TSV files, indicating they are core fields
2. **Partial coverage:** Many headers appear in subsets of files, suggesting different data collection workflows or file types
3. **Removed headers:** All 10 removed headers had 0% occurrence, confirming they were unused

## Script Usage

The cleanup was performed using `scripts/clean_unused_headers.py`:

```bash
# Preview changes (dry run)
python scripts/clean_unused_headers.py --dry-run

# Execute cleanup
python scripts/clean_unused_headers.py
```

The script:
1. Scans all TSV files in `data/` directory
2. Counts occurrences of each header defined in `metadata/headers.tsv`
3. Removes headers with 0 occurrences
4. Generates an occurrence report in `reports/header_occurrences.md`

## Testing

All 187 existing tests continue to pass after the cleanup:
```bash
python -m pytest tests/ -v
```

## Related Documentation

- `metadata/headers.tsv` - Expected header definitions (now cleaned)
- `tests/test_tsv_headers.py` - Header validation tests
- `scripts/clean_unused_headers.py` - Cleanup script
- `docs/TSV_COVERAGE_ANALYSIS.md` - Detailed coverage analysis
