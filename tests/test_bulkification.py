import json
import pytest
from src.utils import chunk_list, setup_logging
from scripts.upload_data import perform_operation_in_batches

# Create a fake Salesforce client that simulates successful API responses
class FakeSalesforce:
    def __init__(self):
        self.sf = self

    def restful(self, endpoint, method, data=None):
        # Parse the payload to determine how many records were sent in this batch
        if data:
            payload = json.loads(data)
            records = payload.get("records", [])
        else:
            records = []
        # Simulate a successful response for each record in the batch
        response = []
        for i in range(len(records)):
            response.append({
                "id": f"fake_id_{i}",
                "success": True,
                "errors": []
            })
        return response

@pytest.fixture
def logger():
    return setup_logging('config/config.yaml')

def test_chunk_list_large_number_of_records():
    # Create a list of 450 dummy items
    records = list(range(450))
    # Use a batch size of 200 (default)
    chunks = chunk_list(records, 200)
    # Expect 3 chunks: 200, 200, and 50 items respectively
    assert len(chunks) == 3, "Expected 3 chunks for 450 records with batch_size=200"
    assert len(chunks[0]) == 200, "First chunk should have 200 records"
    assert len(chunks[1]) == 200, "Second chunk should have 200 records"
    assert len(chunks[2]) == 50, "Third chunk should have 50 records"

def test_bulkify_large_number_of_records(logger):
    # Create 450 dummy records (simulate an unlimited record set)
    records = [{"Field": f"Value {i}"} for i in range(450)]
    fake_sf = FakeSalesforce()
    # Call perform_operation_in_batches with batch_size defaulting to 200
    successes, failures = perform_operation_in_batches(
        "FakeObject",
        "insert",
        records,
        fake_sf,
        external_id_field=None,
        batch_size=200,
        logger=logger
    )
    # Verify that all records are processed successfully with no failures
    assert len(successes) == 450, "All 450 records should be processed successfully"
    assert len(failures) == 0, "There should be no failures in processing the records"