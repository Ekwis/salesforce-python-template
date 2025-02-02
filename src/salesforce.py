"""
Salesforce connection and operations module.
"""
import os
from typing import Dict, List, Optional, Union
import yaml
from dotenv import load_dotenv
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError


class SalesforceClient:
    """Handles Salesforce authentication and operations."""

    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize Salesforce client with configuration."""
        load_dotenv()

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize Salesforce connection
        self.sf = self._authenticate()

    def _authenticate(self) -> Salesforce:
        """Authenticate with Salesforce using environment variables."""
        try:
            return Salesforce(
                username=os.getenv('SALESFORCE_USERNAME'),
                password=os.getenv('SALESFORCE_PASSWORD'),
                security_token=os.getenv('SALESFORCE_SECURITY_TOKEN'),
                domain=os.getenv('SALESFORCE_DOMAIN', 'login'),
                version=self.config['api']['version']
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Salesforce: {str(e)}")

    def query(self, soql: str) -> List[Dict]:
        """Execute a SOQL query and return results."""
        try:
            results = self.sf.query(soql)
            return results['records']
        except SalesforceError as e:
            raise Exception(f"Query failed: {str(e)}")

    def bulk_insert(self, object_name: str, data: List[Dict]) -> List[Dict]:
        """Insert multiple records using bulk API."""
        try:
            results = self.sf.bulk.__getattr__(object_name).insert(data)
            return results
        except SalesforceError as e:
            raise Exception(f"Bulk insert failed: {str(e)}")

    def bulk_update(self, object_name: str, data: List[Dict]) -> List[Dict]:
        """Update multiple records using bulk API."""
        try:
            results = self.sf.bulk.__getattr__(object_name).update(data)
            return results
        except SalesforceError as e:
            raise Exception(f"Bulk update failed: {str(e)}")

    def get_object_fields(self, object_name: str) -> Dict:
        """Get field descriptions for a Salesforce object."""
        try:
            return self.sf.__getattr__(object_name).describe()
        except SalesforceError as e:
            raise Exception(f"Failed to get object description: {str(e)}")
