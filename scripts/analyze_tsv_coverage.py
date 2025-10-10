#!/usr/bin/env python3
"""
Analyze TSV header coverage patterns.

This script analyzes all TSV files in the data folder and groups them by
their header coverage pattern relative to metadata/headers.tsv.

Usage: python scripts/analyze_tsv_coverage.py [--output-dir DIR]
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List, Tuple


def get_expected_headers(repo_root: Path) -> Set[str]:
    """
    Read expected headers from metadata/headers.tsv.
    
    Args:
        repo_root: Repository root directory
        
    Returns:
        Set of expected column names
    """
    headers_file = repo_root / "metadata" / "headers.tsv"
    
    expected_headers = set()
    with open(headers_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip the header row
        for row in reader:
            if row:  # Skip empty rows
                header_name = row[0].strip()
                expected_headers.add(header_name)
    
    return expected_headers


def get_tsv_headers(tsv_file: Path) -> Set[str]:
    """
    Get headers from a TSV file.
    
    Args:
        tsv_file: Path to TSV file
        
    Returns:
        Set of header names from the file
    """
    try:
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            headers = set(next(reader))
        return headers
    except Exception as e:
        print(f"Warning: Could not read {tsv_file}: {e}")
        return set()


def analyze_coverage(repo_root: Path) -> Dict[str, List[Path]]:
    """
    Analyze coverage patterns across all TSV files.
    
    Args:
        repo_root: Repository root directory
        
    Returns:
        Dictionary mapping coverage pattern (as sorted tuple) to list of files
    """
    data_dir = repo_root / "data"
    expected_headers = get_expected_headers(repo_root)
    
    # Group files by their header set
    pattern_to_files = defaultdict(list)
    
    for tsv_file in data_dir.glob("**/*.tsv"):
        headers = get_tsv_headers(tsv_file)
        if headers:
            # Create a pattern key from the sorted header set
            pattern = tuple(sorted(headers))
            relative_path = tsv_file.relative_to(repo_root)
            pattern_to_files[pattern].append(relative_path)
    
    return pattern_to_files, expected_headers


def calculate_coverage_stats(headers: Set[str], expected_headers: Set[str]) -> Dict:
    """
    Calculate coverage statistics for a header set.
    
    Args:
        headers: Set of headers in the file
        expected_headers: Set of expected headers
        
    Returns:
        Dictionary with coverage statistics
    """
    present_headers = headers & expected_headers
    missing_headers = expected_headers - headers
    unexpected_headers = headers - expected_headers
    
    coverage_percent = (len(present_headers) / len(expected_headers)) * 100 if expected_headers else 0
    
    return {
        'total_expected': len(expected_headers),
        'present': len(present_headers),
        'missing': len(missing_headers),
        'unexpected': len(unexpected_headers),
        'coverage_percent': coverage_percent,
        'present_headers': sorted(present_headers),
        'missing_headers': sorted(missing_headers),
        'unexpected_headers': sorted(unexpected_headers)
    }


def generate_report(pattern_to_files: Dict[Tuple, List[Path]], 
                   expected_headers: Set[str],
                   output_dir: Path) -> None:
    """
    Generate coverage report and save to files.
    
    Args:
        pattern_to_files: Dictionary mapping patterns to file lists
        expected_headers: Set of expected headers
        output_dir: Directory to save report files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sort patterns by coverage (descending) and then by number of files (descending)
    sorted_patterns = sorted(
        pattern_to_files.items(),
        key=lambda x: (len(set(x[0]) & expected_headers), len(x[1])),
        reverse=True
    )
    
    # Generate summary report
    summary_file = output_dir / "coverage_summary.md"
    with open(summary_file, 'w') as f:
        f.write("# TSV Header Coverage Analysis\n\n")
        f.write(f"Total TSV files analyzed: {sum(len(files) for files in pattern_to_files.values())}\n")
        f.write(f"Number of unique header patterns: {len(pattern_to_files)}\n")
        f.write(f"Total expected headers: {len(expected_headers)}\n\n")
        
        f.write("## Coverage Patterns\n\n")
        
        for pattern_idx, (pattern, files) in enumerate(sorted_patterns, 1):
            headers = set(pattern)
            stats = calculate_coverage_stats(headers, expected_headers)
            
            f.write(f"### Pattern {pattern_idx}\n\n")
            f.write(f"- **Files affected:** {len(files)}\n")
            f.write(f"- **Coverage:** {stats['coverage_percent']:.1f}% ({stats['present']}/{stats['total_expected']} headers)\n")
            f.write(f"- **Headers in files:** {len(headers)}\n")
            
            if stats['unexpected']:
                f.write(f"- **Unexpected headers:** {stats['unexpected']}\n")
            
            f.write(f"\n**Files:**\n")
            for file_path in sorted(files)[:10]:  # Show first 10 files
                f.write(f"- `{file_path}`\n")
            
            if len(files) > 10:
                f.write(f"- ... and {len(files) - 10} more files\n")
            
            f.write("\n")
    
    print(f"Summary report saved to: {summary_file}")
    
    # Generate detailed pattern reports
    patterns_dir = output_dir / "patterns"
    patterns_dir.mkdir(exist_ok=True)
    
    for pattern_idx, (pattern, files) in enumerate(sorted_patterns, 1):
        headers = set(pattern)
        stats = calculate_coverage_stats(headers, expected_headers)
        
        pattern_file = patterns_dir / f"pattern_{pattern_idx}.md"
        with open(pattern_file, 'w') as f:
            f.write(f"# Coverage Pattern {pattern_idx}\n\n")
            f.write(f"## Statistics\n\n")
            f.write(f"- Files with this pattern: {len(files)}\n")
            f.write(f"- Coverage: {stats['coverage_percent']:.1f}%\n")
            f.write(f"- Headers present: {stats['present']}/{stats['total_expected']}\n")
            f.write(f"- Missing headers: {stats['missing']}\n")
            f.write(f"- Unexpected headers: {stats['unexpected']}\n\n")
            
            f.write(f"## Headers Present ({len(stats['present_headers'])})\n\n")
            for header in stats['present_headers']:
                f.write(f"- `{header}`\n")
            
            if stats['missing_headers']:
                f.write(f"\n## Missing Headers ({len(stats['missing_headers'])})\n\n")
                for header in stats['missing_headers']:
                    f.write(f"- `{header}`\n")
            
            if stats['unexpected_headers']:
                f.write(f"\n## Unexpected Headers ({len(stats['unexpected_headers'])})\n\n")
                f.write("These headers are present in files but not defined in metadata/headers.tsv:\n\n")
                for header in stats['unexpected_headers']:
                    f.write(f"- `{header}`\n")
            
            f.write(f"\n## Affected Files ({len(files)})\n\n")
            for file_path in sorted(files):
                f.write(f"- `{file_path}`\n")
    
    print(f"Detailed pattern reports saved to: {patterns_dir}")
    
    # Generate JSON data for programmatic access
    json_data = []
    for pattern_idx, (pattern, files) in enumerate(sorted_patterns, 1):
        headers = set(pattern)
        stats = calculate_coverage_stats(headers, expected_headers)
        json_data.append({
            'pattern_id': pattern_idx,
            'file_count': len(files),
            'files': [str(f) for f in sorted(files)],
            'statistics': stats
        })
    
    json_file = output_dir / "coverage_data.json"
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"JSON data saved to: {json_file}")


