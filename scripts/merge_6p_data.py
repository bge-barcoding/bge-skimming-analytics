#!/usr/bin/env python3
"""
Merge TSV and CSV files from 6p validation data.

This script finds matching BGE00*** TSV and CSV files, performs preprocessing
on the CSV files to create a join column, and merges them based on sequence_id.

TSV files: data/naturalis/1step/6p/BGE00***.tsv
CSV files: data/naturalis/1step/6p/BGE00***_MGE-BGE_r1_1.3_1.5_s50_100.csv

The CSV files have a 'Filename' column with values like "PROCESS-ID_r_1.3_s_100_PROCESS-ID"
and a 'Process ID' column. The join column is created by stripping the suffix "_PROCESS-ID"
from the Filename, which matches the 'sequence_id' column in the TSV files.

Output files: data/naturalis/1step/6p/BGE00***_merged.tsv

Usage: python merge_6p_data.py
"""

import argparse
import csv
import glob
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

import pandas as pd


def find_matching_files(tsv_dir: str, csv_dir: str) -> List[Tuple[str, str, str]]:
    """
    Find matching TSV and CSV files based on BGE numbers.
    
    Args:
        tsv_dir: Directory containing TSV files
        csv_dir: Directory containing CSV files
    
    Returns:
        List of tuples (bge_number, tsv_path, csv_path)
    """
    # Find TSV files
    tsv_pattern = os.path.join(tsv_dir, "BGE*.tsv")
    tsv_files = glob.glob(tsv_pattern)
    
    # Find CSV files
    csv_pattern = os.path.join(csv_dir, "BGE*_MGE-BGE_r1_1.3_1.5_s50_100.csv")
    csv_files = glob.glob(csv_pattern)
    
    # Extract BGE numbers
    tsv_dict = {}
    for tsv_file in tsv_files:
        match = re.search(r'BGE(\d+)\.tsv', os.path.basename(tsv_file))
        if match:
            tsv_dict[match.group(1)] = tsv_file
    
    csv_dict = {}
    for csv_file in csv_files:
        match = re.search(r'BGE(\d+)_MGE', os.path.basename(csv_file))
        if match:
            csv_dict[match.group(1)] = csv_file
    
    # Find matches
    matching_numbers = set(tsv_dict.keys()) & set(csv_dict.keys())
    
    matches = []
    for bge_num in sorted(matching_numbers):
        matches.append((bge_num, tsv_dict[bge_num], csv_dict[bge_num]))
    
    return matches


