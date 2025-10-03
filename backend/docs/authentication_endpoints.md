# Authentication Endpoints

This document describes the authentication endpoints implemented for the Clash Royale Deck Builder backend.

## Overview

The authentication system uses Google OAuth 2.0 for user authentication and JWT tokens for session management. All authentication endpoints are prefixed with `/api/auth`.

## Endpoints

### POST /api/auth/google

Handles Google OAuth authentication callback.

**Request Body:**
```json
{
  "id_token": "google-id-token-from-oauth-flow"
}
```

**Response (200 OK):**
```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "user-uuid",
    "google_id": "google-user-id",
    "email": "user@example.com",
    "name": "User Name",
    "avatar": "card-id-or-null",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid Google token or authentication failed
- `422 Unprocessable Entity`: Missing or invalid request body
- `500 Internal Server Error`: Server error during authentication

### POST /api/auth/refresh

Refreshes an access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "valid-refresh-token"
}
```

**Response (200 OK):**
```json
{
  "access_token": "new-jwt-access-token",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token, or user no longer exists
- `422 Unprocessable Entity`: Missing or invalid request body
- `500 Internal Server Error`: Server error during token refresh

### POST /api/auth/logout

Logs out the current user (requires authentication).

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `403 Forbidden`: Missing authorization header
- `500 Internal Server Error`: Server error during logout

### GET /api/auth/me

Gets current authenticated user information.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "id": "user-uuid",
  "google_id": "google-user-id",
  "email": "user@example.com",
  "name": "User Name",
  "avatar": "card-id-or-null"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `403 Forbidden`: Missing authorization header
- `500 Internal Server Error`: Server error fetching user info

## Authentication Middleware

The authentication system provides middleware functions that can be used to protect other endpoints:

### require_auth

Use this dependency to require authentication for an endpoint:

```python
from src.middleware.auth_middleware import require_auth

@router.get("/protected")
async def protected_endpoint(user: Dict = Depends(require_auth)):
    return {"user_id": user["user_id"]}
```

### optional_auth

Use this dependency for endpoints that work with or without authentication:

```python
from src.middleware.auth_middleware import optional_auth

@router.get("/maybe-protected")
async def maybe_protected_endpoint(user: Optional[Dict] = Depends(optional_auth)):
    if user:
        return {"message": f"Hello {user['name']}"}
    else:
        return {"message": "Hello anonymous user"}
```

## Token Management

### Access Tokens
- **Lifetime**: 15 minutes (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Purpose**: Used for API authentication
- **Storage**: Should be stored in memory or secure storage on the client

### Refresh Tokens
- **Lifetime**: 30 days (configurable via `JWT_REFRESH_TOKEN_EXPIRE_DAYS`)
- **Purpose**: Used to obtain new access tokens
- **Storage**: Should be stored securely (e.g., httpOnly cookies)

### Token Refresh Flow
1. Client detects access token is expired (401 response)
2. Client calls `/api/auth/refresh` with refresh token
3. Server returns new access token
4. Client retries original request with new access token

## Error Handling

All authentication endpoints use the standardized error response format:

```json
{
  "error": {
    "type": "error_type",
    "message": "Human-readable error message"
  }
}
```

Common error types:
- `http_error`: General HTTP errors (401, 403, etc.)
- `validation_error`: Request validation failures
- `internal_error`: Server-side errors

## Security Considerations

1. **Token Storage**: Access tokens should be stored in memory, refresh tokens in secure storage
2. **HTTPS Only**: All authentication endpoints should only be used over HTTPS in production
3. **Token Validation**: All protected endpoints validate tokens server-side
4. **User Verification**: User existence is verified on each authenticated request
5. **Google OAuth**: Tokens are verified directly with Google's servers

## Configuration

Required environment variables:
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `JWT_SECRET`: Secret key for JWT signing (minimum 32 characters)
- `JWT_ALGORITHM`: JWT signing algorithm (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime (default: 15)
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime (default: 30)