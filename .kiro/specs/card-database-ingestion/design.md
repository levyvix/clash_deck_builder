# Design Document

## Overview

This design outlines the migration of card data management from external API calls to a database-backed system. The solution includes a data ingestion script to populate the database from a JSON file and refactored services to retrieve card data from the database instead of the Clash Royale API. This approach improves performance, reduces external dependencies, and provides better control over card data.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  all_cards.json │
└────────┬────────┘
         │
         │ (one-time ingestion)
         ▼
┌─────────────────────┐
│ Ingestion Script    │
│ (ingest_cards.py)   │
└────────┬────────────┘
         │
         │ INSERT/UPDATE
         ▼
┌─────────────────────┐
│   MySQL Database    │
│   (cards table)     │
└────────┬────────────┘
         │
         │ SELECT queries
         ▼
┌─────────────────────┐
│   Card Service      │
│ (card_service.py)   │
└────────┬────────────┘
         │
         │ Card models
         ▼
┌─────────────────────┐
│   Cards API         │
│   (GET /cards)      │
└────────┬────────────┘
         │
         │ JSON response
         ▼
┌─────────────────────┐
│   Frontend App      │
└─────────────────────┘
```

### Component Interaction Flow

1. **Ingestion Phase** (one-time or periodic):
   - Administrator runs `python backend/src/scripts/ingest_cards.py`
   - Script reads `all_cards.json` from project root
   - Script transforms and inserts/updates data in MySQL `cards` table

2. **Runtime Phase** (normal operation):
   - Frontend requests `GET /api/cards`
   - API endpoint calls `CardService.get_all_cards()`
   - Service queries database and returns `List[Card]`
   - API returns JSON response to frontend
   - Frontend displays cards with images loaded from external URLs

## Components and Interfaces

### 1. Data Ingestion Script

**File**: `backend/src/scripts/ingest_cards.py`

**Purpose**: Load card data from JSON file into the database

**Key Functions**:

```python
def load_json_file(file_path: str) -> dict:
    """Load and parse the JSON file"""
    
def determine_card_type(card_id: int) -> str:
    """Determine card type based on ID range"""
    # 26000000-26999999: Troop
    # 27000000-27999999: Building
    # 28000000-28999999: Spell
    
def transform_card_data(card_json: dict) -> dict:
    """Transform JSON structure to database schema"""
    # Maps: elixirCost → elixir_cost
    # Maps: iconUrls.medium → image_url
    # Maps: iconUrls.evolutionMedium → image_url_evo
    # Normalizes: rarity (lowercase → Title Case)
    
def ingest_cards(db_session, cards_data: list) -> tuple[int, int]:
    """Insert or update cards in database"""
    # Returns: (inserted_count, updated_count)
    
def main():
    """Main execution function"""
```

**Database Operations**:
- Uses `INSERT ... ON DUPLICATE KEY UPDATE` for upsert logic
- Batch processing for efficiency
- Transaction management for data integrity

### 2. Card Service

**File**: `backend/src/services/card_service.py`

**Purpose**: Provide database operations for card data

**Class**: `CardService`

```python
class CardService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def get_all_cards(self) -> List[Card]:
        """Retrieve all cards from database"""
        # SELECT * FROM cards ORDER BY id
        
    async def get_card_by_id(self, card_id: int) -> Optional[Card]:
        """Retrieve a single card by ID"""
        # SELECT * FROM cards WHERE id = %s
        
    def _transform_db_row_to_card(self, row: dict) -> Card:
        """Transform database row to Card model"""
```

**Error Handling**:
- Raises `DatabaseError` for query failures
- Handles NULL values for optional fields
- Validates data before creating Card models

### 3. Updated Cards API Endpoint

**File**: `backend/src/api/cards.py`

**Changes**:
- Remove dependency on `ClashRoyaleAPIService`
- Add dependency on `CardService`
- Update error handling for database errors

**New Endpoint Signature**:

```python
@router.get("/cards", response_model=List[Card])
async def get_all_cards(
    card_service: CardService = Depends(get_card_service),
):
    """Fetch all cards from database"""
```

### 4. Dependency Injection

**File**: `backend/src/utils/dependencies.py`

**New Function**:

```python
def get_card_service() -> CardService:
    """Dependency injection for CardService"""
    with get_db_session() as session:
        yield CardService(session)
```

## Data Models

### Database Schema (Existing)

The `cards` table already exists in `schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS cards (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    elixir_cost INT NOT NULL,
    rarity ENUM('Common', 'Rare', 'Epic', 'Legendary', 'Champion') NOT NULL,
    type ENUM('Troop', 'Spell', 'Building') NOT NULL,
    arena VARCHAR(100) DEFAULT NULL,
    image_url VARCHAR(500) NOT NULL,
    image_url_evo VARCHAR(500) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- Indexes and constraints...
);
```

### JSON to Database Mapping

| JSON Field | Database Column | Transformation |
|------------|----------------|----------------|
| `id` | `id` | Direct mapping |
| `name` | `name` | Direct mapping |
| `elixirCost` | `elixir_cost` | Snake case conversion |
| `rarity` | `rarity` | Lowercase → Title Case |
| `iconUrls.medium` | `image_url` | Extract nested field |
| `iconUrls.evolutionMedium` | `image_url_evo` | Extract nested field (optional) |
| (derived from id) | `type` | ID range-based logic |
| `arena.name` | `arena` | Extract nested field (optional) |

### Card Model (Unchanged)

The existing `Card` Pydantic model remains unchanged to maintain backward compatibility:

```python
class Card(BaseModel):
    id: int
    name: str
    elixir_cost: int
    rarity: str
    type: str
    arena: Optional[str]
    image_url: str
    image_url_evo: Optional[str]
