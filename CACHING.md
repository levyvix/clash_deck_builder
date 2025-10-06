# Card Data Caching Implementation

This document describes the comprehensive caching strategy implemented for card data in the Clash Royale Deck Builder application.

## Overview

Since Clash Royale card data rarely changes, we've implemented a multi-layered caching strategy to minimize database queries and API calls, improving application performance and reducing server load.

## Architecture

### Three-Layer Caching Strategy

1. **Backend In-Memory Cache** (Server-side)
   - TTL: 24 hours
   - Storage: Python `cachetools.TTLCache`
   - Scope: Shared across all users

2. **HTTP Cache Headers** (Browser-side)
   - TTL: 24 hours
   - Mechanism: `Cache-Control` and `ETag` headers
   - Scope: Per-browser

3. **Frontend localStorage Cache** (Client-side)
   - TTL: 24 hours
   - Storage: Browser localStorage
   - Scope: Per-browser

## Backend Implementation

### Cache Utility Module (`backend/src/utils/cache.py`)

A centralized cache manager using `cachetools` library:

```python
from src.utils.cache import cards_cache

# Global cache instance with 24-hour TTL
cards_cache = CacheManager(maxsize=10, ttl=86400)
```

**Features:**
- Automatic TTL-based expiration
- Cache hit/miss statistics
- Manual cache invalidation
- Support for multiple cache instances (cards, users, decks)

### CardService Integration (`backend/src/services/card_service.py`)

The `CardService` class now includes caching logic:

```python
async def get_all_cards(self) -> List[Card]:
    # Check cache first
    cache_key = "all_cards"
    cached_cards = cards_cache.get(cache_key)
    if cached_cards is not None:
        return cached_cards

    # Cache miss - fetch from database and cache
    cards = await fetch_from_database()
    cards_cache.set(cache_key, cards)
    return cards
```

**New Methods:**
- `invalidate_cache()` - Clears all card caches
- `get_cache_stats()` - Returns cache performance metrics

### API Endpoints (`backend/src/api/cards.py`)

Enhanced with cache headers and new endpoints:

1. **GET /api/cards/cards**
   - Returns cards with HTTP cache headers
   - `Cache-Control: public, max-age=86400` (24 hours)
   - `ETag: cards-{count}` for conditional requests

2. **POST /api/cards/invalidate-cache**
   - Manually invalidates backend cache
   - Call after data updates (e.g., after `ingest_cards.py`)

3. **GET /api/cards/cache-stats**
   - Returns cache performance statistics
   - Useful for monitoring and debugging

### Card Ingestion Script (`backend/src/scripts/ingest_cards.py`)

Automatically invalidates cache after updating card data:

```python
# After successful ingestion
if inserted > 0 or updated > 0:
    cards_cache.clear()
```

## Frontend Implementation

### Card Cache Service (`frontend/src/services/cardCacheService.ts`)

Manages localStorage-based caching with TTL validation:

**Functions:**
- `cacheCards(cards)` - Store cards in localStorage
- `getCachedCards()` - Retrieve cards if cache is valid
- `invalidateCardCache()` - Clear card cache
- `getCardCacheStats()` - Get cache age and status

**Features:**
- Automatic expiration after 24 hours
- Version checking for cache compatibility
- Graceful error handling for localStorage quota issues
- Human-readable cache age formatting

### API Integration (`frontend/src/services/api.ts`)

The `fetchCards()` function now checks cache before making API calls:

```typescript
export const fetchCards = async () => {
  // Check localStorage cache first
  const cachedCards = getCachedCards();
  if (cachedCards !== null) {
    return cachedCards;
  }

  // Cache miss - fetch from API and cache
  const cards = await fetchFromAPI();
  cacheCards(cards);
  return cards;
};
```

## Cache Flow Diagram

```
User Request
     │
     ▼
Frontend localStorage Cache
     │ (miss)
     ▼
HTTP Request to Backend
     │
     ▼
Backend In-Memory Cache
     │ (miss)
     ▼
MySQL Database
     │
     ▼
Cache & Return Data
```

## Cache Invalidation

### When to Invalidate

Cache should be invalidated when:
1. Card data is updated via `ingest_cards.py` (automatic)
2. Card properties are modified directly in database (manual)
3. Testing cache behavior (manual)

### How to Invalidate

**Backend:**
```bash
# Automatic - runs after card ingestion
uv run src/scripts/ingest_cards.py

# Manual - via API
curl -X POST http://localhost:8000/api/cards/invalidate-cache
```

**Frontend:**
```typescript
// Programmatic
import { invalidateCardCache } from './services/cardCacheService';
invalidateCardCache();

// Or clear localStorage manually
localStorage.removeItem('clash_cards_cache');
```

