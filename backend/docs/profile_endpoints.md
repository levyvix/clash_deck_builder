# Profile Management Endpoints

This document describes the profile management endpoints for the Clash Royale Deck Builder API.

## Overview

The profile endpoints allow authenticated users to view and update their profile information, including display name and avatar selection.

## Authentication

All profile endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Endpoints

### GET /api/profile

Retrieve the current user's profile information.

**Response (200 OK):**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "name": "User Display Name",
  "avatar": "knight",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing authentication token
- `404 Not Found`: User profile not found
- `500 Internal Server Error`: Database or server error

### PUT /api/profile

Update the current user's profile information.

**Request Body:**
```json
{
  "name": "New Display Name",  // Optional: 1-50 characters, alphanumeric and spaces only
  "avatar": "wizard"           // Optional: Clash Royale card ID
}
```

**Validation Rules:**
- **Name**: 
  - Length: 1-50 characters
  - Pattern: Only letters, numbers, and spaces allowed
  - No leading/trailing spaces
- **Avatar**: 
  - Must be a valid Clash Royale card ID
  - Maximum 50 characters
- At least one field (name or avatar) must be provided

**Response (200 OK):**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "name": "New Display Name",
  "avatar": "wizard",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Validation error or no fields provided
- `401 Unauthorized`: Invalid or missing authentication token
- `404 Not Found`: User profile not found
- `422 Unprocessable Entity`: Invalid input format
- `500 Internal Server Error`: Database or server error

## Example Usage

### Get Profile
```bash
curl -X GET "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer your_jwt_token"
```

### Update Name Only
```bash
curl -X PUT "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'
```

### Update Avatar Only
```bash
curl -X PUT "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"avatar": "wizard"}'
```

### Update Both Name and Avatar
```bash
curl -X PUT "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name", "avatar": "wizard"}'
```

## Error Response Format

All error responses follow the standard format:
```json
{
  "error": {
    "type": "error_type",
    "message": "Human-readable error message",
    "details": {
      // Additional error details (optional)
    }
  }
}
```

## Validation Examples

### Valid Names
- "John Doe"
- "Player123"
- "Cool Gamer"

### Invalid Names
- "User@123" (contains special characters)
- "" (empty)
- "   " (only spaces)
- "a" * 51 (too long)

### Valid Avatars
- "knight"
- "wizard"
- "archer"
- Any valid Clash Royale card ID

## Requirements Covered

This implementation satisfies the following requirements from the specification:

- **4.1**: Display current display name in profile section
- **4.2**: Provide input field for name editing
- **4.3**: Validate display name (no special characters)
- **4.4**: Prevent saving names with special characters
- **4.5**: Update and display new name immediately