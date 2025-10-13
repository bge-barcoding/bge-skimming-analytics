#!/usr/bin/env python3
"""
Merge all TSV files in the data directory into a single gzip-compressed TSV file.

This script:
1. Finds all TSV files in the data directory (excluding metadata directory)
2. Collects the union of all columns across all files
3. Merges files into a single DataFrame with standardized columns
4. Infers data types for each column
5. Standardizes missing data values
6. Standardizes boolean values
7. Writes the merged data to data/bge-skimming-analytics.tsv.gz (compressed)
8. Generates a frictionless data package JSON metadata file

Usage:
    python scripts/merge_all_tsv.py [--dry-run]
"""

import argparse
import gzip
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Set
import hashlib

import pandas as pd


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )


def find_all_tsv_files(data_dir: Path) -> List[Path]:
    """Find all TSV files in the data directory.
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        List of TSV file paths
    """
    # Exclude files in metadata directory and the output file itself
    tsv_files = []
    for f in data_dir.rglob('*.tsv'):
        # Exclude metadata files and the output file
        if 'metadata' not in f.parts and f.name != 'bge-skimming-analytics.tsv':
            tsv_files.append(f)
    
    return sorted(tsv_files)


def collect_all_columns(files: List[Path]) -> Set[str]:
    """Collect union of all column names from all files.
    
    Args:
        files: List of TSV file paths
        
    Returns:
        Set of all unique column names
    """
    all_columns = set()
    for f in files:
        df = pd.read_csv(f, sep='\t', nrows=0)
        all_columns.update(df.columns)
    
    return all_columns


