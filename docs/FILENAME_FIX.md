# Filename Column Fix

## Problem Statement

Some TSV files in the `data` folder had a column named `Filename` in addition to a `sequence_id` column. Analysis revealed that in many cases, the `sequence_id` column followed specific patterns where the `Filename` was redundant and could be derived from other columns.

The task was to:
1. Identify all TSV files with a `Filename` column
2. Check if they also have a `sequence_id` column
3. Identify files matching known patterns where `Filename` is redundant
4. Remove the `Filename` column from files matching these patterns
5. Report files with other patterns for manual review

## Pattern Definitions

### Pattern 1
Pattern 1 files are those where **all** rows satisfy one of the following conditions:
- `sequence_id` == `Filename` (exact match)
- `sequence_id` == `Filename + '_merge'` (sequence_id has merge suffix)

In Pattern 1 files, the `sequence_id` is the correct identifier and the `Filename` column can be safely removed.

### Pattern 2
Pattern 2 files are those where **all** rows satisfy:
- `Filename` == `sequence_id + '_' + group_id`

In Pattern 2 files, the `Filename` can be reconstructed from `sequence_id` and `group_id` (the process ID), making the `Filename` column redundant.

## Solution

Created a Python script `scripts/fix_filename_column.py` that:

1. Scans all TSV files in the data directory for a `Filename` column
2. For each file with a `Filename` column:
   - Checks if `sequence_id` column exists
   - Checks if `group_id` column exists (for Pattern 2 detection)
   - Analyzes all rows to determine if they match Pattern 1 or Pattern 2
   - If all rows match Pattern 1 or Pattern 2: marks file for automatic fixing (removal of `Filename` column)
   - If any row violates both patterns: marks file for manual review
3. Removes the `Filename` column from files matching Pattern 1 or Pattern 2
4. Reports files not matching either pattern with examples of violations

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
- **55 files** total with a `Filename` column (from previous runs)
- **40 files** matching Pattern 1 (automatically fixed in previous runs)
- **14 files** not matching Pattern 1 (reported for manual review)

Subsequent analysis and fixes:
- **11 files** matching Pattern 2 (automatically fixed in this update)
- **3 files** still requiring manual review

### Files Fixed in This Update (Pattern 2)

11 files had their `Filename` column removed because they matched Pattern 2 (all rows had `Filename` = `sequence_id` + `_` + `group_id`):

1. `data/naturalis/2step/6p/BGE00197.tsv`
2. `data/naturalis/2step/6p/BGE00119.tsv`
3. `data/naturalis/2step/6p/BGE00513.tsv`
4. `data/naturalis/2step/6p/BGE00433.tsv`
5. `data/naturalis/2step/6p/BGE00581.tsv`
6. `data/naturalis/2step/6p/BGE00503.tsv`
7. `data/naturalis/2step/6p/BGE00195.tsv`
8. `data/naturalis/2step/6p/BGE00509.tsv`
9. `data/naturalis/2step/6p/BGE00579.tsv`
10. `data/naturalis/2step/6p/BGE00304.tsv`
11. `data/naturalis/2step/6p/BGE00582.tsv`

### Fixed Files (Pattern 1)

40 files were automatically fixed in previous runs.

The `Filename` column was automatically removed from 40 files:

**24p files (34 files):**
- `data/naturalis/2step/24p/BGE00514.tsv`
- `data/naturalis/2step/24p/BGE00317.tsv`
- `data/naturalis/2step/24p/BGE00550.tsv`
... and 31 more files in `data/naturalis/2step/24p/` and `data/nhm/2step/24p/`

These files had rows where `sequence_id` was either identical to `Filename` or equal to `Filename + '_merge'`, indicating that the `sequence_id` is the correct identifier.

### Files Requiring Manual Review (3 files)

3 files were identified where the relationship between `Filename` and `sequence_id` does not consistently match Pattern 1 or Pattern 2. These files were **NOT** modified and require manual review.

**Files with mixed patterns:**

1. `data/naturalis/2step/24p/BGE00927.tsv` (2,251 rows, 4 with empty Filename)
2. `data/naturalis/2step/24p/BGE00547.tsv` (2,275 rows, 4 with empty Filename)
3. `data/naturalis/2step/24p/BGE00505.tsv` (2,252 rows, 1 with empty Filename)

**Pattern in files requiring manual review:**

Most rows in these files follow Pattern 1:
- `Filename`: `BGEGR2084-25_r_1.3_s_100_BGEGR2084-25` (equals sequence_id)
- `sequence_id`: `BGEGR2084-25_r_1.3_s_100_BGEGR2084-25` (exact match)

However, some rows have empty `Filename` values while `sequence_id` is populated (e.g., `BGEGR2105-25_r_1.5_s_100_BGEGR2105-25`).

This mixed pattern suggests incomplete data or rows that failed certain validation steps. The empty Filename values prevent automatic removal of the column.

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

### Pattern 2 - Before (Filename = sequence_id + '_' + group_id)
```tsv
sequence_id	Filename	group_id	species
BGENL2946-24_r_1.3_s_100	BGENL2946-24_r_1.3_s_100_BGENL2946-24	BGENL2946-24	Species A
BGENL2946-24_r_1.3_s_50	BGENL2946-24_r_1.3_s_50_BGENL2946-24	BGENL2946-24	Species A
```

### Pattern 2 - After (Filename removed)
```tsv
sequence_id	group_id	species
BGENL2946-24_r_1.3_s_100	BGENL2946-24	Species A
BGENL2946-24_r_1.3_s_50	BGENL2946-24	Species A
```

### Mixed Pattern - Files NOT Modified (empty Filename values)
```tsv
# Most rows follow Pattern 1, but some have empty Filename
Row 1: Filename='BGEGR2084-25_r_1.3_s_100_BGEGR2084-25', sequence_id='BGEGR2084-25_r_1.3_s_100_BGEGR2084-25'  (Match)
Row 512: Filename='', sequence_id='BGEGR2105-25_r_1.5_s_100_BGEGR2105-25'  (Violation - empty Filename)
```

## Related Documentation

- `docs/PROCESS_ID_FIX.md` - Similar script for handling `process_id` vs `group_id` columns
- `docs/SEQUENCE_ID_PARSING.md` - Script for parsing and populating columns from `sequence_id` patterns

## Recommendations

For the 3 files with mixed patterns (not matching Pattern 1 or Pattern 2 consistently), consider:

1. **Investigate empty Filename values**: Understand why some rows have empty `Filename` values while having populated `sequence_id` values
2. **Check data pipeline**: Determine if empty Filename values indicate:
   - Rows that failed certain validation steps
   - Merged sequences that don't have original filenames
   - Data processing artifacts
3. **Options for handling**:
   - If empty values are expected for certain row types: Consider keeping the Filename column
   - If empty values represent missing data: Fill in the values and then remove the column
   - If the Filename column is no longer needed: Manually remove it after investigation
4. **Update metadata documentation**: Document the purpose and relationship between `Filename` and `sequence_id` columns

The script provides detailed output showing examples of violations to help with manual review decisions.
