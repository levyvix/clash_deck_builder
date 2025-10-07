# Testing Guide

Comprehensive testing strategy and guidelines for the Clash Royale Deck Builder project.

## Testing Philosophy

- **Test-Driven Development**: Write tests before or alongside code
- **Test Pyramid**: More unit tests, fewer integration tests, minimal E2E
- **Test Behavior**: Test what the code does, not how it does it
- **Keep Tests Simple**: Each test should verify one thing
- **Maintainable**: Tests should be easy to understand and update

## Test Types

### Unit Tests

**Purpose**: Test individual functions/methods in isolation

**Location**:
- Backend: `backend/tests/unit/`
- Frontend: `frontend/src/components/*.test.tsx`

**Example (Backend):**

```python
# backend/tests/unit/test_card_service.py
import pytest
from src.services.card_service import CardService
from src.models.card import Card

@pytest.fixture
def card_service():
    return CardService()

def test_get_all_cards(card_service):
    cards = card_service.get_all_cards()
    assert isinstance(cards, list)
    assert all(isinstance(c, Card) for c in cards)

def test_get_cards_by_rarity(card_service):
    legendary_cards = card_service.get_cards_by_rarity('Legendary')
    assert all(c.rarity == 'Legendary' for c in legendary_cards)

def test_filter_evolution_cards(card_service):
    evo_cards = card_service.get_evolution_cards()
    assert all(c.image_url_evo is not None for c in evo_cards)
```

**Example (Frontend):**

```typescript
// frontend/src/services/evolutionService.test.ts
import { evolutionService } from './evolutionService';

describe('evolutionService', () => {
  it('identifies evolution capable cards', () => {
    const card = { id: 1, name: 'Knight', image_url_evo: 'url' };
    expect(evolutionService.canEvolve(card)).toBe(true);
  });

  it('validates evolution slot limits', () => {
    const slots = [
      { card: {}, isEvolution: true },
      { card: {}, isEvolution: true },
      { card: {}, isEvolution: true },  // 3rd evolution - invalid
    ];

    const result = evolutionService.validateEvolutionSlots(slots);
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Maximum 2 evolution slots allowed');
  });
});
```

### Integration Tests

**Purpose**: Test multiple components working together

**Location**:
- Backend: `backend/tests/integration/`
- Frontend: `frontend/src/services/*.integration.test.ts`

**Example (Backend):**

```python
# backend/tests/integration/test_deck_operations.py
import pytest
from src.services.deck_service import DeckService
from src.services.card_service import CardService
from src.models.deck import Deck

@pytest.mark.integration
def test_full_deck_lifecycle(test_db, test_user):
    deck_service = DeckService()
    card_service = CardService()

    # Get some cards
    cards = card_service.get_all_cards()[:8]
    card_ids = [c.id for c in cards]

    # Create deck
    deck = Deck(name="Integration Test Deck", cards=card_ids)
    created_deck = deck_service.create_deck(deck, test_user)

    assert created_deck.id is not None
    assert created_deck.average_elixir > 0

    # Retrieve deck
    retrieved_deck = deck_service.get_deck(created_deck.id, test_user)
    assert retrieved_deck.name == "Integration Test Deck"
    assert len(retrieved_deck.cards) == 8

    # Update deck
    retrieved_deck.name = "Updated Deck"
    updated_deck = deck_service.update_deck(retrieved_deck, test_user)
    assert updated_deck.name == "Updated Deck"

    # Delete deck
    success = deck_service.delete_deck(created_deck.id, test_user)
    assert success is True

    # Verify deletion
    deleted_deck = deck_service.get_deck(created_deck.id, test_user)
    assert deleted_deck is None
```

**Example (Frontend):**

```typescript
// frontend/src/services/deckStorageService.integration.test.ts
describe('DeckStorageService Integration', () => {
  it('handles transition from anonymous to authenticated', async () => {
    const storage = new DeckStorageService(() => false);

    // Save deck as anonymous user
    const deck = { name: 'Test', slots: [...] };
    await storage.saveDeck(deck);

    // Verify saved locally
    const localDecks = await storage.getAllDecks();
    expect(localDecks).toHaveLength(1);
    expect(localDecks[0].storageType).toBe('local');

    // Simulate user login
    const authStorage = new DeckStorageService(() => true);

    // Migrate data
    await authStorage.migrateLocalDecksToServer();

    // Verify migrated to server
    const serverDecks = await authStorage.getAllDecks();
    expect(serverDecks[0].storageType).toBe('server');
  });
});
```

