# BOLD container data

This folder contains TSV data from the BOLD workbench container for BGE. From among those files, the following
is of interest:

- [lab](lab.tsv): Joining on the `Process ID` column provides the `Sample ID`, which is of interest to link
  validation results from [the data folder](../data) to the metadata provided here. The `Process ID` is represented
  in the validation file structure as the first word of the FASTA definition line and the `group_id` in the
  validation TSV files.
- [collection_data](collection_data.tsv): Joining on the `Sample ID` column provides the collection date in
  dd-Mmm-yyyy format, which is of interest when assessing whether the age of specimens affects sequencing success.
- [voucher](voucher.tsv): Joining on the `Sample ID` column provides the `Institution Storing`, which is of interest
  to know the source of the specimens.
- [taxonomy](taxonomy.tsv): Joining on the `Sample ID` column provides the taxonomic lineage for each specimen at 
  the levels of `Phylum`, `Class`, `Order`, `Family`, `Subfamily`, `Tribe`, `Genus`, `Species`, `Subspecies`. Lower
  levels may be empty if not identified to that level.