#!/usr/bin/env python3
"""
Script to upload CSV data to Salesforce.
"""
from src.salesforce import SalesforceClient
from src.utils import setup_logging, read_csv, save_failed_records, chunk_list
import os
import sys
import argparse
from typing import List, Dict

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Upload CSV data to Salesforce')
    parser.add_argument('csv_file', help='Path to the CSV file to upload')
    parser.add_argument(
        'object_name', help='Salesforce object name (e.g., Account, Contact)')
    parser.add_argument('--config', default='config/config.yaml',
                        help='Path to configuration file')
    return parser.parse_args()


def process_results(results: List[Dict], records: List[Dict],
                    csv_file: str, logger) -> None:
    """Process bulk upload results and handle failures."""
    failed_records = []

    for result, record in zip(results, records):
        if not result['success']:
            logger.error(f"Failed to upload record: {result['errors']}")
            failed_records.append(record)

    if failed_records:
        error_file = save_failed_records(failed_records, csv_file)
        logger.info(f"Failed records saved to: {error_file}")

    success_count = len(records) - len(failed_records)
    logger.info(f"Successfully uploaded {success_count} records")
    logger.info(f"Failed to upload {len(failed_records)} records")


def main():
    """Main function to handle CSV upload to Salesforce."""
    args = parse_args()
    logger = setup_logging(args.config)

    try:
        # Initialize Salesforce client
        sf = SalesforceClient(args.config)
        logger.info(f"Connected to Salesforce as {sf.sf.session_id}")

        # Read CSV data
        records = read_csv(args.csv_file, args.config)
        logger.info(f"Read {len(records)} records from {args.csv_file}")

        # Process in chunks
        chunk_size = sf.config['api']['batch_size']
        for i, chunk in enumerate(chunk_list(records, chunk_size)):
            logger.info(
                f"Processing chunk {i+1} of {len(records)//chunk_size + 1}")
            results = sf.bulk_insert(args.object_name, chunk)
            process_results(results, chunk, args.csv_file, logger)

    except Exception as e:
        logger.error(f"Error during upload: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
