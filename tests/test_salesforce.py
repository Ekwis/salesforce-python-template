"""
Unit tests for Salesforce client.
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from src.salesforce import SalesforceClient
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError


@pytest.fixture
def mock_config():
    """Fixture for mock configuration."""
    return {
        'api': {
            'version': '57.0',
            'batch_size': 200,
            'timeout': 30
        }
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set mock environment variables."""
    monkeypatch.setenv('SALESFORCE_USERNAME', 'test@example.com')
    monkeypatch.setenv('SALESFORCE_PASSWORD', 'password123')
    monkeypatch.setenv('SALESFORCE_SECURITY_TOKEN', 'token123')
    monkeypatch.setenv('SALESFORCE_DOMAIN', 'test')


@pytest.fixture
def mock_sf_client(mock_config):
    """Fixture for mock Salesforce client."""
    with patch('src.salesforce.Salesforce') as mock_sf:
        with patch('src.salesforce.yaml.safe_load', return_value=mock_config):
            client = SalesforceClient()
            client.sf = mock_sf.return_value
            yield client


def test_authentication(mock_env_vars, mock_config):
    """Test Salesforce authentication."""
    with patch('src.salesforce.Salesforce') as mock_sf:
        with patch('src.salesforce.yaml.safe_load', return_value=mock_config):
            client = SalesforceClient()
            mock_sf.assert_called_once_with(
                username='test@example.com',
                password='password123',
                security_token='token123',
                domain='test',
                version='57.0'
            )


def test_query_success(mock_sf_client):
    """Test successful SOQL query."""
    mock_sf_client.sf.query.return_value = {
        'records': [{'Id': '001', 'Name': 'Test'}]
    }

    results = mock_sf_client.query('SELECT Id, Name FROM Account')
    assert results == [{'Id': '001', 'Name': 'Test'}]
    mock_sf_client.sf.query.assert_called_once_with(
        'SELECT Id, Name FROM Account')


def test_query_error(mock_sf_client):
    """Test SOQL query error handling."""
    error = SalesforceError('Query failed', status=400,
                            resource_name='query', content={})
    mock_sf_client.sf.query.side_effect = error

    with pytest.raises(Exception) as exc_info:
        mock_sf_client.query('SELECT Invalid FROM Account')
    expected_error = 'Query failed: Unknown error occurred for {url}. Response content: {content}'
    assert str(exc_info.value) == expected_error


def test_bulk_insert_success(mock_sf_client):
    """Test successful bulk insert."""
    mock_bulk = MagicMock()
    mock_sf_client.sf.bulk = mock_bulk
    mock_bulk.Account.insert.return_value = [{'success': True, 'id': '001'}]

    records = [{'Name': 'Test Account'}]
    results = mock_sf_client.bulk_insert('Account', records)

    assert results == [{'success': True, 'id': '001'}]
    mock_bulk.Account.insert.assert_called_once_with(records)


def test_bulk_insert_error(mock_sf_client):
    """Test bulk insert error handling."""
    mock_bulk = MagicMock()
    mock_sf_client.sf.bulk = mock_bulk
    error = SalesforceError('Insert failed', status=400,
                            resource_name='insert', content={})
    mock_bulk.Account.insert.side_effect = error

    with pytest.raises(Exception) as exc_info:
        mock_sf_client.bulk_insert('Account', [{'Name': 'Test'}])
    expected_error = 'Bulk insert failed: Unknown error occurred for {url}. Response content: {content}'
    assert str(exc_info.value) == expected_error
