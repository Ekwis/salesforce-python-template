"""Tests for the data manipulation and enrichment functionality."""
from scripts.manipulate_data import (
    clean_text,
    extract_phone_number,
    extract_email,
    extract_address,
    search_company_info,
    get_salesforce_record,
    prepare_record_update
)
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
import json
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


# Test data
MOCK_HTML = """
<html>
    <body>
        <div class="contact-info">
            <div class="address">
                123 Tech Street, Suite 100, San Francisco, CA 94105
            </div>
            <div class="phone">
                Contact us: +1 (555) 123-4567
            </div>
            <div class="email">
                Email: contact@testcompany.com
            </div>
        </div>
    </body>
</html>
"""

MOCK_SALESFORCE_RECORD = {
    'Id': '001XX000003G9yyYAC',
    'Name': 'Test Company',
    'Phone': None,
    'Website': None,
    'BillingStreet': None,
    'BillingCity': None,
    'BillingState': None,
    'BillingPostalCode': None,
    'BillingCountry': None
}


@pytest.fixture
def mock_soup():
    """Create a BeautifulSoup fixture for testing."""
    return BeautifulSoup(MOCK_HTML, 'html.parser')


def test_clean_text():
    """Test text cleaning functionality."""
    assert clean_text("  Hello   World  ") == "Hello World"
    assert clean_text("") == ""
    assert clean_text(None) == ""
    assert clean_text(
        "  Multiple    Spaces   Here  ") == "Multiple Spaces Here"


def test_extract_phone_number():
    """Test phone number extraction."""
    # Test US format
    assert extract_phone_number(
        "Call us at +1 (555) 123-4567") == "+1 (555) 123-4567"
    assert extract_phone_number("Phone: 555-123-4567") == "555-123-4567"
    assert extract_phone_number("No phone here") is None

    # Test international format
    assert extract_phone_number("Int: +44 20 7123 4567") == "+44 20 7123 4567"


def test_extract_email():
    """Test email extraction."""
    assert extract_email("Email us at test@example.com") == "test@example.com"
    assert extract_email(
        "contact@test.co.uk and more text") == "contact@test.co.uk"
    assert extract_email("No email here") is None


def test_extract_address(mock_soup):
    """Test address extraction from HTML."""
    address = extract_address(mock_soup)
    assert address is not None
    assert "123 Tech Street" in address
    assert "San Francisco" in address


@patch('requests.get')
def test_search_company_info(mock_get):
    """Test company information search with mocked requests."""
    # Mock the Google search response
    mock_google_response = Mock()
    mock_google_response.text = """
        <html>
            <a href="url?q=https://testcompany.com&sa=U">Test Company</a>
        </html>
    """

    # Mock the company website response
    mock_company_response = Mock()
    mock_company_response.text = MOCK_HTML

    # Configure the mock to return different responses for different URLs
    def mock_get_response(*args, **kwargs):
        if 'google.com' in args[0]:
            return mock_google_response
        return mock_company_response

    mock_get.side_effect = mock_get_response

    # Test the search function
    result = search_company_info("Test Company")

    assert result['phone'] == "+1 (555) 123-4567"
    assert result['email'] == "contact@testcompany.com"
    assert "123 Tech Street" in result['address']
    assert result['website'] == "https://testcompany.com"


@patch('src.salesforce.SalesforceClient')
def test_get_salesforce_record(mock_sf_client):
    """Test Salesforce record retrieval."""
    # Mock the Salesforce query response
    mock_sf_client.query.return_value = [MOCK_SALESFORCE_RECORD]

    # Test fields to query
    fields = {'Phone', 'Website', 'BillingStreet'}

    record = get_salesforce_record(
        mock_sf_client, '001XX000003G9yyYAC', 'Account', fields)

    assert record is not None
    assert record['Id'] == '001XX000003G9yyYAC'
    assert record['Name'] == 'Test Company'


def test_prepare_record_update():
    """Test preparation of record updates."""
    record_id = '001XX000003G9yyYAC'
    enriched_data = {
        'phone': '+1 (555) 123-4567',
        'email': 'contact@testcompany.com',
        'website': 'https://testcompany.com',
        'address': '123 Tech Street, Suite 100, San Francisco, CA, 94105'
    }
    fields = {'Phone', 'Website', 'BillingStreet',
              'BillingCity', 'BillingState'}

    update_data = prepare_record_update(
        record_id, enriched_data, 'Account', fields)

    assert update_data['Id'] == record_id
    assert update_data['Phone'] == '+1 (555) 123-4567'
    assert update_data['Website'] == 'https://testcompany.com'
    assert update_data['BillingStreet'] == '123 Tech Street, Suite 100'
    assert update_data['BillingCity'] == 'San Francisco'
    assert update_data['BillingState'] == 'CA'


@pytest.mark.integration
def test_full_integration():
    """
    Full integration test.
    Note: This test requires actual Salesforce credentials and is marked as integration.
    """
    pytest.skip("Integration test - requires Salesforce credentials")
    # Add integration test implementation here if needed
