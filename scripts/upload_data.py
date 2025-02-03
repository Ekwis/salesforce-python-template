#!/usr/bin/env python3
"""
Script to upload CSV data to Salesforce, allowing:
- insert, update, delete, upsert
- batch size of up to 200 records per call to the normal API (SObject Collections)
- interactive field mapping with the option to skip fields
"""

from src.utils import (
    setup_logging,
    read_csv,
    save_failed_records,
    chunk_list
)
from src.salesforce import SalesforceClient
import os
import sys
import argparse
from typing import List, Dict
import json

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Upload CSV data to Salesforce with field mapping, supporting "
            "insert, update, delete, or upsert (via SObject Collections)."
        )
    )
    parser.add_argument("csv_file", help="Path to the CSV file to upload")
    parser.add_argument(
        "object_name", help="Salesforce object name (e.g., Account, Contact)")
    parser.add_argument(
        "--operation",
        choices=["insert", "update", "delete", "upsert"],
        default="insert",
        help="Salesforce operation: insert, update, delete, or upsert",
    )
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--external_id_field",
        default=None,
        help=(
            "If using upsert, specify the external ID field name, e.g. 'External_Id__c'. "
            "Ignored for other operations."
        ),
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=200,
        help="Number of records per API call (max 200). Defaults to 200."
    )
    return parser.parse_args()


def prompt_field_mapping(records: List[Dict], logger) -> Dict[str, str]:
    """
    Prompt the user to map CSV fields to Salesforce fields.
    Returns a dictionary of { original_field_name: new_field_name }.
    If a field is skipped, it won't appear in this dictionary at all.
    """
    if not records:
        logger.warning("No records found in CSV; skipping field mapping.")
        return {}

    fieldnames = list(records[0].keys())
    field_mapping = {}

    logger.info("Starting interactive field mapping...")

    for field in fieldnames:
        print(f"\nField detected: '{field}'")
        response = input(
            "Map this field to Salesforce? (y to map, n to skip): ").strip().lower()

        # If user chooses to skip the field entirely, do not include it in field_mapping
        if response == "n":
            logger.info(f"Skipping field '{field}'. It will not be uploaded.")
            continue

        # Otherwise, user wants to map
        new_name = input(
            f"Enter the Salesforce field name to map '{field}' to.\n"
            f"(Press Enter to keep '{field}'): "
        ).strip()

        # If new_name is empty, keep original
        if not new_name:
            new_name = field

        field_mapping[field] = new_name
        logger.info(
            f"Mapping CSV field '{field}' -> Salesforce field '{new_name}'.")
    return field_mapping


def apply_field_mapping(records: List[Dict], field_mapping: Dict[str, str]) -> List[Dict]:
    """
    Return a new list of records that apply the given field mapping.
    Skips fields not in field_mapping at all.
    """
    mapped_records = []
    for record in records:
        new_record = {}
        for original_field, mapped_field in field_mapping.items():
            if original_field in record:
                new_record[mapped_field] = record[original_field]
        mapped_records.append(new_record)
    return mapped_records


def send_sobject_collection_request(sf, payload, logger):
    """
    Make a single call to the SObject Collections endpoint:
    POST /services/data/vXX.X/composite/sobjects
    Return the raw result or raise an exception if the call fails at the HTTP level.

    The result is typically a list of results, e.g.:
    [
      {
        "id": "001...",
        "success": true,
        "errors": []
      },
      ...
    ]
    We'll parse it in the calling function.
    """
    try:
        # Use the appropriate endpoint and method based on the operation
        if "records" in payload and len(payload["records"]) > 0:
            first_record = payload["records"][0]
            operation = first_record["attributes"].get("operation", "insert")

            if operation == "insert":
                endpoint = "composite/sobjects"
                method = "POST"
            elif operation == "update":
                endpoint = "composite/sobjects"
                method = "PATCH"
            elif operation == "delete":
                # For delete, we need to extract the IDs and use a different endpoint
                ids = [record["Id"] for record in payload["records"]]
                endpoint = f"composite/sobjects?ids={','.join(ids)}"
                method = "DELETE"
                payload = None  # DELETE doesn't need a payload
            elif operation == "upsert":
                # For upsert, we need the external ID field
                external_id_field = first_record["attributes"].get("externalIdField")
                if not external_id_field:
                    raise ValueError("External ID field is required for upsert")
                endpoint = f"composite/sobjects/{first_record['attributes']['type']}/{external_id_field}"
                method = "PATCH"
            else:
                raise ValueError(f"Unknown operation: {operation}")

            result = sf.sf.restful(
                endpoint,
                method=method,
                data=json.dumps(payload) if payload is not None else None
            )
            return result
        else:
            raise ValueError("No records in payload")
    except Exception as e:
        logger.error(f"SObject Collection API request failed: {str(e)}")
        raise


