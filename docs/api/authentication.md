# Authentication API

The authentication system uses Google OAuth 2.0 for identity and JWT tokens for session management.

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Google
    participant Backend
    participant Database

    User->>Frontend: Click "Sign in with Google"
    Frontend->>Google: Open OAuth popup
    Google->>User: Request authorization
    User->>Google: Approve
    Google->>Frontend: Return ID token
    Frontend->>Backend: POST /api/auth/google {id_token}
    Backend->>Google: Verify token
    Google->>Backend: Token valid + user info
    Backend->>Database: Create/update user
    Backend->>Backend: Generate JWT tokens
    Backend->>Frontend: Return access + refresh tokens
    Frontend->>Frontend: Store tokens in localStorage
    Frontend->>User: Redirect to authenticated state
```

## Endpoints

### Login with Google OAuth

Authenticate a user using a Google OAuth ID token and receive JWT tokens.

**Endpoint:** `POST /api/auth/google`

**Authentication Required:** No

**Request Body:**

```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
  "migration_data": {
    "decks": [...],
    "preferences": {...}
  }
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id_token` | string | Yes | Google OAuth ID token from client-side authentication |
| `migration_data` | object | No | Optional anonymous user data to migrate (decks, preferences) |

**Success Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 123,
    "google_id": "1234567890",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar": "knight",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "onboarding": {
    "is_new_user": true,
    "decks_migrated": 3,
    "migration_status": "success"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token for API requests (15 minutes) |
| `refresh_token` | string | JWT refresh token for obtaining new access tokens (7 days) |
| `token_type` | string | Always "bearer" |
| `expires_in` | integer | Access token expiration time in seconds (900 = 15 minutes) |
| `user` | object | Authenticated user information |
| `onboarding` | object | Optional onboarding result if migration data provided |

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 401 Unauthorized | Invalid or expired Google token | `{"detail": "Invalid Google ID token"}` |
| 500 Internal Server Error | Server error during authentication | `{"detail": "Internal server error during authentication"}` |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
    "migration_data": {
      "decks": [
        {
          "name": "My Deck",
          "slots": [...]
        }
      ]
    }
  }'
```

**Example Response:**

```javascript
// Frontend usage
const response = await fetch(`${API_BASE_URL}/api/auth/google`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id_token: googleCredential.credential
  })
});

const data = await response.json();
// Store tokens
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
```

---

### Refresh Access Token

Obtain a new access token using a valid refresh token.

**Endpoint:** `POST /api/auth/refresh`

**Authentication Required:** No (uses refresh token in body)

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 401 Unauthorized | Invalid or expired refresh token | `{"detail": "Invalid refresh token"}` |
| 401 Unauthorized | User not found | `{"detail": "User not found"}` |
| 500 Internal Server Error | Server error during refresh | `{"detail": "Internal server error during token refresh"}` |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Usage Pattern:**

```javascript
// Automatic token refresh when access token expires
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');

  const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data.access_token;
  } else {
    // Refresh token expired - user must login again
    localStorage.clear();
    window.location.href = '/login';
  }
}
```

---

### Logout

Logout the current user. In a stateless JWT system, this is primarily client-side token deletion.

**Endpoint:** `POST /api/auth/logout`

**Authentication Required:** Yes (Bearer token)

**Request Body:** None

**Success Response (200 OK):**

