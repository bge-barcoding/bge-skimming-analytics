#!/usr/bin/env python3
"""
Process validation data from last_addition folder.

This script processes all batches in the last_addition folder by:
1. Merging structural and taxon validation TSV files
2. Joining merged TSV with CSV assembly metrics
3. Applying data transformations
4. Copying FASTA files to final locations

Usage: python scripts/process_last_addition.py [--dry-run]
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

import pandas as pd


def find_batches(base_path: Path) -> List[str]:
    """Find all batch IDs in the last_addition folder."""
    taxon_dir = base_path / "BGEE_validation_015_out" / "taxon-validation-outputs"
    batches = set()
    
    if taxon_dir.exists():
        for file in taxon_dir.glob("BGE*_taxonval_out.tsv"):
            batch_id = file.name.split("_")[0]
            batches.add(batch_id)
    
    return sorted(batches)


def merge_validation_files(batch_id: str, base_path: Path, output_dir: Path, dry_run: bool = False) -> Path:
    """
    Step 1: Merge structural and taxon validation TSV files using bv_metrics_merger.py.
    
    Returns path to merged TSV file.
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Step 1: Merging validation files for {batch_id}...")
    
    taxval_file = base_path / "BGEE_validation_015_out" / "taxon-validation-outputs" / f"{batch_id}_taxonval_out.tsv"
    structval_file = base_path / "BGEE_validation_015_out" / "structural-validation-outputs" / f"{batch_id}_structval_out.tsv"
    merged_file = output_dir / f"{batch_id}_merged.tsv"
    
    if not taxval_file.exists():
        raise FileNotFoundError(f"Taxval file not found: {taxval_file}")
    if not structval_file.exists():
        raise FileNotFoundError(f"Structval file not found: {structval_file}")
    
    if dry_run:
        print(f"  Would merge: {taxval_file.name} + {structval_file.name} -> {merged_file.name}")
        return merged_file
    
    # Call bv_metrics_merger.py
    cmd = [
        sys.executable,
        "scripts/bv_metrics_merger.py",
        "-t", str(taxval_file),
        "-s", str(structval_file),
        "-o", str(merged_file)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running bv_metrics_merger.py:")
        print(result.stderr)
        raise RuntimeError(f"Failed to merge validation files for {batch_id}")
    
    print(f"  Merged file created: {merged_file.name}")
    return merged_file


def join_with_csv(batch_id: str, merged_tsv: Path, base_path: Path, output_dir: Path, dry_run: bool = False) -> Path:
    """
    Step 2: Join merged TSV with CSV assembly metrics on Filename column.
    
    Returns path to joined TSV file.
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Step 2: Joining with CSV for {batch_id}...")
    
    csv_file = base_path / "BGEE_validation_015" / f"{batch_id}_BGEE_r1_1.3_1.5_s50_100_combined_stats.csv"
    joined_file = output_dir / f"{batch_id}_joined.tsv"
    
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    if dry_run:
        print(f"  Would join: {merged_tsv.name} + {csv_file.name} -> {joined_file.name}")
        return joined_file
    
    # Read TSV file
    tsv_df = pd.read_csv(merged_tsv, sep='\t', dtype=str, keep_default_na=False)
    print(f"  TSV shape: {tsv_df.shape}")
    
    # Read CSV file
    csv_df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)
    print(f"  CSV shape: {csv_df.shape}")
    
    # Preprocess CSV to create sequence_id column for joining
    def create_join_key(row):
        filename = row['Filename']
        process_id = row.get('ID', '')
        if not process_id:
            return filename
        suffix = '_' + str(process_id)
        if filename.endswith(suffix):
            return filename.rsplit(suffix, 1)[0]
        return filename
    
    csv_df['sequence_id'] = csv_df.apply(create_join_key, axis=1)
    
    # Rename CSV columns to match expected headers
    column_mapping = {
        'n_reads': 'n_reads_in',
        'n_aligned': 'n_reads_aligned',
        'skipped_reads_low_rel': 'n_reads_skipped',
        'length': 'ref_length'
    }
    csv_df = csv_df.rename(columns=column_mapping)
    
    # Check for matches
    tsv_ids = set(tsv_df['sequence_id'])
    csv_ids = set(csv_df['sequence_id'])
    common_ids = tsv_ids & csv_ids
    print(f"  Common sequence_ids: {len(common_ids)} out of {len(tsv_ids)} (TSV) and {len(csv_ids)} (CSV)")
    
    # Remove columns from CSV that already exist in TSV (except sequence_id)
    overlapping_cols = set(csv_df.columns) & set(tsv_df.columns) - {'sequence_id'}
    if overlapping_cols:
        print(f"  Dropping {len(overlapping_cols)} overlapping columns from CSV: {sorted(overlapping_cols)}")
        csv_df = csv_df.drop(columns=list(overlapping_cols))
    
    # Perform left join
    merged_df = pd.merge(
        tsv_df,
        csv_df,
        on='sequence_id',
        how='left',
        suffixes=('', '_csv')
    )
    
    print(f"  Merged shape: {merged_df.shape}")
    
    # Remove redundant columns (Filename and ID if they still exist)
    columns_to_remove = ['Filename', 'ID', 'Filename_csv', 'ID_csv']
    columns_to_drop = [col for col in columns_to_remove if col in merged_df.columns]
    if columns_to_drop:
        print(f"  Removing redundant columns: {columns_to_drop}")
        merged_df = merged_df.drop(columns=columns_to_drop)
    
    # Write output
    merged_df.to_csv(joined_file, sep='\t', index=False)
    print(f"  Joined file created: {joined_file.name}")
    
    return joined_file


def apply_transformations(batch_id: str, input_file: Path, output_file: Path, dry_run: bool = False):
    """
    Step 3: Apply all data transformations to make tests pass.
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Step 3: Applying transformations for {batch_id}...")
    
    if dry_run:
        print(f"  Would transform: {input_file.name} -> {output_file.name}")
        return
    
    # Read the joined TSV
    df = pd.read_csv(input_file, sep='\t', dtype=str, keep_default_na=False)
    print(f"  Initial shape: {df.shape}")
    print(f"  Initial columns: {list(df.columns)[:10]}...")
    
    # Fix n_aligned column if present
    if 'n_aligned' in df.columns and 'n_reads_aligned' not in df.columns:
        print("  Renaming n_aligned -> n_reads_aligned")
        df = df.rename(columns={'n_aligned': 'n_reads_aligned'})
    
    # Fix process_id column - standardize to group_id
    if 'group_id' not in df.columns and 'process_id' in df.columns:
        print("  Renaming process_id -> group_id")
        df = df.rename(columns={'process_id': 'group_id'})
    
    # Parse mge_params to get r and s columns if needed
    if 'r' not in df.columns and 's' not in df.columns and 'mge_params' in df.columns:
        print("  Parsing mge_params to extract r and s")
        pattern = re.compile(r'^r_([0-9.]+)_s_(\d+)(?:_.*)?$')
        
        r_values = []
        s_values = []
        
        for val in df['mge_params']:
            if not val or val in ('None', 'null', ''):
                r_values.append('')
                s_values.append('')
            else:
                match = pattern.match(val)
                if match:
                    r_values.append(match.group(1))
                    s_values.append(match.group(2))
                else:
                    r_values.append('')
                    s_values.append('')
        
        df['r'] = r_values
        df['s'] = s_values
    
    # Parse sequence_id to get r and s if still needed
    if 'r' not in df.columns and 's' not in df.columns and 'sequence_id' in df.columns:
        print("  Parsing sequence_id to extract r and s")
        pattern = re.compile(r'_r_([0-9.]+)_s_(\d+)(?:_|$)')
        
        r_values = []
        s_values = []
        
        for val in df['sequence_id']:
            match = pattern.search(val)
            if match:
                r_values.append(match.group(1))
                s_values.append(match.group(2))
            else:
                r_values.append('')
                s_values.append('')
        
        df['r'] = r_values
        df['s'] = s_values
    
    # Add fcleaner and merge columns
    if 'fcleaner' not in df.columns or 'merge' not in df.columns:
        print("  Adding fcleaner and merge columns")
        
        if 'sequence_id' in df.columns:
            fcleaner_values = []
            merge_values = []
            
            for val in df['sequence_id']:
                has_fcleaner = '_fcleaner' in str(val)
                has_merge = '_merge' in str(val)
                fcleaner_values.append('True' if has_fcleaner else 'False')
                merge_values.append('True' if has_merge else 'False')
            
            if 'fcleaner' not in df.columns:
                df['fcleaner'] = fcleaner_values
            if 'merge' not in df.columns:
                df['merge'] = merge_values
    
    # Remove backbone_source column if present
    if 'backbone_source' in df.columns:
        print("  Removing backbone_source column")
        df = df.drop(columns=['backbone_source'])
    
    # Remove negative controls
    initial_rows = len(df)
    if 'group_id' in df.columns:
        # Remove rows where group_id ends with -NC
        df = df[~df['group_id'].str.endswith('-NC', na=False)]
        
        # Remove rows where error contains '-NC not in BOLD'
        if 'error' in df.columns:
            df = df[~df['error'].str.contains(r'-NC not in BOLD', na=False, regex=True)]
    
    removed_rows = initial_rows - len(df)
    if removed_rows > 0:
        print(f"  Removed {removed_rows} negative control rows")
    
    # Write final output
    print(f"  Final shape: {df.shape}")
    df.to_csv(output_file, sep='\t', index=False)
    print(f"  Transformed file created: {output_file.name}")


def copy_fasta_files(batch_id: str, base_path: Path, dest_dir: Path, dry_run: bool = False):
    """
    Step 4: Copy assemblies and taxonval FASTA files to final locations.
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Step 4: Copying FASTA files for {batch_id}...")
    
    # Copy assemblies FASTA
    assemblies_src = base_path / "BGEE_validation_015" / f"{batch_id}_assemblies.fasta"
    assemblies_dst = dest_dir / f"{batch_id}_assemblies.fasta"
    
    if assemblies_src.exists():
        if dry_run:
            print(f"  Would copy: {assemblies_src.name} -> {assemblies_dst.name}")
        else:
            shutil.copy2(assemblies_src, assemblies_dst)
            print(f"  Copied: {assemblies_dst.name}")
    else:
        print(f"  Warning: Assemblies file not found: {assemblies_src}")
    
    # Copy taxonval FASTA (this is the final output)
    taxonval_src = base_path / "BGEE_validation_015_out" / "taxon-validation-outputs" / f"{batch_id}_taxonval_out.fasta"
    taxonval_dst = dest_dir / f"{batch_id}.fasta"
    
    if taxonval_src.exists():
        if dry_run:
            print(f"  Would copy: {taxonval_src.name} -> {taxonval_dst.name}")
        else:
            shutil.copy2(taxonval_src, taxonval_dst)
            print(f"  Copied: {taxonval_dst.name}")
    else:
        print(f"  Warning: Taxonval FASTA not found: {taxonval_src}")


def process_batch(batch_id: str, base_path: Path, dest_dir: Path, work_dir: Path, dry_run: bool = False):
    """Process a single batch through all steps."""
    print(f"\n{'='*70}")
    print(f"{'[DRY RUN] ' if dry_run else ''}Processing batch: {batch_id}")
    print(f"{'='*70}")
    
    try:
        # Step 1: Merge validation files
        merged_file = merge_validation_files(batch_id, base_path, work_dir, dry_run)
        
        # Step 2: Join with CSV
        joined_file = join_with_csv(batch_id, merged_file, base_path, work_dir, dry_run)
        
        # Step 3: Apply transformations
        final_tsv = dest_dir / f"{batch_id}.tsv"
        apply_transformations(batch_id, joined_file, final_tsv, dry_run)
        
        # Step 4: Copy FASTA files
        copy_fasta_files(batch_id, base_path, dest_dir, dry_run)
        
        print(f"\n✓ Batch {batch_id} processed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error processing batch {batch_id}: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description='Process validation data from last_addition folder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--batch',
        type=str,
        help='Process only a specific batch (e.g., BGE00086)'
    )
    
    args = parser.parse_args()
    
    # Set up paths
    base_path = Path("data/naturalis/2step/24p/last_addition")
    dest_dir = Path("data/naturalis/2step/24p")
    work_dir = Path("/tmp/process_last_addition")
    
    if not args.dry_run:
        work_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate paths
    if not base_path.exists():
        print(f"Error: Base path does not exist: {base_path}")
        return 1
    
    if not dest_dir.exists():
        print(f"Error: Destination directory does not exist: {dest_dir}")
        return 1
    
    # Find batches
    batches = find_batches(base_path)
    
    if not batches:
        print("No batches found in last_addition folder")
        return 1
    
    print(f"Found {len(batches)} batches: {', '.join(batches)}")
    
    # Filter to specific batch if requested
    if args.batch:
        if args.batch in batches:
            batches = [args.batch]
        else:
            print(f"Error: Batch {args.batch} not found")
            return 1
    
    # Process each batch
    for batch_id in batches:
        try:
            process_batch(batch_id, base_path, dest_dir, work_dir, args.dry_run)
        except Exception as e:
            print(f"Failed to process batch {batch_id}: {e}")
            return 1
    
    print(f"\n{'='*70}")
    print(f"{'[DRY RUN] ' if args.dry_run else ''}All batches processed successfully!")
    print(f"{'='*70}")
    
    if not args.dry_run:
        # Clean up work directory
        if work_dir.exists():
            shutil.rmtree(work_dir)
            print(f"\nCleaned up temporary work directory: {work_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
