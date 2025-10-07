# API Reference Overview

The Clash Royale Deck Builder backend provides a RESTful API for managing users, decks, and card data.

## Documentation

- [Detailed API Reference](reference.md) - Complete endpoint documentation with examples
- [Interactive Documentation](#interactive-documentation) - Try the API in your browser

## Base URL

**Development**: `http://localhost:8000`
**Production**: `https://your-domain.com`

All API endpoints are prefixed with `/api/`.

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Most endpoints require authentication using JWT Bearer tokens.

### Getting a Token

```bash
# Login with Google OAuth
POST /api/auth/google
Content-Type: application/json

{
  "credential": "<google_oauth_token>"
}

# Response
{
  "access_token": "eyJhbGciOiJI...",
  "refresh_token": "eyJhbGciOiJI...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Using the Token

Include the access token in the Authorization header:

```bash
GET /api/decks
Authorization: Bearer eyJhbGciOiJI...
```

### Token Refresh

Access tokens expire after 15 minutes. Use the refresh token to get a new access token:

```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJI..."
}

# Response
{
  "access_token": "new_access_token...",
  "token_type": "bearer"
}
```

## Endpoints Overview

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/google` | Login with Google OAuth | No |
| POST | `/api/auth/refresh` | Refresh access token | No |
| POST | `/api/auth/logout` | Logout (invalidate refresh token) | Yes |

See [Authentication API](authentication.md) for details.

### Profile Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/profile` | Get current user profile | Yes |
| PUT | `/api/profile` | Update user profile | Yes |
| PUT | `/api/profile/avatar` | Update user avatar | Yes |

See [Profile API](profile.md) for details.

### Card Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/cards` | List all cards | No |
| GET | `/api/cards/{card_id}` | Get card details | No |

See [Cards API](cards.md) for details.

### Deck Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/decks` | List user's decks | Yes |
| POST | `/api/decks` | Create new deck | Yes |
| GET | `/api/decks/{deck_id}` | Get deck details | Yes |
| PUT | `/api/decks/{deck_id}` | Update deck | Yes |
| DELETE | `/api/decks/{deck_id}` | Delete deck | Yes |

See [Decks API](decks.md) for details.

## Response Format

### Success Response

```json
{
  "data": {
    // Resource data
  },
  "message": "Optional success message"
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Invalid request format/data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server-side error |

## Pagination

Endpoints that return lists support pagination:

```bash
GET /api/decks?skip=0&limit=20
```

**Parameters:**
- `skip` - Number of items to skip (default: 0)
- `limit` - Maximum items to return (default: 20, max: 100)

**Response:**
```json
{
  "data": [...],
  "total": 50,
  "skip": 0,
  "limit": 20
}
```

## Filtering

Some endpoints support filtering:

```bash
GET /api/cards?rarity=legendary&type=troop
```

Check individual endpoint documentation for supported filters.

## Rate Limiting

Currently, no rate limiting is enforced in development.

**Future**: Production will have rate limits:
- 100 requests/minute for authenticated users
- 20 requests/minute for anonymous users

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for allowed origins.

**Allowed Origins** (configured via `CORS_ORIGINS` env var):
- `http://localhost:3000` (development frontend)
- `http://127.0.0.1:3000`
- Production frontend domain

## Versioning

Currently at v1 (implicit in all endpoints).

Future API versions will use URL versioning:
- `/api/v1/decks`
- `/api/v2/decks`

## Examples

### Using cURL

```bash
# Get all cards
curl http://localhost:8000/api/cards

# Login with Google
curl -X POST http://localhost:8000/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{"credential":"<google_token>"}'

# Get user's decks (with auth)
curl http://localhost:8000/api/decks \
  -H "Authorization: Bearer <access_token>"

# Create a deck
curl -X POST http://localhost:8000/api/decks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "My Deck",
    "cards": [1, 2, 3, 4, 5, 6, 7, 8],
    "evolution_slots": [1, 2]
  }'
```

### Using JavaScript (fetch)

```javascript
// Get all cards
const response = await fetch('http://localhost:8000/api/cards');
const cards = await response.json();

// Create a deck (with auth)
const response = await fetch('http://localhost:8000/api/decks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    name: 'My Deck',
    cards: [1, 2, 3, 4, 5, 6, 7, 8],
    evolution_slots: [1, 2]
  })
});
const deck = await response.json();
```

### Using Python (httpx)

```python
import httpx

# Get all cards
async with httpx.AsyncClient() as client:
    response = await client.get('http://localhost:8000/api/cards')
    cards = response.json()

# Create a deck (with auth)
async with httpx.AsyncClient() as client:
    response = await client.post(
        'http://localhost:8000/api/decks',
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            'name': 'My Deck',
            'cards': [1, 2, 3, 4, 5, 6, 7, 8],
            'evolution_slots': [1, 2]
        }
    )
    deck = response.json()
```

## Testing the API

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter Bearer token: `Bearer <your_access_token>`
4. Test endpoints interactively

### Using Postman

1. Import OpenAPI spec from http://localhost:8000/openapi.json
2. Set environment variable: `base_url` = `http://localhost:8000`
3. Set Authorization header: `Bearer <access_token>`
4. Test endpoints

### Using Backend Tests

```bash
cd backend
uv run pytest tests/contract/  # Test API contracts
uv run pytest tests/integration/  # Test full API workflows
```

## Health Check

```bash
GET /health

# Response
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

Use for monitoring and load balancer health checks.

## Related Documentation

- [Authentication API](authentication.md) - Detailed auth endpoints
- [Profile API](profile.md) - User profile management
- [Cards API](cards.md) - Card data access
- [Decks API](decks.md) - Deck management operations
- [Backend Architecture](../architecture/backend.md) - How the API is structured
