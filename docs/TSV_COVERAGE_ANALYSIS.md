# TSV Header Coverage Analysis

## Overview

This document describes the TSV header coverage analysis tools and the patterns found in the repository's data files.

The analysis compares headers in TSV files against the expected headers defined in `metadata/headers.tsv`. Different TSV files have different subsets of headers, and files are grouped by their coverage patterns.

## Quick Start

### Running the Analysis

```bash
# Generate coverage reports
python scripts/analyze_tsv_coverage.py

# View the summary
cat reports/coverage/coverage_summary.md

# Generate issue creation instructions
python scripts/create_coverage_issues.py --output-file reports/coverage/ISSUE_CREATION_INSTRUCTIONS.md
```

### Output Structure

```
reports/coverage/
├── README.md                          # Overview and instructions
├── coverage_summary.md                 # High-level summary
├── coverage_data.json                  # Machine-readable data
├── ISSUE_CREATION_INSTRUCTIONS.md      # Guide for creating GitHub issues
├── patterns/
│   ├── pattern_1.md                   # Detailed pattern analysis
│   ├── pattern_2.md
│   └── ...
└── issues/
    ├── pattern_1_issue.md             # GitHub issue template
    ├── pattern_2_issue.md
    └── ...
```

## Analysis Results

### Summary (as of October 2025)

- **Total TSV files analyzed:** 168
- **Unique header patterns found:** 5
- **Total expected headers:** 56 (defined in metadata/headers.tsv)

### Coverage Patterns

| Pattern | Files | Coverage | Missing Headers | Primary Location |
|---------|-------|----------|-----------------|------------------|
| 1 | 44 | 69.6% | 17 | data/naturalis/2step/24p/ |
| 2 | 11 | 50.0% | 28 | data/naturalis/2step/6p/ |
| 3 | 4 | 32.1% | 38 | data/naturalis/1step/ |
| 4 | 1 | 26.8% | 41 | data/naturalis/2step/24p/ |
| 5 | 108 | 23.2% | 43 | data/naturalis/1step/ |

## Pattern Details

### Pattern 1: Highest Coverage (69.6%)

**Files:** 44 files in `data/naturalis/2step/24p/`

**Present (39 headers):** BOLD_submission, Filename, ambig_basecount, ambig_full_basecount, ambig_original, cleaning_ambig_bases, cleaning_cov_percent, cleaning_removed_at, cleaning_removed_human, cleaning_removed_outlier, cleaning_removed_reference, cov_avg, cov_max, cov_med, cov_min, dataset, error, fasta_header, group_id, identification, identification_method, identification_rank, marker_code, mge_params, n_reads_aligned, n_reads_in, n_reads_skipped, nuc_basecount, nuc_full_basecount, obs_taxon, reading_frame, ref_accession, ref_length, ref_rank, sample_taxid, sequence, sequence_id, species, stop_codons

**Missing (17 headers):** cleaned, cleaning_kept_reads, family, fasta_file, genes, length, n_aligned, n_reads, nuc, output_dir, protein_reference_file, r, run_name, s, samples_file, skipped_reads_low_rel, skipped_reads_low_rel_score

### Pattern 5: Lowest Coverage (23.2%)

**Files:** 108 files (most common pattern) in `data/naturalis/1step/`

**Present (13 headers):** ambig_basecount, ambig_full_basecount, dataset, error, identification, identification_method, identification_rank, nuc_basecount, nuc_full_basecount, obs_taxon, sequence_id, species, stop_codons

**Missing (43 headers):** Most MGE pipeline fields, cleaning statistics, and detailed metadata

## Scripts

### analyze_tsv_coverage.py

Main analysis script that scans all TSV files and generates comprehensive reports.

**Features:**
- Discovers all TSV files recursively in data/
- Groups files by header coverage pattern
- Calculates coverage statistics
- Generates multiple report formats (Markdown, JSON)
- Creates GitHub issue templates

**Usage:**
```bash
python scripts/analyze_tsv_coverage.py [--output-dir DIR]

# Options:
#   --output-dir DIR    Output directory (default: reports/coverage)
```

