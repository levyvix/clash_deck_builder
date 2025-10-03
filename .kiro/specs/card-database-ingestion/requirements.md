# Requirements Document

## Introduction

This feature will migrate the card data management from fetching directly from the Clash Royale API to using a local database. The system will ingest card data from a JSON file into the MySQL database and modify the card retrieval endpoints to fetch from the database instead of making external API calls. Card images and evolution images will continue to be served via external URLs.

## Requirements

### Requirement 1: Database Card Data Ingestion

**User Story:** As a system administrator, I want to load card data from a JSON file into the database, so that the application can serve card data without depending on external API calls.

#### Acceptance Criteria

1. WHEN the ingestion script is executed THEN the system SHALL read the all_cards.json file from the project root
2. WHEN card data is read from the JSON file THEN the system SHALL parse each card's properties including id, name, elixirCost, rarity, iconUrls, and maxEvolutionLevel
3. WHEN inserting card data into the database THEN the system SHALL map JSON field names to database column names (elixirCost → elixir_cost, iconUrls.medium → image_url, iconUrls.evolutionMedium → image_url_evo)
4. WHEN a card already exists in the database THEN the system SHALL update the existing record with new data
5. WHEN the ingestion completes successfully THEN the system SHALL log the number of cards processed and any errors encountered
6. WHEN the ingestion encounters an invalid card record THEN the system SHALL log the error and continue processing remaining cards

### Requirement 2: Card Type Detection

**User Story:** As a system administrator, I want the ingestion script to automatically determine card types from the JSON data, so that cards are properly categorized in the database.

#### Acceptance Criteria

1. WHEN a card's ID is between 26000000-26999999 THEN the system SHALL classify it as type "Troop"
2. WHEN a card's ID is between 27000000-27999999 THEN the system SHALL classify it as type "Building"
3. WHEN a card's ID is between 28000000-28999999 THEN the system SHALL classify it as type "Spell"
4. WHEN a card's type cannot be determined from its ID THEN the system SHALL default to "Troop" and log a warning

### Requirement 3: Database-Backed Card Retrieval

**User Story:** As a frontend developer, I want the GET /cards endpoint to return card data from the database, so that the application loads faster and doesn't depend on external API availability.

#### Acceptance Criteria

1. WHEN the GET /cards endpoint is called THEN the system SHALL query the cards table in the database
2. WHEN cards are retrieved from the database THEN the system SHALL return all card fields including id, name, elixir_cost, rarity, type, arena, image_url, and image_url_evo
3. WHEN the database query succeeds THEN the system SHALL return a 200 status code with the list of cards
4. WHEN the database query fails THEN the system SHALL return a 500 status code with an appropriate error message
5. WHEN no cards exist in the database THEN the system SHALL return a 200 status code with an empty array

### Requirement 4: Card Service Refactoring

**User Story:** As a backend developer, I want a new card service that handles database operations, so that card data access is centralized and maintainable.

#### Acceptance Criteria

1. WHEN the card service is initialized THEN the system SHALL accept a database session as a dependency
2. WHEN get_all_cards is called THEN the service SHALL execute a SELECT query on the cards table
3. WHEN get_all_cards returns data THEN the service SHALL transform database rows into Card model instances
4. WHEN a database error occurs THEN the service SHALL raise a custom DatabaseError exception with details
5. WHEN the service transforms database rows THEN the system SHALL handle NULL values for optional fields (arena, image_url_evo)

### Requirement 5: Backward Compatibility

**User Story:** As a developer, I want the Card model and API response format to remain unchanged, so that the frontend application continues to work without modifications.

#### Acceptance Criteria

1. WHEN cards are returned from the API THEN the response format SHALL match the existing Card model structure
2. WHEN the Card model is used THEN all existing validation rules SHALL continue to apply
3. WHEN image URLs are returned THEN they SHALL remain as external URLs pointing to Clash Royale CDN
4. WHEN evolution image URLs are missing THEN the system SHALL return NULL for image_url_evo field

### Requirement 6: Data Freshness Management

**User Story:** As a system administrator, I want the ability to re-run the ingestion script, so that I can update card data when new cards are released.

#### Acceptance Criteria

1. WHEN the ingestion script is run multiple times THEN the system SHALL use INSERT ... ON DUPLICATE KEY UPDATE to upsert records
2. WHEN updating existing cards THEN the system SHALL preserve the created_at timestamp
3. WHEN updating existing cards THEN the system SHALL update the updated_at timestamp automatically
4. WHEN the ingestion completes THEN the system SHALL provide a summary of records inserted vs updated
