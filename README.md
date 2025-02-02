# Salesforce Python Template

A Python template for interacting with Salesforce, featuring bulk data operations, SOQL queries, and CSV processing.

## Features

- Salesforce authentication using environment variables
- Bulk data upload from CSV files
- SOQL query execution and CSV export
- Error handling and logging
- Configurable settings via YAML
- Unit tests with pytest

## Directory Structure

```
salesforce_project/
├── csvs/               # Store input CSV files
├── errors/            # Store error logs and failed CSVs
├── scripts/           # One-off scripts for uploading/querying
├── src/              # Shared modules
├── config/           # Configuration files
├── tests/            # Unit tests
├── venv/             # Virtual environment
├── .env              # Environment variables
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Prerequisites

- Python 3.9+
- Salesforce account with API access
- Salesforce security token

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd salesforce_project
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and update with your Salesforce credentials:
   ```bash
   cp .env.example .env
   ```

## Configuration

1. Update `.env` file with your Salesforce credentials:
   ```
   SALESFORCE_USERNAME=your_username
   SALESFORCE_PASSWORD=your_password
   SALESFORCE_SECURITY_TOKEN=your_token
   SALESFORCE_DOMAIN=login
   ```

2. Modify `config/config.yaml` for custom settings:
   ```yaml
   api:
     version: '57.0'
     batch_size: 200
     timeout: 30
   ```

## Usage

### Upload Data to Salesforce

```bash
python scripts/upload_data.py path/to/input.csv ObjectName
```

Example:
```bash
python scripts/upload_data.py csvs/accounts.csv Account
```

### Query Data from Salesforce

```bash
python scripts/query_data.py "SELECT Id, Name FROM Account" output.csv
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Error Handling

- Failed records during upload are saved to the `errors/` directory
- Error logs are stored in `errors/app.log`
- Each error file includes timestamp and original filename

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 