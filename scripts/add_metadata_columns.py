#!/usr/bin/env python3
"""
Add metadata columns to TSV files based on directory structure.

This script adds three metadata columns to all TSV files in the data directory:
- inst: Institute that processed the data (based on naturalis/nhm directory)
- validation_steps: Number of validation steps (based on 1step/2step directory)
- assembly_params: Number of assembly parameters (based on 6p/24p directory)

Usage: python scripts/add_metadata_columns.py [--dry-run]
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def extract_metadata_from_path(tsv_file: Path, data_dir: Path) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """
    Extract metadata values from file path.
    
    Args:
        tsv_file: Path to TSV file
        data_dir: Root data directory
        
    Returns:
        Tuple of (inst, validation_steps, assembly_params)
        - inst: "Naturalis Biodiversity Center" or "Natural History Museum" or None
        - validation_steps: 1 or 2 or None
        - assembly_params: 6 or 24 or None
    """
    # Get the relative path from data directory
    try:
        rel_path = tsv_file.relative_to(data_dir)
    except ValueError:
        return (None, None, None)
    
    parts = rel_path.parts
    
    # Extract institute from first directory level
    inst = None
    if len(parts) >= 1:
        if parts[0] == 'naturalis':
            inst = 'Naturalis Biodiversity Center'
        elif parts[0] == 'nhm':
            inst = 'Natural History Museum'
    
    # Extract validation steps from second directory level
    validation_steps = None
    if len(parts) >= 2:
        if parts[1] == '1step':
            validation_steps = 1
        elif parts[1] == '2step':
            validation_steps = 2
    
    # Extract assembly params from third directory level
    assembly_params = None
    if len(parts) >= 3:
        if parts[2] == '6p':
            assembly_params = 6
        elif parts[2] == '24p':
            assembly_params = 24
    
    return (inst, validation_steps, assembly_params)


def find_tsv_files(data_dir: Path) -> List[Path]:
    """
    Find all TSV files in the data directory.
    
    Args:
        data_dir: Root data directory to search
        
    Returns:
        List of Path objects for all TSV files
    """
    return sorted(data_dir.glob("**/*.tsv"))


def add_columns_to_file(tsv_file: Path, data_dir: Path, dry_run: bool = False) -> bool:
    """
    Add metadata columns to a TSV file based on its directory path.
    
    Args:
        tsv_file: Path to TSV file
        data_dir: Root data directory
        dry_run: If True, don't actually modify files
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Extract metadata from path
        inst, validation_steps, assembly_params = extract_metadata_from_path(tsv_file, data_dir)
        
        # Read the file
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)
            rows = list(reader)
        
        # Check which columns already exist
        has_inst = 'inst' in header
        has_validation_steps = 'validation_steps' in header
        has_assembly_params = 'assembly_params' in header
        
        # If all columns already exist, skip this file
        if has_inst and has_validation_steps and has_assembly_params:
            return True
        
        # Determine which columns to add
        columns_to_add = []
        values_to_add = []
        
        if not has_inst:
            columns_to_add.append('inst')
            values_to_add.append(inst if inst else '')
        
        if not has_validation_steps:
            columns_to_add.append('validation_steps')
            values_to_add.append(str(validation_steps) if validation_steps is not None else '')
        
        if not has_assembly_params:
            columns_to_add.append('assembly_params')
            values_to_add.append(str(assembly_params) if assembly_params is not None else '')
        
        # If no columns to add, skip
        if not columns_to_add:
            return True
        
        # Add new columns to header
        new_header = header + columns_to_add
        
        # Process rows and add values for new columns
        new_rows = []
        for row in rows:
            new_row = row.copy()
            new_row.extend(values_to_add)
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
    """Main function to add metadata columns."""
    parser = argparse.ArgumentParser(
        description='Add metadata columns to TSV files based on directory structure'
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
    
    # Resolve data directory path
    args.data_dir = args.data_dir.resolve()
    
    # Find all TSV files
    print(f"Scanning {args.data_dir} for TSV files...")
    tsv_files = find_tsv_files(args.data_dir)
    
    if not tsv_files:
        print("No TSV files found.")
        return 0
    
    print(f"Found {len(tsv_files)} TSV files.")
    
    if args.dry_run:
        print("\nDRY RUN MODE - No files will be modified\n")
    
    # Process each file
    processed = 0
    skipped = 0
    failed = 0
    
    for tsv_file in tsv_files:
        rel_path = tsv_file.relative_to(args.data_dir.parent)
        
        # Check if file needs processing
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)
        
        has_inst = 'inst' in header
        has_validation_steps = 'validation_steps' in header
        has_assembly_params = 'assembly_params' in header
        
        if has_inst and has_validation_steps and has_assembly_params:
            skipped += 1
            continue
        
        # Extract metadata to show what will be added
        inst, validation_steps, assembly_params = extract_metadata_from_path(tsv_file, args.data_dir)
        
        print(f"\nProcessing: {rel_path}")
        if not has_inst:
            print(f"  Adding inst: {inst}")
        if not has_validation_steps:
            print(f"  Adding validation_steps: {validation_steps}")
        if not has_assembly_params:
            print(f"  Adding assembly_params: {assembly_params}")
        
        if add_columns_to_file(tsv_file, args.data_dir, args.dry_run):
            processed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total files: {len(tsv_files)}")
    print(f"Processed: {processed}")
    print(f"Skipped (already have columns): {skipped}")
    print(f"Failed: {failed}")
    
    if args.dry_run:
        print("\nThis was a DRY RUN. No files were modified.")
        print("Run without --dry-run to apply changes.")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