def build_sobject_collection_payload(
    records: List[Dict],
    object_name: str,
    operation: str,
    external_id_field: str = None
):
    """
    Build a payload for Salesforce's SObject Collection API for up to 200 records at once.
    This covers insert, update, delete, upsert. Upsert requires an external ID field.
    """
    payload = {"allOrNone": False, "records": []}
    for r in records:
        # Base record
        sobject = {
            "attributes": {
                "type": object_name,
                "operation": operation
            }
        }

        if operation == "insert":
            # Just pass fields
            sobject.update(r)
        elif operation == "update":
            # Must have an Id
            if "Id" not in r:
                raise ValueError("Record is missing an 'Id' field for update.")
            sobject.update(r)
        elif operation == "delete":
            # Must have an Id
            if "Id" not in r:
                raise ValueError("Record is missing an 'Id' field for delete.")
            # We only need the Id
            sobject["Id"] = r["Id"]
        elif operation == "upsert":
            # Upsert requires the external ID field
            if not external_id_field:
                raise ValueError("Must specify --external_id_field for upsert.")
            if external_id_field not in r:
                raise ValueError(f"Record is missing '{external_id_field}' field for upsert.")
            sobject["attributes"]["externalIdField"] = external_id_field
            sobject.update(r)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        payload["records"].append(sobject)
    return payload


def perform_operation_in_batches(
    object_name: str,
    operation: str,
    records: List[Dict],
    sf: SalesforceClient,
    external_id_field: str,
    batch_size: int,
    logger
):
    """
    Chunk the records by batch_size and perform the given operation using
    the SObject Collections endpoint (up to 200 records per batch).
    Returns (successes, failures).
    Each item in successes/failures is a dict of form:
      {
        "record": original_record_data,
        "id": "CreatedOrUpdatedId",
        "error": "Error Message if any"
      }
    """
    all_successes = []
    all_failures = []

    for chunk_idx, chunk in enumerate(chunk_list(records, batch_size), start=1):
        logger.info(f"Processing chunk {chunk_idx} with {len(chunk)} records (operation = {operation})")
        payload = build_sobject_collection_payload(chunk, object_name, operation, external_id_field)
        result = send_sobject_collection_request(sf, payload, logger)
        result_records = result.get("results", []) if isinstance(result, dict) else result
        if len(result_records) != len(chunk):
            logger.warning("Response count does not match request count - check API behavior")
        for original, response in zip(chunk, result_records):
            if response.get("success", False):
                all_successes.append({
                    "record": original,
                    "id": response.get("id")
                })
            else:
                errors = response.get("errors", [])
                combined_errors = "; ".join(e.get("message", "") for e in errors)
                all_failures.append({
                    "record": original,
                    "error": combined_errors
                })
    return all_successes, all_failures


def save_upload_results(successes: List[Dict], failures: List[Dict], csv_file: str, logger) -> None:
    """
    Save record-by-record playback of upload results to CSV files.
    Creates two files: one for successes and one for failures, in a 'results' directory.
    Each record includes original input fields and additional columns indicating the result.
    """
    import csv
    import os
    from datetime import datetime

    results_dir = os.path.join(os.getcwd(), "results")
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    success_filename = os.path.join(results_dir, f"upload_success_{timestamp}.csv")
    error_filename = os.path.join(results_dir, f"upload_errors_{timestamp}.csv")

    if successes:
        # Assume all records have the same keys
        fieldnames = list(successes[0]["record"].keys())
        fieldnames.extend(["Result", "SalesforceId"])
        with open(success_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()
            for item in successes:
                rec = item["record"].copy()
                rec["Result"] = "Success"
                rec["SalesforceId"] = item.get("id", "")
                writer.writerow(rec)
    else:
        with open(success_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Result", "SalesforceId"], delimiter=',')
            writer.writeheader()

    if failures:
        fieldnames = list(failures[0]["record"].keys())
        fieldnames.extend(["Result", "Error"])
        with open(error_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()
            for item in failures:
                rec = item["record"].copy()
                rec["Result"] = "Error"
                rec["Error"] = item.get("error", "")
                writer.writerow(rec)
    else:
        with open(error_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Result", "Error"], delimiter=',')
            writer.writeheader()

    logger.info(f"Success records saved to: {success_filename}")
    logger.info(f"Error records saved to: {error_filename}")


def process_failures(failures: List[Dict], csv_file: str, logger) -> None:
    """Legacy function to save failed records using save_failed_records from utils."""
    if not failures:
        return
    failed_records = []
    for f in failures:
        r = dict(f.get("record", {}))
        r["Error"] = f.get("error", "")
        failed_records.append(r)
    error_file = save_failed_records(failed_records, csv_file)
    logger.info(f"Legacy failed records saved to: {error_file}")


def main():
    args = parse_args()
    logger = setup_logging(args.config)

    try:
        sf = SalesforceClient(args.config)
        logger.info(f"Initialised connection to Salesforce. Session ID: {sf.sf.session_id}")
        records = read_csv(args.csv_file, args.config)
        logger.info(f"Read {len(records)} records from {args.csv_file}")
        field_mapping = prompt_field_mapping(records, logger)
        mapped_records = apply_field_mapping(records, field_mapping)
        successes, failures = perform_operation_in_batches(
            args.object_name,
            args.operation,
            mapped_records,
            sf,
            args.external_id_field,
            args.batch_size,
            logger
        )
        logger.info(f"Operation '{args.operation}' completed.")
        logger.info(f"  Successful records: {len(successes)}")
        logger.info(f"  Failed records:     {len(failures)}")
        save_upload_results(successes, failures, args.csv_file, logger)
    except Exception as e:
        logger.error(f"Error during upload: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()