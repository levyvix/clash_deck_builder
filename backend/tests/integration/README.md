# Integration Tests

This directory contains integration tests that verify the complete workflow of card database operations and API endpoints.

## Test Files

### test_card_database.py
Tests the full card ingestion workflow and database operations:
- Full ingestion workflow from JSON to database
- Card retrieval using CardService
- Upsert behavior (insert then update)
- Handling of optional fields and invalid data

### test_cards_api.py
Tests the Cards API endpoint with database backend:
- GET /cards endpoint returning database data
- Empty database handling
- Response format validation
- Error handling (connection errors, query errors)
- Backward compatibility with Card model

## Prerequisites

These integration tests require a running test database. The tests use the `clean_database` fixture which:
1. Connects to the test database (port 3307 by default)
2. Cleans all tables before each test
3. Seeds test data as needed

### Running the Test Database

You can start the test database using Docker Compose:

```bash
# From project root
docker-compose -f docker-compose.test.yml up -d
```

This will start a MySQL test database on port 3307 with the following credentials:
- Host: localhost
- Port: 3307
- Database: clash_deck_builder_test
- User: test_user
- Password: test_password

## Running the Tests

### Run all integration tests
```bash
cd backend
uv run pytest tests/integration/ -v
```

### Run specific test file
```bash
cd backend
uv run pytest tests/integration/test_card_database.py -v
uv run pytest tests/integration/test_cards_api.py -v
```

### Run specific test class
```bash
cd backend
uv run pytest tests/integration/test_card_database.py::TestCardIngestionWorkflow -v
```

### Run specific test
```bash
cd backend
uv run pytest tests/integration/test_card_database.py::TestCardIngestionWorkflow::test_full_ingestion_workflow_with_test_data -v
```

## Test Coverage

### Card Database Tests (test_card_database.py)

**TestCardIngestionWorkflow**
- `test_full_ingestion_workflow_with_test_data`: Complete workflow from JSON to database
- `test_ingestion_with_missing_optional_fields`: Handling NULL optional fields
- `test_ingestion_with_invalid_card_skipped`: Invalid cards are skipped gracefully

**TestCardRetrieval**
- `test_retrieve_cards_after_ingestion`: Retrieve cards using CardService
- `test_retrieve_single_card_by_id`: Get specific card by ID
- `test_retrieve_nonexistent_card_returns_none`: Handle missing cards
- `test_retrieve_cards_with_null_optional_fields`: NULL field handling

**TestUpsertBehavior**
- `test_insert_then_update_same_card`: Upsert updates existing records
- `test_upsert_preserves_created_at`: Timestamps handled correctly
- `test_batch_upsert_mixed_insert_and_update`: Mixed batch operations

### Cards API Tests (test_cards_api.py)

**TestCardsAPIWithDatabase**
- `test_get_cards_returns_database_data`: API returns database data
- `test_get_cards_with_empty_database`: Empty array for empty database
- `test_get_cards_response_format_matches_card_model`: Response format validation
- `test_get_cards_with_null_optional_fields`: NULL field handling in API
- `test_get_cards_ordered_by_id`: Cards ordered by ID

**TestCardsAPIErrorHandling**
- `test_get_cards_database_connection_error`: 503 for connection failures
- `test_get_cards_database_query_error`: 500 for query errors
- `test_get_cards_unexpected_error`: 500 for unexpected errors

**TestBackwardCompatibility**
- `test_response_format_unchanged_from_api_version`: Format matches Card model
- `test_image_urls_remain_external`: URLs remain as CDN links
- `test_card_model_validation_still_applies`: Validation rules enforced

## Notes

- Tests that require database access will fail with "Failed to setup test database" if the test database is not running
- Tests that only mock dependencies (like error handling tests) can run without a database
- The test database is automatically cleaned before each test to ensure isolation
- Integration tests verify the complete stack: ingestion → database → service → API
