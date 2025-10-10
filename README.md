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