### Contract Tests

**Purpose**: Verify API contracts between frontend and backend

**Location**: `backend/tests/contract/`

**Example:**

```python
# backend/tests/contract/test_decks_create.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_deck_contract(auth_token):
    # Request format
    request_body = {
        "name": "Test Deck",
        "cards": [1, 2, 3, 4, 5, 6, 7, 8],
        "evolution_slots": [1, 2]
    }

    response = client.post(
        "/api/decks",
        json=request_body,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Response format
    assert response.status_code == 201
    data = response.json()

    # Verify response schema
    assert "id" in data
    assert "name" in data
    assert "cards" in data
    assert "evolution_slots" in data
    assert "average_elixir" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify types
    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["cards"], list)
    assert isinstance(data["evolution_slots"], list)
    assert isinstance(data["average_elixir"], float)

    # Verify data
    assert data["name"] == "Test Deck"
    assert len(data["cards"]) == 8
    assert len(data["evolution_slots"]) == 2
```

### End-to-End Tests

**Purpose**: Test complete user workflows

**Location**: `frontend/tests/`

**Tool**: Playwright

**Example:**

```typescript
// frontend/tests/e2e-essential.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Deck Building Flow', () => {
  test('user can build and save a deck', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:3000');

    // Wait for cards to load
    await expect(page.locator('.card-display')).toHaveCount(109, { timeout: 5000 });

    // Add 8 cards to deck
    for (let i = 0; i < 8; i++) {
      await page.locator('.card-display').nth(i).click();
    }

    // Verify deck is full
    const deckSlots = page.locator('.deck-slot--filled');
    await expect(deckSlots).toHaveCount(8);

    // Sign in
    await page.click('text=Sign in with Google');
    // (mock Google OAuth in test environment)

    // Save deck
    await page.fill('input[placeholder="Deck Name"]', 'E2E Test Deck');
    await page.click('button:has-text("Save Deck")');

    // Verify success message
    await expect(page.locator('text=Deck saved successfully')).toBeVisible();

    // Navigate to saved decks
    await page.click('text=My Decks');

    // Verify deck appears in list
    await expect(page.locator('text=E2E Test Deck')).toBeVisible();
  });
});
```

## Backend Testing

### Running Tests

```bash
cd backend

# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Contract tests only
uv run pytest tests/contract/

# Specific file
uv run pytest tests/test_deck_service.py

# With coverage
uv run pytest --cov=src --cov-report=html

# Verbose
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Show print output
uv run pytest -s
```

### Test Fixtures

```python
# backend/tests/conftest.py
import pytest
from src.utils.database import DatabaseManager
from src.models.user import User
from src.services.auth_service import AuthService

@pytest.fixture(scope="session")
def db_manager():
    """Provide database manager for tests."""
    return DatabaseManager()

@pytest.fixture(scope="function")
def test_db(db_manager):
    """Provide clean database for each test."""
    # Setup: Create tables
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        # Run migrations
        cursor.execute(open('database/init/01-schema.sql').read())
        conn.commit()

    yield db_manager

    # Teardown: Clean database
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS decks")
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()

@pytest.fixture
def test_user():
    """Provide test user."""
    return User(
        id="test-user-123",
        google_id="google-123",
        email="test@example.com",
        name="Test User"
    )

@pytest.fixture
def auth_token(test_user):
    """Provide authentication token."""
    auth_service = AuthService()
    tokens = auth_service.generate_jwt_tokens(test_user)
    return tokens["access_token"]
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock():
    # Mock external API
    with patch('src.services.clash_api_service.httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        service = ClashAPIService()
        cards = service.fetch_cards()

        assert cards == []
```

## Frontend Testing

### Running Tests

```bash
cd frontend

# Interactive mode (watch for changes)
npm test

# Run all tests once
npm run test:run

# With coverage
npm test -- --coverage

# Specific file
npm test -- DeckBuilder.test.tsx

# Update snapshots
npm test -- -u
```

### Component Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DeckBuilder } from './DeckBuilder';

