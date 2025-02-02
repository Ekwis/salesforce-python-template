# Salesforce Python Template

A robust Python template designed for seamless interaction with Salesforce. This project enables bulk data operations, SOQL queries, CSV processing, interactive field mapping, and data enrichment via web scraping.

## Features

- **Salesforce Authentication:** Utilises environment variables for secure access
- **Bulk Data Operations:** Supports insert, update, delete, and upsert operations
- **SOQL Query Execution:** Run queries against Salesforce and export results to CSV
- **Interactive Field Mapping:** Map CSV columns to Salesforce fields during upload
- **Data Enrichment:** Enhances Salesforce records by scraping additional company information
- **Customisable Configuration:** Easily adjust settings via a YAML configuration file
- **Comprehensive Logging and Error Handling**
- **Unit and Integration Tests:** Ensuring high code quality with pytest

## Project Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Salesforce-Python-Template
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate

# Confirm Python version (3.9 or higher required)
python --version
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a copy of the environment file and update it with your Salesforce credentials:

```bash
cp .env.example .env
```

Open the `.env` file in your preferred editor and configure the following variables:
```plaintext
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_token
SALESFORCE_DOMAIN=login  # Use 'test' for sandbox environments
```

## Configuration

Review and modify the configuration file located at `config/config.yaml` to suit your requirements.

### Key Configuration Areas:
- **Salesforce API Settings:** API version, batch size, and timeout
- **Logging:** Log level, format, and file destination
- **CSV Processing:** Encoding, delimiter, and directories for input and error files
- **Data Enrichment Fields:** Specify which fields to update for different Salesforce objects

### Example Configuration:
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

enrichment:
  fields:
    Account:
      - Phone
      - Website
      - BillingStreet
      - BillingCity
      - BillingState
      - BillingPostalCode
      - BillingCountry
    Contact:
      - Phone
      - Email
      - MailingStreet
      - MailingCity
      - MailingState
      - MailingPostalCode
      - MailingCountry
    Lead:
      - Phone
      - Email
      - Street
      - City
      - State
      - PostalCode
      - Country
```

## Usage

### 1. Upload Data Script (`scripts/upload_data.py`)

This script uploads CSV data to Salesforce with interactive field mapping.

#### Supported Operations:
- insert
- update
- delete
- upsert

#### Features:
- **Field Mapping:** Interactive CSV headers to Salesforce fields mapping
- **Batch Processing:** Records processed in configurable batches (up to 200 records per call)
- **Flexible Operations:** Support for all major bulk operations

#### Command-Line Options:
| Option | Description | Required |
|--------|-------------|----------|
| `csv_file` | Path to the CSV file | Yes |
| `object_name` | Salesforce object name (e.g., Account, Contact) | Yes |
| `--operation` | Operation type (insert, update, delete, upsert) | No (default: insert) |
| `--config` | Path to configuration file | No (default: config/config.yaml) |
| `--external_id_field` | External ID field for upsert | Only for upsert |
| `--batch_size` | Number of records per API call | No |

#### Example Usage:
```bash
source venv/bin/activate
python scripts/upload_data.py path/to/input.csv Account --operation insert
```

### 2. Query Data Script (`scripts/query_data.py`)

Execute SOQL queries and export results to CSV.

#### Command-Line Options:
| Option | Description | Required |
|--------|-------------|----------|
| `soql` | SOQL query (in quotes) | Yes |
| `output_file` | CSV output file path | Yes |
| `--config` | Path to configuration file | No |

#### Example Usage:
```bash
source venv/bin/activate
python scripts/query_data.py "SELECT Id, Name FROM Account" output/accounts.csv
```

### 3. Data Enrichment Script (`scripts/manipulate_data.py`)

Enrich Salesforce records with additional data through web scraping.

#### Command-Line Options:
| Option | Description | Required |
|--------|-------------|----------|
| `record_id` | Salesforce Record ID | Yes |
| `sobject_type` | Object type (Account, Contact, Lead) | Yes |
| `--config` | Path to configuration file | No |
| `--fields` | Specific fields to update | No |

#### Example Usage:
```bash
source venv/bin/activate
python scripts/manipulate_data.py 0016g000009yzfpAAA Account --fields Phone Website BillingStreet
```

## Testing

Run the complete test suite:
```bash
pytest tests/
```

Generate test coverage report:
```bash
pytest --cov=src tests/
```

## Troubleshooting

### Common Issues and Solutions:

1. **ModuleNotFoundError for 'src'**
   - Run scripts from project root
   - Adjust PYTHONPATH if needed

2. **Authentication Failures**
   - Verify Salesforce credentials in `.env`
   - Confirm API access is enabled

3. **API Errors**
   - Check API version in `config/config.yaml`
   - Verify user permissions in Salesforce

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed descriptions

## License

This project is licensed under the MIT License.

---

Thank you for using the Salesforce Python Template. We hope this tool streamlines your Salesforce data operations and enrichments. For any issues or further assistance, please open an issue on GitHub.