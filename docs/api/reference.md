# API Reference

This document provides detailed information about the Clash Royale Deck Builder API endpoints.

## Base URL

All API endpoints are relative to the base URL:
```
https://api.yourdomain.com/v1
```

## Authentication

Most endpoints require authentication using Google OAuth. Include the JWT token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

## Cards

### Get All Cards

Retrieve all Clash Royale cards with optional filtering.

```http
GET /cards
```

#### Query Parameters
- `rarity` (optional): Filter by card rarity (e.g., "Common", "Rare", "Epic", "Legendary")
- `elixir` (optional): Filter by elixir cost (e.g., 3)
- `type` (optional): Filter by card type (e.g., "Troop", "Spell", "Building")

#### Response
```json
[
  {
    "id": 26000000,
    "name": "Knight",
    "maxLevel": 14,
    "iconUrls": {
      "medium": "https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png"
    },
    "elixir": 3,
    "rarity": "Common",
    "type": "Troop"
  },
  // ... more cards
]
```

### Invalidate Card Cache

Manually invalidate the card cache (admin only).

```http
POST /cards/invalidate-cache
```

#### Response
```json
{
  "message": "Card cache invalidated successfully"
}
```

## Decks

### Create Deck

Create a new deck for the authenticated user.

```http
POST /decks
```

#### Request Body
```json
{
  "name": "My Awesome Deck",
  "cards": [
    {"id": 26000000, "level": 13},
    {"id": 26000001, "level": 12},
    // ... 6 more cards
  ],
  "evolutions": [26000000] // Optional: List of card IDs that are evolved
}
```

#### Response (201 Created)
```json
{
  "id": 123,
  "name": "My Awesome Deck",
  "cards": [
    {"id": 26000000, "level": 13, "name": "Knight"},
    // ... other cards with names included
  ],
  "evolutions": [26000000],
  "averageElixir": 3.4,
  "createdAt": "2025-10-06T20:00:00Z",
  "updatedAt": "2025-10-06T20:00:00Z"
}
```

### Get User Decks

Get all decks for the authenticated user.

```http
GET /decks
```

#### Response
```json
[
  {
    "id": 123,
    "name": "My Awesome Deck",
    "cards": [
      {"id": 26000000, "level": 13, "name": "Knight"}
      // ... other cards
    ],
    "averageElixir": 3.4,
    "createdAt": "2025-10-06T20:00:00Z"
  }
  // ... more decks (up to 20 per user)
]
```

### Get Single Deck

Get a specific deck by ID.

```http
GET /decks/{deck_id}
```

#### Path Parameters
- `deck_id` (required): The ID of the deck to retrieve

#### Response
```json
{
  "id": 123,
  "name": "My Awesome Deck",
  "cards": [
    {"id": 26000000, "level": 13, "name": "Knight"}
    // ... other cards
  ],
  "evolutions": [26000000],
  "averageElixir": 3.4,
  "createdAt": "2025-10-06T20:00:00Z",
  "updatedAt": "2025-10-06T21:30:00Z"
}
```

### Update Deck

Update an existing deck.

```http
PUT /decks/{deck_id}
```

#### Path Parameters
- `deck_id` (required): The ID of the deck to update

#### Request Body
Same as create deck, but all fields are optional.

#### Response
```json
{
  "id": 123,
  "name": "Updated Deck Name",
  "cards": [
    // Updated cards
  ],
  "evolutions": [26000001],
  "averageElixir": 3.8,
  "createdAt": "2025-10-06T20:00:00Z",
  "updatedAt": "2025-10-06T22:00:00Z"
}
```

### Delete Deck

Delete a deck.

```http
DELETE /decks/{deck_id}
```

#### Path Parameters
- `deck_id` (required): The ID of the deck to delete

#### Response
- `204 No Content` on success

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Deck with ID 123 not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "cards"],
      "msg": "ensure this value has at most 8 items",
      "type": "value_error.list.max_items"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
## Rate Limiting

The API is rate limited to 100 requests per minute per IP address. Exceeding this limit will result in a `429 Too Many Requests` response.

## Caching

Card data is cached for 24 hours. The following headers are included in card responses:
- `Cache-Control: public, max-age=86400`
- `ETag: cards-{count}`

## Versioning

API versioning is handled through the URL path (e.g., `/v1/...`). Breaking changes will result in a new version number.

## Changelog

### v1.0.0 (2025-10-06)
- Initial API release
- Basic CRUD operations for decks
- Card listing and filtering
- Google OAuth authentication

## Profile Endpoints

### Get User Profile

Retrieve the profile of the currently authenticated user.

- **Endpoint**: `GET /api/profile`
- **Authentication Required**: Yes (Bearer token)

**Request Body**: None

**Success Response (200 OK)**:
```json
{
  "id": 123,
  "google_id": "1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar": "knight",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Response Fields**:
| Field        | Type    | Description                              |
|--------------|---------|------------------------------------------|
| `id`           | integer | User's unique ID                       |
| `google_id`    | string  | Google ID from OAuth                   |
| `email`        | string  | User's email address                     |
| `name`         | string  | User's display name                      |
| `avatar`       | string  | User's selected avatar identifier        |
| `created_at`   | string  | Timestamp of user creation (ISO 8601)    |
| `updated_at`   | string  | Timestamp of last profile update (ISO 8601) |

**Error Responses**:
| Status Code       | Description              | Example                         |
|-------------------|--------------------------|---------------------------------|
| 401 Unauthorized  | Missing or invalid token | `{"detail": "Not authenticated"}` |
| 404 Not Found     | User not found           | `{"detail": "User not found"}`  |

---

### Update User Profile

Update the profile information for the authenticated user.

- **Endpoint**: `PUT /api/profile`
- **Authentication Required**: Yes (Bearer token)

**Request Body**:
```json
{
  "name": "Jane Smith",
  "avatar": "wizard"
}
```

**Request Fields**:
| Field    | Type   | Required | Description                     |
|----------|--------|----------|---------------------------------|
| `name`     | string | No       | New display name (max 255 chars) |
| `avatar`   | string | No       | New avatar identifier           |

**Success Response (200 OK)**:
```json
{
  "id": 123,
  "google_id": "1234567890",
  "email": "user@example.com",
  "name": "Jane Smith",
  "avatar": "wizard",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

**Error Responses**:
| Status Code            | Description                   | Example                                         |
|------------------------|-------------------------------|-------------------------------------------------|
| 401 Unauthorized       | Not authenticated             | `{"detail": "Not authenticated"}`             |
| 422 Unprocessable Entity | Validation error              | `{"detail": [{"loc": ["body", "name"], "msg": "string too long"}]}` |

---

### Update User Avatar

Update only the avatar for the authenticated user.

- **Endpoint**: `PUT /api/profile/avatar`
- **Authentication Required**: Yes (Bearer token)

**Request Body**:
```json
{
  "avatar": "pekka"
}
```

**Request Fields**:
| Field    | Type   | Required | Description            |
|----------|--------|----------|------------------------|
| `avatar`   | string | Yes      | New avatar identifier  |

**Success Response (200 OK)**:
```json
{
  "id": 123,
  "google_id": "1234567890",
  "email": "user@example.com",
  "name": "Jane Smith",
  "avatar": "pekka",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T15:00:00Z"
}
```

**Error Responses**:
| Status Code            | Description                   | Example                                         |
|------------------------|-------------------------------|-------------------------------------------------|
| 401 Unauthorized       | Not authenticated             | `{"detail": "Not authenticated"}`             |
| 422 Unprocessable Entity | Validation error              | `{"detail": [{"loc": ["body", "avatar"], "msg": "field required"}]}` |