describe('DeckBuilder', () => {
  beforeEach(() => {
    // Reset any global state
    jest.clearAllMocks();
  });

  it('renders empty deck slots', () => {
    render(<DeckBuilder />);

    // Find all deck slots
    const slots = screen.getAllByTestId(/deck-slot-\d/);
    expect(slots).toHaveLength(8);

    // Verify all slots are empty
    slots.forEach(slot => {
      expect(slot).toHaveTextContent('Empty Slot');
    });
  });

  it('adds card to first empty slot', () => {
    render(<DeckBuilder />);

    // Click a card
    const card = screen.getByTestId('card-26000000');
    fireEvent.click(card);

    // Verify card added to first slot
    const firstSlot = screen.getByTestId('deck-slot-0');
    expect(firstSlot).toHaveTextContent('Knight');
  });

  it('shows validation error for invalid deck', async () => {
    render(<DeckBuilder />);

    // Try to save empty deck
    const saveButton = screen.getByText('Save Deck');
    fireEvent.click(saveButton);

    // Verify error message
    await waitFor(() => {
      expect(screen.getByText('Deck must have 8 cards')).toBeInTheDocument();
    });
  });
});
```

### Async Testing

```typescript
it('fetches and displays cards', async () => {
  // Mock API response
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve([
        { id: 1, name: 'Knight', elixir_cost: 3 },
      ]),
    } as Response)
  );

  render(<CardGallery />);

  // Wait for loading to finish
  await waitFor(() => {
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  // Verify cards displayed
  expect(screen.getByText('Knight')).toBeInTheDocument();

  // Clean up
  (global.fetch as jest.Mock).mockRestore();
});
```

### User Event Testing

```typescript
import userEvent from '@testing-library/user-event';

it('allows user to type in search box', async () => {
  const user = userEvent.setup();
  render(<CardGallery />);

  const searchBox = screen.getByPlaceholderText('Search cards...');

  await user.type(searchBox, 'Knight');

  expect(searchBox).toHaveValue('Knight');
});
```

## Test Coverage

### Coverage Reports

```bash
# Backend
cd backend
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html

# Frontend
cd frontend
npm test -- --coverage
# Open coverage/lcov-report/index.html
```

### Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: Critical paths covered
- **Contract Tests**: All API endpoints covered
- **E2E Tests**: Key user workflows covered

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install UV
        run: pip install uv
      - name: Install dependencies
        run: cd backend && uv sync
      - name: Run tests
        run: cd backend && uv run pytest --cov=src

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run tests
        run: cd frontend && npm test -- --coverage
```

## Best Practices

### Write Testable Code

```python
# L Hard to test
def process_data():
    db = DatabaseManager()
    data = db.query("SELECT * FROM table")
    return transform(data)

#  Easy to test
def process_data(db: DatabaseManager):
    data = db.query("SELECT * FROM table")
    return transform(data)

def transform(data: list) -> list:
    return [item.upper() for item in data]
```

### One Assertion Per Test

```python
# L Too many assertions
def test_deck_creation():
    deck = create_deck()
    assert deck.id is not None
    assert deck.name == "Test"
    assert len(deck.cards) == 8
    assert deck.average_elixir > 0

#  Focused tests
def test_deck_has_id():
    deck = create_deck()
    assert deck.id is not None

def test_deck_has_correct_name():
    deck = create_deck()
    assert deck.name == "Test"

def test_deck_has_eight_cards():
    deck = create_deck()
    assert len(deck.cards) == 8
```

### Test Edge Cases

```python
def test_deck_validation():
    # Normal case
    assert validate_deck([1, 2, 3, 4, 5, 6, 7, 8]) == True

    # Edge cases
    assert validate_deck([]) == False  # Empty
    assert validate_deck([1, 2, 3]) == False  # Too few
    assert validate_deck([1, 2, 3, 4, 5, 6, 7, 8, 9]) == False  # Too many
    assert validate_deck([1, 1, 1, 1, 1, 1, 1, 1]) == True  # Duplicates allowed
    assert validate_deck(None) == False  # None
```

### Use Descriptive Names

```python
# L Unclear
def test_deck():
    ...

#  Clear
def test_create_deck_returns_deck_with_id():
    ...

def test_create_deck_fails_when_user_has_20_decks():
    ...
```

## Debugging Tests

### Print Debugging

```python
def test_something():
    result = my_function()
    print(f"Result: {result}")  # Will show with pytest -s
    assert result == expected
```

### Pytest Debugger

```python
def test_something():
    result = my_function()
    import pdb; pdb.set_trace()  # Debugger stops here
    assert result == expected
```

### React Testing Library Debug

```typescript
it('debugs component', () => {
  const { debug } = render(<MyComponent />);
  debug();  // Prints current DOM
});
```

## Related Documentation

- [Backend Development](backend.md) - Backend testing setup
- [Frontend Development](frontend.md) - Frontend testing setup
- [CI/CD Guide](../operations/deployment.md) - Automated testing
- [Code Quality](../architecture/overview.md) - Quality standards
