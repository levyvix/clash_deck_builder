# Decks API

The Decks API provides CRUD operations for user decks, including support for evolution card slots and deck validation.

## Overview

Key features:

- **Maximum 20 decks per user** - Enforced at API level
- **8 cards per deck** - Standard Clash Royale deck size
- **Up to 2 evolution slots** - Special evolution card tracking
- **User-scoped resources** - Users can only access their own decks
- **Automatic elixir calculation** - Average elixir cost computed on save

## Data Format Transformation

!!! important "Frontend vs Backend Format"
    The frontend and backend use different deck formats. The API layer transforms between them.

**Frontend Format (DeckBuilder component):**

```json
{
  "id": 123,
  "name": "My Deck",
  "slots": [
    {
      "card": { "id": 26000000, "name": "Knight", "elixir_cost": 3 },
      "isEvolution": false
    },
    {
      "card": { "id": 26000001, "name": "Archers", "elixir_cost": 3 },
      "isEvolution": true
    }
  ]
}
```

**Backend Format (API request/response):**

```json
{
  "id": 123,
  "name": "My Deck",
  "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000007],
  "evolution_slots": [26000001],
  "average_elixir": 3.5,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

See [Deck Management](../features/deck-management.md) for transformation details.

## Endpoints

### Create Deck

Create a new deck for the authenticated user.

**Endpoint:** `POST /api/decks`

**Authentication Required:** Yes (Bearer token)

**Request Body:**

```json
{
  "name": "Hog Cycle",
  "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000007],
  "evolution_slots": [26000001, 26000002]
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Deck name (1-255 characters) |
| `cards` | array[integer] | Yes | Array of 8 card IDs |
| `evolution_slots` | array[integer] | No | Array of up to 2 card IDs (must be in `cards`) |

**Validation Rules:**

- Deck name must be 1-255 characters
- Must have exactly 8 cards
- All card IDs must exist in database
- Evolution slots must contain max 2 cards
- Evolution slot card IDs must be in the main `cards` array
- User cannot exceed 20 deck limit

**Success Response (201 Created):**

```json
{
  "id": 123,
  "name": "Hog Cycle",
  "user_id": 456,
  "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000007],
  "evolution_slots": [26000001, 26000002],
  "average_elixir": 3.5,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 400 Bad Request | Invalid deck data | `{"detail": "Deck must have exactly 8 cards"}` |
| 400 Bad Request | Deck limit exceeded | `{"detail": "Maximum 20 decks allowed per user"}` |
| 401 Unauthorized | Not authenticated | `{"detail": "Not authenticated"}` |
| 422 Unprocessable Entity | Validation error | `{"detail": [{"loc": ["body", "name"], "msg": "field required"}]}` |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/decks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "name": "Hog Cycle",
    "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000007],
    "evolution_slots": [26000001]
  }'
```

**Frontend Usage:**

```javascript
// Transform frontend format to backend format
function transformDeckForBackend(deck) {
  return {
    name: deck.name,
    cards: deck.slots.map(slot => slot.card.id),
    evolution_slots: deck.slots
      .filter(slot => slot.isEvolution)
      .map(slot => slot.card.id)
  };
}

// Create deck
async function createDeck(deck) {
  const payload = transformDeckForBackend(deck);

  const response = await fetch('/api/decks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAccessToken()}`
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error('Failed to create deck');
  }

  return await response.json();
}
```

---

### Get All User Decks

Retrieve all decks for the authenticated user.

**Endpoint:** `GET /api/decks`

**Authentication Required:** Yes (Bearer token)

**Request Parameters:** None

**Success Response (200 OK):**

```json
[
  {
    "id": 123,
    "name": "Hog Cycle",
    "user_id": 456,
    "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000007],
    "evolution_slots": [26000001],
    "average_elixir": 3.5,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  },
  {
    "id": 124,
    "name": "Golem Beatdown",
    "user_id": 456,
    "cards": [26000008, 26000009, 26000010, 26000011, 26000012, 26000013, 26000014, 26000015],
    "evolution_slots": [],
    "average_elixir": 4.2,
    "created_at": "2024-01-16T11:00:00Z",
    "updated_at": "2024-01-16T11:00:00Z"
  }
]
```

**Example Request:**

```bash
curl http://localhost:8000/api/decks \
  -H "Authorization: Bearer your-token"
