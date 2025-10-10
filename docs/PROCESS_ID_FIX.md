# Process ID Column Fix

## Problem Statement

Some TSV files in the data folder may have a column `process_id` (with underscore). The presence of this column causes unit tests to fail because `process_id` is not defined in `metadata/headers.tsv`. The standard column name according to the metadata specification is `group_id`.

## Solution

Created a Python script `scripts/fix_process_id_column.py` that:

1. Scans all TSV files in the data directory for a `process_id` column
2. Takes appropriate action based on the situation:
   - **Remove**: If `group_id` exists and all values match, remove the `process_id` column
   - **Rename**: If `group_id` doesn't exist, rename `process_id` to `group_id`
   - **Flag**: If values don't match, flag the file for manual review

## Usage

```bash
# Dry run (show what would be done without making changes)
python scripts/fix_process_id_column.py --dry-run

# Apply fixes
python scripts/fix_process_id_column.py

# Specify custom data directory
python scripts/fix_process_id_column.py --data-dir /path/to/data
```

## Current Status

As of the implementation date:
- No TSV files in the repository currently have a `process_id` column
- All 177 tests pass
- The solution is proactive and ready for future data imports

## Metadata Specification

According to `metadata/headers.tsv`:
- `group_id` (line 20): "i.e. Process ID" - This is the standard column name
- `processid` (line 40): "Process ID (alternative column name for ID)" - lowercase, no underscore
- `process_id` (with underscore): Not defined, would cause test failures

## Tests

Comprehensive unit tests are provided in `tests/test_fix_process_id.py` covering:
- Detection of files requiring removal, rename, or conflict flagging
- Correct removal of the process_id column
- Correct renaming to group_id
- Dry-run mode functionality
- Data preservation during fixes
- Edge cases with multiple columns and special characters

Run tests with:
```bash
python -m pytest tests/test_fix_process_id.py -v
```