def generate_issue_templates(pattern_to_files: Dict[Tuple, List[Path]], 
                             expected_headers: Set[str],
                             output_dir: Path) -> None:
    """
    Generate GitHub issue templates for each pattern.
    
    Args:
        pattern_to_files: Dictionary mapping patterns to file lists
        expected_headers: Set of expected headers
        output_dir: Directory to save issue templates
    """
    issues_dir = output_dir / "issues"
    issues_dir.mkdir(exist_ok=True)
    
    # Sort patterns by coverage (descending)
    sorted_patterns = sorted(
        pattern_to_files.items(),
        key=lambda x: (len(set(x[0]) & expected_headers), len(x[1])),
        reverse=True
    )
    
    for pattern_idx, (pattern, files) in enumerate(sorted_patterns, 1):
        headers = set(pattern)
        stats = calculate_coverage_stats(headers, expected_headers)
        
        issue_file = issues_dir / f"pattern_{pattern_idx}_issue.md"
        with open(issue_file, 'w') as f:
            # Generate issue title
            f.write(f"# TSV Header Coverage Pattern {pattern_idx}\n\n")
            
            # Add labels suggestion
            labels = ["data-quality", "headers"]
            if stats['unexpected']:
                labels.append("unexpected-headers")
            if stats['coverage_percent'] < 50:
                labels.append("low-coverage")
            
            f.write(f"**Suggested labels:** {', '.join(labels)}\n\n")
            
            # Issue body
            f.write("## Summary\n\n")
            f.write(f"This issue tracks TSV files with a specific header coverage pattern.\n\n")
            
            f.write("## Statistics\n\n")
            f.write(f"- **Files affected:** {len(files)}\n")
            f.write(f"- **Coverage:** {stats['coverage_percent']:.1f}% ({stats['present']}/{stats['total_expected']} headers)\n")
            f.write(f"- **Missing headers:** {stats['missing']}\n")
            
            if stats['unexpected']:
                f.write(f"- **Unexpected headers:** {stats['unexpected']} ⚠️\n")
            
            f.write("\n")
            
            if stats['unexpected_headers']:
                f.write("### ⚠️ Unexpected Headers\n\n")
                f.write("These headers are NOT defined in `metadata/headers.tsv`:\n\n")
                for header in stats['unexpected_headers']:
                    f.write(f"- `{header}`\n")
                f.write("\n")
            
            if stats['missing_headers']:
                f.write("### Missing Headers\n\n")
                f.write(f"The following {len(stats['missing_headers'])} headers are defined in metadata but missing from these files:\n\n")
                
                # Show first 20 missing headers
                for header in stats['missing_headers'][:20]:
                    f.write(f"- `{header}`\n")
                
                if len(stats['missing_headers']) > 20:
                    f.write(f"\n<details>\n<summary>... and {len(stats['missing_headers']) - 20} more (click to expand)</summary>\n\n")
                    for header in stats['missing_headers'][20:]:
                        f.write(f"- `{header}`\n")
                    f.write("\n</details>\n")
                
                f.write("\n")
            
            f.write("## Affected Files\n\n")
            f.write(f"Total: {len(files)} files\n\n")
            
            # Show first 20 files
            for file_path in sorted(files)[:20]:
                f.write(f"- `{file_path}`\n")
            
            if len(files) > 20:
                f.write(f"\n<details>\n<summary>... and {len(files) - 20} more (click to expand)</summary>\n\n")
                for file_path in sorted(files)[20:]:
                    f.write(f"- `{file_path}`\n")
                f.write("\n</details>\n")
            
            f.write("\n## Next Steps\n\n")
            f.write("- [ ] Review whether missing headers should be added to these files\n")
            f.write("- [ ] Review whether unexpected headers should be added to metadata/headers.tsv\n")
            f.write("- [ ] Determine if this pattern represents a legitimate data subset or requires correction\n")
    
    print(f"Issue templates saved to: {issues_dir}")


def main():
    """Main function to run coverage analysis."""
    parser = argparse.ArgumentParser(
        description='Analyze TSV header coverage patterns'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'reports' / 'coverage',
        help='Directory for output reports (default: reports/coverage)'
    )
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    
    print("Analyzing TSV header coverage patterns...")
    print(f"Repository root: {repo_root}")
    
    # Analyze coverage
    pattern_to_files, expected_headers = analyze_coverage(repo_root)
    
    print(f"\nFound {len(pattern_to_files)} unique header patterns")
    print(f"Total files analyzed: {sum(len(files) for files in pattern_to_files.values())}")
    
    # Generate reports
    print("\nGenerating reports...")
    generate_report(pattern_to_files, expected_headers, args.output_dir)
    
    # Generate issue templates
    print("\nGenerating issue templates...")
    generate_issue_templates(pattern_to_files, expected_headers, args.output_dir)
    
    print("\n✓ Coverage analysis complete!")
    print(f"\nReports saved to: {args.output_dir}")


if __name__ == '__main__':
    main()
