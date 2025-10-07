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
