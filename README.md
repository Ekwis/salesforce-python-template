# Salesforce Python Template

A Python template for interacting with Salesforce, featuring bulk data operations, SOQL queries, CSV processing, and interactive field mapping.

## Features

- Salesforce authentication using environment variables
- Bulk data upload from CSV files (with optional field mapping)
- SOQL query execution and CSV export
- Data manipulation script for custom transformations
- Error handling and logging
- Configurable settings via YAML
- Unit tests with pytest

## Directory Structure

Salesforce-Python-Template/
├── config/               # Configuration files
│   └── config.yaml
├── errors/               # Error logs and failed CSVs
├── input/                # Input CSV files
├── output/               # Output CSV files (queried or manipulated)
├── scripts/              # One-off scripts for uploading/querying/manipulating
│   ├── manipulate_data.py
│   ├── query_data.py
│   └── upload_data.py
├── src/                  # Shared modules
│   ├── __init__.py
│   ├── salesforce.py
│   └── utils.py
├── tests/                # Unit tests and integration tests
├── .env                  # Environment variables
├── .env.example
├── README.md             # This file
└── requirements.txt      # Python dependencies

## Prerequisites

- Python 3.9+
- A Salesforce account with API access
- Salesforce security token
- Git
- Homebrew (for macOS users)

## Detailed Setup Guide

### 1. System Setup (macOS)

1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python 3.9+ using Homebrew:
   ```bash
   brew install python@3.9
   ```

3. Install Git if not already installed:
   ```bash
   brew install git
   ```

### 2. Salesforce Setup

1. Enable API Access in Salesforce:
   - Log in to Salesforce
   - Go to Setup → Users → Profiles
   - Select your profile
   - Ensure "API Enabled" permission is checked

2. Generate a Security Token:
   - Go to Settings → My Personal Information → Reset Security Token
   - Click "Reset Security Token"
   - Check your email for the new token

3. Note down the following information:
   - Your Salesforce username
   - Your Salesforce password
   - Your security token (from step 2)
   - Your Salesforce domain (e.g., login.salesforce.com for production)

### 3. Project Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Salesforce-Python-Template
   ```

2. Create and activate a virtual environment:
   ```bash
   # Create a new virtual environment
   python3 -m venv venv
   
   # Activate the virtual environment
   source venv/bin/activate
   
   # Verify Python version
   python --version  # Should show Python 3.9+
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Open .env in your preferred editor
   open -e .env  # For macOS
   ```

5. Update the .env file with your Salesforce credentials:
   ```plaintext
   SALESFORCE_USERNAME=your_username
   SALESFORCE_PASSWORD=your_password
   SALESFORCE_SECURITY_TOKEN=your_token
   SALESFORCE_DOMAIN=login  # Use 'test' for sandbox
   ```

### 4. Configuration

1. Review and update config/config.yaml as needed:
   ```yaml
   api:
     version: '57.0'
     batch_size: 200
     timeout: 30
   logging:
     level: INFO
     format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
     file: 'errors/app.log'
   csv:
     encoding: 'utf-8'
     delimiter: ','
     error_directory: 'errors'
     input_directory: 'input'
   ```

2. Create necessary directories:
   ```bash
   mkdir -p input output errors
   ```

## Usage

### 1. Upload Data to Salesforce

This script allows you to upload CSV data to Salesforce with interactive field mapping.

```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Run upload script
python scripts/upload_data.py path/to/input.csv ObjectName
```

During the upload process, you'll be prompted for field mapping:
- For each CSV column, you'll see: `Map this field to Salesforce? (y to map, n to skip)`
- If yes, enter the corresponding Salesforce field name (or press Enter to keep the original)
- If no, the field will be skipped

### 2. Data Upload Operations

The Salesforce Python Template now supports the following data upload operations:

- **Insert**: Insert new records. You can upload a single record or multiple records in a batch (up to 200 records per API call).
- **Update**: Update existing records by providing the record ID. You can update one or many records in a single batch.
- **Upsert**: Insert or update records based on an external ID field. When using upsert, specify the external ID field (e.g., `External_Id__c`).
- **Delete**: Delete records by providing their record ID. Supports single or batch deletion.

#### Examples:

**Insert Single Record**
```bash
python scripts/upload_data.py input/single_record.csv Account --operation insert
```

**Insert Multiple Records (Batch)**
```bash
python scripts/upload_data.py input/multiple_records.csv Account --operation insert --batch_size 10
```

**Update Single Record**
```bash
python scripts/upload_data.py input/update_single_record.csv Account --operation update
```

**Update Multiple Records (Batch)**
```bash
python scripts/upload_data.py input/update_multiple_records.csv Account --operation update --batch_size 10
```

**Upsert Single Record**
```bash
python scripts/upload_data.py input/upsert_single_record.csv Account --operation upsert --external_id_field External_Id__c
```

**Upsert Multiple Records (Batch)**
```bash
python scripts/upload_data.py input/upsert_multiple_records.csv Account --operation upsert --external_id_field External_Id__c --batch_size 10
```

**Delete Single Record**
```bash
python scripts/upload_data.py input/delete_single_record.csv Account --operation delete
```

**Delete Multiple Records (Batch)**
```bash
python scripts/upload_data.py input/delete_multiple_records.csv Account --operation delete --batch_size 10
```

All operations support batch processing with the `--batch_size` parameter (max 200 records per API call).

## Testing

1. Run the full test suite:
   ```bash
   pytest tests/
   ```

2. Run specific test files:
   ```bash
   pytest tests/test_salesforce.py
   pytest tests/test_upload_operations.py
   ```

3. Run tests with coverage:
   ```bash
   pytest --cov=src tests/
   ```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify credentials in the .env file.
   - Ensure the security token is current.
   - Check if your IP is whitelisted in Salesforce.

2. **API Errors**
   - Verify API access is enabled.
   - Check the API version in config.yaml.
   - Ensure object permissions are correct.

3. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   deactivate  # If already in a venv
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Logging

- Check errors/app.log for detailed error messages.
- Failed records during upload are saved in errors/.
- Each error file includes a timestamp for tracking.

## Development

### Setting Up Development Environment

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -am 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Create a Pull Request.

## License

This project is licensed under the MIT License – see the LICENSE file for details.

## Support

For support and questions:
1. Check existing issues in the repository.
2. Create a new issue with detailed information about your problem.
3. Include relevant logs and error messages.

---