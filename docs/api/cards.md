# Cards API

The Cards API provides access to Clash Royale card data stored in the local database. Card data is ingested from the official Clash Royale API and cached locally for performance.

## Overview

Card data rarely changes, so the API implements aggressive caching strategies:

- **Client-side caching**: 24-hour `max-age` headers
- **ETags**: For conditional requests
- **Server-side caching**: In-memory cache with invalidation

## Endpoints

### Get All Cards

Retrieve all Clash Royale cards from the database.

**Endpoint:** `GET /api/cards`

**Authentication Required:** No

**Request Parameters:** None

**Success Response (200 OK):**

```json
[
  {
    "id": 26000000,
    "name": "Knight",
    "elixir_cost": 3,
    "rarity": "Common",
    "type": "Troop",
    "arena": "Training Camp",
    "image_url": "https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png",
    "image_url_evo": null,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  },
  {
    "id": 26000001,
    "name": "Archers",
    "elixir_cost": 3,
    "rarity": "Common",
    "type": "Troop",
    "arena": "Training Camp",
    "image_url": "https://api-assets.clashroyale.com/cards/300/W7hpFWR8E5TQCmn-AX0Kx0YCnLMzD6L2VyV_pqIJWlc.png",
    "image_url_evo": "https://api-assets.clashroyale.com/cards/300/W7hpFWR8E5TQCmn-AX0Kx0YCnLMzD6L2VyV_pqIJWlc_evo.png",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique card identifier from Clash Royale API |
| `name` | string | Card display name |
| `elixir_cost` | integer | Elixir cost (0-10) |
| `rarity` | string | Card rarity: Common, Rare, Epic, Legendary, Champion |
| `type` | string | Card type: Troop, Spell, Building |
| `arena` | string | Arena where card unlocks |
| `image_url` | string | URL to card image |
| `image_url_evo` | string | URL to evolution card image (null if no evolution) |
| `created_at` | string | Timestamp when card was added to database |
| `updated_at` | string | Timestamp when card was last updated |

**Response Headers:**

```
Cache-Control: public, max-age=86400
ETag: cards-109
```

**Example Request:**

```bash
# Basic request
curl http://localhost:8000/api/cards

# With ETag validation
curl http://localhost:8000/api/cards \
  -H "If-None-Match: cards-109"
```

**Example Response (JavaScript):**

```javascript
// Fetch all cards
const response = await fetch('http://localhost:8000/api/cards');
const cards = await response.json();

console.log(`Loaded ${cards.length} cards`);

// Filter by rarity
const legendaries = cards.filter(c => c.rarity === 'Legendary');

// Filter by type
const troops = cards.filter(c => c.type === 'Troop');

// Filter by elixir cost
const lowCost = cards.filter(c => c.elixir_cost <= 3);

// Cards with evolution
const evolutionCards = cards.filter(c => c.image_url_evo !== null);
```

**Client-Side Filtering:**

The API returns all cards and relies on client-side filtering for performance. Common filters include:

```javascript
// Filter by rarity
function filterByRarity(cards, rarity) {
  if (!rarity || rarity === 'All') return cards;
  return cards.filter(card => card.rarity === rarity);
}

// Filter by type
function filterByType(cards, type) {
  if (!type || type === 'All') return cards;
  return cards.filter(card => card.type === type);
}

// Filter by elixir cost
function filterByElixir(cards, minCost, maxCost) {
  return cards.filter(card =>
    card.elixir_cost >= minCost && card.elixir_cost <= maxCost
  );
}

// Search by name
function searchCards(cards, query) {
  const lowerQuery = query.toLowerCase();
  return cards.filter(card =>
    card.name.toLowerCase().includes(lowerQuery)
  );
}

