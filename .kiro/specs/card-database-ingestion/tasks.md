# Implementation Plan

- [x] 1. Create card service for database operations





  - Create `backend/src/services/card_service.py` with `CardService` class
  - Implement `get_all_cards()` method to query cards table and return `List[Card]`
  - Implement `_transform_db_row_to_card()` to convert database rows to Card models
  - Add error handling for database failures with custom `DatabaseError` exceptions
  - Handle NULL values for optional fields (arena, image_url_evo)
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 2. Update dependency injection for card service





  - Add `get_card_service()` function to `backend/src/utils/dependencies.py`
  - Configure dependency to provide database session to CardService
  - Ensure proper session lifecycle management
  - _Requirements: 4.1_

- [x] 3. Create data ingestion script





  - Create `backend/src/scripts/` directory if it doesn't exist
  - Create `backend/src/scripts/ingest_cards.py` with main ingestion logic
  - Implement `load_json_file()` to read and parse all_cards.json
  - Implement `determine_card_type()` to classify cards by ID range (26M=Troop, 27M=Building, 28M=Spell)
  - Implement `transform_card_data()` to map JSON fields to database columns
  - Implement `ingest_cards()` with INSERT...ON DUPLICATE KEY UPDATE logic
  - Add transaction management and batch processing
  - Add logging for processed cards count and errors
  - Add error handling for file not found, invalid JSON, and database errors
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 6.1, 6.2, 6.3, 6.4_

- [ ] 4. Update cards API endpoint to use database
  - Modify `backend/src/api/cards.py` to remove ClashRoyaleAPIService dependency
  - Update `get_all_cards()` endpoint to use CardService instead
  - Update error handling to handle DatabaseError exceptions
  - Map database errors to appropriate HTTP status codes (503 for connection failures, 500 for query errors)
  - Ensure response format remains unchanged for backward compatibility
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2_

- [ ] 5. Run ingestion script and verify data
  - Execute `python backend/src/scripts/ingest_cards.py` to populate database
  - Verify cards are inserted into database with SQL query
  - Check that all required fields are populated correctly
  - Verify image URLs remain as external CDN links
  - Test re-running script to verify upsert behavior
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4_

- [ ] 6. Unit testing for card service
  - Create `backend/tests/unit/test_card_service.py`
  - Write test for `get_all_cards()` with mock database returning multiple cards
  - Write test for `get_all_cards()` with empty database
  - Write test for `_transform_db_row_to_card()` with complete data
  - Write test for `_transform_db_row_to_card()` with NULL optional fields
  - Write test for database error handling
  - _Requirements: 4.2, 4.3, 4.4, 4.5_

- [ ] 7. Unit testing for ingestion script
  - Create `backend/tests/unit/test_ingest_cards.py`
  - Write test for `determine_card_type()` with Troop ID range (26000000-26999999)
  - Write test for `determine_card_type()` with Building ID range (27000000-27999999)
  - Write test for `determine_card_type()` with Spell ID range (28000000-28999999)
  - Write test for `transform_card_data()` with complete JSON data
  - Write test for `transform_card_data()` with missing optional fields
  - Write test for `load_json_file()` with valid JSON
  - Write test for error handling with invalid JSON
  - _Requirements: 1.2, 1.3, 1.6, 2.1, 2.2, 2.3, 2.4_

- [ ] 8. Integration testing
  - Create `backend/tests/integration/test_card_database.py`
  - Write test for full ingestion workflow with test JSON data
  - Write test for card retrieval after ingestion
  - Write test for upsert behavior (insert then update same card)
  - Create `backend/tests/integration/test_cards_api.py`
  - Write test for GET /cards endpoint returning database data
  - Write test for endpoint with empty database
  - Write test for endpoint response format matching Card model
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2_
