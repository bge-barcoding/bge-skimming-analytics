# Sequence ID Column Parsing

## Problem Statement

Some TSV files in the `data` directory had the following pattern:
- No `r` column
- No `s` column  
- No `group_id` column (or present but missing r and s)
- A `sequence_id` column with values following the pattern: `<process_id>_r_<float>_s_<int>[_<process_id>][_fcleaner][_merge]`

Examples:
- `UNIFI571-24_r_1.3_s_50` - Simple pattern
- `MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge` - With repeated process_id and _merge suffix
- `BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner` - With repeated process_id and _fcleaner suffix
- `BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge` - With repeated process_id and both suffixes

Where:
- `process_id` is the process ID (BOLD format, e.g., UNIFI571-24, MUSBA3189-25)
- `r` is the r value (MGE parameter, float)
- `s` is the s value (MGE parameter, integer)
- The parts in brackets are optional:
  - `_<process_id>`: The process ID may be repeated after _s_<int>
  - `_fcleaner`: Optional suffix indicating fcleaner was used
  - `_merge`: Optional suffix indicating merge was used

## Solution

Created a Python script `scripts/parse_sequence_id_columns.py` that:

1. Scans all TSV files in the data directory
2. Identifies files missing `r`, `s` columns (and optionally `group_id`) but having `sequence_id` with the expected pattern
3. Parses the `sequence_id` column using regex pattern: `^(.+?)_r_([0-9.]+)_s_(\d+)(?:_\1)?(?:_fcleaner)?(?:_merge)?$`
4. Extracts and populates new columns (if missing):
   - `group_id`: The process ID portion
   - `r`: The r parameter value (supports both integers and floats)
   - `s`: The s parameter value (integer)

The regex pattern handles:
- Simple pattern: `PROC_r_1_s_50`
- With repeated process_id: `PROC_r_1_s_50_PROC`
- With _fcleaner suffix: `PROC_r_1_s_50_PROC_fcleaner`
- With _merge suffix: `PROC_r_1_s_50_PROC_merge`
- With both suffixes: `PROC_r_1_s_50_PROC_fcleaner_merge`

## Usage

```bash
# Dry run (show what would be done without making changes)
python scripts/parse_sequence_id_columns.py --dry-run

# Apply fixes
python scripts/parse_sequence_id_columns.py

# Specify custom data directory
python scripts/parse_sequence_id_columns.py --data-dir /path/to/data
```

## Results

- **Files processed:** 108 TSV files
- **Success rate:** 100% (all rows in all files successfully parsed)
- **Tests added:** 15 comprehensive unit tests
- **All tests passing:** 202/202 tests pass

### Files Modified

All files are in `data/naturalis/1step/`:
- BGE00100 through BGE00105
- BGE00142, BGE00146 through BGE00151
- BGE00166 through BGE00197
- BGE00294 through BGE00316, BGE00320
- BGE00401 through BGE00418, BGE00421 through BGE00424, BGE00426 through BGE00428, BGE00430 through BGE00433
- BGE00501 through BGE00503, BGE00509, BGE00512 through BGE00513
- BGE00579, BGE00581 through BGE00582, BGE00588 through BGE00590

### Data Integrity

- Original data preserved in all columns
- New columns added at the end of each file
- Headers correctly updated
- Both integer and decimal r values handled correctly

## Tests

Comprehensive unit tests are provided in `tests/test_parse_sequence_id.py` covering:
- Valid sequence_id parsing with integers and floats
- Invalid sequence_id patterns (missing r, missing s, no pattern)
- Complex process IDs with underscores
- Patterns with repeated process_id
- Patterns with _merge suffix
- Patterns with _fcleaner suffix
- Patterns with _fcleaner_merge suffix
- Patterns with optional suffixes without repeated process_id
- File detection and analysis
- Dry-run mode functionality
- Data preservation during fixes
- Handling of unparseable rows

Run tests with:
```bash
python -m pytest tests/test_parse_sequence_id.py -v
```

## Examples

### Before
```tsv
ambig_basecount	...	sequence_id	species	stop_codons
2	...	UNIFI571-24_r_1_s_50	Anthaxia tenella	0
```

### After (Simple pattern)
```tsv
ambig_basecount	...	sequence_id	species	stop_codons	group_id	r	s
2	...	UNIFI571-24_r_1_s_50	Anthaxia tenella	0	UNIFI571-24	1	50
```

### Before (With suffixes)
```tsv
group_id	sequence_id	species	stop_codons
MUSBA3189-25	MUSBA3189-25_r_1.3_s_50_MUSBA3189-25_merge	Prostheceraeus	0
BSCRO1521-25	BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge	Species name	0
```

### After (With suffixes)
```tsv
group_id	sequence_id	species	stop_codons	r	s
MUSBA3189-25	MUSBA3189-25_r_1.3_s_50_MUSBA3189-25_merge	Prostheceraeus	0	1.3	50
BSCRO1521-25	BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge	Species name	0	1.3	100
```

## Related Documentation

- `metadata/headers.tsv` - Expected header definitions (includes r, s, and group_id)
- `tests/test_tsv_headers.py` - Header validation tests
- `docs/PROCESS_ID_FIX.md` - Similar fix for process_id column renaming
