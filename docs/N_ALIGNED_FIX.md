# n_aligned Column Fix

## Problem Statement

Some TSV files in the `data/naturalis/2step/6p/` folder had a column named `n_aligned` instead of the standard `n_reads_aligned` column name. According to the metadata definitions in `metadata/headers.tsv`, the correct column name is `n_reads_aligned` which represents "Number of input reads aligned to the pseudo-reference by MGE and used for generation of the consensus sequence".

The task was to:
1. Identify all TSV files with an `n_aligned` column but not an `n_reads_aligned` column
2. Rename the `n_aligned` column to `n_reads_aligned` in those files
3. Preserve all data values during the rename

## Solution

A Python script `scripts/fix_n_aligned_column.py` was created to:
- Scan all TSV files in the `data` directory
- Identify files with `n_aligned` but not `n_reads_aligned` column
- Rename the column while preserving all data values
- Provide dry-run mode for verification before applying changes

The script follows the same pattern as `scripts/fix_process_id_column.py` for consistency with the existing codebase.

## Usage

```bash
# Dry run mode (show what would be changed without making changes)
python scripts/fix_n_aligned_column.py --dry-run

# Apply changes
python scripts/fix_n_aligned_column.py

# Specify custom data directory
python scripts/fix_n_aligned_column.py --data-dir /path/to/data
```

## Results

### Files Modified

11 files in `data/naturalis/2step/6p/` were modified:
- BGE00119.tsv
- BGE00195.tsv
- BGE00197.tsv
- BGE00304.tsv
- BGE00433.tsv
- BGE00503.tsv
- BGE00509.tsv
- BGE00513.tsv
- BGE00579.tsv
- BGE00581.tsv
- BGE00582.tsv

### Data Integrity

- Original data preserved in all columns
- Only the column name changed from `n_aligned` to `n_reads_aligned`
- Column order and position maintained
- All data values remain unchanged

## Tests

Comprehensive unit tests are provided in `tests/test_fix_n_aligned.py` covering:
- File analysis to identify files needing the rename
- Column renaming functionality
- Files with both columns (should skip)
- Files with only n_reads_aligned (should skip)
- Dry-run mode functionality
- Data preservation during fixes

Run tests with:
```bash
python -m pytest tests/test_fix_n_aligned.py -v
```

All existing tests (216 total) continue to pass after the changes.

## Examples

### Before
```tsv
ambig_basecount	...	n_reads	n_aligned	skipped_reads_low_rel	...
0	...	4098068	21377	10299	...
```

### After
```tsv
ambig_basecount	...	n_reads	n_reads_aligned	skipped_reads_low_rel	...
0	...	4098068	21377	10299	...
```

## Related Documentation

- `docs/PROCESS_ID_FIX.md` - Similar script for handling `process_id` vs `group_id` columns
- `docs/FILENAME_FIX.md` - Script for handling redundant `Filename` column
- `metadata/headers.tsv` - Authoritative list of column names and their definitions

## Notes

The `metadata/headers.tsv` file contains both `n_aligned` and `n_reads_aligned` definitions:
- `n_reads_aligned` is the standard column name
- `n_aligned` is listed as an "alternative column name"

This fix standardizes all files to use the preferred `n_reads_aligned` column name for consistency across the dataset.
