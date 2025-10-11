#!/usr/bin/env python3
"""
Fix Filename column in TSV files.

This script handles TSV files that have a 'Filename' column by:
1. Removing it if 'sequence_id' exists and all values match
2. Reporting files where values don't match for manual review

Usage: python scripts/fix_filename_column.py [--dry-run]
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Tuple


def find_tsv_files_with_filename(data_dir: Path) -> List[Path]:
    """
    Find all TSV files that have a 'Filename' column.
    
    Args:
        data_dir: Root data directory to search
        
    Returns:
        List of Path objects for TSV files with Filename column
    """
    tsv_files_with_filename = []
    
    for tsv_file in data_dir.glob("**/*.tsv"):
        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                if 'Filename' in headers:
                    tsv_files_with_filename.append(tsv_file)
        except Exception as e:
            print(f"Warning: Could not read {tsv_file}: {e}", file=sys.stderr)
    
    return tsv_files_with_filename


def analyze_file(tsv_file: Path) -> Tuple[str, str]:
    """
    Analyze a TSV file to determine what action to take.
    
    Args:
        tsv_file: Path to TSV file
        
    Returns:
        Tuple of (action, message) where action is one of:
        - 'remove': Remove Filename column (sequence_id exists and matches Pattern 1 or Pattern 2)
        - 'keep': Values don't match pattern or no sequence_id, manual review needed
        - 'error': Error reading file
        
    Pattern 1: sequence_id is either equal to Filename or Filename + '_merge'
    Pattern 2: Filename is equal to sequence_id + '_' + group_id
    In both patterns, the sequence_id is correct and Filename can be removed.
    """
    try:
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            # Check if both columns exist
            if 'Filename' not in reader.fieldnames:
                return 'error', 'Filename column not found'
            
            has_sequence_id = 'sequence_id' in reader.fieldnames
            has_group_id = 'group_id' in reader.fieldnames
            
            if not has_sequence_id:
                return 'keep', 'sequence_id column absent, cannot remove Filename'
            
            # Check if values match Pattern 1 or Pattern 2
            pattern_violations = []
            row_num = 1
            for row in reader:
                row_num += 1
                filename_val = row.get('Filename', '').strip()
                sequence_id_val = row.get('sequence_id', '').strip()
                group_id_val = row.get('group_id', '').strip() if has_group_id else ''
                
                # Check if it matches Pattern 1:
                # sequence_id == Filename OR sequence_id == Filename + '_merge'
                is_pattern_1 = (
                    filename_val == sequence_id_val or 
                    sequence_id_val == filename_val + '_merge'
                )
                
                # Check if it matches Pattern 2:
                # Filename == sequence_id + '_' + group_id
                is_pattern_2 = (
                    has_group_id and 
                    group_id_val and 
                    filename_val == sequence_id_val + '_' + group_id_val
                )
                
                if not is_pattern_1 and not is_pattern_2:
                    pattern_violations.append((row_num, filename_val, sequence_id_val, group_id_val))
                    if len(pattern_violations) >= 5:  # Only report first 5 violations
                        break
            
            if pattern_violations:
                violation_details = '; '.join([
                    f"row {r}: Filename='{f}' vs sequence_id='{s}' vs group_id='{g}'"
                    for r, f, s, g in pattern_violations
                ])
                return 'keep', f"Does not match Pattern 1 or Pattern 2: {violation_details}"
            
            return 'remove', 'Matches Pattern 1 or Pattern 2, will remove Filename'
            
    except Exception as e:
        return 'error', f"Error reading file: {e}"


def fix_file(tsv_file: Path, dry_run: bool = False) -> bool:
    """
    Fix a TSV file by removing the Filename column.
    
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
        
        # Remove Filename column
        new_fieldnames = [f for f in fieldnames if f != 'Filename']
        
        # Copy rows without Filename column
        new_rows = []
        for row in rows:
            new_row = {}
            for field in new_fieldnames:
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
    """Main function to run the Filename fixer."""
    parser = argparse.ArgumentParser(
        description='Fix Filename column in TSV files'
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
    
    # Find files with Filename column
    print(f"Scanning {args.data_dir} for TSV files with Filename column...")
    files_with_filename = find_tsv_files_with_filename(args.data_dir)
    
    if not files_with_filename:
        print("No TSV files with Filename column found.")
        return 0
    
    print(f"\nFound {len(files_with_filename)} file(s) with Filename column:\n")
    
    # Analyze each file
    files_to_remove = []
    files_to_keep = []
    files_with_errors = []
    
    for tsv_file in files_with_filename:
        action, message = analyze_file(tsv_file)
        rel_path = tsv_file.relative_to(args.data_dir.parent)
        
        print(f"{rel_path}")
        print(f"  Action: {action}")
        print(f"  Details: {message}\n")
        
        if action == 'remove':
            files_to_remove.append(tsv_file)
        elif action == 'keep':
            files_to_keep.append((tsv_file, message))
        else:  # error
            files_with_errors.append((tsv_file, message))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files to fix (remove Filename): {len(files_to_remove)}")
    print(f"Files to keep (manual review needed): {len(files_to_keep)}")
    print(f"Files with errors: {len(files_with_errors)}")
    
    if files_to_keep:
        print("\n" + "="*70)
        print("FILES WITH DIFFERING VALUES (MANUAL REVIEW NEEDED)")
        print("="*70)
        for tsv_file, message in files_to_keep:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"\n{rel_path}")
            print(f"  {message}")
    
    if files_with_errors:
        print("\n" + "="*70)
        print("FILES WITH ERRORS")
        print("="*70)
        for tsv_file, message in files_with_errors:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"\n{rel_path}")
            print(f"  {message}")
    
    # Apply fixes if not dry run
    if not args.dry_run and files_to_remove:
        print("\n" + "="*70)
        print("APPLYING FIXES")
        print("="*70)
        
        for tsv_file in files_to_remove:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"Removing Filename from {rel_path}...", end=' ')
            if fix_file(tsv_file, dry_run=False):
                print("✓")
            else:
                print("✗ FAILED")
        
        print("\nFixes applied successfully!")
    elif args.dry_run:
        print("\n(Dry run mode - no changes were made)")
    
    # Return success - files to keep are expected and documented
    return 0


if __name__ == '__main__':
    sys.exit(main())
