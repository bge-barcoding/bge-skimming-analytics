#!/usr/bin/env python3
"""
Merge taxval and structval TSV files produced by barcode_validator.

Combines two TSV files by matching sequence IDs, replacing null values with 
actual data, combining dataset paths if conflicts arise, and adding missing columns from both files.

Usage: python bv_metrics_merger.py -t taxval.tsv -s structval.tsv -o merged.tsv

Optional:
--key [column_header]: column header in both TSVs to merge on (default: sequence_id)
"""
import pandas as pd
import sys
import argparse
from pathlib import Path

def is_null_value(value):
    null_values = {'None', 'none', 'Null', 'null', 'NA', 'na', '', 'NULL', None}
    return pd.isna(value) or str(value).strip() in null_values

def find_tsv_in_directory(directory_path, file_type=""):
    directory = Path(directory_path)
    if not directory.is_dir():
        return directory_path
    
    # Look for TSV files
    tsv_files = list(directory.glob("*.tsv"))
    
    if not tsv_files:
        return None
    
    if file_type:
        matching_files = [f for f in tsv_files if file_type.lower() in f.name.lower()]
        if matching_files:
            return str(matching_files[0])
    
    # Return the first TSV file found
    return str(tsv_files[0])

def merge_tsv_files(taxval_path, structval_path, output_path, key_column='sequence_id'):  
    # Read TSV files
    print(f"Reading {taxval_path}...")
    taxval_df = pd.read_csv(taxval_path, sep='\t', dtype=str, keep_default_na=False)
    
    print(f"Reading {structval_path}...")
    structval_df = pd.read_csv(structval_path, sep='\t', dtype=str, keep_default_na=False)
    
    print(f"Taxval shape: {taxval_df.shape}")
    print(f"Structval shape: {structval_df.shape}")
    
    # Get all unique columns from both files
    all_columns = list(set(taxval_df.columns.tolist() + structval_df.columns.tolist()))
    all_columns.sort()  # Sort for consistent output
    
    # Find columns unique to each file
    taxval_only = set(taxval_df.columns) - set(structval_df.columns)
    structval_only = set(structval_df.columns) - set(taxval_df.columns)
    common_columns = set(taxval_df.columns) & set(structval_df.columns)
    
    # Create a comprehensive merge on the key column
    merged_df = pd.merge(
        taxval_df, structval_df, 
        on=key_column, 
        how='outer', 
        suffixes=('_taxval', '_structval')
    )
    
    print(f"Merged shape before cleanup: {merged_df.shape}")
    
    result_df = pd.DataFrame()
    result_df[key_column] = merged_df[key_column]
    
    unresolvable_conflicts = []
    dataset_combinations = 0
    null_replacements = 0
    
    # Process each column
    for col in all_columns:
        if col == key_column:
            continue
            
        taxval_col = f"{col}_taxval" if f"{col}_taxval" in merged_df.columns else col
        structval_col = f"{col}_structval" if f"{col}_structval" in merged_df.columns else col
        
        result_values = []
        
        for idx in range(len(merged_df)):
            taxval_val = merged_df[taxval_col].iloc[idx] if taxval_col in merged_df.columns else None
            structval_val = merged_df[structval_col].iloc[idx] if structval_col in merged_df.columns else None
            
            taxval_is_null = is_null_value(taxval_val)
            structval_is_null = is_null_value(structval_val)
            
            # Special handling for 'dataset' column - always combine
            if col == 'dataset':
                paths = []
                if not structval_is_null:
                    paths.append(str(structval_val))
                if not taxval_is_null:
                    paths.append(str(taxval_val))
                
                if len(paths) == 2:
                    result_values.append(f"{paths[0]}; {paths[1]}")
                    dataset_combinations += 1
                elif len(paths) == 1:
                    result_values.append(paths[0])
                else:
                    result_values.append('')
            
            # Standard null replacement logic for other columns
            elif taxval_is_null and structval_is_null:
                # Both null - keep null
                result_values.append('')
            elif taxval_is_null and not structval_is_null:
                # Taxval null, structval has data - use structval
                result_values.append(structval_val)
                null_replacements += 1
            elif not taxval_is_null and structval_is_null:
                # Structval null, taxval has data - use taxval
                result_values.append(taxval_val)
                null_replacements += 1
            elif taxval_val == structval_val:
                # Both have same value - use either
                result_values.append(taxval_val)
            else:
                # Unresolvable conflict - both have different non-null values
                # Default to structval but report as conflict to log
                sample_id = merged_df[key_column].iloc[idx]
                unresolvable_conflicts.append({
                    'sample_id': sample_id,
                    'column': col,
                    'taxval': taxval_val,
                    'structval': structval_val,
                    'chosen': structval_val
                })
                result_values.append(structval_val)
        
        result_df[col] = result_values
    
    # Report processing summary
    print(f"\nProcessing Summary:")
    print(f"Dataset path combinations: {dataset_combinations}")
    print(f"Null value replacements: {null_replacements}")
    print(f"Unresolvable conflicts: {len(unresolvable_conflicts)}")
    
    # Report unresolvable conflicts
    if unresolvable_conflicts:
        print(f"\nFound {len(unresolvable_conflicts)} unresolvable conflicts:")
        for conflict in unresolvable_conflicts[:10]:  # Show first 10
            print(f"  Sample {conflict['sample_id']}, Column '{conflict['column']}':")
            print(f"    Taxval: '{conflict['taxval']}'")
            print(f"    Structval: '{conflict['structval']}'") 
            print(f"    Chosen: '{conflict['chosen']}'")
        if len(unresolvable_conflicts) > 10:
            print(f"    ... and {len(unresolvable_conflicts) - 10} more conflicts")
    
    # Reorder columns to match original order (taxval first, then structval-only columns)
    original_order = []
    
    for col in taxval_df.columns:
        if col in result_df.columns:
            original_order.append(col)
    
    structval_only_sorted = sorted(list(structval_only))
    for col in structval_only_sorted:
        if col in result_df.columns:
            original_order.append(col)
    
    result_df = result_df[original_order]
    
    # Write the merged file
    print(f"\nWriting merged file to {output_path}...")
    result_df.to_csv(output_path, sep='\t', index=False)
    
    print(f"Merge completed!")
    print(f"Final shape: {result_df.shape}")
    print(f"Added columns from structval: {list(structval_only)}")
    print(f"Added columns from taxval: {list(taxval_only)}")
    
    return result_df, unresolvable_conflicts

