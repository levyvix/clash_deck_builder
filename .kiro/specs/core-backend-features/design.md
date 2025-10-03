# Design Document

## Overview

This design document outlines the implementation of core backend features for the Clash Royale Deck Builder. The focus is on creating a robust, production-ready FastAPI application with proper dependency injection, database integration, external API integration, and comprehensive error handling.

## Architecture

### Application Structure
```
backend/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── cards.py           # Card-related endpoints
│   │   └── decks.py           # Deck-related endpoints
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── card.py
│   │   ├── deck.py
│   │   └── user.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── clash_api_service.py
│   │   └── deck_service.py
│   ├── utils/                  # Utilities and configuration
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── dependencies.py
│   └── exceptions/             # Custom exceptions
│       ├── __init__.py
│       └── handlers.py
```

### Layered Architecture Pattern
- **API Layer**: FastAPI routers handling HTTP requests/responses
- **Service Layer**: Business logic and external integrations
- **Data Layer**: Database operations and data persistence
- **Configuration Layer**: Environment-based configuration management

## Components and Interfaces

### 1. Main Application (main.py)
**Purpose**: FastAPI application factory and configuration
**Key Features**:
- Application lifecycle management
- Router registration
- Middleware configuration
- Exception handler registration
- CORS configuration for frontend integration

### 2. Configuration Management (utils/config.py)
**Purpose**: Centralized configuration using Pydantic Settings
**Key Features**:
- Environment variable loading
- Configuration validation
- Type-safe configuration access
- Default values for development

```python
class Settings(BaseSettings):
    database_url: str
    clash_royale_api_key: str
    cors_origins: List[str] = ["http://localhost:3000"]
    debug: bool = False
    
    class Config:
        env_file = ".env"
```

### 3. Database Integration (utils/database.py)
**Purpose**: Database connection management and session handling
**Key Features**:
- Connection pooling
- Session management with context managers
- Transaction handling
- Database initialization

### 4. Dependency Injection (utils/dependencies.py)
**Purpose**: FastAPI dependency providers
**Key Dependencies**:
- Database session provider
- Clash Royale API service provider
- Current user provider (placeholder for future auth)

### 5. Enhanced Clash Royale API Service
**Purpose**: Real integration with Clash Royale API
**Key Features**:
- HTTP client with proper error handling
- Rate limiting consideration
- Data transformation from API format to internal models
- Caching strategy for card data

### 6. Enhanced Deck Service
**Purpose**: Deck CRUD operations with proper database integration
**Key Features**:
- Transactional operations
- JSON serialization/deserialization for card data
- Automatic average elixir calculation
- User-scoped operations

### 7. Exception Handling (exceptions/handlers.py)
**Purpose**: Centralized error handling and HTTP response mapping
**Key Features**:
- Custom exception classes
- HTTP status code mapping
- Structured error responses
- Logging integration

## Data Models

### Enhanced Card Model
```python
class Card(BaseModel):
    id: int
    name: str
    elixir_cost: int
    rarity: str  # Common, Rare, Epic, Legendary, Champion
    type: str    # Troop, Spell, Building
    arena: Optional[str] = None
    image_url: str
    image_url_evo: Optional[str] = None
    
    @validator('rarity')
    def validate_rarity(cls, v):
        allowed = ['Common', 'Rare', 'Epic', 'Legendary', 'Champion']
        if v not in allowed:
            raise ValueError(f'Rarity must be one of {allowed}')
        return v
```

### Enhanced Deck Model
```python
class Deck(BaseModel):
    id: Optional[int] = None
    name: str
    user_id: Optional[int] = None
    cards: List[Card]
    evolution_slots: List[Card] = []
    average_elixir: Optional[float] = None
    
    @validator('cards')
    def validate_cards_count(cls, v):
        if len(v) > 8:
            raise ValueError('Deck cannot have more than 8 cards')
        return v
    
    @validator('evolution_slots')
    def validate_evo_slots(cls, v):
        if len(v) > 2:
            raise ValueError('Deck cannot have more than 2 evolution slots')
        return v
    
    def calculate_average_elixir(self) -> float:
        if not self.cards:
            return 0.0
        total_elixir = sum(card.elixir_cost for card in self.cards)
        total_elixir += sum(card.elixir_cost for card in self.evolution_slots)
        total_cards = len(self.cards) + len(self.evolution_slots)
        return round(total_elixir / total_cards, 2) if total_cards > 0 else 0.0
```

## Error Handling

### Custom Exception Classes
```python
class ClashAPIError(Exception):
    """Raised when Clash Royale API calls fail"""
    pass

class DatabaseError(Exception):
    """Raised when database operations fail"""
    pass

class DeckNotFoundError(Exception):
    """Raised when a deck is not found"""
    pass
```

### HTTP Status Code Mapping
- 400 Bad Request: Validation errors, invalid input
- 404 Not Found: Deck not found, user not found
- 500 Internal Server Error: Database errors, unexpected errors
- 503 Service Unavailable: Clash Royale API unavailable

## Testing Strategy

### Unit Tests
- Service layer methods with mocked dependencies
- Model validation and business logic
- Utility functions and configuration loading

### Integration Tests
- Database operations with test database
- API endpoints with test client
- External API integration with mock responses

### Contract Tests
- Clash Royale API response format validation
- Database schema validation
- API endpoint contract validation

## Performance Considerations

### Caching Strategy
- Cache Clash Royale API card data (cards rarely change)
- Use Redis or in-memory caching for frequently accessed data
- Implement cache invalidation strategy

### Database Optimization
- Proper indexing on frequently queried columns
- Connection pooling for concurrent requests
- Query optimization for deck retrieval

### API Rate Limiting
- Respect Clash Royale API rate limits
- Implement exponential backoff for failed requests
- Consider request queuing for high traffic

## Security Considerations

### API Key Management
- Store Clash Royale API key in environment variables
- Never expose API keys in logs or error messages
- Implement key rotation strategy

### Database Security
- Use parameterized queries to prevent SQL injection
- Implement proper connection string security
- Database user with minimal required permissions

### Input Validation
- Validate all input data using Pydantic models
- Sanitize user input for deck names
- Implement request size limits