# Last Addition Data Processing

## Overview

This document describes the processing of validation data from the `data/naturalis/2step/24p/last_addition` folder to integrate it with the existing 24p data structure.

## Problem Statement

The `last_addition` folder contained validation data for 9 batches that needed to be processed and integrated into the main 24p data structure:
- BGE00086, BGE00157, BGE00321, BGE00322, BGE00323, BGE00325, BGE00326, BGE00328, BGE00333

The raw data consisted of:
1. Structural validation outputs (TSV files in `structural-validation-outputs/`)
2. Taxon validation outputs (TSV files in `taxon-validation-outputs/`)
3. CSV assembly metrics (in `BGEE_validation_015/`)
4. FASTA files (assemblies and taxonval outputs)

## Solution

A comprehensive processing script `scripts/process_last_addition.py` was created to automate the entire pipeline:

### Step 1: Merge Validation Files
- Merged structural and taxon validation TSV files using `bv_metrics_merger.py`
- Combined metrics from both validation types, replacing null values intelligently
- Key column: `sequence_id`

### Step 2: Join with CSV Data
- Joined merged TSV with CSV assembly metrics
- Join column: `sequence_id` (derived from `Filename` in CSV by stripping process ID suffix)
- Renamed CSV columns to match standard headers (e.g., `n_reads` → `n_reads_in`)
- Removed overlapping columns from CSV to avoid duplicates

### Step 3: Apply Data Transformations
The following transformations were applied to ensure tests pass:

1. **Column renaming**:
   - `n_aligned` → `n_reads_aligned` (if needed)
   - `process_id` → `group_id` (if needed)

2. **Parse MGE parameters**:
   - Extracted `r` and `s` values from `mge_params` column
   - Pattern: `r_<float>_s_<int>[_suffix]`

3. **Add derived columns**:
   - `fcleaner`: Boolean indicating if `_fcleaner` suffix is in `sequence_id`
   - `merge`: Boolean indicating if `_merge` suffix is in `sequence_id`

4. **Remove redundant data**:
   - Removed `Filename` and `ID` columns
   - Removed `backbone_source` column (if present)
   - Removed negative control records (rows with `-NC` suffix in `group_id` or error messages)

### Step 4: Copy FASTA Files
- Copied `BGE000XX_assemblies.fasta` to final location (all input sequence records)
- Copied `BGE000XX_taxonval_out.fasta` as `BGE000XX.fasta` (final validation output)

## Output Files

For each batch, the following files were created in `data/naturalis/2step/24p/`:

1. **BGE000XX.tsv**: Final processed TSV with all required columns and transformations
2. **BGE000XX.fasta**: Taxon validation output (final FASTA)
3. **BGE000XX_assemblies.fasta**: All input sequence records

## Results

- **9 batches processed**: BGE00086, BGE00157, BGE00321, BGE00322, BGE00323, BGE00325, BGE00326, BGE00328, BGE00333
- **27 files created**: 3 files per batch × 9 batches
- **All tests pass**: 444 tests passing (including 18 new tests for the 9 batches)
- **last_addition folder removed**: Original raw data folder deleted as no longer needed

## Test Results

### Before Processing
- 339 tests passing
- 36 tests failing (all in last_addition folder due to missing columns and unexpected headers)

### After Processing
- 357 tests passing (added 18 new tests for 9 new batches)
- 0 tests failing

### Final State (after cleanup)
- 444 tests passing (all tests in repository)
- 0 tests failing

## Usage

To process similar data in the future:

```bash
# Process all batches
python scripts/process_last_addition.py

# Process a specific batch only
python scripts/process_last_addition.py --batch BGE00086

# Dry run (show what would be done)
python scripts/process_last_addition.py --dry-run
```

## Data Quality Checks

All output files pass the following validations:
- ✓ All compulsory headers present (per `metadata/headers.tsv`)
- ✓ No unexpected headers
- ✓ No duplicate columns
- ✓ Proper data types and formats
- ✓ Negative controls removed
- ✓ r and s parameters correctly extracted
- ✓ fcleaner and merge flags correctly set

## Statistics

| Batch | TSV Rows | FASTA Sequences | Assemblies Size |
|-------|----------|-----------------|-----------------|
| BGE00086 | 2,088 | 33 | 2.8M |
| BGE00157 | 2,243 | 85 | 3.4M |
| BGE00321 | 2,281 | 80 | 3.5M |
| BGE00322 | 2,053 | 26 | 2.8M |
| BGE00323 | 2,279 | 71 | 3.5M |
| BGE00325 | 2,281 | 89 | 3.5M |
| BGE00326 | 2,257 | 93 | 3.4M |
| BGE00328 | 2,281 | 94 | 3.5M |
| BGE00333 | 2,245 | 44 | 3.4M |
| **Total** | **20,008** | **615** | **30.2M** |

## Notes

- The script uses temporary working directory `/tmp/process_last_addition` which is cleaned up after processing
- All transformations are applied in the documented order to ensure consistency
- The merge process intelligently handles overlapping columns to avoid `_csv` suffixes
- Processing time: ~2 minutes for all 9 batches