def main():
    parser = argparse.ArgumentParser(
        description='Merge taxval and structval TSV files from barcode_validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Merge Rules:
1. dataset column: combine paths (structval; taxval)
2. Missing columns: add to merged TSV
3. Null/None replacement: use actual data over null values

Examples:
  python bv_metrics_merger.py -t taxval.tsv -s structval.tsv -o merged.tsv
  python bv_metrics_merger.py --taxval data/taxval.tsv --structval data/structval.tsv --output results/merged.tsv --key ID
        """
    )
    
    parser.add_argument(
        '-t', '--taxval',
        required=True,
        help='Path to the taxval TSV file'
    )
    
    parser.add_argument(
        '-s', '--structval', 
        required=True,
        help='Path to the structval TSV file'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Path for the merged output TSV file'
    )
    
    parser.add_argument(
        '-k', '--key',
        default='sequence_id',
        help='Column name to use for matching rows (default: sequence_id)'
    )
    
    parser.add_argument(
        '--no-conflicts-report',
        action='store_true',
        help='Skip generating the conflicts report file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Handle directory inputs - try to auto-detect TSV files
    taxval_file = find_tsv_in_directory(args.taxval, "taxval")
    structval_file = find_tsv_in_directory(args.structval, "structval")
    
    if taxval_file is None:
        if Path(args.taxval).is_dir():
            print(f"Error: No TSV files found in taxval directory: {args.taxval}")
            tsv_files = list(Path(args.taxval).glob("*"))
            if tsv_files:
                print(f"   Files found: {[f.name for f in tsv_files[:5]]}")
        else:
            print(f"Error: Taxval file not found: {args.taxval}")
        sys.exit(1)
    
    if structval_file is None:
        if Path(args.structval).is_dir():
            print(f"Error: No TSV files found in structval directory: {args.structval}")
            tsv_files = list(Path(args.structval).glob("*"))
            if tsv_files:
                print(f"   Files found: {[f.name for f in tsv_files[:5]]}")
        else:
            print(f"Error: Structval file not found: {args.structval}")
        sys.exit(1)
    
    # Validate the detected/provided files exist
    if not Path(taxval_file).exists():
        print(f"Error: Taxval file not found: {taxval_file}")
        sys.exit(1)
        
    if not Path(structval_file).exists():
        print(f"Error: Structval file not found: {structval_file}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.verbose:
        print(f"Configuration:")
        print(f"  Taxval file: {taxval_file}")
        print(f"  Structval file: {structval_file}")
        print(f"  Output file: {args.output}")
        print(f"  Key column: {args.key}")
        print(f"  Generate conflicts report: {not args.no_conflicts_report}")
    
    try:
        merged_df, conflicts = merge_tsv_files(
            taxval_file, 
            structval_file, 
            args.output,
            key_column=args.key
        )
        
        # Save conflicts report if any unresolvable conflicts and not disabled
        if conflicts and not args.no_conflicts_report:
            conflicts_path = str(output_path).replace('.tsv', '_conflicts.txt')
            with open(conflicts_path, 'w') as f:
                f.write("Unresolvable Data Conflicts Report\n")
                f.write("===================================\n\n")
                f.write("These are conflicts where both files had different non-null values.\n")
                f.write("The structval value was chosen in each case.\n\n")
                
                for conflict in conflicts:
                    f.write(f"Sample: {conflict['sample_id']}\n")
                    f.write(f"Column: {conflict['column']}\n")
                    f.write(f"Taxval value: {conflict['taxval']}\n")
                    f.write(f"Structval value: {conflict['structval']}\n")
                    f.write(f"Chosen value: {conflict['chosen']}\n")
                    f.write("-" * 50 + "\n")
            print(f"Unresolvable conflicts report saved to: {conflicts_path}")
        elif conflicts and args.no_conflicts_report:
            print(f"{len(conflicts)} unresolvable conflicts found (report generation skipped)")
            
    except Exception as e:
        print(f"Error during merge: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
