#!/usr/bin/env python3
"""
Parse sequence_id to populate missing r, s, and group_id columns in TSV files.

This script handles TSV files that have a sequence_id column with the pattern:
    <process_id>_r_<float>_s_<int>

Where:
- process_id: A BOLD process ID (e.g., UNIFI571-24, BBIOP1901-24)
- r: A float value (MGE parameter r value)
- s: An integer value (MGE parameter s value)

If the file is missing r, s, and group_id columns, this script will:
1. Parse the sequence_id to extract these values
2. Add the three new columns to the TSV file
3. Populate them with the extracted values

Usage: python scripts/parse_sequence_id_columns.py [--dry-run]
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def parse_sequence_id(sequence_id: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse a sequence_id to extract group_id (process_id), r, and s values.
    
    Pattern: <process_id>_r_<float>_s_<int>
    
    Args:
        sequence_id: The sequence_id string to parse
        
    Returns:
        Tuple of (group_id, r, s) if pattern matches, None otherwise
    """
    # Pattern: <process_id>_r_<float>_s_<int>
    # Process ID pattern: capital letters and digits, dash, two more digits
    # e.g., UNIFI571-24, BBIOP1901-24
    pattern = r'^(.+)_r_([0-9.]+)_s_(\d+)$'
    match = re.match(pattern, sequence_id)
    
    if match:
        group_id = match.group(1)
        r = match.group(2)
        s = match.group(3)
        return (group_id, r, s)
    
    return None


def find_tsv_files_to_fix(data_dir: Path) -> List[Path]:
    """
    Find all TSV files that need fixing.
    
    A file needs fixing if:
    - It has no 'r' column
    - It has no 's' column
    - It has no 'group_id' column
    - It has a 'sequence_id' column with the expected pattern
    
    Args:
        data_dir: Root data directory to search
        
    Returns:
        List of Path objects for TSV files that need fixing
    """
    tsv_files_to_fix = []
    
    for tsv_file in data_dir.glob("**/*.tsv"):
        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                headers = reader.fieldnames
                
                # Check if columns are missing
                has_r = 'r' in headers
                has_s = 's' in headers
                has_group_id = 'group_id' in headers
                has_sequence_id = 'sequence_id' in headers
                
                if not has_r and not has_s and not has_group_id and has_sequence_id:
                    # Check if at least one row has the expected pattern
                    for row in reader:
                        seq_id = row.get('sequence_id', '')
                        if parse_sequence_id(seq_id) is not None:
                            tsv_files_to_fix.append(tsv_file)
                            break
                        
        except Exception as e:
            print(f"Warning: Could not read {tsv_file}: {e}", file=sys.stderr)
    
    return tsv_files_to_fix


def analyze_file(tsv_file: Path) -> Tuple[str, str, int]:
    """
    Analyze a TSV file to determine if it can be fixed.
    
    Args:
        tsv_file: Path to TSV file
        
    Returns:
        Tuple of (status, message, parseable_count) where status is one of:
        - 'fix': File can be fixed
        - 'partial': Some rows can't be parsed
        - 'error': Error reading file
    """
    try:
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            if 'sequence_id' not in reader.fieldnames:
                return 'error', 'sequence_id column not found', 0
            
            total_rows = 0
            parseable_rows = 0
            unparseable_examples = []
            
            for row in reader:
                total_rows += 1
                seq_id = row.get('sequence_id', '')
                
                if parse_sequence_id(seq_id) is not None:
                    parseable_rows += 1
                else:
                    if len(unparseable_examples) < 3:
                        unparseable_examples.append(seq_id)
            
            if parseable_rows == total_rows:
                return 'fix', f'All {total_rows} rows can be parsed', parseable_rows
            elif parseable_rows > 0:
                examples = ', '.join([f"'{e}'" for e in unparseable_examples])
                return 'partial', f'{parseable_rows}/{total_rows} rows parseable. Examples of unparseable: {examples}', parseable_rows
            else:
                return 'error', f'No rows can be parsed from {total_rows} total rows', 0
                
    except Exception as e:
        return 'error', f'Error reading file: {e}', 0


def fix_file(tsv_file: Path, dry_run: bool = False) -> bool:
    """
    Fix a TSV file by adding r, s, and group_id columns parsed from sequence_id.
    
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
        
        # Add new columns at the end
        new_fieldnames = fieldnames + ['group_id', 'r', 's']
        
        # Parse and populate new columns
        new_rows = []
        for row in rows:
            new_row = row.copy()
            seq_id = row.get('sequence_id', '')
            parsed = parse_sequence_id(seq_id)
            
            if parsed:
                group_id, r, s = parsed
                new_row['group_id'] = group_id
                new_row['r'] = r
                new_row['s'] = s
            else:
                # If parsing fails, leave empty
                new_row['group_id'] = ''
                new_row['r'] = ''
                new_row['s'] = ''
            
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
    """Main function to run the sequence_id parser."""
    parser = argparse.ArgumentParser(
        description='Parse sequence_id to populate missing r, s, and group_id columns'
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
    
    # Find files that need fixing
    print(f"Scanning {args.data_dir} for TSV files with missing r, s, and group_id columns...")
    files_to_fix = find_tsv_files_to_fix(args.data_dir)
    
    if not files_to_fix:
        print("No TSV files found that need fixing.")
        return 0
    
    print(f"\nFound {len(files_to_fix)} file(s) that need fixing:\n")
    
    # Analyze each file
    files_can_fix = []
    files_partial = []
    files_with_errors = []
    
    for tsv_file in files_to_fix:
        status, message, count = analyze_file(tsv_file)
        rel_path = tsv_file.relative_to(args.data_dir.parent)
        
        print(f"{rel_path}")
        print(f"  Status: {status}")
        print(f"  Details: {message}\n")
        
        if status == 'fix':
            files_can_fix.append(tsv_file)
        elif status == 'partial':
            files_partial.append((tsv_file, message))
        else:  # error
            files_with_errors.append((tsv_file, message))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files that can be fixed: {len(files_can_fix)}")
    print(f"Files with partial matches: {len(files_partial)}")
    print(f"Files with errors: {len(files_with_errors)}")
    
    if files_partial:
        print("\n" + "="*70)
        print("FILES WITH PARTIAL MATCHES")
        print("="*70)
        for tsv_file, message in files_partial:
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
    if not args.dry_run and files_can_fix:
        print("\n" + "="*70)
        print("APPLYING FIXES")
        print("="*70)
        
        for tsv_file in files_can_fix:
            rel_path = tsv_file.relative_to(args.data_dir.parent)
            print(f"Adding columns to {rel_path}...", end=' ')
            if fix_file(tsv_file, dry_run=False):
                print("✓")
            else:
                print("✗ FAILED")
        
        print("\nFixes applied successfully!")
    elif args.dry_run:
        print("\n(Dry run mode - no changes were made)")
    
    # Return error code if there are errors (but not partial matches)
    if files_with_errors:
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
