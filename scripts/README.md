# BGE Skimming Analytics Scripts

This directory contains scripts for processing, validating, and analyzing genome skimming data.

## Available Scripts

### Data Analysis

#### analyze_tsv_coverage.py

Analyzes header coverage patterns across all TSV files in the data folder.

**Usage:**
```bash
python scripts/analyze_tsv_coverage.py [--output-dir DIR]
```

**Description:**

This script analyzes all TSV files and compares their headers against the expected headers defined in `metadata/headers.tsv`. It groups files by their header coverage patterns and generates comprehensive reports including:

- Summary report with all patterns
- Detailed reports for each pattern
- GitHub issue templates for tracking each pattern
- JSON data for programmatic access

**Options:**
- `--output-dir`: Output directory for reports (default: `reports/coverage`)

**Documentation:** See [docs/TSV_COVERAGE_ANALYSIS.md](../docs/TSV_COVERAGE_ANALYSIS.md) for detailed information.

---

#### create_coverage_issues.py

Helper script that generates instructions for creating GitHub issues from coverage analysis results.

**Usage:**
```bash
python scripts/create_coverage_issues.py [--reports-dir DIR] [--output-file FILE]
```

**Options:**
- `--reports-dir`: Coverage reports directory (default: `reports/coverage`)
- `--output-file`: Output file for instructions (default: stdout)

---

### Data Cleaning and Fixes

#### fix_filename_column.py

Handles TSV files with a `Filename` column to identify and remove redundant data where Pattern 1 is detected.

**Usage:**
```bash
python scripts/fix_filename_column.py [--dry-run] [--data-dir DIR]
```

**Description:**

This script scans TSV files in the data directory for a `Filename` column and takes appropriate action:

1. **Remove** the `Filename` column if files match Pattern 1 (sequence_id equals Filename or Filename + '_merge')
2. **Report** files not matching Pattern 1 for manual review

**Pattern 1 Definition:**
Files where all rows satisfy: `sequence_id` == `Filename` OR `sequence_id` == `Filename + '_merge'`

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

**Documentation:** See [docs/FILENAME_FIX.md](../docs/FILENAME_FIX.md) for detailed information.

---

#### fix_process_id_column.py

Handles TSV files with a `process_id` column to ensure consistency with the `group_id` standard.

**Usage:**
```bash
python scripts/fix_process_id_column.py [--dry-run] [--data-dir DIR]
```

**Description:**

This script scans TSV files in the data directory for a `process_id` column and takes appropriate action:

1. **Remove** the `process_id` column if `group_id` exists and all values match
2. **Rename** `process_id` to `group_id` if `group_id` column doesn't exist
3. **Flag** files where `process_id` and `group_id` values don't match for manual review

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

**Exit codes:**
- `0`: Success (all files fixed or no process_id columns found)
- `1`: Manual review required (conflicts or errors detected)

**Documentation:** See [docs/PROCESS_ID_FIX.md](../docs/PROCESS_ID_FIX.md) for detailed information.

---

#### fix_n_aligned_column.py

Renames `n_aligned` column to the standard `n_reads_aligned` column name.

**Usage:**
```bash
python scripts/fix_n_aligned_column.py [--dry-run] [--data-dir DIR]
```

**Description:**

According to the metadata definitions in `metadata/headers.tsv`, the correct column name is `n_reads_aligned`. This script identifies files with an `n_aligned` column and renames it to maintain consistency.

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

**Documentation:** See [docs/N_ALIGNED_FIX.md](../docs/N_ALIGNED_FIX.md) for detailed information.

---

#### remove_backbone_source_column.py

Removes the `backbone_source` column from TSV files where it exists.

**Usage:**
```bash
python scripts/remove_backbone_source_column.py [--dry-run] [--data-dir DIR]
```

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

---

#### remove_negative_controls.py

Removes rows identified as negative controls from TSV files.

**Usage:**
```bash
python scripts/remove_negative_controls.py [--dry-run] [--data-dir DIR]
```

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

---

### Data Parsing and Enhancement

#### parse_sequence_id_columns.py

