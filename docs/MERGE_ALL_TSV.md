# Merging All TSV Files

## Overview

The `merge_all_tsv.py` script merges all TSV files in the `data/` directory into a single gzip-compressed TSV file with standardized columns and generates frictionless data metadata.

## What It Does

1. **Finds all TSV files** - Recursively searches the `data/` directory for all `.tsv` files (excluding metadata directory)
2. **Collects column union** - Identifies all unique column names across all 177 input files
3. **Merges data** - Combines all files into a single DataFrame with 46 columns (the union of all columns)
4. **Standardizes missing values** - Converts various missing value representations (`None`, `null`, `NaN`, etc.) to proper NA values
5. **Standardizes boolean values** - Ensures boolean columns use `True`/`False` capitalization
6. **Infers data types** - Automatically detects and applies appropriate data types:
   - 21 integer columns
   - 4 number (float) columns
   - 2 boolean columns
   - 19 string columns
7. **Compresses output** - Uses gzip compression (level 9 by default) to dramatically reduce file size
8. **Generates frictionless metadata** - Creates a `datapackage.json` file following the [frictionless data](https://frictionlessdata.io/) specification

## Output Files

### `data/bge-skimming-analytics.tsv.gz`

The gzip-compressed merged TSV file containing all data from 177 individual TSV files:
- **Rows**: 330,456 data rows (plus 1 header row)
- **Columns**: 46 columns (union of all columns from source files)
- **Uncompressed size**: ~288 MB
- **Compressed size**: ~15 MB
- **Compression ratio**: 94.8%

The high compression ratio (94.8%) is achieved because:
- The table is quite sparse (many empty cells)
- The data contains many repetitive patterns
- Text-based TSV format compresses very well with gzip

### `data/datapackage.json`

The frictionless data package metadata file that describes the merged dataset:
- Column names and descriptions (from `metadata/headers.tsv`)
- Data types for each column (inferred from the data)
- Required/optional constraints (from `metadata/headers.tsv`)
- File hash for validation (MD5 of the gzip file)
- Compression metadata (encoding: utf-8, compression: gzip)
- License information (CC-BY-SA-4.0)

## Usage

```bash
# Merge all TSV files
python scripts/merge_all_tsv.py

# Preview what would be merged (dry run)
python scripts/merge_all_tsv.py --dry-run
```

## Working with the Compressed File

The output file is gzip-compressed to stay within GitHub's file size limits. You can work with it in several ways:

### Command Line

```bash
# View the file
zcat data/bge-skimming-analytics.tsv.gz | head

# Count rows
zcat data/bge-skimming-analytics.tsv.gz | wc -l

# Extract specific columns
zcat data/bge-skimming-analytics.tsv.gz | cut -f1,2,3 | head

# Decompress to a file (if needed)
gunzip -c data/bge-skimming-analytics.tsv.gz > bge-skimming-analytics.tsv
```

### Python

```python
import pandas as pd
import gzip

# Read directly from gzip file
with gzip.open('data/bge-skimming-analytics.tsv.gz', 'rt', encoding='utf-8') as f:
    df = pd.read_csv(f, sep='\t')

# Or use pandas built-in compression support
df = pd.read_csv('data/bge-skimming-analytics.tsv.gz', sep='\t', compression='gzip')
```

### R

```r
library(readr)

# Read directly from gzip file
df <- read_tsv("data/bge-skimming-analytics.tsv.gz")
```

## Data Standardization

### Missing Values

Various representations of missing data are standardized:
- `None`, `null`, `NULL`, `nan`, `NaN`, `N/A`, `n/a` → empty string or NA (depending on column type)

### Boolean Values

Boolean columns (`fcleaner`, `merge`) use standard capitalization:
- Input: `true`, `True`, `TRUE`, `yes`, `false`, `False`, etc.
- Output: `True` or `False`

### Data Types

The script infers appropriate data types based on the actual values in each column:

**Integer columns** (21 total):
- `ambig_basecount`, `ambig_full_basecount`, `ambig_original`
- `assembly_params`
- `cleaning_ambig_bases`, `cleaning_removed_at`, `cleaning_removed_human`, `cleaning_removed_outlier`, `cleaning_removed_reference`
- `cov_max`, `cov_min`
- `length`
- `n_reads_aligned`, `n_reads_in`, `n_reads_skipped`
- `nuc_basecount`, `nuc_full_basecount`
- `ref_length`
- `s`, `stop_codons`, `validation_steps`

**Number/Float columns** (4 total):
- `r`
- `cleaning_cov_percent`
- `cov_avg`, `cov_med`

**Boolean columns** (2 total):
- `fcleaner`
- `merge`

**String columns** (19 total):
- All other columns including identifiers, taxonomic names, sequences, etc.

## Column Definitions

All column definitions and descriptions are sourced from `metadata/headers.tsv`. The merged file includes all 46 columns defined in that file.

## Validation

The script includes comprehensive tests in `tests/test_merge_all_tsv.py`:
- Verifies output files exist
- Validates JSON structure
- Checks column completeness
- Verifies data type inference
- Confirms boolean standardization
- Tests constraint marking
- Validates compression effectiveness

Run tests with:
```bash
python -m pytest tests/test_merge_all_tsv.py -v
```

## Frictionless Data Compliance

The generated `datapackage.json` follows the [Tabular Data Resource](https://specs.frictionlessdata.io/tabular-data-resource/) specification:

- **Package metadata**: name, title, description, version, licenses, contributors
- **Resource metadata**: file path, hash (MD5), profile, encoding, compression
- **Schema**: complete field definitions with types, formats, descriptions, and constraints

This makes the dataset compatible with frictionless data tools and enables automatic validation, type checking, and documentation generation.

## GitHub Storage Considerations

**Why compression is necessary:**
- GitHub has a 100 MB file size limit and recommends keeping files under 50 MB
- The uncompressed merged file would be ~288 MB
- With gzip compression, the file is only ~15 MB (94.8% compression)
- The sparse, repetitive nature of the data makes it highly compressible

**Benefits of gzip compression:**
- ✅ Widely supported (all major tools can read gzip files natively)
- ✅ Excellent compression ratio for text data
- ✅ No loss of data (lossless compression)
- ✅ Standard format for distributing large datasets
- ✅ Can be read directly without manual decompression in most tools

## Related Scripts

- `metadata/headers.tsv` - Source of column definitions and constraints
- `metadata/package.metadata.template.json` - Template for frictionless data structure
- `scripts/concat_tsv.py` - Legacy script for merging MGE files (different use case)

## Notes

- The merge preserves all data from source files
- Files with different column sets are handled gracefully (missing columns are added with NA values)
- The script is idempotent - it can be run multiple times with the same result
- The compressed file is suitable for version control and distribution
- GitHub automatically serves gzip files with appropriate Content-Encoding headers when accessed via raw URLs
