# Filename Column Fix

## Problem Statement

Some TSV files in the `data` folder had a column named `Filename` in addition to a `sequence_id` column. Analysis revealed that in many cases, the `sequence_id` column followed a specific pattern where it was either identical to `Filename` or equal to `Filename + '_merge'`. This pattern (Pattern 1) indicates that the `sequence_id` is the correct identifier and the `Filename` column is redundant.

The task was to:
1. Identify all TSV files with a `Filename` column
2. Check if they also have a `sequence_id` column
3. Identify files matching Pattern 1 (sequence_id equals Filename or Filename + '_merge')
4. Remove the `Filename` column from Pattern 1 files
5. Report files with other patterns for manual review

## Pattern 1 Definition

Pattern 1 files are those where **all** rows satisfy one of the following conditions:
- `sequence_id` == `Filename` (exact match)
- `sequence_id` == `Filename + '_merge'` (sequence_id has merge suffix)

In Pattern 1 files, the `sequence_id` is the correct identifier and the `Filename` column can be safely removed.

## Solution

Created a Python script `scripts/fix_filename_column.py` that:

1. Scans all TSV files in the data directory for a `Filename` column
2. For each file with a `Filename` column:
   - Checks if `sequence_id` column exists
   - Analyzes all rows to determine if they match Pattern 1
   - If all rows match Pattern 1: marks file for automatic fixing (removal of `Filename` column)
   - If any row violates Pattern 1: marks file for manual review
3. Removes the `Filename` column from Pattern 1 files
4. Reports files not matching Pattern 1 with examples of violations

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
- **40 files** matching Pattern 1 (automatically fixed)
- **14 files** not matching Pattern 1 (reported for manual review)
- **1 file** was already fixed in a previous run

### Fixed Files (Pattern 1)

The `Filename` column was automatically removed from 40 files:

**24p files (34 files):**
- `data/naturalis/2step/24p/BGE00514.tsv`
- `data/naturalis/2step/24p/BGE00317.tsv`
- `data/naturalis/2step/24p/BGE00550.tsv`
... and 31 more files in `data/naturalis/2step/24p/` and `data/nhm/2step/24p/`

These files had rows where `sequence_id` was either identical to `Filename` or equal to `Filename + '_merge'`, indicating that the `sequence_id` is the correct identifier.

### Files Requiring Manual Review (14 files)

14 files were identified where the relationship between `Filename` and `sequence_id` does not match Pattern 1. These files were **NOT** modified and require manual review.

**Common pattern in files requiring manual review (Pattern 2):**

Most of these files are in `data/naturalis/2step/6p/` and show a pattern where:
- `Filename`: `BGSNH001-24_r_1.3_s_100_BGSNH001-24` (includes trailing process ID)
- `sequence_id`: `BGSNH001-24_r_1.3_s_100` (excludes trailing process ID)

Example files:
- `data/naturalis/2step/6p/BGE00197.tsv`
- `data/naturalis/2step/6p/BGE00119.tsv`
- `data/naturalis/2step/6p/BGE00513.tsv`
... and 11 more

This pattern suggests that `Filename` preserves the original input filename (with trailing process ID) while `sequence_id` has been normalized. Both columns may serve different purposes for data provenance and traceability.

## Tests

Comprehensive unit tests are provided in `tests/test_fix_filename.py` covering:
- Detection of files matching Pattern 1 (exact match)
- Detection of files matching Pattern 1 (with _merge suffix)
- Correct identification of files not matching Pattern 1
- Correct removal of the `Filename` column
- Dry-run mode functionality
- Data preservation during fixes
- Column order preservation (except for removed column)

Run tests with:
```bash
python -m pytest tests/test_fix_filename.py -v
```

## Examples

### Pattern 1 - Before (exact match case)
```tsv
ambig_basecount	Filename	error	sequence_id	species
2	BGSNL096-23_r_1.3_s_100_BGSNL096-23	None	BGSNL096-23_r_1.3_s_100_BGSNL096-23	Species A
```

### Pattern 1 - Before (_merge suffix case)
```tsv
ambig_basecount	Filename	error	sequence_id	species
2	BSCRO1521-25_r_1.3_s_100_BSCRO1521-25	None	BSCRO1521-25_r_1.3_s_100_BSCRO1521-25	Species A
3	BSCRO1521-25_r_1.3_s_100_BSCRO1521-25	None	BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_merge	Species A
```

### Pattern 1 - After (Filename removed)
```tsv
ambig_basecount	error	sequence_id	species
2	None	BGSNL096-23_r_1.3_s_100_BGSNL096-23	Species A
3	None	BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_merge	Species A
```

### Pattern 2 - Files NOT Modified (trailing process ID difference)
```tsv
# sequence_id is missing the trailing process ID that Filename has
Filename: BGSNH001-24_r_1.3_s_100_BGSNH001-24
sequence_id: BGSNH001-24_r_1.3_s_100
```

## Related Documentation

- `docs/PROCESS_ID_FIX.md` - Similar script for handling `process_id` vs `group_id` columns
- `docs/SEQUENCE_ID_PARSING.md` - Script for parsing and populating columns from `sequence_id` patterns

## Recommendations

For the 14 files with Pattern 2 (not matching Pattern 1), consider:

1. **Investigate the data pipeline**: Understand why the trailing process ID is present in `Filename` but absent in `sequence_id`
2. **Determine data provenance needs**: If `Filename` represents original input filenames, it may be valuable for traceability
3. **Consider normalization**: If the difference is systematic and the trailing process ID is redundant information, consider normalizing `Filename` to match `sequence_id` format
4. **Update metadata documentation**: Document the purpose and relationship between `Filename` and `sequence_id` columns

The script provides detailed output showing examples of violations to help with manual review decisions.
