#!/usr/bin/env python3
"""
Script to upload CSV data to Salesforce, with optional field mapping.
"""
import os
import sys
import argparse
from typing import List, Dict

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.salesforce import SalesforceClient
from src.utils import setup_logging, read_csv, save_failed_records, chunk_list


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Upload CSV data to Salesforce (with optional field mapping).')
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


def prompt_field_mapping(records: List[Dict], logger) -> Dict[str, str]:
    """
    Prompt the user to map CSV fields to Salesforce fields.
    Returns a dictionary mapping {original_field_name: new_field_name}.
    """
    if not records:
        logger.warning("No records found in CSV, skipping field mapping.")
        return {}

    fieldnames = list(records[0].keys())
    field_mapping = {}

    logger.info("Starting interactive field mapping...")
    for field in fieldnames:
        response = input(f"Do you want to map the field '{field}'? (y/n): ").strip().lower()
        if response == 'y':
            new_name = input(
                f"Enter the Salesforce field name to map '{field}' to. "
                f"(Press Enter to keep '{field}'): ").strip()
            if new_name:
                field_mapping[field] = new_name
            else:
                field_mapping[field] = field
        else:
            # If user does not want to map, we keep the original name
            field_mapping[field] = field

    return field_mapping


def apply_field_mapping(records: List[Dict], field_mapping: Dict[str, str]) -> None:
    """
    Apply the field mapping to the list of records in-place.
    """
    for record in records:
        for old_field, new_field in list(field_mapping.items()):
            if old_field in record and new_field != old_field:
                record[new_field] = record.pop(old_field)


def main():
    """Main function to handle CSV upload to Salesforce."""
    args = parse_args()
    logger = setup_logging(args.config)

    try:
        # Initialise Salesforce client
        sf = SalesforceClient(args.config)
        logger.info(f"Initialised connection to Salesforce. Session ID is {sf.sf.session_id}")

        # Read CSV data
        records = read_csv(args.csv_file, args.config)
        logger.info(f"Read {len(records)} records from {args.csv_file}")

        # Field mapping (interactive)
        field_mapping = prompt_field_mapping(records, logger)
        apply_field_mapping(records, field_mapping)

        # Process in chunks
        chunk_size = sf.config['api']['batch_size']
        total_chunks = (len(records) + chunk_size - 1) // chunk_size  # ceiling division
        for i, chunk in enumerate(chunk_list(records, chunk_size), start=1):
            logger.info(f"Processing chunk {i} of {total_chunks}")
            results = sf.bulk_insert(args.object_name, chunk)
            process_results(results, chunk, args.csv_file, logger)

    except Exception as e:
        logger.error(f"Error during upload: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()