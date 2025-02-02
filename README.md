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
│   ├── init.py
│   ├── salesforce.py
│   └── utils.py
├── tests/                # Unit tests
├── .env                  # Environment variables
├── .env.example
├── README.md             # This file
└── requirements.txt      # Python dependencies

## Prerequisites

- Python 3.9+
- A Salesforce account with API access
- Salesforce security token

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Salesforce-Python-Template

    2.	Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate  # On macOS/Linux


    3.	Install dependencies:

pip install -r requirements.txt


    4.	Copy .env.example to .env and update it with your Salesforce credentials:

cp .env.example .env



Configuration

Update .env file with your Salesforce credentials:

SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_token
SALESFORCE_DOMAIN=login

Then edit config/config.yaml if you need to modify:

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

Usage

1. Upload Data to Salesforce (with Optional Field Mapping)

python scripts/upload_data.py path/to/input.csv ObjectName

During the upload process, you will be prompted for each CSV column:

Do you want to map the field 'ColumnName'? (y/n)

If you choose “y”, you can specify a new Salesforce field name; otherwise, the original name is used. After mapping, the script will upload in batches.

2. Query Data from Salesforce

python scripts/query_data.py "SELECT Id, Name FROM Account" output.csv

This will run the SOQL query and export results to the specified CSV file.

3. Manipulate Data

You can perform custom transformations using the manipulate_data.py script. For example:

python scripts/manipulate_data.py path/to/input.csv --output path/to/modified_data.csv

Edit the process_data function in scripts/manipulate_data.py to define your specific data manipulation logic.

Testing

Run the test suite with pytest:

pytest tests/

Error Handling
    •	Failed records during upload are saved to the errors/ directory.
    •	Error logs are stored in errors/app.log.
    •	Each error file includes a timestamp and the original filename for easier troubleshooting.

Contributing
    1.	Fork the repository.
    2.	Create a feature branch.
    3.	Commit your changes.
    4.	Push to the branch.
    5.	Create a Pull Request.

Licence

This project is licensed under the MIT Licence - see the LICENSE file for details.