Parses structured `sequence_id` values to extract and populate `group_id`, `r`, and `s` columns.

**Usage:**
```bash
python scripts/parse_sequence_id_columns.py [--dry-run] [--data-dir DIR]
```

**Description:**

This script identifies files where `sequence_id` follows the pattern `<process_id>_r_<float>_s_<int>[_<process_id>][_fcleaner][_merge]` and extracts the components into separate columns.

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

**Documentation:** See [docs/SEQUENCE_ID_PARSING.md](../docs/SEQUENCE_ID_PARSING.md) for detailed information.

---

#### parse_mge_params_columns.py

Parses `mge_params` column values to extract and populate `r` and `s` columns.

**Usage:**
```bash
python scripts/parse_mge_params_columns.py [--dry-run] [--data-dir DIR]
```

**Description:**

This script identifies files where `mge_params` follows the pattern `r_<float>_s_<int>[_suffix]` and extracts the r and s values into separate columns.

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

**Documentation:** See [docs/MGE_PARAMS_PARSING.md](../docs/MGE_PARAMS_PARSING.md) for detailed information.

---

#### add_fcleaner_merge_columns.py

Adds boolean columns `fcleaner` and `merge` based on suffixes in `sequence_id` values.

**Usage:**
```bash
python scripts/add_fcleaner_merge_columns.py [--dry-run] [--data-dir DIR]
```

**Description:**

This script detects `_fcleaner` and `_merge` suffixes in `sequence_id` values and adds corresponding boolean columns to indicate which data cleaning steps were applied.

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

**Documentation:** See [docs/FCLEANER_MERGE_COLUMNS.md](../docs/FCLEANER_MERGE_COLUMNS.md) for detailed information.

---

### Data Merging

#### merge_6p_data.py

Merges TSV validation files with CSV assembly metrics for the 6p dataset.

**Usage:**
```bash
python scripts/merge_6p_data.py [--tsv-dir DIR] [--csv-dir DIR] [--output-dir DIR] [--dry-run]
```

**Description:**

This script finds matching `BGE00***` TSV and CSV file pairs, performs preprocessing on the CSV files to create a join column, and merges them based on the `sequence_id` column.

- **TSV files:** `data/naturalis/2step/6p/BGE00***.tsv` - Output from barcode_validator
- **CSV files:** `data/naturalis/2step/6p/inputs/BGE00***_MGE-BGE_r1_1.3_1.5_s50_100.csv` - Assembly metrics
- **Output files:** `data/naturalis/2step/6p/BGE00***_merged.tsv` - Merged data

**Options:**
- `--tsv-dir`: Directory containing TSV files (default: `data/naturalis/2step/6p`)
- `--csv-dir`: Directory containing CSV files (default: `data/naturalis/2step/6p/inputs`)
- `--output-dir`: Directory for output files (default: `data/naturalis/2step/6p`)
- `--dry-run`: Show what would be processed without writing files

**Documentation:** See [docs/1step_6p_merge_report.md](../docs/1step_6p_merge_report.md) for detailed information.

---

#### bv_metrics_merger.py

Merges barcode validator outputs with assembly metrics files.

**Usage:**
```bash
python scripts/bv_metrics_merger.py [options]
```

---

#### concat_tsv.py

Concatenates multiple TSV files into a single file.

**Usage:**
```bash
python scripts/concat_tsv.py [options]
```

---

### Utility Scripts

#### fasta-splitter.pl

Perl script for splitting FASTA files.

**Usage:**
```bash
perl scripts/fasta-splitter.pl [options]
```

---

#### concat.sh

Shell script for concatenating files.

**Usage:**
```bash
bash scripts/concat.sh [options]
```

---

## Common Options

Most scripts support the following common options:

- `--dry-run`: Preview changes without modifying files
- `--data-dir DIR`: Specify a custom data directory (default: `data/`)

## Testing

All scripts have corresponding unit tests in the `tests/` directory. Run tests with:

```bash
python -m pytest tests/ -v
```

## Getting Help

For detailed information about any script, see the corresponding documentation file in the `docs/` directory, or run the script with `--help`:

```bash
python scripts/<script_name>.py --help
```
