# Profile API

The Profile API provides endpoints for managing user profile information including display name and avatar selection.

## Overview

User profiles contain:

- **Basic Info**: Name, email, Google ID (from OAuth)
- **Avatar**: Selected Clash Royale card as avatar
- **Metadata**: Creation and update timestamps

## Endpoints

### Get Profile

Retrieve the current authenticated user's profile information.

**Endpoint:** `GET /api/profile`

**Authentication Required:** Yes (Bearer token)

**Request Body:** None

**Success Response (200 OK):**

```json
{
  "id": "123",
  "googleId": "1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar": "knight",
  "createdAt": "2024-01-15T10:00:00Z",
  "updatedAt": "2024-01-15T12:30:00Z"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | User's unique ID |
| `googleId` | string | Google OAuth user ID |
| `email` | string | User's email from Google |
| `name` | string | Display name (default: Google name) |
| `avatar` | string | Selected avatar card ID or null |
| `createdAt` | string | Account creation timestamp (ISO 8601) |
| `updatedAt` | string | Last profile update timestamp (ISO 8601) |

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 401 Unauthorized | Not authenticated | `{"detail": "Not authenticated"}` |
| 404 Not Found | User profile not found | `{"detail": "User profile not found"}` |

**Example Request:**

```bash
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer your-token"
```

**Frontend Usage:**

```javascript
async function fetchProfile() {
  const response = await fetch('/api/profile', {
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch profile');
  }

  return await response.json();
}

// Use in React component
function ProfileSection() {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    fetchProfile().then(setProfile);
  }, []);

  if (!profile) return <div>Loading...</div>;

  return (
    <div>
      <h2>{profile.name}</h2>
      <p>{profile.email}</p>
      {profile.avatar && <img src={getAvatarUrl(profile.avatar)} />}
    </div>
  );
}
```

---

### Update Profile

Update the authenticated user's profile (name and/or avatar).

**Endpoint:** `PUT /api/profile`

**Authentication Required:** Yes (Bearer token)

**Request Body:**

```json
{
  "name": "New Display Name",
  "avatar": "knight"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | Display name (1-50 chars, alphanumeric + spaces) |
| `avatar` | string | No | Avatar card ID (max 50 chars) |

**Validation Rules:**

- At least one field (name or avatar) must be provided
- Name must be 1-50 characters
- Name can only contain letters, numbers, and spaces
- Name cannot be empty or only whitespace
- Avatar must be a valid card identifier

**Success Response (200 OK):**

```json
{
  "id": "123",
  "googleId": "1234567890",
  "email": "user@example.com",
  "name": "New Display Name",
  "avatar": "knight",
  "createdAt": "2024-01-15T10:00:00Z",
  "updatedAt": "2024-01-15T14:00:00Z"
}
```

**Error Responses:**

| Status Code | Description | Example |
|-------------|-------------|---------|
| 400 Bad Request | No fields provided | `{"detail": "At least one field (name or avatar) must be provided for update"}` |
| 400 Bad Request | Invalid name format | `{"detail": "Name can only contain letters, numbers, and spaces"}` |
| 401 Unauthorized | Not authenticated | `{"detail": "Not authenticated"}` |
| 422 Unprocessable Entity | Validation error | `{"detail": [{"loc": ["body", "name"], "msg": "ensure this value has at most 50 characters"}]}` |

**Example Request:**

```bash
# Update name only
curl -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"name": "New Display Name"}'

# Update avatar only
curl -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"avatar": "knight"}'

# Update both
curl -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"name": "New Name", "avatar": "knight"}'
```

**Frontend Usage:**

```javascript
async function updateProfile(updates) {
  const response = await fetch('/api/profile', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAccessToken()}`
    },
    body: JSON.stringify(updates)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update profile');
  }

  return await response.json();
}

// Update name
async function updateDisplayName(name) {
  return await updateProfile({ name });
}

// Update avatar
async function updateAvatar(avatar) {
  return await updateProfile({ avatar });
}

// Update both
async function updateFullProfile(name, avatar) {
  return await updateProfile({ name, avatar });
}
```

---

## Profile Data Model

### User Profile Structure

```typescript
interface UserProfile {
  id: string;              // User ID
  googleId: string;        // Google OAuth ID
  email: string;           // Email from Google
  name: string;            // Display name
  avatar: string | null;   // Selected card ID or null
  createdAt: string;       // ISO 8601 timestamp
  updatedAt: string;       // ISO 8601 timestamp
}
```

### Avatar Selection

Avatars are Clash Royale card identifiers:

```javascript
// Common avatar choices
const popularAvatars = [
  'knight',
  'archer',
  'pekka',
  'wizard',
  'dragon',
  'prince',
  'witch',
  'giant'
];

// Get card details for avatar
function getAvatarCard(avatar, allCards) {
  return allCards.find(card =>
    card.name.toLowerCase() === avatar.toLowerCase()
  );
}

