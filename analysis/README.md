# BGE Skimming Analytics - Analysis

This directory contains RMarkdown documents for analyzing the BGE skimming analytics data.

## Available Analyses

### bold_metadata_analysis.Rmd

An RMarkdown document that demonstrates how to:

1. Read the compressed, frictionless BGE skimming analytics data (`data/bge-skimming-analytics.tsv.gz`)
2. Join it with BOLD metadata files to enrich the dataset:
   - `lab.tsv`: Links Process ID to Sample ID
   - `collection_data.tsv`: Provides collection dates
   - `voucher.tsv`: Provides institution information
   - `taxonomy.tsv`: Provides taxonomic lineage (Phylum through Subspecies)

The document includes:
- Step-by-step joins with BOLD metadata
- Data coverage statistics
- Example visualizations (collection dates, taxonomic distribution, institution distribution)
- Option to export enriched data

### institution_sequencing_success.Rmd

An RMarkdown document that analyzes COI-5P sequencing success rates by institution:

1. Reads `metadata/bold/lab.tsv` directly
2. Groups data by the `Institution` column
3. Calculates for each institution:
   - **Registered specimens**: Any data in `COI-5P Seq. Length` column (indicates specimen was registered for COI-5P sequencing)
   - **Successfully sequenced**: `COI-5P Seq. Length` is not `0[n]` (indicates sequence was recovered and uploaded to BOLD)

The document includes:
- Summary statistics across 97 institutions (90,453 total registered specimens, 40.4% overall success rate)
- Stacked bar chart showing successful vs. failed sequencing for all institutions (ordered by total registered)
- Top 15 institutions chart with success rate percentages
- Detailed statistics table with success rates
- Distribution histogram of success rates across institutions

## Requirements

To run these analyses, you need R with the following packages:

```r
install.packages(c("readr", "dplyr", "ggplot2", "knitr", "rmarkdown", "tidyr"))
```

## Usage

### Render RMarkdown to HTML

From the repository root:

```bash
# Render the BOLD metadata analysis
Rscript -e "rmarkdown::render('analysis/bold_metadata_analysis.Rmd')"

# Render the institution sequencing success analysis
Rscript -e "rmarkdown::render('analysis/institution_sequencing_success.Rmd')"
```

This will create HTML files in the `analysis/` directory.

### Interactive Use in RStudio

1. Open an RMarkdown file (e.g., `analysis/bold_metadata_analysis.Rmd` or `analysis/institution_sequencing_success.Rmd`) in RStudio
2. Click "Knit" to render the document
3. Or run code chunks interactively

## Data Sources

- **Main Data**: `data/bge-skimming-analytics.tsv.gz` - Merged and compressed validation results
- **BOLD Metadata**: `metadata/bold/` - TSV files from BOLD workbench container

See also:
- [BOLD Metadata README](../metadata/bold/README.md)
- [Merged TSV Documentation](../docs/MERGE_ALL_TSV.md)

## Join Strategy

The joins follow this sequence:

1. **Analytics → Lab**: Join on `group_id` = `Process ID` to get `Sample ID`
2. **Lab → Collection**: Join on `Sample ID` to get collection date
3. **Lab → Voucher**: Join on `Sample ID` to get institution storing
4. **Lab → Taxonomy**: Join on `Sample ID` to get taxonomic lineage

All joins are left joins to preserve all rows from the analytics data.