```

**Frontend Usage:**

```javascript
// Transform backend format to frontend format
function transformDeckForFrontend(backendDeck, allCards) {
  const cardMap = new Map(allCards.map(c => [c.id, c]));

  return {
    id: backendDeck.id,
    name: backendDeck.name,
    averageElixir: backendDeck.average_elixir,
    createdAt: backendDeck.created_at,
    updatedAt: backendDeck.updated_at,
    slots: backendDeck.cards.map(cardId => ({
      card: cardMap.get(cardId),
      isEvolution: backendDeck.evolution_slots.includes(cardId)
    }))
  };
}

// Fetch all decks
async function fetchDecks() {
  const response = await fetch('/api/decks', {
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`
    }
  });

  const backendDecks = await response.json();
  const allCards = await fetchCards(); // Get card details

  return backendDecks.map(deck =>
    transformDeckForFrontend(deck, allCards)
  );
}
```

---

### Get Single Deck

Retrieve a specific deck by ID for the authenticated user.

**Endpoint:** `GET /api/decks/{deck_id}`

**Authentication Required:** Yes (Bearer token)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID to retrieve |

**Success Response (200 OK):**

```json
{
  "id": 123,
  "name": "Hog Cycle",
  "user_id": 456,
  "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000007],
  "evolution_slots": [26000001],
  "average_elixir": 3.5,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 404 Not Found | Deck doesn't exist or not authorized | `{"detail": "Deck with ID 123 not found"}` |
| 401 Unauthorized | Not authenticated | `{"detail": "Not authenticated"}` |

**Example Request:**

```bash
curl http://localhost:8000/api/decks/123 \
  -H "Authorization: Bearer your-token"
```

---

### Update Deck

Update an existing deck for the authenticated user.

**Endpoint:** `PUT /api/decks/{deck_id}`

**Authentication Required:** Yes (Bearer token)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID to update |

**Request Body:**

```json
{
  "name": "Updated Hog Cycle",
  "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000016],
  "evolution_slots": [26000001, 26000016]
}
```

**Validation Rules:**

Same as Create Deck, plus:

- Deck must belong to authenticated user
- Deck ID in path must match existing deck

**Success Response (200 OK):**

```json
{
  "id": 123,
  "name": "Updated Hog Cycle",
  "user_id": 456,
  "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000016],
  "evolution_slots": [26000001, 26000016],
  "average_elixir": 3.6,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T12:30:00Z"
}
```

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 400 Bad Request | Invalid deck data | `{"detail": "Deck must have exactly 8 cards"}` |
| 404 Not Found | Deck doesn't exist or not authorized | `{"detail": "Deck with ID 123 not found or not authorized"}` |
| 401 Unauthorized | Not authenticated | `{"detail": "Not authenticated"}` |

**Example Request:**

```bash
curl -X PUT http://localhost:8000/api/decks/123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "name": "Updated Hog Cycle",
    "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 26000006, 26000016],
    "evolution_slots": [26000001, 26000016]
  }'
```

---

### Delete Deck

Delete a deck for the authenticated user.

**Endpoint:** `DELETE /api/decks/{deck_id}`

**Authentication Required:** Yes (Bearer token)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck_id` | integer | Deck ID to delete |

**Success Response (204 No Content):**

No response body

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 404 Not Found | Deck doesn't exist or not authorized | `{"detail": "Deck with ID 123 not found or not authorized"}` |
| 401 Unauthorized | Not authenticated | `{"detail": "Not authenticated"}` |

**Example Request:**

```bash
curl -X DELETE http://localhost:8000/api/decks/123 \
  -H "Authorization: Bearer your-token"
```

**Frontend Usage:**

```javascript
async function deleteDeck(deckId) {
  const response = await fetch(`/api/decks/${deckId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`
    }
  });

  if (response.status === 204) {
    console.log('Deck deleted successfully');
    return true;
  } else if (response.status === 404) {
    console.error('Deck not found');
    return false;
  } else {
    throw new Error('Failed to delete deck');
  }
}
```

---

## Business Rules

### Deck Limit

- **Maximum:** 20 decks per user
- **Enforcement:** Backend validates on creation
- **Error:** 400 Bad Request with message "Maximum 20 decks allowed per user"

```python
# Backend validation (deck_service.py)
async def create_deck(self, deck: Deck, user: User) -> Deck:
    existing_decks = await self.get_user_decks(user)
    if len(existing_decks) >= 20:
        raise DeckLimitExceededError("Maximum 20 decks allowed per user")
    # ... continue creation
```

### Card Validation

- **Count:** Exactly 8 cards required
- **Existence:** All card IDs must exist in `cards` table
- **Uniqueness:** Cards can be duplicated (Clash Royale allows this)

### Evolution Slots

- **Maximum:** 2 evolution slots per deck
- **Subset:** Evolution card IDs must be in main `cards` array
- **Optional:** Empty evolution slots array is valid

```javascript
// Frontend validation
function validateDeck(deck) {
  const errors = [];

  if (deck.slots.length !== 8) {
    errors.push('Deck must have exactly 8 cards');
  }

  const evolutionCount = deck.slots.filter(s => s.isEvolution).length;
  if (evolutionCount > 2) {
    errors.push('Maximum 2 evolution slots allowed');
  }

  return errors;
}
```

### Average Elixir Calculation

Automatically computed on save:

```python
# Backend calculation
def calculate_average_elixir(card_ids: List[int], card_service: CardService) -> float:
    cards = card_service.get_cards_by_ids(card_ids)
    total_elixir = sum(card.elixir_cost for card in cards)
    return round(total_elixir / len(cards), 2)
```

## Authorization

All deck endpoints use user-scoped authorization:

```python
# Backend authorization check
async def get_deck(self, deck_id: int, user: User) -> Optional[Deck]:
    deck = self.db.get_deck_by_id(deck_id)

    # Verify deck belongs to requesting user
    if deck and deck.user_id != user.id:
        return None  # Act as if deck doesn't exist

    return deck
```

This prevents:

- Users accessing other users' decks
- Users modifying other users' decks
- Deck ID enumeration attacks

## Testing

### Manual Testing

```bash
# Create deck
curl -X POST http://localhost:8000/api/decks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Test","cards":[26000000,26000001,26000002,26000003,26000004,26000005,26000006,26000007]}'

# Get all decks
curl http://localhost:8000/api/decks \
  -H "Authorization: Bearer $TOKEN"

# Get specific deck
curl http://localhost:8000/api/decks/1 \
  -H "Authorization: Bearer $TOKEN"

# Update deck
curl -X PUT http://localhost:8000/api/decks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Updated","cards":[26000000,26000001,26000002,26000003,26000004,26000005,26000006,26000008]}'

# Delete deck
curl -X DELETE http://localhost:8000/api/decks/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Automated Testing

```bash
cd backend

# Contract tests - verify API contract
uv run pytest tests/contract/test_decks_*.py -v

# Integration tests - full workflow
uv run pytest tests/integration/test_deck_operations.py -v

# Unit tests - service logic
uv run pytest tests/test_deck_service.py -v
```

## Related Documentation

- [Deck Management Feature](../features/deck-management.md) - Full deck management flow
- [Evolution Cards Feature](../features/evolution-cards.md) - Evolution system
- [Backend Architecture](../architecture/backend.md) - Deck service implementation
- [Frontend Development](../development/frontend.md) - DeckBuilder component
