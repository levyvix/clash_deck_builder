# Profile API

The Profile API allows authenticated users to view and manage their profile information.

## Endpoints

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

---

## Related Documentation

- [Authentication API](authentication.md) - Details on user authentication and JWT tokens
- [Profile Section in Frontend](../frontend.md#profile-section) - Frontend implementation of profile management