def standardize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize missing value representations.
    
    Converts 'None', 'null', 'NULL', 'nan', 'NaN', 'N/A', 'n/a' to proper NA.
    
    Args:
        df: DataFrame to standardize
        
    Returns:
        Standardized DataFrame
    """
    # Replace common missing value representations with pd.NA
    missing_values = ['None', 'null', 'NULL', 'nan', 'NaN', 'N/A', 'n/a']
    
    for col in df.columns:
        # Replace missing value strings with pd.NA
        df[col] = df[col].replace(missing_values, pd.NA)
        # Also handle empty strings for string columns
        if df[col].dtype == 'object':
            df[col] = df[col].replace('', pd.NA)
    
    return df


def standardize_boolean_columns(df: pd.DataFrame, boolean_cols: List[str]) -> pd.DataFrame:
    """Standardize boolean column values to 'True'/'False'.
    
    Args:
        df: DataFrame to standardize
        boolean_cols: List of columns that should be boolean
        
    Returns:
        Standardized DataFrame
    """
    for col in boolean_cols:
        if col in df.columns:
            # Convert to string first, then standardize
            df[col] = df[col].astype(str)
            # Map various boolean representations
            bool_map = {
                'true': 'True',
                'True': 'True',
                'TRUE': 'True',
                'yes': 'True',
                'Yes': 'True',
                'YES': 'True',
                '1': 'True',
                'false': 'False',
                'False': 'False',
                'FALSE': 'False',
                'no': 'False',
                'No': 'False',
                'NO': 'False',
                '0': 'False',
            }
            df[col] = df[col].replace(bool_map)
            # Handle NA values
            df[col] = df[col].replace(['None', 'nan', '<NA>'], pd.NA)
    
    return df


def infer_column_types(df: pd.DataFrame, headers_info: pd.DataFrame) -> Dict[str, Dict]:
    """Infer data types for columns based on the data and definitions.
    
    Args:
        df: DataFrame with data
        headers_info: DataFrame with column definitions from headers.tsv
        
    Returns:
        Dictionary mapping column names to type info
    """
    type_info = {}
    
    # Boolean columns based on metadata
    boolean_cols = ['fcleaner', 'merge']
    
    for col in df.columns:
        # Get definition from headers.tsv if available
        header_row = headers_info[headers_info['barcode_validator TSV header'] == col]
        is_compulsory = header_row['Compulsory'].values[0] if len(header_row) > 0 else False
        definition = header_row['Definition'].values[0] if len(header_row) > 0 else ''
        
        # Try to infer type
        col_type = 'string'  # default
        format_type = 'default'
        
        # Check if boolean (using pandas bool dtype or boolean dtype)
        if col in boolean_cols or df[col].dtype == 'bool' or str(df[col].dtype) == 'boolean':
            col_type = 'boolean'
        # Check if integer (including nullable Int64)
        elif df[col].dtype in ['int64', 'int32', 'Int64', 'Int32'] or str(df[col].dtype) in ['Int64', 'Int32']:
            col_type = 'integer'
        # Check if float
        elif df[col].dtype in ['float64', 'float32']:
            # Check if this is actually integer with some NaN values
            non_null = df[col].dropna()
            if len(non_null) > 0 and (non_null % 1 == 0).all():
                col_type = 'integer'
            else:
                col_type = 'number'
        # For object/string types, try to infer more specific types
        elif df[col].dtype == 'object':
            non_null = df[col].dropna()
            if len(non_null) > 0:
                sample = non_null.iloc[0] if len(non_null) > 0 else ''
                # Could add more sophisticated type detection here
                # For now, keep as string
                col_type = 'string'
        
        type_info[col] = {
            'name': col,
            'type': col_type,
            'format': format_type,
            'description': definition,
            'constraints': {}
        }
        
        # Add required constraint for compulsory columns
        if is_compulsory:
            type_info[col]['constraints']['required'] = True
    
    return type_info


def merge_tsv_files(files: List[Path], all_columns: Set[str]) -> pd.DataFrame:
    """Merge all TSV files into a single DataFrame.
    
    Args:
        files: List of TSV file paths
        all_columns: Set of all column names
        
    Returns:
        Merged DataFrame
    """
    dfs = []
    
    for f in files:
        logging.info(f"Processing {f}")
        
        # Read file - use dtype=str to preserve all data initially
        df = pd.read_csv(f, sep='\t', dtype=str, keep_default_na=False)
        
        # Add missing columns
        missing_cols = all_columns - set(df.columns)
        for col in missing_cols:
            df[col] = pd.NA
        
        # Reorder columns to match all_columns order
        df = df[sorted(all_columns)]
        
        dfs.append(df)
    
    # Concatenate all DataFrames
    logging.info(f"Concatenating {len(dfs)} DataFrames...")
    merged = pd.concat(dfs, ignore_index=True)
    
    return merged


def convert_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Convert DataFrame columns to appropriate dtypes.
    
    Args:
        df: DataFrame to convert
        
    Returns:
        DataFrame with converted dtypes
    """
    # Boolean columns
    boolean_cols = ['fcleaner', 'merge']
    for col in boolean_cols:
        if col in df.columns:
            # Map to boolean, keeping NA
            bool_map = {'True': True, 'False': False}
            df[col] = df[col].map(bool_map)
    
    # Integer columns (based on headers.tsv knowledge)
    int_cols = [
        'ambig_basecount', 'ambig_full_basecount', 'ambig_original',
        'stop_codons', 'nuc_basecount', 'nuc_full_basecount',
        'n_reads_aligned', 'n_reads_in', 'n_reads_skipped',
        'ref_length', 'cleaning_ambig_bases', 'cleaning_removed_at',
        'cleaning_removed_human', 'cleaning_removed_outlier',
        'cleaning_removed_reference', 'length',
        's', 'validation_steps', 'assembly_params'
    ]
    
    for col in int_cols:
        if col in df.columns:
            # Convert to numeric, coercing errors to NA
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    
    # Float columns
    float_cols = [
        'r', 'cov_min', 'cov_max', 'cov_avg', 'cov_med',
        'cleaning_cov_percent'
    ]
    
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def calculate_gzip_md5(filepath: Path) -> str:
    """Calculate MD5 hash of a gzip file.
    
    Args:
        filepath: Path to gzip file
        
    Returns:
        MD5 hash string
    """
    md5_hash = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def generate_datapackage_json(
    output_file: Path,
    type_info: Dict[str, Dict],
    headers_info: pd.DataFrame
) -> Dict:
    """Generate frictionless data package JSON metadata.
    
    Args:
        output_file: Path to the output TSV.GZ file
        type_info: Column type information
        headers_info: DataFrame with column definitions
        
    Returns:
        Dictionary containing the data package metadata
    """
    # Calculate MD5 hash of the output file
    file_hash = calculate_gzip_md5(output_file)
    
    # Create field definitions
    fields = []
    for col_name in sorted(type_info.keys()):
        info = type_info[col_name]
        field = {
            'name': info['name'],
            'type': info['type'],
            'format': info['format'],
            'description': info['description']
        }
        
        # Add constraints if any
        if info.get('constraints'):
            field['constraints'] = info['constraints']
        
        fields.append(field)
    
    # Create the data package structure
    datapackage = {
        'name': 'bge-skimming-analytics',
        'title': 'BGE Skimming Analytics - Merged Dataset',
        'description': 'Merged dataset containing all barcode validation results from BGE genome skimming project',
        'version': '1.0.0',
        'licenses': [
            {
                'name': 'CC-BY-SA-4.0',
                'title': 'Creative Commons Attribution Share-Alike 4.0',
                'path': 'https://creativecommons.org/licenses/by-sa/4.0/'
            }
        ],
        'contributors': [
            {
                'title': 'BGE Consortium',
                'role': 'author'
            }
        ],
        'profile': 'tabular-data-resource',
        'resources': [
            {
                'name': 'bge-skimming-analytics',
                'path': output_file.name,
                'hash': f'md5:{file_hash}',
                'profile': 'tabular-data-resource',
                'encoding': 'utf-8',
                'compression': 'gzip',
                'schema': {
                    'fields': fields
                }
            }
        ]
    }
    
    return datapackage


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Merge all TSV files in data directory into a single gzip-compressed file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview merge without writing output'
    )
    args = parser.parse_args()
    
    setup_logging()
    
    # Set paths
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / 'data'
    metadata_dir = repo_root / 'metadata'
    output_file = data_dir / 'bge-skimming-analytics.tsv.gz'
    datapackage_file = data_dir / 'datapackage.json'
    headers_file = metadata_dir / 'headers.tsv'
    
    # Load headers.tsv for column definitions
    logging.info(f"Loading column definitions from {headers_file}")
    headers_info = pd.read_csv(headers_file, sep='\t')
    
    # Find all TSV files
    logging.info(f"Finding TSV files in {data_dir}")
    tsv_files = find_all_tsv_files(data_dir)
    logging.info(f"Found {len(tsv_files)} TSV files")
    
    if len(tsv_files) == 0:
        logging.error("No TSV files found")
        return 1
    
    # Collect all columns
    logging.info("Collecting column names from all files")
    all_columns = collect_all_columns(tsv_files)
    logging.info(f"Found {len(all_columns)} unique columns")
    
    if args.dry_run:
        logging.info("Dry run mode - would merge files with these columns:")
        for col in sorted(all_columns):
            logging.info(f"  - {col}")
        return 0
    
    # Merge all files
    logging.info("Merging all TSV files...")
    merged_df = merge_tsv_files(tsv_files, all_columns)
    logging.info(f"Merged DataFrame shape: {merged_df.shape}")
    
    # Standardize missing values
    logging.info("Standardizing missing values...")
    merged_df = standardize_missing_values(merged_df)
    
    # Standardize boolean columns
    logging.info("Standardizing boolean columns...")
    boolean_cols = ['fcleaner', 'merge']
    merged_df = standardize_boolean_columns(merged_df, boolean_cols)
    
    # Convert to appropriate dtypes
    logging.info("Converting column types...")
    merged_df = convert_dtypes(merged_df)
    
    # Write merged file as gzip-compressed TSV
    logging.info(f"Writing compressed merged file to {output_file}")
    with gzip.open(output_file, 'wt', encoding='utf-8') as f:
        merged_df.to_csv(f, sep='\t', index=False, na_rep='')
    
    # Check file sizes
    uncompressed_size = len(merged_df.to_csv(sep='\t', index=False, na_rep=''))
    compressed_size = output_file.stat().st_size
    compression_ratio = (1 - compressed_size / uncompressed_size) * 100
    
    logging.info(f"Uncompressed size: {uncompressed_size / (1024*1024):.2f} MB")
    logging.info(f"Compressed size: {compressed_size / (1024*1024):.2f} MB")
    logging.info(f"Compression ratio: {compression_ratio:.1f}%")
    
    # Infer column types for metadata
    logging.info("Inferring column types for metadata...")
    type_info = infer_column_types(merged_df, headers_info)
    
    # Generate datapackage.json
    logging.info("Generating datapackage.json...")
    datapackage = generate_datapackage_json(output_file, type_info, headers_info)
    
    # Write datapackage.json
    logging.info(f"Writing datapackage.json to {datapackage_file}")
    with open(datapackage_file, 'w') as f:
        json.dump(datapackage, f, indent=2)
    
    logging.info("Done!")
    logging.info(f"Output files:")
    logging.info(f"  - {output_file} ({compressed_size / (1024*1024):.2f} MB)")
    logging.info(f"  - {datapackage_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
