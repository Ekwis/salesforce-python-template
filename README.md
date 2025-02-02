# Salesforce Python Template

A robust Python template designed for seamless interaction with Salesforce. This project enables bulk data operations, SOQL queries, CSV processing, interactive field mapping, and data enrichment via web scraping.

## Features

- **Salesforce Authentication:** Utilises environment variables for secure access.
- **Bulk Data Operations:** Supports insert, update, delete, and upsert operations.
- **SOQL Query Execution:** Run queries against Salesforce and export results to CSV.
- **Interactive Field Mapping:** Map CSV columns to Salesforce fields during upload.
- **Data Enrichment:** Enhances Salesforce records by scraping additional company information.
- **Customisable Configuration:** Easily adjust settings via a YAML configuration file.
- **Comprehensive Logging and Error Handling**
- **Unit and Integration Tests:** Ensuring high code quality with pytest.

## Project Setup

Follow these steps to set up the project:

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Salesforce-Python-Template

    2.	Create and Activate a Virtual Environment

python3 -m venv venv
source venv/bin/activate

Confirm that your Python version is 3.9 or higher:

python --version


    3.	Install Dependencies
Install all required Python packages using:

pip install -r requirements.txt


    4.	Set Up Environment Variables
Create a copy of the environment file and update it with your Salesforce credentials:

cp .env.example .env

Open the .env file in your preferred editor and configure the following variables:

SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_token
SALESFORCE_DOMAIN=login  # Use 'test' for sandbox environments



Configuration

Review and modify the configuration file located at config/config.yaml to suit your requirements. Key configuration areas include:
    •	Salesforce API Settings: API version, batch size, and timeout.
    •	Logging: Log level, format, and file destination.
    •	CSV Processing: Encoding, delimiter, and directories for input and error files.
    •	Data Enrichment Fields: Specify which fields to update for different Salesforce objects (Account, Contact, Lead).

Example snippet from config/config.yaml:

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

Usage

Below are detailed instructions for each script included in the project.

1. Upload Data Script (scripts/upload_data.py)

This script uploads CSV data to Salesforce with interactive field mapping. It supports the following operations:
    •	insert
    •	update
    •	delete
    •	upsert

How It Works:
    •	Field Mapping: The script will prompt you to map CSV headers to corresponding Salesforce fields. You can choose to skip any fields.
    •	Batch Processing: Records are processed in batches (up to 200 records per call) as defined in the configuration.
    •	Operations: For upsert operations, ensure you specify the external ID field using the --external_id_field option.

Command-Line Options:
    •	csv_file: Path to the CSV file to be uploaded.
    •	object_name: Salesforce object name (e.g., Account, Contact).
    •	–operation: Choose the operation (insert, update, delete, upsert). Default is insert.
    •	–config: (Optional) Path to the configuration file. Default is config/config.yaml.
    •	–external_id_field: (Required for upsert) The external ID field to use.
    •	–batch_size: (Optional) Number of records per API call.

Example Usage:

source venv/bin/activate
python scripts/upload_data.py path/to/input.csv Account --operation insert

Follow the interactive prompts to map CSV fields to Salesforce fields.

2. Query Data Script (scripts/query_data.py)

This script executes a SOQL query against Salesforce and exports the results to a CSV file.

How It Works:
    •	SOQL Query Execution: Provide a valid SOQL query to retrieve data from Salesforce.
    •	CSV Export: The retrieved records are saved to a CSV file at the specified output path.
    •	Logging: The script logs the query execution progress and any errors encountered.

Command-Line Options:
    •	soql: The SOQL query to execute (enclose the query in quotes).
    •	output_file: The file path where the CSV output will be saved.
    •	–config: (Optional) Path to the configuration file. Default is config/config.yaml.

Example Usage:

source venv/bin/activate
python scripts/query_data.py "SELECT Id, Name FROM Account" output/accounts.csv

The script will log the number of records retrieved and confirm the CSV export location.

3. Data Enrichment Script (scripts/manipulate_data.py)

This script enriches a Salesforce record by:
    •	Querying the record by ID and object type.
    •	Performing web scraping to collect additional company information (e.g., phone, email, address, website).
    •	Preparing and optionally updating the record in Salesforce after user confirmation.

How It Works:
    •	Record Retrieval: Fetch the specified Salesforce record.
    •	Web Scraping: Search for and extract additional information using a web scraper.
    •	Update Preparation: Map the enriched data to the appropriate Salesforce fields based on configuration or provided options.
    •	User Confirmation: Display current record data alongside proposed updates and prompt for confirmation before updating.

Command-Line Options:
    •	record_id: The Salesforce Record ID to enrich.
    •	sobject_type: The Salesforce object type (e.g., Account, Contact, Lead).
    •	–config: (Optional) Path to the configuration file. Default is config/config.yaml.
    •	–fields: (Optional) Specific fields to update. If not provided, defaults from the configuration are used.

Example Usage:

source venv/bin/activate
python scripts/manipulate_data.py 0016g000009yzfpAAA Account --fields Phone Website BillingStreet

The script will display the current Salesforce data, show the proposed updates based on the web-scraped information, and ask for your confirmation before applying the update.

Testing

To run the complete test suite, ensure you are in your virtual environment and execute:

pytest tests/

For test coverage, run:

pytest --cov=src tests/

Troubleshooting
    •	ModuleNotFoundError for ‘src’:
Ensure you run the scripts from the project root or adjust your PYTHONPATH accordingly.
    •	Authentication Failures:
Verify your Salesforce credentials in the .env file and ensure API access is enabled.
    •	API Errors:
Check the API version and other settings in config/config.yaml. Also, confirm that your Salesforce user has the necessary permissions.

Contributing

Contributions are welcome, lord knight! If you wish to contribute:
    •	Fork the repository.
    •	Create a feature branch.
    •	Submit a pull request with detailed descriptions of your changes.

License

This project is licensed under the MIT License.

Thank you for using the Salesforce Python Template. We hope this tool streamlines your Salesforce data operations and enrichments. For any issues or further assistance, please open an issue on GitHub.