def preprocess_csv(csv_df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess CSV file to create a join column.
    
    The 'Filename' column contains values like "PROCESS-ID_r_1.3_s_100_PROCESS-ID"
    and the 'Process ID' column contains "PROCESS-ID".
    We strip the suffix "_PROCESS-ID" from Filename to create the join column.
    
    Also renames columns to match metadata/headers.tsv:
    - n_reads -> n_reads_in
    - n_aligned -> n_reads_aligned
    - skipped_reads_low_rel -> n_reads_skipped
    - length -> ref_length
    
    Args:
        csv_df: DataFrame from CSV file
    
    Returns:
        DataFrame with added 'sequence_id' column for joining and renamed columns
    """
    # Create a copy to avoid modifying the original
    df = csv_df.copy()
    
    # Create join column by stripping the suffix "_<Process ID>" from Filename
    def create_join_key(row):
        filename = row['Filename']
        process_id = row['Process ID']
        # Strip the suffix "_<process_id>" from the end of filename
        suffix = '_' + str(process_id)
        if filename.endswith(suffix):
            return filename.rsplit(suffix, 1)[0]
        return filename
    
    df['sequence_id'] = df.apply(create_join_key, axis=1)
    
    # Rename columns to match expected headers
    column_mapping = {
        'n_reads': 'n_reads_in',
        'n_aligned': 'n_reads_aligned',
        'skipped_reads_low_rel': 'n_reads_skipped',
        'length': 'ref_length'
    }
    df = df.rename(columns=column_mapping)
    
    return df


def merge_files(tsv_path: str, csv_path: str, output_path: str) -> pd.DataFrame:
    """
    Merge a TSV and CSV file pair.
    
    Args:
        tsv_path: Path to TSV file
        csv_path: Path to CSV file
        output_path: Path for output merged TSV file
    
    Returns:
        Merged DataFrame
    """
    print(f"Processing: {os.path.basename(tsv_path)} + {os.path.basename(csv_path)}")
    
    # Read TSV file
    print(f"  Reading {tsv_path}...")
    # Use csv module to detect duplicate columns and handle them
    import csv
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)
        # Check for duplicates and deduplicate by keeping only unique headers
        seen = {}
        unique_headers = []
        cols_to_keep = []
        for i, header in enumerate(headers):
            if header not in seen:
                seen[header] = i
                unique_headers.append(header)
                cols_to_keep.append(i)
            else:
                print(f"  Warning: Duplicate column '{header}' found at positions {seen[header]} and {i}, keeping first occurrence")
        
        # Read the rest of the data with only unique columns
        rows = []
        for row in reader:
            filtered_row = [row[i] for i in cols_to_keep if i < len(row)]
            rows.append(filtered_row)
    
    tsv_df = pd.DataFrame(rows, columns=unique_headers)
    # Convert all to string type
    for col in tsv_df.columns:
        tsv_df[col] = tsv_df[col].astype(str).replace('nan', '')
    
    print(f"  TSV shape: {tsv_df.shape}")
    
    # Read CSV file
    print(f"  Reading {csv_path}...")
    csv_df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    print(f"  CSV shape: {csv_df.shape}")
    
    # Preprocess CSV to create join column
    print(f"  Preprocessing CSV...")
    csv_processed = preprocess_csv(csv_df)
    
    # Check for sequence_id matches
    tsv_ids = set(tsv_df['sequence_id'])
    csv_ids = set(csv_processed['sequence_id'])
    common_ids = tsv_ids & csv_ids
    print(f"  Common sequence_ids: {len(common_ids)} out of {len(tsv_ids)} (TSV) and {len(csv_ids)} (CSV)")
    
    # Perform merge
    print(f"  Merging files...")
    merged_df = pd.merge(
        tsv_df,
        csv_processed,
        on='sequence_id',
        how='left',
        suffixes=('', '_csv')
    )
    
    print(f"  Merged shape: {merged_df.shape}")
    
    # Remove redundant columns (Filename and Process ID)
    columns_to_remove = ['Filename', 'Process ID']
    columns_to_drop = [col for col in columns_to_remove if col in merged_df.columns]
    if columns_to_drop:
        print(f"  Removing redundant columns: {columns_to_drop}")
        merged_df = merged_df.drop(columns=columns_to_drop)
    
    # Write output
    print(f"  Writing to {output_path}...")
    merged_df.to_csv(output_path, sep='\t', index=False)
    
    print(f"  Merge completed!")
    print()
    
    return merged_df


def main():
    """Main function to run the merger pipeline."""
    parser = argparse.ArgumentParser(
        description='Merge TSV and CSV files from 6p validation data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--tsv-dir',
        default='data/naturalis/1step/6p',
        help='Directory containing TSV files (default: data/naturalis/1step/6p)'
    )
    parser.add_argument(
        '--csv-dir',
        default='data/naturalis/1step/6p',
        help='Directory containing CSV files (default: data/naturalis/1step/6p)'
    )
    parser.add_argument(
        '--output-dir',
        default='data/naturalis/1step/6p',
        help='Directory for output files (default: data/naturalis/1step/6p)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only show what would be processed without writing files'
    )
    
    args = parser.parse_args()
    
    # Validate directories
    if not os.path.isdir(args.tsv_dir):
        print(f"Error: TSV directory does not exist: {args.tsv_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isdir(args.csv_dir):
        print(f"Error: CSV directory does not exist: {args.csv_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find matching files
    print(f"Searching for matching files...")
    matches = find_matching_files(args.tsv_dir, args.csv_dir)
    
    if not matches:
        print("Error: No matching files found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(matches)} matching file pairs:")
    for bge_num, tsv_path, csv_path in matches:
        print(f"  BGE{bge_num}: {os.path.basename(tsv_path)} + {os.path.basename(csv_path)}")
    print()
    
    if args.dry_run:
        print("Dry run completed, no files written")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process each pair
    for bge_num, tsv_path, csv_path in matches:
        output_path = os.path.join(args.output_dir, f"BGE{bge_num}_merged.tsv")
        try:
            merge_files(tsv_path, csv_path, output_path)
        except Exception as e:
            print(f"Error processing BGE{bge_num}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    print(f"All merges completed successfully!")
    print(f"Output files written to: {args.output_dir}")


if __name__ == "__main__":
    main()
