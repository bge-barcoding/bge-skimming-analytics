#!/usr/bin/env python3
"""
Assess collection dates in BOLD metadata for implausible values.

This script analyzes the collection_data.tsv file from BOLD metadata and reports
specimens with collection dates that are implausible (e.g., too old or in the future).
By default, it considers plausible dates to be within the last 200 years.

Usage: python scripts/assess_collection_dates.py [--min-year YEAR] [--max-year YEAR] [--output FILE]
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional


def parse_collection_date(date_str: str) -> Optional[int]:
    """
    Extract year from collection date string.
    
    Collection dates are in format: dd-Mmm-yyyy (e.g., 23-Aug-1983)
    
    Args:
        date_str: Date string from collection data
        
    Returns:
        Year as integer, or None if date cannot be parsed
    """
    if not date_str or date_str.strip() == '':
        return None
    
    try:
        # Extract last 4 characters as year
        year_str = date_str.strip()[-4:]
        return int(year_str)
    except (ValueError, IndexError):
        return None


def assess_collection_dates(
    collection_file: Path,
    min_year: int,
    max_year: int
) -> List[Tuple[str, str, int, str]]:
    """
    Assess collection dates and identify implausible ones.
    
    Args:
        collection_file: Path to collection_data.tsv
        min_year: Minimum plausible year (inclusive)
        max_year: Maximum plausible year (inclusive)
        
    Returns:
        List of tuples: (sample_id, collection_date, year, reason)
    """
    implausible_dates = []
    
    with open(collection_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            sample_id = row.get('Sample ID', '')
            date_str = row.get('Collection Date', '')
            
            if not date_str:
                continue
            
            year = parse_collection_date(date_str)
            
            if year is None:
                continue
            
            reason = None
            if year < min_year:
                reason = f"too old (before {min_year})"
            elif year > max_year:
                reason = f"in the future (after {max_year})"
            
            if reason:
                implausible_dates.append((sample_id, date_str, year, reason))
    
    return implausible_dates


def write_csv_report(
    implausible_dates: List[Tuple[str, str, int, str]],
    output_file: Path
):
    """
    Write assessment report as CSV file.
    
    Args:
        implausible_dates: List of implausible date records
        output_file: Path to output CSV file
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Sample ID', 'Collection Date', 'Year', 'Issue'])
        for sample_id, date_str, year, reason in implausible_dates:
            writer.writerow([sample_id, date_str, year, reason])


def write_report(
    implausible_dates: List[Tuple[str, str, int, str]],
    output_file: Optional[Path],
    min_year: int,
    max_year: int
):
    """
    Write assessment report to file or stdout.
    
    Args:
        implausible_dates: List of implausible date records
        output_file: Path to output file, or None for stdout
        min_year: Minimum plausible year used in assessment
        max_year: Maximum plausible year used in assessment
    """
    import io
    
    # Sort by year for easier review
    implausible_dates.sort(key=lambda x: x[2])
    
    # Prepare output
    output = io.StringIO()
    
    output.write("=" * 80 + "\n")
    output.write("BOLD Collection Date Assessment Report\n")
    output.write("=" * 80 + "\n\n")
    
    output.write(f"Assessment criteria:\n")
    output.write(f"  - Plausible year range: {min_year} to {max_year}\n")
    output.write(f"  - Total implausible dates found: {len(implausible_dates)}\n\n")
    
    if not implausible_dates:
        output.write("No implausible dates found.\n")
    else:
        output.write("-" * 80 + "\n")
        output.write(f"{'Sample ID':<25} {'Collection Date':<20} {'Year':>6} {'Issue'}\n")
        output.write("-" * 80 + "\n")
        
        for sample_id, date_str, year, reason in implausible_dates:
            output.write(f"{sample_id:<25} {date_str:<20} {year:6d} {reason}\n")
        
        output.write("-" * 80 + "\n\n")
        
        # Statistics by issue type
        too_old = sum(1 for _, _, _, reason in implausible_dates if "too old" in reason)
        in_future = sum(1 for _, _, _, reason in implausible_dates if "future" in reason)
        
        output.write("Summary by issue type:\n")
        output.write(f"  - Dates too old (before {min_year}): {too_old}\n")
        output.write(f"  - Dates in the future (after {max_year}): {in_future}\n\n")
        
        # Year distribution
        year_counts = {}
        for _, _, year, _ in implausible_dates:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        output.write("Distribution by year:\n")
        for year in sorted(year_counts.keys()):
            count = year_counts[year]
            output.write(f"  - {year}: {count} specimen(s)\n")
    
    output.write("\n" + "=" * 80 + "\n")
    
    report_text = output.getvalue()
    
    # Write to file or stdout
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Report written to: {output_file}")
    else:
        print(report_text)


def main():
    """Main function to assess collection dates."""
    parser = argparse.ArgumentParser(
        description="Assess BOLD collection dates for implausible values"
    )
    parser.add_argument(
        '--min-year',
        type=int,
        default=datetime.now().year - 200,
        help='Minimum plausible year (default: current year - 200)'
    )
    parser.add_argument(
        '--max-year',
        type=int,
        default=datetime.now().year,
        help='Maximum plausible year (default: current year)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file for report (default: stdout)'
    )
    parser.add_argument(
        '--csv',
        type=Path,
        help='Output TSV file with the list of implausible dates'
    )
    parser.add_argument(
        '--collection-file',
        type=Path,
        help='Path to collection_data.tsv (default: metadata/bold/collection_data.tsv)'
    )
    
    args = parser.parse_args()
    
    # Determine repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    # Determine collection file path
    if args.collection_file:
        collection_file = args.collection_file
    else:
        collection_file = repo_root / "metadata" / "bold" / "collection_data.tsv"
    
    # Check if collection file exists
    if not collection_file.exists():
        print(f"Error: Collection file not found: {collection_file}", file=sys.stderr)
        return 1
    
    # Assess collection dates
    implausible_dates = assess_collection_dates(
        collection_file,
        args.min_year,
        args.max_year
    )
    
    # Write report
    write_report(implausible_dates, args.output, args.min_year, args.max_year)
    
    # Write CSV if requested
    if args.csv:
        write_csv_report(implausible_dates, args.csv)
        print(f"CSV report written to: {args.csv}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
