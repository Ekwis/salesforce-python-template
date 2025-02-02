from src.utils import setup_logging
from scripts.upload_data import perform_operation_in_batches
from src.salesforce import SalesforceClient
import os
import sys
import time
import uuid
import pytest

# Ensure project root is in the path
sys.path.insert(0, os.path.abspath('.'))


# Helper functions to query cases by ID

def query_case_by_id(sf_client, case_id):
    query = f"SELECT Id, Subject, CaseNumber FROM Case WHERE Id = '{case_id}'"
    records = sf_client.query(query)
    return records

# Helper to query cases by subject


def query_case_by_subject(sf_client, subject):
    query = f"SELECT Id, Subject FROM Case WHERE Subject = '{subject}'"
    records = sf_client.query(query)
    return records

# Helper to query cases by case number


def query_case_by_number(sf_client, case_number):
    query = f"SELECT Id, Subject, CaseNumber FROM Case WHERE CaseNumber = '{case_number}'"
    records = sf_client.query(query)
    return records

# ----------------------------
# Insert Operations Tests
# ----------------------------


def test_insert_single_record():
    logger = setup_logging('config/config.yaml')
    sf_client = SalesforceClient('config/config.yaml')
    unique_id = str(uuid.uuid4())[:8]
    test_subject = f"Test Case Insert Single {unique_id}"
    record = {"Subject": test_subject}
    successes, failures = perform_operation_in_batches(
        "Case", "insert", [record], sf_client, None, 200, logger)
    assert len(failures) == 0, f"Failures occurred: {failures}"
    assert len(successes) == 1
    inserted_id = successes[0]["id"]
    rec = query_case_by_id(sf_client, inserted_id)
    assert rec and rec[0]["Subject"] == test_subject
    # Cleanup: delete record
    del_successes, del_failures = perform_operation_in_batches(
        "Case", "delete", [{"Id": inserted_id}], sf_client, None, 200, logger)
    assert len(del_failures) == 0
    time.sleep(2)
    rec_after = query_case_by_id(sf_client, inserted_id)
    assert rec_after == []


def test_insert_batch_records():
    logger = setup_logging('config/config.yaml')
    sf_client = SalesforceClient('config/config.yaml')
    unique_id = str(uuid.uuid4())[:8]
    test_subject_prefix = f"Test Case Insert Batch {unique_id}"
    records = [{"Subject": f"{test_subject_prefix} {i}"} for i in range(10)]
    successes, failures = perform_operation_in_batches(
        "Case", "insert", records, sf_client, None, 200, logger)
    assert len(failures) == 0
    assert len(successes) == 10
    inserted_ids = [s["id"] for s in successes]
    for case_id in inserted_ids:
        rec = query_case_by_id(sf_client, case_id)
        assert rec, f"Record with id {case_id} not found"
    # Cleanup: delete records
    delete_records = [{"Id": case_id} for case_id in inserted_ids]
    del_successes, del_failures = perform_operation_in_batches(
        "Case", "delete", delete_records, sf_client, None, 200, logger)
    assert len(del_failures) == 0
    time.sleep(2)
    for case_id in inserted_ids:
        rec = query_case_by_id(sf_client, case_id)
        assert rec == []

# ----------------------------
# Update Operations Tests
# ----------------------------


def test_update_single_record():
    logger = setup_logging('config/config.yaml')
    sf_client = SalesforceClient('config/config.yaml')
    unique_id = str(uuid.uuid4())[:8]
    original_subject = f"Test Case Update Single {unique_id}"
    record = {"Subject": original_subject}
    ins_successes, ins_failures = perform_operation_in_batches(
        "Case", "insert", [record], sf_client, None, 200, logger)
    assert len(ins_failures) == 0
    inserted_id = ins_successes[0]["id"]
    updated_subject = original_subject + " Updated"
    update_record = {"Id": inserted_id, "Subject": updated_subject}
    upd_successes, upd_failures = perform_operation_in_batches(
        "Case", "update", [update_record], sf_client, None, 200, logger)
    assert len(upd_failures) == 0
    rec = query_case_by_id(sf_client, inserted_id)
    assert rec and rec[0]["Subject"] == updated_subject
    # Cleanup: delete record
    del_successes, del_failures = perform_operation_in_batches(
        "Case", "delete", [{"Id": inserted_id}], sf_client, None, 200, logger)
    assert len(del_failures) == 0
    time.sleep(2)
    rec_after = query_case_by_id(sf_client, inserted_id)
    assert rec_after == []


def test_update_batch_records():
    logger = setup_logging('config/config.yaml')
    sf_client = SalesforceClient('config/config.yaml')
    unique_id = str(uuid.uuid4())[:8]
    test_subject_prefix = f"Test Case Update Batch {unique_id}"
    records = [{"Subject": f"{test_subject_prefix} {i}"} for i in range(10)]
    ins_successes, ins_failures = perform_operation_in_batches(
        "Case", "insert", records, sf_client, None, 200, logger)
    assert len(ins_failures) == 0
    inserted_ids = [s["id"] for s in ins_successes]
    update_records = [{"Id": case_id, "Subject": f"{test_subject_prefix} {i} Updated"}
                      for i, case_id in enumerate(inserted_ids)]
    upd_successes, upd_failures = perform_operation_in_batches(
        "Case", "update", update_records, sf_client, None, 200, logger)
    assert len(upd_failures) == 0
    for i, case_id in enumerate(inserted_ids):
        rec = query_case_by_id(sf_client, case_id)
        expected_subject = f"{test_subject_prefix} {i} Updated"
        assert rec and rec[0]["Subject"] == expected_subject
    delete_records = [{"Id": case_id} for case_id in inserted_ids]
    del_successes, del_failures = perform_operation_in_batches(
        "Case", "delete", delete_records, sf_client, None, 200, logger)
    assert len(del_failures) == 0
    time.sleep(2)
    for case_id in inserted_ids:
        rec = query_case_by_id(sf_client, case_id)
        assert rec == []

