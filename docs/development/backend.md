# Backend Development Guide

Complete guide for developing backend features for the Clash Royale Deck Builder.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- UV package manager (not pip or poetry)
- MySQL 8.0 (Docker or local)
- Git

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd clash_deck_builder/backend

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Environment Variables

```bash
# Database
DB_HOST=localhost  # or 'database' for Docker
DB_PORT=3306
DB_NAME=clash_deck_builder
DB_USER=clash_user
DB_PASSWORD=your_secure_password

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# JWT
JWT_SECRET_KEY=$(openssl rand -base64 32)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Clash Royale API
CLASH_ROYALE_API_KEY=your_api_key

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
```

### Running the Backend

```bash
# Start development server with hot reload
uv run uvicorn src.main:app --reload

# Or specify host and port
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Backend available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

## Development Workflow

### Adding a New Endpoint

**1. Define the Model** (`src/models/`)

```python
# src/models/achievement.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Achievement(BaseModel):
    id: Optional[int] = None
    user_id: str
    achievement_type: str = Field(..., min_length=1)
    earned_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

**2. Create Service Logic** (`src/services/`)

```python
# src/services/achievement_service.py
from typing import List
from ..models.achievement import Achievement
from ..utils.database import get_db_manager

class AchievementService:
    def __init__(self):
        self.db_manager = get_db_manager()

    def get_user_achievements(self, user_id: str) -> List[Achievement]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM achievements WHERE user_id = %s",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [Achievement(**row) for row in rows]

    def award_achievement(self, user_id: str, achievement_type: str) -> Achievement:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO achievements (user_id, achievement_type) VALUES (%s, %s)",
                (user_id, achievement_type)
            )
            conn.commit()

            return Achievement(
                id=cursor.lastrowid,
                user_id=user_id,
                achievement_type=achievement_type
            )
```

**3. Create API Route** (`src/api/`)

```python
# src/api/achievements.py
from fastapi import APIRouter, Depends
from typing import List
from ..models.achievement import Achievement
from ..services.achievement_service import AchievementService
from ..middleware.auth_middleware import require_auth

router = APIRouter()

@router.get("/achievements", response_model=List[Achievement])
async def get_achievements(
    current_user: dict = Depends(require_auth),
    achievement_service: AchievementService = Depends(lambda: AchievementService())
):
    """Get all achievements for the current user."""
    return achievement_service.get_user_achievements(current_user["user_id"])

@router.post("/achievements", response_model=Achievement, status_code=201)
async def award_achievement(
    achievement_type: str,
    current_user: dict = Depends(require_auth),
    achievement_service: AchievementService = Depends(lambda: AchievementService())
):
    """Award an achievement to the current user."""
    return achievement_service.award_achievement(
        current_user["user_id"],
        achievement_type
    )
```

**4. Register Router** (`src/main.py`)

```python
from .api import achievements

app.include_router(
    achievements.router,
    prefix="/api",
    tags=["Achievements"]
)
```

**5. Add Tests**

```python
# tests/test_achievement_service.py
import pytest
from src.services.achievement_service import AchievementService

@pytest.fixture
def achievement_service():
    return AchievementService()

def test_get_user_achievements(achievement_service, test_user):
    achievements = achievement_service.get_user_achievements(test_user.id)
    assert isinstance(achievements, list)

def test_award_achievement(achievement_service, test_user):
    achievement = achievement_service.award_achievement(
        test_user.id,
        "first_deck"
    )
    assert achievement.id is not None
    assert achievement.achievement_type == "first_deck"
```

### Database Operations

**Direct SQL (Preferred):**

```python
# SELECT query
with self.db_manager.get_connection() as conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM decks WHERE user_id = %s", (user_id,))
    rows = cursor.fetchall()

# INSERT query
with self.db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO decks (name, user_id, cards) VALUES (%s, %s, %s)",
        (deck.name, user_id, json.dumps(deck.cards))
    )
    conn.commit()
    deck_id = cursor.lastrowid

# UPDATE query
with self.db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET name = %s WHERE id = %s",
        (new_name, user_id)
    )
    conn.commit()

# DELETE query
with self.db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM decks WHERE id = %s", (deck_id,))
    conn.commit()
```

