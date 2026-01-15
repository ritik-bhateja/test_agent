#!/usr/bin/env python3
"""
Script to analyze insurance_synthetic_data.csv and generate column list with data types.
This script extracts all column names and determines appropriate data types based on sample data.
"""

import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

def infer_data_type(values):
    """
    Infer the data type for a column based on sample values.
    Returns: STRING, INTEGER, DECIMAL, or TIMESTAMP
    """
    # Remove empty/null values for analysis
    non_empty_values = [v for v in values if v and v.strip() and v.lower() not in ('', 'null', 'nan', 'none')]
    
    if not non_empty_values:
        return "STRING"  # Default for empty columns
    
    # Check if all values are integers
    all_integers = True
    all_decimals = True
    all_timestamps = True
    
    for value in non_empty_values:
        value = value.strip()
        
        # Check for timestamp patterns (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
        timestamp_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
        ]
        
        is_timestamp = any(re.match(pattern, value) for pattern in timestamp_patterns)
        if not is_timestamp:
            all_timestamps = False
        
        # Check for integer
        try:
            int_val = int(float(value))
            if float(value) != int_val:
                all_integers = False
        except (ValueError, InvalidOperation):
            all_integers = False
        
        # Check for decimal/numeric
        try:
            Decimal(value)
        except (ValueError, InvalidOperation):
            all_decimals = False
    
    # Determine type based on checks
    if all_timestamps:
        return "TIMESTAMP"
    elif all_integers:
        return "INTEGER"
    elif all_decimals:
        return "DECIMAL"
    else:
        return "STRING"

def analyze_csv(filepath):
    """
    Analyze CSV file and return list of (column_name, data_type) tuples.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Read sample rows to analyze data types
        sample_rows = []
        for i, row in enumerate(reader):
            sample_rows.append(row)
            if i >= 99:  # Analyze first 100 rows
                break
        
        # Transpose to get column values
        columns_data = {}
        for col_idx, header in enumerate(headers):
            column_values = [row[col_idx] if col_idx < len(row) else '' for row in sample_rows]
            columns_data[header] = column_values
        
        # Infer data types
        results = []
        for header in headers:
            data_type = infer_data_type(columns_data[header])
            results.append((header, data_type))
        
        return results

def main():
    csv_path = '.kiro/sample_data/insurance_synthetic_data.csv'
    
    print("Analyzing insurance_synthetic_data.csv...")
    print("=" * 80)
    
    column_types = analyze_csv(csv_path)
    
    print(f"\nTotal columns found: {len(column_types)}")
    print("\nFormatted column list with data types:")
    print("=" * 80)
    
    for col_name, data_type in column_types:
        print(f"- {col_name} ({data_type})")
    
    print("\n" + "=" * 80)
    print(f"Analysis complete. Total: {len(column_types)} columns")
    
    # Save to file for reference
    output_file = 'insurance_columns_with_types.txt'
    with open(output_file, 'w') as f:
        f.write("INSURANCE_DATA Table Columns\n")
        f.write("=" * 80 + "\n\n")
        for col_name, data_type in column_types:
            f.write(f"- {col_name} ({data_type})\n")
        f.write(f"\nTotal: {len(column_types)} columns\n")
    
    print(f"\nColumn list saved to: {output_file}")

if __name__ == "__main__":
    main()
