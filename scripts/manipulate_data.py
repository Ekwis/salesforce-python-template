#!/usr/bin/env python3
"""
Script to demonstrate data enrichment and Salesforce integration.

This script shows how to:
1. Query a Salesforce record by ID and object type
2. Search the internet for additional company information using web scraping
3. Update specific fields in Salesforce with enriched data after user confirmation
"""

import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils import setup_logging
from src.salesforce import SalesforceClient
from typing import List, Dict, Optional, Tuple, Set
from bs4 import BeautifulSoup
import requests
import yaml
import argparse
import time
import json
import re
import os
from pathlib import Path
import sys

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Enrich Salesforce record data with information found online.')
    parser.add_argument(
        'record_id',
        help='Salesforce Record ID to enrich'
    )
    parser.add_argument(
        'sobject_type',
        help='Salesforce Object Type (e.g., Account, Contact, Lead)'
    )
    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--fields',
        nargs='+',
        help='Specific fields to update (space-separated). If not provided, will use defaults from config.'
    )
    return parser.parse_args()


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def get_default_fields(config: Dict, sobject_type: str) -> Set[str]:
    """Get default updateable fields for the given SObject type."""
    defaults = {
        'Account': {
            'Phone', 'Website', 'BillingStreet', 'BillingCity',
            'BillingState', 'BillingPostalCode', 'BillingCountry'
        },
        'Contact': {
            'Phone', 'Email', 'MailingStreet', 'MailingCity',
            'MailingState', 'MailingPostalCode', 'MailingCountry'
        },
        'Lead': {
            'Phone', 'Email', 'Street', 'City',
            'State', 'PostalCode', 'Country'
        }
    }

    # Use config if available, otherwise use defaults
    return set(config.get('enrichment', {}).get('fields', {}).get(sobject_type, defaults.get(sobject_type, set())))


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    return ' '.join(text.strip().split())


def extract_phone_number(text: str) -> Optional[str]:
    """Extract phone number from text using regex."""
    patterns = [
        r'\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US/Canada
        # International
        r'\+?[0-9]{1,4}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{2,4}'
    ]

    for pattern in patterns:
        if match := re.search(pattern, text):
            return clean_text(match.group(0))
    return None


