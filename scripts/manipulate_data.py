#!/usr/bin/env python3
"""
Script to manipulate data before uploading or after querying.

This script provides a skeleton for future data manipulation.
Users can modify the process_data function according to their needs.
"""
import os
import sys
import argparse
from typing import List, Dict

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.salesforce import SalesforceClient
from src.utils import setup_logging, read_csv


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Manipulate data using Python.')
    parser.add_argument('csv_file', help='Path to the CSV file to manipulate')
    parser.add_argument('--config', default='config/config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--output', default='output/modified_data.csv',
                        help='Path to save the manipulated CSV')
    return parser.parse_args()


def process_data(records: List[Dict]) -> List[Dict]:
    """
    Manipulate records as needed. This is a placeholder
    function; modify it according to your requirements.
    """
    # Example manipulation: Trim whitespace from every field
    new_records = []
    for row in records:
        new_row = {k: v.strip() if isinstance(v, str) else v
                   for k, v in row.items()}
        new_records.append(new_row)
    return new_records


def write_csv(filepath: str, records: List[Dict]) -> None:
    """Write the manipulated records to CSV."""
    if not records:
        print("No records to write.")
        return

    import csv

    fieldnames = list(records[0].keys())
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    args = parse_args()
    logger = setup_logging(args.config)

    try:
        # Read CSV data
        records = read_csv(args.csv_file, args.config)
        logger.info(f"Read {len(records)} records from {args.csv_file}")

        # Manipulate the data here
        manipulated = process_data(records)

        # Write out manipulated data
        write_csv(args.output, manipulated)
        logger.info(f"Manipulated data written to {args.output}")

    except Exception as e:
        logger.error(f"Error manipulating data: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()