**Output:**
1. `coverage_summary.md` - Overview of all patterns
2. `patterns/pattern_N.md` - Detailed report for each pattern
3. `issues/pattern_N_issue.md` - GitHub issue template for each pattern
4. `coverage_data.json` - Machine-readable data

### create_coverage_issues.py

Helper script that generates instructions for creating GitHub issues.

**Usage:**
```bash
python scripts/create_coverage_issues.py [--output-file FILE]

# Options:
#   --reports-dir DIR   Coverage reports directory (default: reports/coverage)
#   --output-file FILE  Output file for instructions (default: stdout)
```

## Creating GitHub Issues

For each coverage pattern, a GitHub issue should be created to track and discuss the pattern.

### Manual Creation

1. Run the analysis: `python scripts/analyze_tsv_coverage.py`
2. Review pattern reports in `reports/coverage/patterns/`
3. For each pattern:
   - Go to https://github.com/bge-barcoding/bge-skimming-analytics/issues/new
   - Copy the title and body from `reports/coverage/issues/pattern_N_issue.md`
   - Add suggested labels (found in each template)
   - Submit the issue

### Using GitHub CLI

```bash
# Install gh CLI: https://cli.github.com/

# Create issues for all patterns
for i in {1..5}; do
  # Get title from pattern data
  gh issue create \
    --label "data-quality,headers" \
    --body-file reports/coverage/issues/pattern_${i}_issue.md
done
```

### Suggested Labels

- `data-quality` - All coverage issues
- `headers` - All coverage issues
- `low-coverage` - Patterns with <50% coverage
- `unexpected-headers` - Patterns with undefined headers

## Understanding Coverage Patterns

### Why Different Patterns Exist

Different coverage patterns typically arise from:

1. **Processing Pipeline Stage:** 1-step vs 2-step processing may generate different metadata
2. **Data Source:** Different institutions or methods may provide different metadata
3. **Evolution Over Time:** Newer files may have more complete metadata
4. **Pipeline Version:** Different versions of barcode_validator may generate different fields

### Pattern Interpretation

**High Coverage (>60%):** Files with comprehensive metadata, likely from complete 2-step processing pipelines with all cleaning and validation steps.

**Medium Coverage (40-60%):** Files with intermediate metadata, possibly from simplified pipelines or partial processing.

**Low Coverage (<40%):** Files with minimal metadata, often from 1-step processing or basic validation without extensive cleaning statistics.

## Next Steps

1. **Track via Issues:** Create GitHub issues for each pattern (5 issues total)
2. **Investigate Patterns:** Determine why each pattern exists
3. **Define Standards:** Document which headers are required vs optional
4. **Update Data:** Add missing headers if data is available
5. **Update Metadata:** Remove headers from metadata/headers.tsv if not applicable
6. **Monitor:** Re-run analysis periodically to track improvements

## Technical Details

### Header Validation

The repository includes tests (`tests/test_tsv_headers.py`) that enforce:
- All headers in TSV files must be defined in `metadata/headers.tsv`
- TSV files may have any subset of defined headers
- No unexpected headers are allowed

### Coverage Calculation

Coverage percentage = (Present headers / Total expected headers) × 100

Where:
- Present headers: Headers that are both in the TSV file AND in metadata/headers.tsv
- Total expected headers: All headers defined in metadata/headers.tsv (56 total)

### Data Sources

- **Expected headers:** `metadata/headers.tsv` (56 headers defined)
- **Actual data:** All `.tsv` files in `data/` directory (168 files)

## Re-running Analysis

Reports are generated in `reports/coverage/` which is in `.gitignore`. To regenerate:

```bash
# Clean old reports (optional)
rm -rf reports/coverage/

# Run analysis
python scripts/analyze_tsv_coverage.py

# Review results
cat reports/coverage/coverage_summary.md
```

## Related Documentation

- `metadata/headers.tsv` - Expected header definitions
- `tests/test_tsv_headers.py` - Header validation tests
- `docs/PROCESS_ID_FIX.md` - Example of fixing header inconsistencies