```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 401 Unauthorized | Missing or invalid token | `{"detail": "Not authenticated"}` |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Frontend Implementation:**

```javascript
async function logout() {
  try {
    // Call backend logout endpoint
    await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
  } finally {
    // Always clear local tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/';
  }
}
```

!!! note "Stateless JWT Tokens"
    This application uses stateless JWT tokens, so logout is primarily handled client-side by deleting the tokens. The backend logout endpoint is provided for logging purposes and future token blacklist implementation.

---

### Get Current User

Retrieve information about the currently authenticated user.

**Endpoint:** `GET /api/auth/me`

**Authentication Required:** Yes (Bearer token)

**Request Body:** None

**Success Response (200 OK):**

```json
{
  "id": 123,
  "google_id": "1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar": "knight"
}
```

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 401 Unauthorized | Missing or invalid token | `{"detail": "Not authenticated"}` |
| 401 Unauthorized | User no longer exists | `{"detail": "User no longer exists"}` |

**Example Request:**

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Get Onboarding Status

Retrieve onboarding status for the current user, including migration information.

**Endpoint:** `GET /api/auth/onboarding`

**Authentication Required:** Yes (Bearer token)

**Request Body:** None

**Success Response (200 OK):**

```json
{
  "is_new_user": false,
  "total_decks": 5,
  "has_completed_onboarding": true,
  "migration_performed": true,
  "migration_timestamp": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 401 Unauthorized | Missing or invalid token | `{"detail": "Not authenticated"}` |
| 404 Not Found | User not found | `{"detail": "User not found"}` |

---

## JWT Token Structure

### Access Token

**Expiration:** 15 minutes

**Payload:**

```json
{
  "user_id": 123,
  "google_id": "1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "exp": 1705318800,
  "iat": 1705318200,
  "type": "access"
}
```

### Refresh Token

**Expiration:** 7 days

**Payload:**

```json
{
  "user_id": 123,
  "exp": 1705923000,
  "iat": 1705318200,
  "type": "refresh"
}
```

## Security Considerations

### Token Storage

!!! warning "Security Best Practice"
    Currently, tokens are stored in `localStorage`. For production, consider:

    - Using `httpOnly` cookies for refresh tokens
    - Storing access tokens in memory only
    - Implementing token rotation on refresh

### CORS Configuration

The backend only accepts requests from allowed origins configured in `CORS_ORIGINS`:

```bash
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Token Validation

All protected endpoints validate tokens by:

1. Checking token signature with `JWT_SECRET_KEY`
2. Verifying token expiration
3. Extracting user information
4. Confirming user still exists in database

## Error Handling

### Common Error Scenarios

| Scenario | Status | Action |
|----------|--------|--------|
| Token expired | 401 | Attempt refresh with refresh token |
| Refresh token expired | 401 | Redirect to login |
| Invalid token format | 401 | Clear tokens and redirect to login |
| User deleted | 401 | Clear tokens and redirect to login |
| Network error | 500 | Retry request with exponential backoff |

### Frontend Error Handling Pattern

```javascript
async function authenticatedRequest(url, options = {}) {
  let token = localStorage.getItem('access_token');

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 401) {
      // Try to refresh token
      token = await refreshAccessToken();

      // Retry original request
      return await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${token}`
        }
      });
    }

    return response;
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}
```

## Environment Configuration

Required environment variables for authentication:

```bash
# Backend (.env)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
JWT_SECRET_KEY=your-32-character-minimum-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend (.env)
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

Generate a secure JWT secret:

```bash
openssl rand -base64 32
```

## Testing

### Manual Testing with cURL

```bash
# 1. Get Google ID token (use browser console)
# In your frontend: console.log(credential.credential)

# 2. Authenticate
curl -X POST http://localhost:8000/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{"id_token": "your-google-token"}'

# Save the tokens from response

# 3. Use access token
curl http://localhost:8000/api/decks \
  -H "Authorization: Bearer your-access-token"

# 4. Refresh token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'

# 5. Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer your-access-token"
```

### Automated Testing

```bash
# Backend tests
cd backend
uv run pytest tests/test_auth_endpoints.py -v
uv run pytest tests/test_auth_service.py -v
uv run pytest tests/test_auth_integration.py -v
```

## Related Documentation

- [Profile API](profile.md) - User profile management
- [Google OAuth Integration](../features/google-oauth.md) - Detailed OAuth flow
- [Backend Architecture](../architecture/backend.md) - Auth service implementation
- [Frontend Development](../development/frontend.md) - AuthContext usage