# ----------------------------
# Upsert Operations Tests
# ----------------------------


def test_upsert_single_record():
    logger = setup_logging('config/config.yaml')
    sf_client = SalesforceClient('config/config.yaml')
    unique_id = str(uuid.uuid4())[:8]
    original_subject = f"Test Case Upsert Single {unique_id}"

    # First, create a record to get a CaseNumber
    record = {"Subject": original_subject}
    insert_successes, insert_failures = perform_operation_in_batches(
        "Case", "insert", [record], sf_client, None, 200, logger)
    assert len(insert_failures) == 0
    inserted_id = insert_successes[0]["id"]

    # Get the CaseNumber
    rec = query_case_by_id(sf_client, inserted_id)
    assert rec
    case_number = rec[0]["CaseNumber"]

    # Now try to upsert using the CaseNumber
    updated_subject = original_subject + " Updated"
    upsert_record = {"CaseNumber": case_number, "Subject": updated_subject}
    upsert_successes, upsert_failures = perform_operation_in_batches(
        "Case", "upsert", [upsert_record], sf_client, "CaseNumber", 200, logger)
    assert len(upsert_failures) == 0

    # Verify the update
    rec = query_case_by_number(sf_client, case_number)
    assert rec and rec[0]["Subject"] == updated_subject

    # Cleanup
    del_successes, del_failures = perform_operation_in_batches(
        "Case", "delete", [{"Id": inserted_id}], sf_client, None, 200, logger)
    assert len(del_failures) == 0
    time.sleep(2)
    rec_after = query_case_by_id(sf_client, inserted_id)
    assert rec_after == []


def test_upsert_batch_records():
    logger = setup_logging('config/config.yaml')
    sf_client = SalesforceClient('config/config.yaml')
    unique_id = str(uuid.uuid4())[:8]
    test_subject_prefix = f"Test Case Upsert Batch {unique_id}"

    # First, create records to get CaseNumbers
    records = [{"Subject": f"{test_subject_prefix} {i}"} for i in range(10)]
    insert_successes, insert_failures = perform_operation_in_batches(
        "Case", "insert", records, sf_client, None, 200, logger)
    assert len(insert_failures) == 0
    inserted_ids = [s["id"] for s in insert_successes]

    # Get all CaseNumbers
    case_numbers = []
    for case_id in inserted_ids:
        rec = query_case_by_id(sf_client, case_id)
        assert rec
        case_numbers.append(rec[0]["CaseNumber"])

    # Now try to upsert using CaseNumbers
    upsert_records = []
    for i, case_number in enumerate(case_numbers):
        updated_subject = f"{test_subject_prefix} {i} Updated"
        upsert_records.append({
            "CaseNumber": case_number,
            "Subject": updated_subject
        })

    upsert_successes, upsert_failures = perform_operation_in_batches(
        "Case", "upsert", upsert_records, sf_client, "CaseNumber", 200, logger)
    assert len(upsert_failures) == 0

    # Verify the updates
    for i, case_number in enumerate(case_numbers):
        rec = query_case_by_number(sf_client, case_number)
        expected_subject = f"{test_subject_prefix} {i} Updated"
        assert rec and rec[0]["Subject"] == expected_subject

    # Cleanup
    delete_records = [{"Id": case_id} for case_id in inserted_ids]
    del_successes, del_failures = perform_operation_in_batches(
        "Case", "delete", delete_records, sf_client, None, 200, logger)
    assert len(del_failures) == 0
    time.sleep(2)
    for case_id in inserted_ids:
        rec = query_case_by_id(sf_client, case_id)
        assert rec == []

# ----------------------------
# Delete Operations Tests
# ----------------------------


def test_delete_single_record():
    logger = setup_logging('config/config.yaml')
    sf_client = SalesforceClient('config/config.yaml')
    unique_id = str(uuid.uuid4())[:8]
    test_subject = f"Test Case Delete Single {unique_id}"
    record = {"Subject": test_subject}
    ins_successes, ins_failures = perform_operation_in_batches(
        "Case", "insert", [record], sf_client, None, 200, logger)
    assert len(ins_failures) == 0
    inserted_id = ins_successes[0]["id"]
    del_successes, del_failures = perform_operation_in_batches(
        "Case", "delete", [{"Id": inserted_id}], sf_client, None, 200, logger)
    assert len(del_failures) == 0
    time.sleep(2)
    rec_after = query_case_by_id(sf_client, inserted_id)
    assert rec_after == []


def test_delete_batch_records():
    logger = setup_logging('config/config.yaml')
    sf_client = SalesforceClient('config/config.yaml')
    unique_id = str(uuid.uuid4())[:8]
    test_subject_prefix = f"Test Case Delete Batch {unique_id}"
    records = [{"Subject": f"{test_subject_prefix} {i}"} for i in range(10)]
    ins_successes, ins_failures = perform_operation_in_batches(
        "Case", "insert", records, sf_client, None, 200, logger)
    assert len(ins_failures) == 0
    inserted_ids = [s["id"] for s in ins_successes]
    delete_records = [{"Id": case_id} for case_id in inserted_ids]
    del_successes, del_failures = perform_operation_in_batches(
        "Case", "delete", delete_records, sf_client, None, 200, logger)
    assert len(del_failures) == 0
    time.sleep(2)
    for case_id in inserted_ids:
        rec = query_case_by_id(sf_client, case_id)
        assert rec == []