**Transactions:**

```python
with self.db_manager.get_connection() as conn:
    cursor = conn.cursor()
    try:
        # Multiple operations in single transaction
        cursor.execute("INSERT INTO decks (...) VALUES (...)", (...))
        deck_id = cursor.lastrowid

        cursor.execute("INSERT INTO deck_stats (...) VALUES (...)", (deck_id, ...))

        conn.commit()  # Commit all changes
    except Exception as e:
        conn.rollback()  # Rollback on error
        raise
```

## Common Development Tasks

### Adding Environment Variable

**1. Add to `.env.example`:**

```bash
NEW_FEATURE_API_KEY=your_api_key_here
```

**2. Add to `src/utils/config.py`:**

```python
class Settings(BaseSettings):
    # ... existing fields ...
    NEW_FEATURE_API_KEY: str

    class Config:
        env_file = ".env"
```

**3. Use in code:**

```python
from ..utils.config import settings

api_key = settings.NEW_FEATURE_API_KEY
```

### Adding Custom Exception

**1. Define exception** (`src/exceptions/`):

```python
# src/exceptions/feature_exceptions.py
class FeatureError(Exception):
    """Base exception for feature errors."""
    pass

class FeatureNotFoundError(FeatureError):
    """Feature resource not found."""
    pass

class FeatureLimitExceededError(FeatureError):
    """Feature usage limit exceeded."""
    pass
```

**2. Register handler** (`src/exceptions/handlers.py`):

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from .feature_exceptions import FeatureNotFoundError

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(FeatureNotFoundError)
    async def feature_not_found_handler(request: Request, exc: FeatureNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)}
        )
```

**3. Use in service:**

```python
from ..exceptions.feature_exceptions import FeatureNotFoundError

def get_feature(self, feature_id: int):
    feature = self.db.get_feature(feature_id)
    if not feature:
        raise FeatureNotFoundError(f"Feature {feature_id} not found")
    return feature
```

### Adding Middleware

```python
# src/middleware/request_logging.py
from fastapi import Request
import logging
import time

logger = logging.getLogger(__name__)

async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} ({process_time:.2f}s)")

    return response

# Register in main.py
from .middleware.request_logging import request_logging_middleware

app.middleware("http")(request_logging_middleware)
```

## Code Style and Standards

### Use UV for Package Management

```bash
#  CORRECT - Use UV
uv add fastapi
uv add pytest --dev
uv run pytest

# L WRONG - Don't use pip
pip install fastapi
```

### Follow FastAPI Patterns

**Use dependency injection:**

```python
from fastapi import Depends

def get_service():
    return MyService()

@router.get("/resource")
async def get_resource(service: MyService = Depends(get_service)):
    return service.get_data()
```

**Use Pydantic for validation:**

```python
from pydantic import BaseModel, Field, field_validator

class UserInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```

**Use async for I/O operations:**

```python
#  CORRECT
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.json()

# L AVOID (unless necessary)
def fetch_data_sync():
    response = requests.get(url)
    return response.json()
```

### Code Formatting

**Use Black and Flake8:**

```bash
# Format code
uv run black .

# Lint code
uv run flake8 .

# Type checking
uv run mypy src/
```

**Configuration** (`.flake8`):

```ini
[flake8]
max-line-length = 120
extend-ignore = E203, W503
exclude = .git,__pycache__,.venv,build,dist
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical system error")

# Log with context
logger.info(f"Creating deck for user {user_id}")
```

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# Specific file
uv run pytest tests/test_deck_service.py

# Specific test
uv run pytest tests/test_deck_service.py::test_create_deck

# With coverage
uv run pytest --cov=src --cov-report=html

# Verbose output
uv run pytest -v

# Show print statements
uv run pytest -s
```

### Writing Tests

**Unit Tests** (test services):

