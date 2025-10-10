#!/usr/bin/env python3
"""
Fix process_id column in TSV files.

This script handles TSV files that have a 'process_id' column by either:
1. Removing it if 'group_id' exists and values match
2. Renaming it to 'group_id' if 'group_id' doesn't exist
3. Flagging files where values don't match for manual review

Usage: python scripts/fix_process_id_column.py [--dry-run]
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Tuple


def find_tsv_files_with_process_id(data_dir: Path) -> List[Path]:
    """
    Find all TSV files that have a 'process_id' column.
    
    Args:
        data_dir: Root data directory to search
        
    Returns:
        List of Path objects for TSV files with process_id column
    """
    tsv_files_with_process_id = []
    
    for tsv_file in data_dir.glob("**/*.tsv"):
        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                if 'process_id' in headers:
                    tsv_files_with_process_id.append(tsv_file)
        except Exception as e:
            print(f"Warning: Could not read {tsv_file}: {e}", file=sys.stderr)
    
    return tsv_files_with_process_id


def analyze_file(tsv_file: Path) -> Tuple[str, str]:
    """
    Analyze a TSV file to determine what action to take.
    
    Args:
        tsv_file: Path to TSV file
        
    Returns:
        Tuple of (action, message) where action is one of:
        - 'remove': Remove process_id column (group_id exists and matches)
        - 'rename': Rename process_id to group_id (group_id doesn't exist)
        - 'conflict': Values don't match, manual review needed
        - 'error': Error reading file
    """
    try:
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            # Check if both columns exist
            if 'process_id' not in reader.fieldnames:
                return 'error', 'process_id column not found'
            
            has_group_id = 'group_id' in reader.fieldnames
            
            if not has_group_id:
                return 'rename', 'group_id column absent, will rename process_id to group_id'
            
            # Both columns exist, check if values match
            mismatches = []
            row_num = 1
            for row in reader:
                row_num += 1
                process_id_val = row.get('process_id', '').strip()
                group_id_val = row.get('group_id', '').strip()
                
                if process_id_val != group_id_val:
                    mismatches.append((row_num, process_id_val, group_id_val))
                    if len(mismatches) >= 5:  # Only report first 5 mismatches
                        break
            
            if mismatches:
                mismatch_details = '; '.join([
                    f"row {r}: process_id='{p}' vs group_id='{g}'"
                    for r, p, g in mismatches
                ])
                return 'conflict', f"Values don't match: {mismatch_details}"
            
            return 'remove', 'group_id exists and all values match, will remove process_id'
            
    except Exception as e:
        return 'error', f"Error reading file: {e}"


def fix_file(tsv_file: Path, action: str, dry_run: bool = False) -> bool:
    """
    Fix a TSV file by removing or renaming the process_id column.
    
    Args:
        tsv_file: Path to TSV file
        action: Action to take ('remove' or 'rename')
        dry_run: If True, don't actually modify files
        
    Returns:
        True if successful, False otherwise
    """
    if action not in ['remove', 'rename']:
        return False
    
    try:
        # Read the file
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            fieldnames = list(reader.fieldnames)
            rows = list(reader)
        
        # Modify fieldnames based on action
        if action == 'remove':
            new_fieldnames = [f for f in fieldnames if f != 'process_id']
        else:  # action == 'rename'
            new_fieldnames = ['group_id' if f == 'process_id' else f for f in fieldnames]
        
        # Modify rows based on action
        new_rows = []
        for row in rows:
            new_row = {}
            if action == 'remove':
                # Simply copy all fields except process_id
                for field in new_fieldnames:
                    new_row[field] = row[field]
            else:  # action == 'rename'
                # Copy all fields, mapping process_id to group_id
                for field in new_fieldnames:
                    if field == 'group_id':
                        new_row[field] = row['process_id']
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
    """Main function to run the process_id fixer."""
    parser = argparse.ArgumentParser(
        description='Fix process_id column in TSV files'
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
    
    # Find files with process_id column
    print(f"Scanning {args.data_dir} for TSV files with process_id column...")
    files_with_process_id = find_tsv_files_with_process_id(args.data_dir)
    
    if not files_with_process_id:
        print("No TSV files with process_id column found.")
        return 0
    
    print(f"\nFound {len(files_with_process_id)} file(s) with process_id column:\n")
    
    # Analyze each file
    files_to_remove = []
    files_to_rename = []
    files_with_conflicts = []
    files_with_errors = []
    
    for tsv_file in files_with_process_id:
        action, message = analyze_file(tsv_file)
        rel_path = tsv_file.relative_to(args.data_dir.parent)
        
        print(f"{rel_path}")
        print(f"  Action: {action}")
        print(f"  Details: {message}\n")
        
        if action == 'remove':
            files_to_remove.append(tsv_file)
        elif action == 'rename':
            files_to_rename.append(tsv_file)
        elif action == 'conflict':
            files_with_conflicts.append((tsv_file, message))
        else:  # error
            files_with_errors.append((tsv_file, message))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files to fix (remove process_id): {len(files_to_remove)}")
    print(f"Files to fix (rename process_id to group_id): {len(files_to_rename)}")
    print(f"Files with conflicts (manual review needed): {len(files_with_conflicts)}")
    print(f"Files with errors: {len(files_with_errors)}")
    
    if files_with_conflicts:
        print("\n" + "="*70)
        print("FILES REQUIRING MANUAL REVIEW")
        print("="*70)
        for tsv_file, message in files_with_conflicts:
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
    if not args.dry_run and (files_to_remove or files_to_rename):
        print("\n" + "="*70)
        print("APPLYING FIXES")
        print("="*70)
        
        for tsv_file in files_to_remove:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"Removing process_id from {rel_path}...", end=' ')
            if fix_file(tsv_file, 'remove', dry_run=False):
                print("✓")
            else:
                print("✗ FAILED")
        
        for tsv_file in files_to_rename:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"Renaming process_id to group_id in {rel_path}...", end=' ')
            if fix_file(tsv_file, 'rename', dry_run=False):
                print("✓")
            else:
                print("✗ FAILED")
        
        print("\nFixes applied successfully!")
    elif args.dry_run:
        print("\n(Dry run mode - no changes were made)")
    
    # Return error code if there are conflicts or errors
    if files_with_conflicts or files_with_errors:
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
