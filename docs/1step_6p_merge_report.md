# 1step/6p CSV Merge Report

## Overview

This document describes the corrections applied to CSV files in `data/naturalis/1step/6p/` to make them compatible with the TSV file format and validation requirements defined in `metadata/headers.tsv`.

## Files Processed

- **TSV files**: 112 files (BGE00XXX.tsv)
- **CSV files**: 112 files (BGE00XXX_MGE-BGE_r1_1.3_1.5_s50_100.csv)
- **Merged output**: 112 files (BGE00XXX_merged.tsv)

## Pre-existing Data Quality Issues

### Duplicate Column Headers

Four TSV files contained duplicate `sequence` column headers:
- BGE00119.tsv
- BGE00141.tsv
- BGE00143.tsv
- BGE00511.tsv

**Resolution**: The merge script now handles duplicate columns by keeping the first occurrence and discarding subsequent duplicates.

## Corrections Applied to CSV Data

### 1. Column Renaming

The CSV files used column names that differed from the expected headers defined in `metadata/headers.tsv`. The following columns were renamed:

| CSV Column Name | TSV Column Name | Description |
|----------------|-----------------|-------------|
| `n_reads` | `n_reads_in` | Number of QC'd/trimmed reads input into MGE |
| `n_aligned` | `n_reads_aligned` | Number of input reads aligned to the pseudo-reference by MGE |
| `skipped_reads_low_rel` | `n_reads_skipped` | Number of input reads omitted from alignment |
| `length` | `ref_length` | Length of pseudo-reference used for generation of the consensus sequence |

### 2. Redundant Columns Removed

Two columns from the CSV files were removed as they were redundant with existing TSV columns:

| Column | Reason for Removal |
|--------|-------------------|
| `Filename` | Redundant with `sequence_id` (after stripping the `_<Process ID>` suffix) |
| `Process ID` | Redundant with `group_id` column in TSV |

### 3. Join Column Creation

The `sequence_id` column was created from the CSV `Filename` column by stripping the `_<Process ID>` suffix:

- CSV Filename format: `PROCESS-ID_r_X.X_s_XX_PROCESS-ID`
- TSV sequence_id format: `PROCESS-ID_r_X.X_s_XX`
- Join key: Strip `_PROCESS-ID` suffix from Filename

Example:
- CSV Filename: `BBIOP1943-24_r_1.3_s_100_BBIOP1943-24`
- Join key: `BBIOP1943-24_r_1.3_s_100`
- Matches TSV sequence_id: `BBIOP1943-24_r_1.3_s_100`

### 4. Columns Preserved

The following columns from the CSV files were kept unchanged as they already matched the expected format:
- `cov_min`
- `cov_max`
- `cov_avg`
- `cov_med`

## Merge Statistics

All 112 file pairs were successfully merged with the following results:
- Average rows per merged file: 570
- Average columns per merged file: 27
- Successful CSV data integration: 100% (all rows with matching sequence_ids received CSV data)

## Validation Results

All merged TSV files pass the following validation tests:
- ✓ All column headers are defined in `metadata/headers.tsv`
- ✓ All compulsory headers are present
- ✓ No unexpected or invalid column names
- ✓ Column naming conventions followed

## Script Details

The corrections were implemented in the `scripts/merge_6p_data.py` script with the following key features:

1. **Automatic file pairing**: Matches TSV and CSV files by BGE number
2. **Column preprocessing**: Renames CSV columns to match expected headers
3. **Join key generation**: Creates sequence_id from CSV Filename column
4. **Duplicate handling**: Detects and resolves duplicate column headers in source files
5. **Redundant column removal**: Removes Filename and Process ID after merge
6. **Left join merge**: Preserves all TSV rows, adds CSV data where available

## Usage

To merge TSV and CSV files:

```bash
# Merge files in 1step/6p (default)
python scripts/merge_6p_data.py

# Merge files in a different directory
python scripts/merge_6p_data.py --tsv-dir data/other/dir --csv-dir data/other/dir --output-dir data/other/dir

# Dry run to preview what would be processed
python scripts/merge_6p_data.py --dry-run
```

## Conclusion

The CSV files in `data/naturalis/1step/6p/` have been successfully merged with their corresponding TSV files. All necessary corrections have been applied to ensure the merged files are valid according to the project's metadata specifications. The merged files are ready for further analysis and processing.