def extract_email(text: str) -> Optional[str]:
    """Extract email from text using regex."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if match := re.search(pattern, text):
        return match.group(0).lower()
    return None


def extract_address(soup: BeautifulSoup) -> Optional[str]:
    """Extract address from common webpage patterns."""
    address_indicators = ['address', 'location', 'headquarters', 'contact']
    for indicator in address_indicators:
        for element in soup.find_all(['div', 'p', 'span'],
                                     class_=lambda x: x and indicator in x.lower()):
            text = clean_text(element.get_text())
            if re.search(r'\d+.*(?:street|st|avenue|ave|road|rd|boulevard|blvd)',
                         text, re.IGNORECASE):
                return text
    return None


def search_company_info(company_name: str) -> Dict:
    """Search for company information online using web scraping."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        search_query = f"{company_name} company contact"
        search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"

        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        company_url = None
        for result in soup.find_all('a'):
            href = result.get('href', '')
            if 'url?q=' in href and not any(x in href for x in ['google.com', 'youtube.com', 'facebook.com']):
                company_url = href.split('url?q=')[1].split('&')[0]
                break

        if not company_url:
            raise ValueError("Could not find company website")

        response = requests.get(company_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()

        return {
            'phone': extract_phone_number(text_content) or '',
            'email': extract_email(text_content) or '',
            'address': extract_address(soup) or '',
            'website': company_url
        }

    except Exception as e:
        print(f"Warning: Error during web scraping: {str(e)}")
        return {
            'phone': '',
            'email': '',
            'address': '',
            'website': ''
        }


def get_salesforce_record(sf_client: SalesforceClient, record_id: str,
                          sobject_type: str, fields: Set[str]) -> Optional[Dict]:
    """Query Salesforce for a record by ID."""
    # Always include Id and Name fields
    query_fields = list(fields | {'Id', 'Name'})

    soql = f"""
        SELECT {', '.join(query_fields)}
        FROM {sobject_type}
        WHERE Id = '{record_id}'
    """

    try:
        results = sf_client.query(soql)
        return results[0] if results else None
    except Exception as e:
        print(f"Error querying Salesforce: {str(e)}")
        return None


def prepare_record_update(record_id: str, enriched_data: Dict,
                          sobject_type: str, fields: Set[str]) -> Dict:
    """Prepare the record data for Salesforce update based on object type."""
    update_data = {'Id': record_id}

    # Map enriched data to Salesforce fields based on object type
    field_mappings = {
        'Account': {
            'phone': 'Phone',
            'website': 'Website',
            'address': ['BillingStreet', 'BillingCity', 'BillingState',
                        'BillingPostalCode', 'BillingCountry']
        },
        'Contact': {
            'phone': 'Phone',
            'email': 'Email',
            'address': ['MailingStreet', 'MailingCity', 'MailingState',
                        'MailingPostalCode', 'MailingCountry']
        },
        'Lead': {
            'phone': 'Phone',
            'email': 'Email',
            'address': ['Street', 'City', 'State', 'PostalCode', 'Country']
        }
    }

    mapping = field_mappings.get(sobject_type, {})

    # Add simple field mappings if they're in the fields to update
    for source, target in mapping.items():
        if isinstance(target, str) and target in fields:
            update_data[target] = enriched_data[source]

    # Handle address fields if any are in the fields to update
    if isinstance(mapping.get('address'), list):
        address = enriched_data.get('address', '')
        if address:
            # Split address into parts and clean up
            parts = [p.strip() for p in address.split(',')]

            # Handle different address formats
            if len(parts) >= 4:  # Full address with suite/unit
                street_parts = parts[0:2]  # Include both street and suite
                city = parts[-3].strip()
                state = parts[-2].strip()
                postal = parts[-1].strip()
            elif len(parts) == 3:  # Basic address format
                street_parts = [parts[0]]
                city = parts[1].strip()
                state = parts[2].strip()
                postal = ''
            else:
                return update_data  # Invalid address format

            address_fields = mapping['address']
            if address_fields[0] in fields:  # Street
                update_data[address_fields[0]] = ', '.join(street_parts)
            if address_fields[1] in fields:  # City
                update_data[address_fields[1]] = city
            if address_fields[2] in fields:  # State
                update_data[address_fields[2]] = state
            if address_fields[3] in fields and postal:  # PostalCode
                update_data[address_fields[3]] = re.sub(r'[^\d]', '', postal)
            if address_fields[4] in fields:  # Country
                update_data[address_fields[4]] = 'United States'

    return update_data


def update_salesforce_record(sf_client: SalesforceClient, update_data: Dict,
                             sobject_type: str) -> bool:
    """Update the record in Salesforce."""
    try:
        result = getattr(sf_client.sf, sobject_type).update(
            update_data['Id'], update_data)
        return True
    except Exception as e:
        print(f"Error updating Salesforce: {str(e)}")
        return False


def get_user_confirmation() -> bool:
    """Get user confirmation for the update."""
    while True:
        response = input(
            "\nWould you like to proceed with the update? (yes/no): ").lower()
        if response in ['yes', 'y']:
            return True
        if response in ['no', 'n']:
            return False
        print("Please answer 'yes' or 'no'")


def main():
    args = parse_args()
    logger = setup_logging(args.config)
    config = load_config(args.config)

    try:
        # Initialize Salesforce client
        sf_client = SalesforceClient(args.config)

        # Get fields to update (from args or config)
        updateable_fields = set(args.fields) if args.fields else get_default_fields(
            config, args.sobject_type)

        # Step 1: Find the record in Salesforce
        record = get_salesforce_record(
            sf_client, args.record_id, args.sobject_type, updateable_fields)
        if not record:
            logger.error(
                f"Record with ID '{args.record_id}' not found in {args.sobject_type}")
            return

        logger.info(f"Found {args.sobject_type}: {record['Name']}")

        # Step 2: Search for additional information
        logger.info("Searching for additional information...")
        enriched_data = search_company_info(record['Name'])

        # Step 3: Prepare the update
        update_data = prepare_record_update(args.record_id, enriched_data,
                                            args.sobject_type, updateable_fields)

        # Step 4: Show what would be updated
        logger.info("The following updates would be made to Salesforce:")
        print("\nCurrent Salesforce Data:")
        print(json.dumps(record, indent=2))
        print("\nProposed Updates:")
        print(json.dumps(update_data, indent=2))

        # Step 5: Get user confirmation and update
        if get_user_confirmation():
            logger.info(f"Updating {args.sobject_type}...")
            if update_salesforce_record(sf_client, update_data, args.sobject_type):
                logger.info(f"Successfully updated {args.sobject_type}!")
            else:
                logger.error(f"Failed to update {args.sobject_type}")
        else:
            logger.info("Update cancelled by user")

    except Exception as e:
        logger.error(f"Error processing record: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()