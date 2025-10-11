#!/usr/bin/env python3
"""
Clean unused headers from metadata/headers.tsv.

This script:
1. Calculates how many TSV files in data/ contain each header from metadata/headers.tsv
2. Removes headers that occur in 0 files from metadata/headers.tsv
3. Creates a table listing headers and their occurrence count (ordered in increasing order)

Usage: python scripts/clean_unused_headers.py [--dry-run]
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def get_headers_from_metadata(repo_root: Path) -> List[Tuple[str, str]]:
    """
    Read headers from metadata/headers.tsv.
    
    Args:
        repo_root: Repository root directory
        
    Returns:
        List of tuples (header_name, definition)
    """
    headers_file = repo_root / "metadata" / "headers.tsv"
    
    headers = []
    with open(headers_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header_row = next(reader)  # Skip the header row
        for row in reader:
            if row and len(row) >= 2:  # Skip empty rows
                header_name = row[0].strip()
                definition = row[1].strip() if len(row) > 1 else ""
                headers.append((header_name, definition))
    
    return headers


def count_header_occurrences(repo_root: Path, expected_headers: List[str]) -> Dict[str, int]:
    """
    Count how many TSV files contain each header.
    
    Args:
        repo_root: Repository root directory
        expected_headers: List of header names to check
        
    Returns:
        Dictionary mapping header name to count of files containing it
    """
    data_dir = repo_root / "data"
    header_counts = defaultdict(int)
    
    # Initialize counts to 0 for all expected headers
    for header in expected_headers:
        header_counts[header] = 0
    
    # Count occurrences in TSV files
    for tsv_file in data_dir.glob("**/*.tsv"):
        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                file_headers = set(next(reader))
                
                # Count each expected header if present
                for header in expected_headers:
                    if header in file_headers:
                        header_counts[header] += 1
        except Exception as e:
            print(f"Warning: Could not read {tsv_file}: {e}")
    
    return header_counts


def generate_report(header_counts: Dict[str, int], output_file: Path) -> None:
    """
    Generate a report showing header occurrence counts.
    
    Args:
        header_counts: Dictionary mapping header name to count
        output_file: Path to save the report
    """
    # Sort by count (increasing), then by header name
    sorted_headers = sorted(header_counts.items(), key=lambda x: (x[1], x[0]))
    
    with open(output_file, 'w') as f:
        f.write("# Header Occurrence Report\n\n")
        f.write("This report shows how many TSV files contain each header defined in metadata/headers.tsv.\n\n")
        f.write(f"Total headers analyzed: {len(header_counts)}\n")
        f.write(f"Total TSV files scanned: counted across all files\n\n")
        
        f.write("| Header | Occurrences |\n")
        f.write("|--------|-------------|\n")
        
        for header, count in sorted_headers:
            f.write(f"| {header} | {count} |\n")
    
    print(f"\nReport saved to: {output_file}")


def update_headers_file(repo_root: Path, headers: List[Tuple[str, str]], 
                       header_counts: Dict[str, int], dry_run: bool = False) -> None:
    """
    Update metadata/headers.tsv by removing headers with 0 occurrences.
    
    Args:
        repo_root: Repository root directory
        headers: List of (header_name, definition) tuples
        header_counts: Dictionary mapping header name to count
        dry_run: If True, don't actually modify the file
    """
    headers_file = repo_root / "metadata" / "headers.tsv"
    
    # Filter out headers with 0 occurrences
    kept_headers = []
    removed_headers = []
    
    for header_name, definition in headers:
        if header_counts.get(header_name, 0) > 0:
            kept_headers.append((header_name, definition))
        else:
            removed_headers.append(header_name)
    
    print(f"\nHeaders to remove (0 occurrences): {len(removed_headers)}")
    if removed_headers:
        for header in removed_headers:
            print(f"  - {header}")
    
    print(f"\nHeaders to keep (>0 occurrences): {len(kept_headers)}")
    
    if dry_run:
        print("\n[DRY RUN] Would update metadata/headers.tsv")
        return
    
    # Write updated file
    with open(headers_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['barcode_validator TSV header', 'Definition'])
        for header_name, definition in kept_headers:
            writer.writerow([header_name, definition])
    
    print(f"\n✓ Updated {headers_file}")
    print(f"  Removed {len(removed_headers)} headers")
    print(f"  Kept {len(kept_headers)} headers")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Clean unused headers from metadata/headers.tsv'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--output-report',
        type=Path,
        default=Path('reports/header_occurrences.md'),
        help='Path for the occurrence report (default: reports/header_occurrences.md)'
    )
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    
    print("Analyzing header occurrences in TSV files...")
    print(f"Repository root: {repo_root}")
    
    # Read headers from metadata
    print("\nReading headers from metadata/headers.tsv...")
    headers = get_headers_from_metadata(repo_root)
    print(f"Found {len(headers)} headers in metadata/headers.tsv")
    
    # Count occurrences
    print("\nScanning TSV files in data/...")
    header_names = [h[0] for h in headers]
    header_counts = count_header_occurrences(repo_root, header_names)
    
    # Generate report
    print("\nGenerating occurrence report...")
    output_report = repo_root / args.output_report
    output_report.parent.mkdir(parents=True, exist_ok=True)
    generate_report(header_counts, output_report)
    
    # Update headers file
    update_headers_file(repo_root, headers, header_counts, args.dry_run)
    
    print("\n✓ Done!")


if __name__ == '__main__':
    main()
