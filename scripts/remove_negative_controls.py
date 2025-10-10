#!/usr/bin/env python3
"""
Remove negative control rows from TSV files.

This script identifies and removes rows that are negative controls by detecting:
1. Rows where 'group_id' ends with the '-NC' suffix
2. Rows where 'error' column contains '<something>-NC not in BOLD'

Usage: python scripts/remove_negative_controls.py [--dry-run]
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import List, Tuple


def find_tsv_files_with_negative_controls(data_dir: Path) -> List[Path]:
    """
    Find all TSV files that have negative control rows.
    
    Args:
        data_dir: Root data directory to search
        
    Returns:
        List of Path objects for TSV files with negative controls
    """
    tsv_files_with_nc = []
    
    for tsv_file in data_dir.glob("**/*.tsv"):
        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                # Check if file has group_id or error column
                if not reader.fieldnames:
                    continue
                
                has_group_id = 'group_id' in reader.fieldnames
                has_error = 'error' in reader.fieldnames
                
                if not (has_group_id or has_error):
                    continue
                
                # Check for negative controls
                for row in reader:
                    # Check group_id ending with -NC
                    if has_group_id and row.get('group_id', '').endswith('-NC'):
                        tsv_files_with_nc.append(tsv_file)
                        break
                    
                    # Check error message containing <something>-NC not in BOLD
                    if has_error:
                        error_msg = row.get('error', '')
                        if re.search(r'\S+-NC\s+not in BOLD', error_msg):
                            tsv_files_with_nc.append(tsv_file)
                            break
                        
        except Exception as e:
            print(f"Warning: Could not read {tsv_file}: {e}", file=sys.stderr)
    
    return tsv_files_with_nc


def analyze_file(tsv_file: Path) -> Tuple[int, int, str]:
    """
    Analyze a TSV file to count negative control rows.
    
    Args:
        tsv_file: Path to TSV file
        
    Returns:
        Tuple of (total_rows, nc_rows, message)
    """
    try:
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            if not reader.fieldnames:
                return 0, 0, 'No headers found'
            
            has_group_id = 'group_id' in reader.fieldnames
            has_error = 'error' in reader.fieldnames
            
            total_rows = 0
            nc_rows = 0
            
            for row in reader:
                total_rows += 1
                is_nc = False
                
                # Check group_id ending with -NC
                if has_group_id and row.get('group_id', '').endswith('-NC'):
                    is_nc = True
                
                # Check error message containing <something>-NC not in BOLD
                if has_error and not is_nc:
                    error_msg = row.get('error', '')
                    if re.search(r'\S+-NC\s+not in BOLD', error_msg):
                        is_nc = True
                
                if is_nc:
                    nc_rows += 1
            
            return total_rows, nc_rows, f'{nc_rows} negative control row(s) found out of {total_rows}'
            
    except Exception as e:
        return 0, 0, f'Error reading file: {e}'


def clean_file(tsv_file: Path, dry_run: bool = False) -> bool:
    """
    Remove negative control rows from a TSV file.
    
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
            
            has_group_id = 'group_id' in fieldnames
            has_error = 'error' in fieldnames
            
            # Filter out negative control rows
            clean_rows = []
            for row in reader:
                is_nc = False
                
                # Check group_id ending with -NC
                if has_group_id and row.get('group_id', '').endswith('-NC'):
                    is_nc = True
                
                # Check error message containing <something>-NC not in BOLD
                if has_error and not is_nc:
                    error_msg = row.get('error', '')
                    if re.search(r'\S+-NC\s+not in BOLD', error_msg):
                        is_nc = True
                
                if not is_nc:
                    clean_rows.append(row)
        
        if not dry_run:
            # Write the cleaned file (preserves original line endings via newline='')
            with open(tsv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(clean_rows)
        
        return True
        
    except Exception as e:
        print(f"Error cleaning {tsv_file}: {e}", file=sys.stderr)
        return False


def main():
    """Main function to run the negative control remover."""
    parser = argparse.ArgumentParser(
        description='Remove negative control rows from TSV files'
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
    
    # Find files with negative controls
    print(f"Scanning {args.data_dir} for TSV files with negative controls...")
    files_with_nc = find_tsv_files_with_negative_controls(args.data_dir)
    
    if not files_with_nc:
        print("No TSV files with negative controls found.")
        return 0
    
    print(f"\nFound {len(files_with_nc)} file(s) with negative controls:\n")
    
    # Analyze each file
    files_to_clean = []
    total_nc_rows = 0
    
    for tsv_file in files_with_nc:
        total_rows, nc_rows, message = analyze_file(tsv_file)
        rel_path = tsv_file.relative_to(args.data_dir.parent)
        
        print(f"{rel_path}")
        print(f"  {message}\n")
        
        if nc_rows > 0:
            files_to_clean.append(tsv_file)
            total_nc_rows += nc_rows
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files to clean: {len(files_to_clean)}")
    print(f"Total negative control rows to remove: {total_nc_rows}")
    
    # Apply cleaning if not dry run
    if not args.dry_run and files_to_clean:
        print("\n" + "="*70)
        print("CLEANING FILES")
        print("="*70)
        
        for tsv_file in files_to_clean:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"Cleaning {rel_path}...", end=' ')
            if clean_file(tsv_file, dry_run=False):
                print("✓")
            else:
                print("✗ FAILED")
        
        print("\nCleaning completed successfully!")
    elif args.dry_run:
        print("\n(Dry run mode - no changes were made)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
