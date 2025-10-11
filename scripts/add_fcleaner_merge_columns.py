#!/usr/bin/env python3
"""
Add fcleaner and merge boolean columns to TSV files.

This script adds fcleaner and merge columns to all TSV files in the data directory.
These columns indicate whether the sequence_id contains _fcleaner and/or _merge suffixes.

The sequence_id pattern is:
    <process_id>_r_<float>_s_<int>[_<process_id>][_fcleaner][_merge]

Examples:
- UNIFI571-24_r_1_s_50 -> fcleaner=False, merge=False
- MUSBA3189-25_r_1_s_50_MUSBA3189-25_merge -> fcleaner=False, merge=True
- BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner -> fcleaner=True, merge=False
- BSCRO1521-25_r_1.3_s_100_BSCRO1521-25_fcleaner_merge -> fcleaner=True, merge=True

Usage: python scripts/add_fcleaner_merge_columns.py [--dry-run]
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List


def check_suffixes(sequence_id: str) -> tuple[bool, bool]:
    """
    Check if sequence_id contains _fcleaner and/or _merge suffixes.
    
    Args:
        sequence_id: The sequence_id string to check
        
    Returns:
        Tuple of (has_fcleaner, has_merge) booleans
    """
    has_fcleaner = '_fcleaner' in sequence_id
    has_merge = '_merge' in sequence_id
    return (has_fcleaner, has_merge)


def find_tsv_files(data_dir: Path) -> List[Path]:
    """
    Find all TSV files in the data directory.
    
    Args:
        data_dir: Root data directory to search
        
    Returns:
        List of Path objects for all TSV files
    """
    return sorted(data_dir.glob("**/*.tsv"))


def add_columns_to_file(tsv_file: Path, dry_run: bool = False) -> bool:
    """
    Add fcleaner and merge boolean columns to a TSV file.
    
    Args:
        tsv_file: Path to TSV file
        dry_run: If True, don't actually modify files
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the file using csv.reader to preserve all columns including duplicates
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)
            rows = list(reader)
        
        # Check if columns already exist
        has_fcleaner = 'fcleaner' in header
        has_merge = 'merge' in header
        has_sequence_id = 'sequence_id' in header
        
        # If both columns already exist, skip this file
        if has_fcleaner and has_merge:
            return True
        
        # If sequence_id doesn't exist, we can't process this file
        if not has_sequence_id:
            print(f"Warning: {tsv_file} has no sequence_id column, skipping", file=sys.stderr)
            return True
        
        # Find the index of sequence_id column
        sequence_id_idx = header.index('sequence_id')
        
        # Add new columns at the end (only the ones that are missing)
        columns_to_add = []
        if not has_fcleaner:
            columns_to_add.append('fcleaner')
        if not has_merge:
            columns_to_add.append('merge')
        
        new_header = header + columns_to_add
        
        # Process rows and populate new columns
        new_rows = []
        for row in rows:
            new_row = row.copy()
            seq_id = row[sequence_id_idx] if sequence_id_idx < len(row) else ''
            
            has_fcleaner_suffix, has_merge_suffix = check_suffixes(seq_id)
            
            if not has_fcleaner:
                new_row.append('True' if has_fcleaner_suffix else 'False')
            if not has_merge:
                new_row.append('True' if has_merge_suffix else 'False')
            
            new_rows.append(new_row)
        
        if not dry_run:
            # Write the modified file
            with open(tsv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(new_header)
                writer.writerows(new_rows)
        
        return True
        
    except Exception as e:
        print(f"Error processing {tsv_file}: {e}", file=sys.stderr)
        return False


def main():
    """Main function to add fcleaner and merge columns."""
    parser = argparse.ArgumentParser(
        description='Add fcleaner and merge boolean columns to TSV files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'data',
        help='Data directory to search (default: ../data)'
    )
    args = parser.parse_args()
    
    # Find all TSV files
    print(f"Scanning {args.data_dir} for TSV files...")
    tsv_files = find_tsv_files(args.data_dir)
    
    if not tsv_files:
        print("No TSV files found.")
        return 0
    
    print(f"Found {len(tsv_files)} TSV file(s)\n")
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made\n")
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for tsv_file in tsv_files:
        rel_path = tsv_file.relative_to(args.data_dir.parent)
        
        if args.dry_run:
            print(f"Would process: {rel_path}")
            success_count += 1
        else:
            print(f"Processing: {rel_path}...", end=' ')
            if add_columns_to_file(tsv_file, dry_run=False):
                print("✓")
                success_count += 1
            else:
                print("✗ FAILED")
                error_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    
    if args.dry_run:
        print("\n(Dry run mode - no changes were made)")
    
    return 1 if error_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
