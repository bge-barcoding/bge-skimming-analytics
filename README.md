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