// Render avatar image
function AvatarImage({ avatar, allCards }) {
  const card = getAvatarCard(avatar, allCards);

  if (!card) return <DefaultAvatar />;

  return <img src={card.image_url} alt={card.name} />;
}
```

## Validation Details

### Name Validation

**Backend Implementation:**

```python
import re

@field_validator("name")
@classmethod
def validate_name(cls, v):
    if v is not None:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        if not re.match(r"^[a-zA-Z0-9\s]+$", v):
            raise ValueError("Name can only contain letters, numbers, and spaces")
        if len(v) > 50:
            raise ValueError("Name cannot exceed 50 characters")
    return v
```

**Frontend Validation:**

```javascript
function validateProfileName(name) {
  const errors = [];

  if (!name || name.trim().length === 0) {
    errors.push('Name cannot be empty');
  }

  if (name.length > 50) {
    errors.push('Name cannot exceed 50 characters');
  }

  if (!/^[a-zA-Z0-9\s]+$/.test(name)) {
    errors.push('Name can only contain letters, numbers, and spaces');
  }

  return errors;
}

// Use in form
function ProfileForm() {
  const [name, setName] = useState('');
  const [errors, setErrors] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validateProfileName(name);
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      await updateProfile({ name });
      setErrors([]);
    } catch (error) {
      setErrors([error.message]);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        maxLength={50}
        pattern="[a-zA-Z0-9\s]+"
      />
      {errors.map((err, i) => <p key={i}>{err}</p>)}
      <button type="submit">Update</button>
    </form>
  );
}
```

## Default Values

### On User Creation

When a user first authenticates via Google OAuth:

```python
user = User(
    google_id=google_user_info["google_id"],
    email=google_user_info["email"],
    name=google_user_info["name"],  # From Google
    avatar=None,  # No avatar selected yet
    created_at=datetime.now(),
    updated_at=datetime.now()
)
```

### Avatar Selection Flow

1. User authenticates ’ Profile created with no avatar
2. User navigates to profile section
3. Avatar selector shows available cards
4. User selects card ’ `PUT /api/profile {avatar: "knight"}`
5. Avatar saved and displayed

## Profile Component Integration

### Complete Profile Section Example

```typescript
import { useState, useEffect } from 'react';
import { fetchProfile, updateProfile } from '../services/api';
import { Card } from '../types';

interface ProfileSectionProps {
  allCards: Card[];
}

export function ProfileSection({ allCards }: ProfileSectionProps) {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      const data = await fetchProfile();
      setProfile(data);
      setName(data.name);
      setSelectedAvatar(data.avatar || '');
    } catch (err) {
      setError('Failed to load profile');
    }
  }

  async function handleSave() {
    try {
      const updates: any = {};

      if (name !== profile.name) {
        updates.name = name;
      }

      if (selectedAvatar !== profile.avatar) {
        updates.avatar = selectedAvatar;
      }

      if (Object.keys(updates).length > 0) {
        const updated = await updateProfile(updates);
        setProfile(updated);
        setEditing(false);
        setError('');
      }
    } catch (err) {
      setError(err.message);
    }
  }

  if (!profile) return <div>Loading...</div>;

  return (
    <div className="profile-section">
      {editing ? (
        <div>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Display Name"
          />
          <AvatarSelector
            cards={allCards}
            selected={selectedAvatar}
            onSelect={setSelectedAvatar}
          />
          <button onClick={handleSave}>Save</button>
          <button onClick={() => setEditing(false)}>Cancel</button>
        </div>
      ) : (
        <div>
          <h2>{profile.name}</h2>
          <p>{profile.email}</p>
          <AvatarDisplay avatar={profile.avatar} cards={allCards} />
          <button onClick={() => setEditing(true)}>Edit Profile</button>
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
```

## Testing

### Manual Testing

```bash
# Get profile
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer $TOKEN"

# Update name
curl -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "New Name"}'

# Update avatar
curl -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"avatar": "knight"}'

# Invalid name (should fail)
curl -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Invalid@Name!"}'

# Empty request (should fail)
curl -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

### Automated Testing

```bash
cd backend

# Profile endpoint tests
uv run pytest tests/test_profile_endpoints.py -v

# User service tests
uv run pytest tests/test_user_service.py -v

# Integration tests
uv run pytest tests/integration/test_profile_workflow.py -v
```

### Frontend Tests

```bash
cd frontend

# Profile component tests
npm test -- ProfileSection.test.tsx

# Avatar selector tests
npm test -- AvatarSelector.test.tsx
```

## Related Documentation

- [Authentication API](authentication.md) - How users authenticate
- [Google OAuth Integration](../features/google-oauth.md) - OAuth flow details
- [Frontend Development](../development/frontend.md) - ProfileSection component
- [Backend Architecture](../architecture/backend.md) - User service implementation
