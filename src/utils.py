"""
Utility functions for logging and data processing.
"""
import logging
import os
import csv
from typing import Dict, List, Optional
import yaml
from datetime import datetime


def setup_logging(config_path: str = 'config/config.yaml') -> logging.Logger:
    """Set up logging configuration."""
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(config['logging']['file']), exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=config['logging']['level'],
        format=config['logging']['format'],
        handlers=[
            logging.FileHandler(config['logging']['file']),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)


def read_csv(filepath: str, config_path: str = 'config/config.yaml') -> List[Dict]:
    """Read CSV file and return list of dictionaries."""
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    data = []
    try:
        with open(filepath, 'r', encoding=config['csv']['encoding']) as f:
            reader = csv.DictReader(f, delimiter=config['csv']['delimiter'])
            data = [row for row in reader]
    except Exception as e:
        logger = setup_logging(config_path)
        logger.error(f"Error reading CSV file {filepath}: {str(e)}")
        raise

    return data


def save_failed_records(records: List[Dict], original_filename: str,
                        config_path: str = 'config/config.yaml') -> str:
    """Save failed records to a new CSV file in the error directory."""
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Create error directory if it doesn't exist
    os.makedirs(config['csv']['error_directory'], exist_ok=True)

    # Generate error filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"failed_{os.path.basename(original_filename)}_{timestamp}.csv"
    filepath = os.path.join(config['csv']['error_directory'], filename)

    try:
        if records:
            with open(filepath, 'w', encoding=config['csv']['encoding'], newline='') as f:
                writer = csv.DictWriter(f, fieldnames=records[0].keys(),
                                        delimiter=config['csv']['delimiter'])
                writer.writeheader()
                writer.writerows(records)
    except Exception as e:
        logger = setup_logging(config_path)
        logger.error(f"Error saving failed records to {filepath}: {str(e)}")
        raise

    return filepath


def chunk_list(data: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