// Evolution cards only
function getEvolutionCards(cards) {
  return cards.filter(card => card.image_url_evo !== null);
}
```

---

### Invalidate Cache

Invalidate the server-side card cache. Call this after updating card data.

**Endpoint:** `POST /api/cards/invalidate-cache`

**Authentication Required:** No (should be protected in production)

**Request Body:** None

**Success Response (200 OK):**

```json
{
  "message": "Card cache invalidated successfully"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/cards/invalidate-cache
```

**When to Use:**

- After running `ingest_cards.py` script
- After manual database updates to cards table
- When deploying card data changes

!!! warning "Production Security"
    In production, this endpoint should be protected with authentication or IP allowlisting to prevent cache invalidation abuse.

---

### Get Cache Statistics

Retrieve cache statistics for monitoring and debugging.

**Endpoint:** `GET /api/cards/cache-stats`

**Authentication Required:** No

**Request Body:** None

**Success Response (200 OK):**

```json
{
  "cached": true,
  "card_count": 109,
  "cache_size_bytes": 524288,
  "last_updated": "2024-01-15T10:00:00Z",
  "hit_count": 1523,
  "miss_count": 42,
  "hit_rate": 0.973
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `cached` | boolean | Whether cards are currently cached in memory |
| `card_count` | integer | Number of cards in cache |
| `cache_size_bytes` | integer | Approximate cache size in bytes |
| `last_updated` | string | Timestamp when cache was last populated |
| `hit_count` | integer | Number of cache hits |
| `miss_count` | integer | Number of cache misses |
| `hit_rate` | number | Cache hit rate (0.0 to 1.0) |

**Example Request:**

```bash
curl http://localhost:8000/api/cards/cache-stats
```

---

## Card Data Model

### Card Fields

```typescript
interface Card {
  id: number;               // Clash Royale API ID
  name: string;             // Display name
  elixir_cost: number;      // 0-10
  rarity: CardRarity;       // Common, Rare, Epic, Legendary, Champion
  type: CardType;           // Troop, Spell, Building
  arena: string;            // Unlock arena
  image_url: string;        // Card image URL
  image_url_evo: string | null; // Evolution image URL
  created_at: string;       // ISO 8601 timestamp
  updated_at: string;       // ISO 8601 timestamp
}

type CardRarity = 'Common' | 'Rare' | 'Epic' | 'Legendary' | 'Champion';
type CardType = 'Troop' | 'Spell' | 'Building';
```

### Evolution Cards

Cards with evolution variants have a non-null `image_url_evo` field:

```javascript
const evolutionCards = cards.filter(card => card.image_url_evo !== null);

// Current evolution cards (as of 2024):
// - Knight
// - Archers
// - Skeletons
// - Bats
// - And more...
```

## Data Source

Card data is sourced from the [Clash Royale Official API](https://developer.clashroyale.com/).

### Ingestion Process

1. **Script:** `backend/src/scripts/ingest_cards.py`
2. **Frequency:** Manual or scheduled
3. **Source:** Clash Royale API `/v1/cards` endpoint
4. **Storage:** MySQL `cards` table

**Run Ingestion:**

```bash
cd backend
uv run src/scripts/ingest_cards.py
```

**Environment Variable Required:**

```bash
CLASH_ROYALE_API_KEY=your_api_key_here
```

## Caching Strategy

### Client-Side Caching

The API sends caching headers to enable browser caching:

```
Cache-Control: public, max-age=86400  # 24 hours
ETag: cards-{count}
```

**Frontend Implementation:**

```javascript
// Cache cards in component state or context
const [cards, setCards] = useState([]);
const [cachedAt, setCachedAt] = useState(null);

async function loadCards(forceRefresh = false) {
  // Check if cache is still valid (24 hours)
  if (!forceRefresh && cachedAt && Date.now() - cachedAt < 86400000) {
    return cards; // Use cached data
  }

  const response = await fetch('/api/cards');
  const freshCards = await response.json();

  setCards(freshCards);
  setCachedAt(Date.now());

  return freshCards;
}
```

### Server-Side Caching

The backend caches cards in memory:

- **Cache Duration:** Until explicitly invalidated
- **Implementation:** `backend/src/services/card_service.py`
- **Invalidation:** Manual via `/api/cards/invalidate-cache`

## Performance Considerations

### Why Cache Cards?

- **Frequency:** Cards are fetched on every page load
- **Size:** ~100 cards with images = ~500KB JSON
- **Change Rate:** Cards rarely change (monthly updates)
- **External API:** Clash Royale API has rate limits

### Optimization Tips

```javascript
// 1. Load cards once at app startup
useEffect(() => {
  loadCards();
}, []); // Empty deps - load once

// 2. Store in React Context for app-wide access
const CardsContext = createContext();

// 3. Use service worker for offline caching
// In service worker:
workbox.routing.registerRoute(
  /\/api\/cards$/,
  new workbox.strategies.CacheFirst({
    cacheName: 'cards-cache',
    plugins: [
      new workbox.expiration.ExpirationPlugin({
        maxAgeSeconds: 86400, // 24 hours
      }),
    ],
  })
);
```

## Error Handling

### Possible Errors

| Status Code | Scenario | Frontend Action |
|-------------|----------|-----------------|
| 200 | Success | Use card data |
| 304 | Not Modified (ETag match) | Use cached data |
| 500 | Database error | Retry with exponential backoff |
| 503 | Service unavailable | Show offline mode |

### Example Error Handling

```javascript
async function fetchCardsWithRetry(retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch('/api/cards');

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Fetch attempt ${i + 1} failed:`, error);

      if (i === retries - 1) {
        // Final retry failed - use fallback
        return loadCardsFromLocalStorage() || [];
      }

      // Wait before retry (exponential backoff)
      await new Promise(resolve =>
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    }
  }
}
```

## Testing

### Manual Testing

```bash
# Get all cards
curl http://localhost:8000/api/cards

# Get cache stats
curl http://localhost:8000/api/cards/cache-stats

# Invalidate cache
curl -X POST http://localhost:8000/api/cards/invalidate-cache

# Verify cache was invalidated
curl http://localhost:8000/api/cards/cache-stats
```

### Automated Testing

```bash
cd backend

# Unit tests
uv run pytest tests/unit/test_card_service.py -v

# Integration tests
uv run pytest tests/integration/test_cards_api.py -v

# Contract tests
uv run pytest tests/contract/test_clash_api.py -v
```

## Related Documentation

- [Deck Management](deck-management.md) - How cards are used in decks
- [Evolution Cards](../features/evolution-cards.md) - Evolution system details
- [Card Service](../architecture/backend.md#card-service) - Backend implementation
- [Caching Strategy](../architecture/backend.md#caching) - Full caching architecture