```python
# tests/unit/test_deck_service.py
import pytest
from src.services.deck_service import DeckService
from src.models.deck import Deck

@pytest.fixture
def deck_service():
    return DeckService()

def test_calculate_average_elixir(deck_service):
    card_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    # Assuming these cards have known elixir costs
    avg = deck_service._calculate_average_elixir(card_ids)
    assert 0 <= avg <= 10
```

**Integration Tests** (test with database):

```python
# tests/integration/test_deck_operations.py
import pytest

@pytest.mark.integration
def test_full_deck_workflow(test_db, test_user):
    deck_service = DeckService()

    # Create deck
    deck = Deck(
        name="Test Deck",
        cards=[1, 2, 3, 4, 5, 6, 7, 8]
    )
    created = deck_service.create_deck(deck, test_user)
    assert created.id is not None

    # Retrieve deck
    retrieved = deck_service.get_deck(created.id, test_user)
    assert retrieved.name == "Test Deck"

    # Update deck
    retrieved.name = "Updated Deck"
    updated = deck_service.update_deck(retrieved, test_user)
    assert updated.name == "Updated Deck"

    # Delete deck
    success = deck_service.delete_deck(created.id, test_user)
    assert success is True
```

**API Tests** (test endpoints):

```python
# tests/contract/test_decks_api.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_deck(auth_token):
    response = client.post(
        "/api/decks",
        json={
            "name": "Test Deck",
            "cards": [1, 2, 3, 4, 5, 6, 7, 8]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Deck"
    assert len(data["cards"]) == 8
```

## Debugging

### Debug Server

```bash
# Run with debugger
python -m debugger src.main:app

# Or use VS Code launch configuration
```

**VS Code `launch.json`:**

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.main:app", "--reload"],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### Logging Debug Info

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# In code
logger.debug(f"Deck data: {deck.dict()}")
logger.debug(f"Query result: {rows}")
```

### Interactive Shell

```bash
# Start Python shell with context
uv run python

>>> from src.services.deck_service import DeckService
>>> service = DeckService()
>>> service.get_all_decks()
```

## Common Pitfalls

### Don't Mix Sync and Async

```python
# L WRONG
async def bad_function():
    result = sync_blocking_call()  # Blocks event loop
    return result

#  CORRECT
async def good_function():
    result = await async_call()
    return result

# Or for unavoidable sync code
import asyncio

async def acceptable_function():
    result = await asyncio.to_thread(sync_blocking_call)
    return result
```

### Always Close Database Connections

```python
#  CORRECT - Use context manager
with self.db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(query)

# L WRONG - Manual management risks leaks
conn = self.db_manager.get_connection()
cursor = conn.cursor()
cursor.execute(query)
# Might not close if exception occurs
conn.close()
```

### Validate User Input

```python
#  CORRECT - Use Pydantic
class DeckInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    cards: List[int] = Field(..., min_length=8, max_length=8)

# L WRONG - Manual validation
def create_deck(name: str, cards: list):
    # Missing validation - security risk
    deck = Deck(name=name, cards=cards)
```

## Performance Tips

### Use Connection Pooling

Already configured in `src/utils/database.py` - reuse connections.

### Cache Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_card_by_id(card_id: int):
    # Expensive database query
    return card
```

### Batch Database Operations

```python
#  GOOD - Single query
cursor.executemany(
    "INSERT INTO table (col1, col2) VALUES (%s, %s)",
    [(val1, val2), (val3, val4), ...]
)

# L BAD - Multiple queries
for item in items:
    cursor.execute("INSERT INTO table (col1, col2) VALUES (%s, %s)", (item.col1, item.col2))
```

### Use Async for Parallel Operations

```python
import asyncio

async def fetch_multiple():
    results = await asyncio.gather(
        fetch_cards(),
        fetch_decks(),
        fetch_user()
    )
    return results
```

## Related Documentation

- [Backend Architecture](../architecture/backend.md) - System design
- [API Reference](../api/overview.md) - API endpoints
- [Testing Guide](testing.md) - Testing strategies
- [Database Architecture](../architecture/database.md) - Database design
