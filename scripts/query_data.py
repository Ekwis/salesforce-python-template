#!/usr/bin/env python3
"""
Script to query data from Salesforce and save to CSV.
"""
import os
import sys
import csv
import argparse
from typing import List, Dict

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.salesforce import SalesforceClient
from src.utils import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Query Salesforce data and save to CSV')
    parser.add_argument('soql', help='SOQL query to execute')
    parser.add_argument('output_file', help='Path to save the output CSV file')
    parser.add_argument('--config', default='config/config.yaml',
                        help='Path to configuration file')
    return parser.parse_args()


def save_to_csv(records: List[Dict], output_file: str, config_path: str) -> None:
    """Save query results to CSV file."""
    if not records:
        return

    # Create output directory if it does not exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Get field names from first record
    fieldnames = list(records[0].keys())

    logger = setup_logging(config_path)
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
    except Exception as e:
        logger.error(f"Error saving to CSV file {output_file}: {str(e)}")
        raise


def main():
    """Main function to handle Salesforce queries."""
    args = parse_args()
    logger = setup_logging(args.config)

    try:
        # Initialise Salesforce client
        sf = SalesforceClient(args.config)
        logger.info(f"Initialised connection to Salesforce. Session ID is {sf.sf.session_id}")

        # Execute query
        logger.info(f"Executing query: {args.soql}")
        records = sf.query(args.soql)
        logger.info(f"Retrieved {len(records)} records")

        # Save results to CSV
        save_to_csv(records, args.output_file, args.config)
        logger.info(f"Results saved to {args.output_file}")

    except Exception as e:
        logger.error(f"Error during query: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()