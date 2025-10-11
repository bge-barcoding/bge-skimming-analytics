# Filename Column Fix

## Problem Statement

Some TSV files in the `data` folder had a column named `Filename` in addition to a `sequence_id` column. In some cases, these columns contained identical values, making the `Filename` column redundant. In other cases, the values differed, indicating that the `Filename` column serves a different purpose and should be retained.

The task was to:
1. Identify all TSV files with a `Filename` column
2. Check if they also have a `sequence_id` column
3. Compare the values in both columns
4. Remove the `Filename` column when all values match `sequence_id`
5. Report files where the values differ for manual review

## Solution

Created a Python script `scripts/fix_filename_column.py` that:

1. Scans all TSV files in the data directory for a `Filename` column
2. For each file with a `Filename` column:
   - Checks if `sequence_id` column exists
   - Compares all values between `Filename` and `sequence_id`
   - If all values match: marks file for automatic fixing (removal of `Filename` column)
   - If values differ or `sequence_id` is absent: marks file for manual review
3. Removes the `Filename` column from files where values match
4. Reports files requiring manual review with examples of differing values

## Usage

```bash
# Dry run (show what would be done without making changes)
python scripts/fix_filename_column.py --dry-run

# Apply fixes
python scripts/fix_filename_column.py

# Specify custom data directory
python scripts/fix_filename_column.py --data-dir /path/to/data
```

## Results

Initial scan found:
- **55 files** total with a `Filename` column
- **1 file** where `Filename` matched `sequence_id` exactly (automatically fixed)
- **54 files** where values differed (reported for manual review)

### Fixed Files

The `Filename` column was automatically removed from:
- `data/nhm/2step/24p/XE-4013.tsv`

In this file, all 32,173 rows had identical values in both `Filename` and `sequence_id` columns, making the `Filename` column redundant.

### Files Requiring Manual Review

54 files were identified where the `Filename` and `sequence_id` values differ. These files were **NOT** modified and require manual review to determine if the `Filename` column should be kept.

Common patterns observed in files requiring manual review:

1. **24p files with `_merge` suffix difference**: Most files in `data/naturalis/2step/24p/` and `data/nhm/2step/24p/` show patterns like:
   - `Filename`: `BSCRO1521-25_r_1.3_s_100_BSCRO1521-25`
   - `sequence_id`: `BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_merge`
   
   The difference is that some rows in `sequence_id` have a `_merge` suffix that is missing from `Filename`.

2. **6p files with trailing process ID difference**: Files in `data/naturalis/2step/6p/` show patterns like:
   - `Filename`: `BGSNH001-24_r_1.3_s_100_BGSNH001-24`
   - `sequence_id`: `BGSNH001-24_r_1.3_s_100`
   
   The difference is that `Filename` includes the trailing process ID while `sequence_id` does not.

These patterns suggest that:
- The `Filename` column may represent the original input filename from data processing steps
- The `sequence_id` column may have been processed/normalized (e.g., adding `_merge` suffix, removing trailing process ID)
- Both columns may be needed for traceability or data provenance purposes

## Tests

Comprehensive unit tests are provided in `tests/test_fix_filename.py` covering:
- Detection of files requiring removal vs. manual review
- Correct removal of the `Filename` column
- Dry-run mode functionality
- Data preservation during fixes
- Column order preservation (except for removed column)

Run tests with:
```bash
python -m pytest tests/test_fix_filename.py -v
```

## Examples

### Before (file with matching values)
```tsv
ambig_basecount	Filename	error	sequence_id	species
2	BGSNL096-23_r_1.3_s_100_BGSNL096-23	None	BGSNL096-23_r_1.3_s_100_BGSNL096-23	Species A
```

### After (file with matching values)
```tsv
ambig_basecount	error	sequence_id	species
2	None	BGSNL096-23_r_1.3_s_100_BGSNL096-23	Species A
```

### Files with Differing Values (NOT modified)
```tsv
# Example 1: _merge suffix difference
Filename: BSCRO1521-25_r_1.3_s_100_BSCRO1521-25
sequence_id: BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_merge

# Example 2: Trailing process ID difference
Filename: BGSNH001-24_r_1.3_s_100_BGSNH001-24
sequence_id: BGSNH001-24_r_1.3_s_100
```

## Related Documentation

- `docs/PROCESS_ID_FIX.md` - Similar script for handling `process_id` vs `group_id` columns
- `docs/SEQUENCE_ID_PARSING.md` - Script for parsing and populating columns from `sequence_id` patterns

## Recommendations

For the 54 files with differing values, consider:

1. **Investigate the data pipeline**: Understand why `Filename` and `sequence_id` differ in these files
2. **Determine data provenance needs**: If `Filename` represents original input filenames, it may be valuable for traceability
3. **Consider consolidation**: If the differences are systematic and not meaningful, create a rule to normalize one of the columns
4. **Update metadata documentation**: Add `Filename` to `metadata/headers.tsv` if it should be a valid column, or document why it's temporary

The script provides detailed output showing the first 5 mismatches in each file to help with manual review decisions.
