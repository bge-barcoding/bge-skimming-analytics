# bge-skimming-analytics
Genome skimming assembly and validation analytics for the BGE project. The roadmap for this activity is as follows:

1. The Naturalis and NHM teams aggregate their TSV files out of the [barcode validator](https://github.com/naturalis/barcode_validator)
   in this repo.
2. We define the headings of the TSV files in a format compatible with [frictionless data](https://frictionlessdata.io/). This means
   formulating a JSON file that follows the syntax of [this](https://github.com/bge-barcoding/bge-skimming-analytics/blob/main/package.metadata.template.json)
   example, which is what BOLD uses for their TSV dumps. Our headings are different, but we have their definitions nearly all set up
   thanks to [this](https://github.com/bge-barcoding/bge-skimming-analytics/blob/main/headers.tsv) table by Dan Parsons.
3. We combine the TSVs into a large table and compute the MD5 checksum, which goes into the JSON. We now have a frictionless data
   package that can be [imported into R](https://github.com/frictionlessdata/frictionless-r) to run stats about the genome skimming, e.g.
   for BGE deliverable reporting.
4. We then combine JSON and TSV into an [RO-Crate](https://www.researchobject.org/ro-crate/). For this we follow the profile that
   Eli Chadwick has been [working](https://docs.google.com/spreadsheets/d/1l33cmZC7SYsbD2JhxZ-XmW5MrwW7bdiBg3tQONWUc1w/edit?gid=1705586496#gid=1705586496) on.
5. We upload the RO-Crate to Zenodo and mint a DOI for it. We now have a state-of-the-art FAIR data package. Bonus points for linking
   it to the DOI of a data set on BOLD (a data set is just a container of process IDs with some descriptive text). This way, the analytics
   data is linked to the published data, including specimen photos, collection localities, etc.

## Scripts

### analyze_tsv_coverage.py

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

The analysis found 5 unique coverage patterns across 168 TSV files, ranging from 23.2% to 69.6% coverage.

**Options:**
- `--output-dir`: Output directory for reports (default: `reports/coverage`)

**Documentation:** See [docs/TSV_COVERAGE_ANALYSIS.md](docs/TSV_COVERAGE_ANALYSIS.md) for detailed information.

### fix_filename_column.py

Handles TSV files with a `Filename` column to identify and remove redundant data.

**Usage:**
```bash
python scripts/fix_filename_column.py [--dry-run] [--data-dir DIR]
```

**Description:**

This script scans TSV files in the data directory for a `Filename` column and takes appropriate action:

1. **Remove** the `Filename` column if `sequence_id` exists and all values match (redundant column)
2. **Report** files where `Filename` and `sequence_id` values differ for manual review

When the `Filename` column contains identical values to the `sequence_id` column, it is redundant and can be safely removed. However, when values differ, both columns may serve different purposes (e.g., original filename vs. normalized sequence identifier) and should be reviewed before removal.

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

**Results:**
- Automatically removed `Filename` from 1 file where all values matched `sequence_id`
- Reported 54 files with differing values for manual review

**Documentation:** See [docs/FILENAME_FIX.md](docs/FILENAME_FIX.md) for detailed information.

### fix_process_id_column.py

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

According to the metadata specification in `metadata/headers.tsv`, `group_id` is the standard column name for Process IDs, while `process_id` (with underscore) is not a recognized column. This script ensures data consistency and prevents test failures.

**Options:**
- `--dry-run`: Show what would be done without making changes
- `--data-dir`: Data directory to search (default: `data/`)

**Exit codes:**
- `0`: Success (all files fixed or no process_id columns found)
- `1`: Manual review required (conflicts or errors detected)

**Documentation:** See [docs/PROCESS_ID_FIX.md](docs/PROCESS_ID_FIX.md) for detailed information.

### merge_6p_data.py

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

The CSV files have a `Filename` column with values like `PROCESS-ID_r_1.3_s_100_PROCESS-ID` and a `Process ID` column. The join column is created by stripping the suffix `_PROCESS-ID` from the Filename, which matches the `sequence_id` column in the TSV files.

**Options:**
- `--tsv-dir`: Directory containing TSV files (default: `data/naturalis/2step/6p`)
- `--csv-dir`: Directory containing CSV files (default: `data/naturalis/2step/6p/inputs`)
- `--output-dir`: Directory for output files (default: `data/naturalis/2step/6p`)
- `--dry-run`: Show what would be processed without writing files