```

## Error Handling

### Ingestion Script Errors

| Error Type | Handling Strategy |
|------------|------------------|
| File not found | Log error and exit with code 1 |
| Invalid JSON | Log error and exit with code 1 |
| Database connection failure | Retry with exponential backoff, then exit |
| Invalid card data | Log warning, skip card, continue processing |
| Constraint violation | Log error, skip card, continue processing |

### Runtime Service Errors

| Error Type | HTTP Status | Response |
|------------|-------------|----------|
| Database connection failure | 503 Service Unavailable | "Database temporarily unavailable" |
| Query execution error | 500 Internal Server Error | "Failed to retrieve cards" |
| No cards found | 200 OK | Empty array `[]` |
| Invalid card data | 500 Internal Server Error | "Data integrity error" |

### Custom Exceptions

```python
class DatabaseError(Exception):
    """Base exception for database operations"""
    
class CardNotFoundError(DatabaseError):
    """Raised when a card is not found"""
    
class CardValidationError(DatabaseError):
    """Raised when card data fails validation"""
```

## Testing Strategy

### Unit Tests

**File**: `backend/tests/unit/test_card_service.py`

- Test `CardService.get_all_cards()` with mock database
- Test `CardService.get_card_by_id()` with valid/invalid IDs
- Test `_transform_db_row_to_card()` with various data scenarios
- Test error handling for database failures

**File**: `backend/tests/unit/test_ingest_cards.py`

- Test `determine_card_type()` with various ID ranges
- Test `transform_card_data()` with complete and partial JSON
- Test `load_json_file()` with valid and invalid files
- Test error handling for malformed data

### Integration Tests

**File**: `backend/tests/integration/test_card_database.py`

- Test full ingestion workflow with test JSON file
- Test card retrieval after ingestion
- Test upsert behavior (insert then update same card)
- Test database constraints (duplicate IDs, invalid enums)

**File**: `backend/tests/integration/test_cards_api.py`

- Test `GET /cards` endpoint returns data from database
- Test endpoint with empty database
- Test endpoint with database connection failure
- Test response format matches Card model

### Manual Testing

1. **Ingestion Test**:
   ```bash
   cd backend
   uv run python src/scripts/ingest_cards.py
   ```
   - Verify console output shows cards processed
   - Check database: `SELECT COUNT(*) FROM cards;`

2. **API Test**:
   ```bash
   curl http://localhost:8000/api/cards
   ```
   - Verify JSON response contains card array
   - Verify image URLs are external CDN links

3. **Re-ingestion Test**:
   - Run ingestion script twice
   - Verify no duplicate entries
   - Verify `updated_at` timestamps change

## Performance Considerations

### Database Indexing

The existing schema includes indexes on:
- `id` (PRIMARY KEY)
- `name` (for filtering)
- `elixir_cost` (for filtering)
- `rarity` (for filtering)
- `type` (for filtering)

These indexes support efficient querying for the frontend's filtering features.

### Query Optimization

- Use `SELECT *` for simplicity (card table has limited columns)
- Consider adding `LIMIT` if pagination is needed in future
- Connection pooling already configured in `DatabaseManager`

### Caching Strategy (Future Enhancement)

While not implemented in this phase, consider:
- Redis cache for card data (TTL: 24 hours)
- In-memory cache in FastAPI with `@lru_cache`
- Cache invalidation on re-ingestion

## Migration Strategy

### Phase 1: Database Preparation
1. Verify `cards` table exists (already in schema.sql)
2. Run ingestion script to populate data
3. Verify data integrity with SQL queries

### Phase 2: Service Implementation
1. Create `CardService` class
2. Add unit tests for service
3. Update dependency injection

### Phase 3: API Update
1. Update `cards.py` endpoint to use `CardService`
2. Remove `ClashRoyaleAPIService` dependency from cards endpoint
3. Update error handling

### Phase 4: Testing & Validation
1. Run integration tests
2. Manual API testing
3. Frontend smoke testing

### Phase 5: Deployment
1. Run ingestion script on production database
2. Deploy updated backend code
3. Monitor for errors

## Rollback Plan

If issues arise:
1. Revert API endpoint to use `ClashRoyaleAPIService`
2. Keep database populated for future retry
3. Investigate and fix issues
4. Re-deploy when ready

## Future Enhancements

1. **Automatic Updates**: Scheduled job to fetch new cards from API and update database
2. **Admin API**: Endpoints to manually trigger re-ingestion
3. **Card Versioning**: Track changes to card stats over time
4. **Filtering Endpoints**: Add query parameters for filtering by rarity, type, etc.
5. **Caching Layer**: Add Redis for improved performance
6. **Audit Logging**: Track when cards are added/updated