## Monitoring and Statistics

### Backend Cache Stats

**Endpoint:** `GET /api/cards/cache-stats`

**Response:**
```json
{
  "hits": 150,
  "misses": 5,
  "sets": 5,
  "invalidations": 1,
  "size": 1,
  "maxsize": 10,
  "ttl": 86400,
  "hit_rate_percent": 96.77,
  "total_requests": 155
}
```

### Frontend Cache Stats

**Usage:**
```typescript
import { getCardCacheStats } from './services/cardCacheService';

const stats = getCardCacheStats();
console.log(stats);
// {
//   exists: true,
//   age: 3600000,
//   ageFormatted: "1h 0m",
//   cardCount: 110,
//   version: "1.0",
//   isExpired: false
// }
```

## Performance Benefits

### Before Caching
- Every card request → Database query
- ~50-100ms per request
- Database load for every user

### After Caching
- First request → Database query (cache miss)
- Subsequent requests → In-memory cache (< 1ms)
- 99%+ reduction in database queries
- Near-instant card data retrieval

### Expected Cache Performance
- **Backend hit rate:** > 95% (after warmup)
- **Frontend hit rate:** > 90% (returning users)
- **Average response time:** < 5ms (from cache)
- **Database queries:** ~1 per 24 hours per instance

## Testing

### Backend Tests

Run cache tests:
```bash
cd backend
uv run pytest tests/unit/test_cache.py -v
```

**Test Coverage:**
- Cache initialization
- Set/get operations
- TTL expiration
- Cache statistics
- Invalidation
- Maxsize limits

### Frontend Tests

Run cache tests:
```bash
cd frontend
npm test -- cardCacheService.test.ts
```

**Test Coverage:**
- cacheCards/getCachedCards operations
- TTL expiration handling
- Version compatibility
- Cache invalidation
- Statistics calculation
- Complete lifecycle testing

## Configuration

### Backend Cache Settings

Located in `backend/src/utils/cache.py`:

```python
# Cards cache: 24 hours (cards rarely change)
cards_cache = CacheManager(maxsize=10, ttl=86400)

# User cache: 1 hour (may change more frequently)
user_cache = CacheManager(maxsize=100, ttl=3600)

# Deck cache: 5 minutes (changes frequently)
deck_cache = CacheManager(maxsize=200, ttl=300)
```

### Frontend Cache Settings

Located in `frontend/src/services/cardCacheService.ts`:

```typescript
const CACHE_KEY = 'clash_cards_cache';
const CACHE_VERSION = '1.0';
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours
```

## Troubleshooting

### Cards Not Updating After Ingestion

**Solution:** Clear backend cache
```bash
curl -X POST http://localhost:8000/api/cards/invalidate-cache
```

### Frontend Shows Stale Data

**Solution:** Clear localStorage cache
```javascript
localStorage.removeItem('clash_cards_cache');
```

### Cache Hit Rate Too Low

**Possible Causes:**
1. TTL too short
2. Cache size too small
3. Frequent cache invalidations

**Solution:** Check cache stats and adjust configuration

### localStorage Quota Exceeded

The cache service automatically handles this by:
1. Catching `QuotaExceededError`
2. Clearing old cache
3. Retrying cache operation

## Best Practices

1. **Don't Cache User-Specific Data:** Only cache data that's shared across all users (like cards)

2. **Set Appropriate TTLs:** Match TTL to data volatility
   - Cards: 24 hours (rarely change)
   - Users: 1 hour (moderate changes)
   - Decks: 5 minutes (frequent changes)

3. **Always Invalidate After Updates:** Ensure cache is cleared when underlying data changes

4. **Monitor Cache Performance:** Regularly check cache hit rates and adjust as needed

5. **Version Your Cache:** Use version strings to ensure compatibility when cache structure changes

## Future Enhancements

Potential improvements for the caching system:

1. **Redis Integration**
   - Replace in-memory cache with Redis
   - Share cache across multiple backend instances
   - Persistent cache across restarts

2. **Smart Invalidation**
   - Webhook integration with Clash Royale API
   - Automatic invalidation when new cards are released

3. **Cache Warming**
   - Pre-populate cache on application startup
   - Reduce cold-start latency

4. **Conditional Requests**
   - Implement ETag validation
   - 304 Not Modified responses
   - Further reduce bandwidth usage

5. **Cache Tiering**
   - Hot cache (frequently accessed cards)
   - Cold cache (rarely accessed cards)
   - Optimize memory usage

## References

- **cachetools Documentation:** https://cachetools.readthedocs.io/
- **HTTP Caching:** https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- **Web Storage API:** https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API
