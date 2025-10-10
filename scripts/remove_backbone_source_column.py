#!/usr/bin/env python3
"""
Remove backbone_source column from TSV files.

This script removes the redundant 'backbone_source' column from TSV files
in the data directory.

Usage: python scripts/remove_backbone_source_column.py [--dry-run]
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List


def find_tsv_files_with_backbone_source(data_dir: Path) -> List[Path]:
    """
    Find all TSV files that have a 'backbone_source' column.
    
    Args:
        data_dir: Root data directory to search
        
    Returns:
        List of Path objects for TSV files with backbone_source column
    """
    tsv_files_with_backbone_source = []
    
    for tsv_file in data_dir.glob("**/*.tsv"):
        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                if 'backbone_source' in headers:
                    tsv_files_with_backbone_source.append(tsv_file)
        except Exception as e:
            print(f"Warning: Could not read {tsv_file}: {e}", file=sys.stderr)
    
    return tsv_files_with_backbone_source


def remove_column(tsv_file: Path, column_name: str, dry_run: bool = False) -> bool:
    """
    Remove a column from a TSV file.
    
    Args:
        tsv_file: Path to TSV file
        column_name: Name of column to remove
        dry_run: If True, don't actually modify files
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the file
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            fieldnames = list(reader.fieldnames)
            rows = list(reader)
        
        # Remove the column from fieldnames
        if column_name not in fieldnames:
            print(f"Warning: Column '{column_name}' not found in {tsv_file}", file=sys.stderr)
            return False
        
        new_fieldnames = [f for f in fieldnames if f != column_name]
        
        # Create new rows without the column
        new_rows = []
        for row in rows:
            new_row = {field: row[field] for field in new_fieldnames}
            new_rows.append(new_row)
        
        if not dry_run:
            # Write the modified file
            with open(tsv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=new_fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(new_rows)
        
        return True
        
    except Exception as e:
        print(f"Error fixing {tsv_file}: {e}", file=sys.stderr)
        return False


def main():
    """Main function to run the backbone_source column remover."""
    parser = argparse.ArgumentParser(
        description='Remove backbone_source column from TSV files'
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
    
    # Find files with backbone_source column
    print(f"Scanning {args.data_dir} for TSV files with backbone_source column...")
    files_with_backbone_source = find_tsv_files_with_backbone_source(args.data_dir)
    
    if not files_with_backbone_source:
        print("No TSV files with backbone_source column found.")
        return 0
    
    print(f"\nFound {len(files_with_backbone_source)} file(s) with backbone_source column:\n")
    
    for tsv_file in files_with_backbone_source:
        rel_path = tsv_file.relative_to(args.data_dir.parent)
        print(f"  - {rel_path}")
    
    # Apply fixes if not dry run
    if not args.dry_run:
        print("\n" + "="*70)
        print("REMOVING BACKBONE_SOURCE COLUMN")
        print("="*70)
        
        for tsv_file in files_with_backbone_source:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"Removing backbone_source from {rel_path}...", end=' ')
            if remove_column(tsv_file, 'backbone_source', dry_run=False):
                print("✓")
            else:
                print("✗ FAILED")
        
        print("\nColumn removal completed successfully!")
    else:
        print("\n(Dry run mode - no changes were made)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
