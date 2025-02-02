#!/usr/bin/env python3
"""
Script to query data from Salesforce and save to CSV.
"""
from src.utils import setup_logging
from src.salesforce import SalesforceClient
import argparse
import csv
import os
import sys
from typing import List, Dict

# Add parent directory to Python path for importing local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Get field names from first record
    fieldnames = list(records[0].keys())

    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
    except Exception as e:
        logger = setup_logging(config_path)
        logger.error(f"Error saving to CSV file {output_file}: {str(e)}")
        raise


def main():
    """Main function to handle Salesforce queries."""
    args = parse_args()
    logger = setup_logging(args.config)

    try:
        # Initialize Salesforce client
        sf = SalesforceClient(args.config)
        logger.info(f"Connected to Salesforce as {sf.sf.session_id}")

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
