# Adding fcleaner and merge Boolean Columns

## Problem Statement

Some TSV files in `data/` had sequence_id columns containing `_fcleaner` and/or `_merge` suffixes, referring to two processing steps applied in some branches of the pipeline:
- `_fcleaner`: FASTA cleaner data cleaning step
- `_merge`: Data merging operation

The goal was to make every TSV file have explicit `fcleaner` and `merge` boolean columns that indicate whether these suffixes appear in the sequence_id.

## Solution

### 1. Created new script: `scripts/add_fcleaner_merge_columns.py`

This script:
- Scans all TSV files in the data directory
- Adds `fcleaner` and `merge` boolean columns to every file
- Sets the values based on whether the suffixes appear in the sequence_id

The script can be run with:
```bash
# Dry run (preview changes)
python scripts/add_fcleaner_merge_columns.py --dry-run

# Apply changes
python scripts/add_fcleaner_merge_columns.py
```

### 2. Updated `scripts/parse_sequence_id_columns.py`

Modified the `parse_sequence_id()` function to return fcleaner and merge flags:
- **Before**: `(group_id, r, s)`
- **After**: `(group_id, r, s, fcleaner, merge)`

This change was made to maintain consistency across the codebase and provide a single source of truth for parsing sequence_id patterns.

### 3. Updated `metadata/headers.tsv`

Added two new column definitions:
- `fcleaner` (non-compulsory): Indicates whether FASTA cleaner (fcleaner) data cleaning step was applied
- `merge` (non-compulsory): Indicates whether data merging operation was applied

### 4. Updated all tests

Updated all existing tests in `tests/test_parse_sequence_id.py` to handle the new return format from `parse_sequence_id()`, including assertions for the fcleaner and merge boolean values.

Created comprehensive tests in `tests/test_add_fcleaner_merge_columns.py` covering:
- Suffix detection for all combinations (none, fcleaner only, merge only, both)
- Adding columns to files with different patterns
- Preserving existing data
- Handling edge cases (already has columns, missing sequence_id column)
- Dry-run mode

## Results

### Files Processed
- **Total TSV files**: 168
- **Files with fcleaner suffix**: 45 (all also have merge)
- **Files with merge suffix only**: 2
- **Files with neither suffix**: 121

### Data Statistics
Within individual files, different rows can have different combinations of fcleaner and merge flags. For example, `data/naturalis/2step/24p/BGE00514.tsv` has:
- 570 rows with `fcleaner=False, merge=False`
- 570 rows with `fcleaner=False, merge=True`
- 570 rows with `fcleaner=True, merge=False`
- 569 rows with `fcleaner=True, merge=True`

### Testing
- **Total tests**: 426 (412 existing + 14 new)
- **All tests passing**: ✓

## Examples

### Before
```tsv
sequence_id	group_id	r	s
UNIFI571-24_r_1_s_50	UNIFI571-24	1	50
MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge	MUSBA3189-25	1	50
BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner	BSCRO1521-25	1.3	100
```

### After
```tsv
sequence_id	group_id	r	s	fcleaner	merge
UNIFI571-24_r_1_s_50	UNIFI571-24	1	50	False	False
MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge	MUSBA3189-25	1	50	False	True
BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner	BSCRO1521-25	1.3	100	True	False
```

## Technical Details

### Suffix Detection
The `check_suffixes()` function uses simple string matching:
```python
has_fcleaner = '_fcleaner' in sequence_id
has_merge = '_merge' in sequence_id
```

This is reliable because the suffixes are part of a structured pattern and always appear at the end:
`<process_id>_r_<float>_s_<int>[_<process_id>][_fcleaner][_merge]`

### Column Placement
New columns are added at the end of the TSV files to minimize disruption to existing column order and any downstream processing that might depend on column positions.

### Boolean Representation
Boolean values are represented as strings `"True"` and `"False"` in the TSV files for compatibility with various data processing tools.

## Related Documentation

- `docs/SEQUENCE_ID_PARSING.md` - Documentation for the original sequence_id parsing functionality
- `metadata/headers.tsv` - Complete header definitions including fcleaner and merge
- `tests/test_parse_sequence_id.py` - Tests for sequence_id parsing
- `tests/test_add_fcleaner_merge_columns.py` - Tests for fcleaner/merge column addition
