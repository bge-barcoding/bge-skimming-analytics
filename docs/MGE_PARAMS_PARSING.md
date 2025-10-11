# MGE Params Column Parsing

## Problem Statement

Some TSV files in the `data` directory had the following pattern:
- No `r` column
- No `s` column
- A `mge_params` column with values following the pattern: `r_<float>_s_<int>[_suffix]`

For example: `r_1.3_s_100` or `r_1.3_s_100_fcleaner` where:
- `1.3` is the r value (MGE parameter)
- `100` is the s value (MGE parameter)
- Optional suffixes include `_fcleaner`, `_merge`, `_fcleaner_merge`, etc.

## Solution

Created a Python script `scripts/parse_mge_params_columns.py` that:

1. Scans all TSV files in the data directory
2. Identifies files missing `r` and `s` columns but having `mge_params` with the expected pattern
3. Parses the `mge_params` column using regex pattern: `^r_([0-9.]+)_s_(\d+)(?:_.*)?$`
4. Extracts and populates two new columns:
   - `r`: The r parameter value (supports both integers and floats)
   - `s`: The s parameter value (integer)
5. Handles partial matches where some rows have empty `mge_params` values (these get empty `r` and `s` values)

## Usage

```bash
# Dry run (show what would be done without making changes)
python scripts/parse_mge_params_columns.py --dry-run

# Apply fixes
python scripts/parse_mge_params_columns.py

# Specify custom data directory
python scripts/parse_mge_params_columns.py --data-dir /path/to/data
```

## Results

### Summary

- **Total files processed**: 44
- **Files with all rows parseable**: 41
- **Files with partial matches**: 3 (some rows had empty `mge_params` values)
- **Files with errors**: 0

### Files Modified

All files are in `data/naturalis/2step/24p/` and `data/nhm/2step/24p/`:

**Naturalis files:**
- BGE00090, BGE00101 through BGE00103, BGE00121
- BGE00141 through BGE00143, BGE00192, BGE00203
- BGE00305, BGE00315, BGE00317, BGE00319, BGE00324
- BGE00425, BGE00429
- BGE00505, BGE00507, BGE00512, BGE00514, BGE00518, BGE00519
- BGE00521 through BGE00525
- BGE00545 through BGE00550
- BGE00926 through BGE00928

**NHM files:**
- WK-3860_BSNHM190.tsv
- XE-4013.tsv
- YB-4226_snpseq01200.tsv
- YB-4227_snpseq01188.tsv
- YB-4228_snpseq01196.tsv
- YE-4306_snpseq01332.tsv
- chiro_demux279.tsv

### Files with Partial Matches

These files had some rows with empty `mge_params` values but were still processed:
- BGE00927.tsv: 2247/2251 rows parseable
- BGE00547.tsv: 2271/2275 rows parseable
- BGE00505.tsv: 2251/2252 rows parseable

### Data Integrity

- Original data preserved in all columns
- New columns added at the end of each file
- Headers correctly updated
- Both integer and decimal r values handled correctly
- Empty `mge_params` values result in empty `r` and `s` values

## Tests

Added comprehensive unit tests in `tests/test_parse_mge_params.py` that verify:
- Parsing of valid patterns with integer and float r values
- Parsing of patterns with various suffixes (_fcleaner, _merge, _fcleaner_merge)
- Handling of invalid patterns
- File identification logic
- File modification logic
- Preservation of existing data
- Handling of unparseable rows

All tests pass successfully.

## Examples

### Before
```tsv
mge_params                      ...
r_1.3_s_100                     ...
r_1.3_s_100_fcleaner            ...
r_1.5_s_50_merge                ...
```

### After
```tsv
mge_params                      ...  r      s
r_1.3_s_100                     ...  1.3    100
r_1.3_s_100_fcleaner            ...  1.3    100
r_1.5_s_50_merge                ...  1.5    50
```

## Related Documentation

- `metadata/headers.tsv` - Expected header definitions (includes r, s, and mge_params)
- `tests/test_tsv_headers.py` - Header validation tests
- `docs/SEQUENCE_ID_PARSING.md` - Similar fix for parsing sequence_id column
- `docs/PROCESS_ID_FIX.md` - Related fix for process_id column renaming
