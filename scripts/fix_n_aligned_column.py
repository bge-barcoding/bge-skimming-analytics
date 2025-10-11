#!/usr/bin/env python3
"""
Fix n_aligned column in TSV files.

This script handles TSV files that have a 'n_aligned' column but not 'n_reads_aligned' column by:
1. Renaming n_aligned to n_reads_aligned if n_reads_aligned doesn't exist

Usage: python scripts/fix_n_aligned_column.py [--dry-run]
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Tuple


def find_tsv_files_with_n_aligned(data_dir: Path) -> List[Path]:
    """
    Find all TSV files that have a 'n_aligned' column but not 'n_reads_aligned'.
    
    Args:
        data_dir: Root data directory to search
        
    Returns:
        List of Path objects for TSV files with n_aligned but not n_reads_aligned column
    """
    tsv_files_with_n_aligned = []
    
    for tsv_file in data_dir.glob("**/*.tsv"):
        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                if 'n_aligned' in headers and 'n_reads_aligned' not in headers:
                    tsv_files_with_n_aligned.append(tsv_file)
        except Exception as e:
            print(f"Warning: Could not read {tsv_file}: {e}", file=sys.stderr)
    
    return tsv_files_with_n_aligned


def analyze_file(tsv_file: Path) -> Tuple[str, str]:
    """
    Analyze a TSV file to determine what action to take.
    
    Args:
        tsv_file: Path to TSV file
        
    Returns:
        Tuple of (action, message) where action is one of:
        - 'rename': Rename n_aligned to n_reads_aligned (n_reads_aligned doesn't exist)
        - 'skip': n_reads_aligned already exists, skip this file
        - 'error': Error reading file
    """
    try:
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            # Check if both columns exist
            if 'n_aligned' not in reader.fieldnames:
                return 'skip', 'n_aligned column not found'
            
            has_n_reads_aligned = 'n_reads_aligned' in reader.fieldnames
            
            if has_n_reads_aligned:
                return 'skip', 'n_reads_aligned already exists, no action needed'
            
            return 'rename', 'n_reads_aligned column absent, will rename n_aligned to n_reads_aligned'
            
    except Exception as e:
        return 'error', f"Error reading file: {e}"


def fix_file(tsv_file: Path, dry_run: bool = False) -> bool:
    """
    Fix a TSV file by renaming the n_aligned column to n_reads_aligned.
    
    Args:
        tsv_file: Path to TSV file
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
        
        # Modify fieldnames - rename n_aligned to n_reads_aligned
        new_fieldnames = ['n_reads_aligned' if f == 'n_aligned' else f for f in fieldnames]
        
        # Modify rows - map n_aligned to n_reads_aligned
        new_rows = []
        for row in rows:
            new_row = {}
            for field in new_fieldnames:
                if field == 'n_reads_aligned':
                    new_row[field] = row['n_aligned']
                else:
                    new_row[field] = row[field]
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
    """Main function to run the n_aligned fixer."""
    parser = argparse.ArgumentParser(
        description='Fix n_aligned column in TSV files'
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
    
    # Find files with n_aligned column but not n_reads_aligned
    print(f"Scanning {args.data_dir} for TSV files with n_aligned but not n_reads_aligned column...")
    files_with_n_aligned = find_tsv_files_with_n_aligned(args.data_dir)
    
    if not files_with_n_aligned:
        print("No TSV files with n_aligned (but not n_reads_aligned) column found.")
        return 0
    
    print(f"\nFound {len(files_with_n_aligned)} file(s) with n_aligned column:\n")
    
    # Analyze each file
    files_to_rename = []
    files_with_errors = []
    
    for tsv_file in files_with_n_aligned:
        action, message = analyze_file(tsv_file)
        rel_path = tsv_file.relative_to(args.data_dir.parent)
        
        print(f"{rel_path}")
        print(f"  Action: {action}")
        print(f"  Details: {message}\n")
        
        if action == 'rename':
            files_to_rename.append(tsv_file)
        elif action == 'error':
            files_with_errors.append((tsv_file, message))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files to fix (rename n_aligned to n_reads_aligned): {len(files_to_rename)}")
    print(f"Files with errors: {len(files_with_errors)}")
    
    if files_with_errors:
        print("\n" + "="*70)
        print("FILES WITH ERRORS")
        print("="*70)
        for tsv_file, message in files_with_errors:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"\n{rel_path}")
            print(f"  {message}")
    
    # Apply fixes if not dry run
    if not args.dry_run and files_to_rename:
        print("\n" + "="*70)
        print("APPLYING FIXES")
        print("="*70)
        
        for tsv_file in files_to_rename:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"Renaming n_aligned to n_reads_aligned in {rel_path}...", end=' ')
            if fix_file(tsv_file, dry_run=False):
                print("✓")
            else:
                print("✗ FAILED")
        
        print("\nFixes applied successfully!")
    elif args.dry_run:
        print("\n(Dry run mode - no changes were made)")
    
    # Return error code if there are errors
    if files_with_errors:
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
