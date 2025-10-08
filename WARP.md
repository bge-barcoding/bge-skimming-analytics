# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This repository contains genome skimming assembly and validation analytics for the BGE (Biodiversity Genomics Europe) project. The primary workflow aggregates TSV files from the barcode validator, formats them as frictionless data packages, and creates FAIR research objects (RO-Crate) for publication.

## Architecture & Data Flow

The project follows a 5-stage pipeline:

1. **Data Aggregation**: Naturalis and NHM teams aggregate TSV files from the barcode_validator
2. **Metadata Definition**: Headers are defined using frictionless data format with JSON schema
3. **Data Combination**: TSVs are merged into large tables with MD5 checksums
4. **RO-Crate Creation**: JSON and TSV are packaged into Research Object Crates
5. **Publication**: RO-Crates are uploaded to Zenodo with DOI minting

### Key Components

- **`package.metadata.template.json`**: Frictionless data package template following BOLD TSV dump format
- **`headers.tsv`**: Column definitions for barcode validator TSV output
- **`scripts/bv_metrics_merger.py`**: Core script for merging taxval and structval TSV files
- **`scripts/concat_tsv.py`**: MGE TSV file concatenation with sequence ID handling
- **`scripts/concat.sh`**: Shell script for FASTA and TSV concatenation

### Data Organization

- `/data/naturalis/`: Contains BGE specimen TSV files from Naturalis team
- `/data/nhm/`: Contains NHM workflow documentation
- `/scripts/`: Contains all executable Python and shell scripts
- Root level contains templates and documentation

## Common Development Commands

### Running TSV Merger
```bash
# Merge taxval and structval files
python scripts/bv_metrics_merger.py -t taxval.tsv -s structval.tsv -o merged.tsv

# Use custom key column
python scripts/bv_metrics_merger.py -t taxval.tsv -s structval.tsv -o merged.tsv --key ID

# Verbose mode with conflicts report
python scripts/bv_metrics_merger.py -t taxval.tsv -s structval.tsv -o merged.tsv -v
```

### Concatenating MGE Files
```bash
# Process MGE TSV files in directory
python scripts/concat_tsv.py -i input_directory/ -o concatenated.tsv

# Dry run for validation
python scripts/concat_tsv.py -i input_directory/ -o output.tsv --dry-run
```

### NHM Workflow
```bash
# Run complete concatenation workflow (FASTA + TSV)
# Note: Run this from the data/nhm/ directory where the input files are located
cd data/nhm/
bash ../../scripts/concat.sh
```

## Development Environment

### Dependencies
The scripts require:
- Python 3.x
- pandas
- pathlib (standard library)
- argparse (standard library)

### Installing Dependencies
```bash
pip install pandas
```

## Data Processing Rules

### TSV Merger Logic
1. **Dataset column**: Always combine paths as "structval; taxval"
2. **Missing columns**: Added to merged TSV with empty values
3. **Null replacement**: Real data takes precedence over null/None values
4. **Conflicts**: Structval values chosen over taxval when both have different non-null data

### MGE File Processing
1. **Sequence ID modification**: 
   - Files starting with `mge_fastp_` get `_fastp` suffix
   - Files starting with `mge_standard_` get `_standard` suffix
2. **Column alignment**: Missing columns filled with 'None' values
3. **Required columns**: Must contain sequence_id, error, ambig_full_basecount, ambig_basecount, stop_codons, nuc_basecount, identification, obs_taxon

## Frictionless Data Schema

The project follows frictionless data standards with:
- **Profile**: "data-package" at package level, "tabular-data-resource" at resource level  
- **Licensing**: CC-BY-SA-4.0 Creative Commons license
- **Field definitions**: Comprehensive schema covering BOLD-compatible fields
- **Data types**: Strings, integers, dates (%d-%b-%Y format), geopoints, URIs

## Integration Points

### Barcode Validator Integration
- Consumes TSV outputs from [naturalis/barcode_validator](https://github.com/naturalis/barcode_validator)
- Processes both taxonomic validation (`taxval`) and structural validation (`structval`) results
- Handles validation workflow via GitHub PR system

### External Systems
- **BOLD Systems**: Process ID and specimen data integration
- **Zenodo**: Final RO-Crate publication endpoint  
- **Frictionless Data**: Package format compliance
- **RO-Crate**: Research object encapsulation following established profiles

## File Naming Conventions

- BGE specimen files: `BGE[0-9]+_MGE-BGE_r1_1.3_1.5_s50_100.fasta.tsv`
- MGE output files: `mge_{fastp|standard}_*_nocontam.{fasta|tsv}`
- Concatenated outputs: `concatenated_untriaged.{fasta|tsv}`