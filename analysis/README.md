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

### assembly_parameter_analysis.Rmd

An RMarkdown document that analyzes how assembly parameters affect sequence quality metrics:

**Independent Variables (Assembly Parameters):**
- `r`: MGE parameter r value (float)
- `s`: MGE parameter s value (integer)
- `fcleaner`: Whether FASTA cleaner was applied (boolean)
- `merge`: Whether data merging was applied (boolean)

**Dependent Variables (Sequence Quality Metrics):**
- `nuc_full_basecount`: Total number of nucleotide bases in the full sequence
- `ambig_full_basecount`: Total number of ambiguous bases in the full sequence
- `stop_codons`: Number of stop codons detected

The document includes:
- Summary statistics for each parameter combination
- Boxplots showing the effect of each parameter on quality metrics
- Interaction plots showing how parameters work together
- ANOVA and t-test results for statistical significance
- Identification of best parameter combinations based on composite quality scores
- Key findings about parameter effects on sequence quality

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

### taxonomic_success_analysis.Rmd

An RMarkdown document that examines genome skimming performance across taxonomic groups:

**Analysis Scope:**
- Aggregates data at the level of Linnean **Orders**
- Only includes Orders with **at least 5 specimens**
- Only analyzes specimens whose process ID (group_id) occurs in the aggregated data

**Success Criteria:**
A specimen is successful if ANY assembly attempt meets ALL of:
- `nuc_basecount >= 500` (barcode region ≥ 500 bp)
- `ambig_full_basecount = 0` (no ambiguous bases in full sequence)
- `stop_codons = 0` (no stop codons detected)

**Key Analyses:**
- Specimen-level success rates aggregated by taxonomic Order
- Chi-square test to determine if success rate is independent of Order
- Cramér's V effect size calculation
- Visualization of success rates across Orders
- Identification of top and bottom performing Orders

The document includes:
- Bar plot of success rates by Order
- Distribution histogram of success rates
- Sample size vs success rate scatter plot
- Statistical tests for taxonomic signal
- Summary of top/bottom performing Orders

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

# Render the assembly parameter analysis
Rscript -e "rmarkdown::render('analysis/assembly_parameter_analysis.Rmd')"

# Render the institution sequencing success analysis
Rscript -e "rmarkdown::render('analysis/institution_sequencing_success.Rmd')"

# Render the taxonomic success analysis
Rscript -e "rmarkdown::render('analysis/taxonomic_success_analysis.Rmd')"
```

This will create HTML files in the `analysis/` directory.

### Interactive Use in RStudio

1. Open an RMarkdown file (e.g., `analysis/bold_metadata_analysis.Rmd`, `analysis/assembly_parameter_analysis.Rmd`, `analysis/institution_sequencing_success.Rmd`, or `analysis/taxonomic_success_analysis.Rmd`) in RStudio
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
