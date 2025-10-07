# API Versioning Strategy

This document outlines the versioning strategy for the Clash Royale Deck Builder API.

## Table of Contents
1. [Versioning Scheme](#versioning-scheme)
2. [Versioning Methods](#versioning-methods)
3. [Deprecation Policy](#deprecation-policy)
4. [Breaking Changes](#breaking-changes)
5. [Version Negotiation](#version-negotiation)
6. [Migration Guide](#migration-guide)
7. [Examples](#examples)
8. [Best Practices](#best-practices)

## Versioning Scheme

### Semantic Versioning (SemVer)
The API follows [Semantic Versioning 2.0.0](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: Backward-compatible features
- **PATCH**: Backward-compatible bug fixes

### Version Format
```
v<MAJOR>.<MINOR>.<PATCH>
```

### Current Versions
| Version | Status      | Release Date  | End of Life   |
|---------|-------------|---------------|---------------|
| v1.0.0  | Stable      | 2025-10-01    | TBD           |
| v0.9.0  | Deprecated  | 2025-09-15    | 2025-12-31    |

## Versioning Methods

### 1. URL Path Versioning
```
https://api.example.com/v1/decks
```

### 2. Custom Header
```http
GET /decks HTTP/1.1
Host: api.example.com
Accept: application/json
Accept-Version: v1.0.0
```

### 3. Media Type Versioning
```http
GET /decks HTTP/1.1
Host: api.example.com
Accept: application/vnd.clashroyale.v1+json
```

### Recommendation
- Use **URL Path Versioning** for simplicity
- Support **Accept Header** for flexibility
- Include version in all responses

## Deprecation Policy

### Timeline
1. **Announcement**: 90 days before deprecation
2. **Deprecation**: Mark version as deprecated
3. **Sunset**: 180 days after deprecation
4. **End of Life**: Version is no longer available

### Deprecation Headers
```http
HTTP/1.1 200 OK
Content-Type: application/json
Deprecation: true
Sunset: Sat, 01 Jan 2026 00:00:00 GMT
Link: <https://api.example.com/docs/v2>; rel="successor-version"

{
  "data": { ... },
  "meta": {
    "deprecation": {
      "is_deprecated": true,
      "message": "This API version is deprecated and will be removed on 2026-01-01.",
      "sunset_date": "2026-01-01T00:00:00Z",
      "migration_guide": "https://docs.example.com/migrate/v1-to-v2"
    }
  }
}
```

## Breaking Changes

### What Constitutes a Breaking Change?
- Removing or renaming endpoints
- Removing or renaming fields
- Changing field types
- Changing authentication or authorization requirements
- Changing error response formats
- Removing enum values

### Non-Breaking Changes
- Adding new endpoints
- Adding new optional request parameters
- Adding new fields to responses
- Adding new enum values
- Adding new error codes

## Version Negotiation

### Default Version
When no version is specified, the latest stable version is used.

### Version Selection
1. Check URL path for version
2. Check `Accept-Version` header
3. Check `Accept` header for media type version
4. Default to latest stable version

### Example
```http
GET /v1/decks HTTP/1.1
Host: api.example.com
Accept: application/json
Accept-Version: 1.0.0
```

## Migration Guide

### v1.0.0 to v2.0.0

#### Breaking Changes
1. **Endpoint Changes**
   - Removed: `GET /decks/{id}/share`
   - Moved: `POST /decks/{id}/copy` to `POST /decks/{id}/duplicate`

2. **Field Changes**
   - Renamed: `deck.cards` to `deck.cards_list`
   - Removed: `deck.is_public` (use `visibility` field instead)
   - Changed type: `deck.average_elixir` from `float` to `decimal(3,1)`

3. **Authentication**
   - New required scope: `decks:write` for write operations
   - Session timeout reduced from 24h to 12h

#### Migration Steps
1. Update all API calls to use the new endpoints
2. Update field names in your application
3. Request the new `decks:write` scope
4. Implement refresh token handling

#### Example Migration
```javascript
// Before
const response = await fetch('/v1/decks/123/share', {
  method: 'POST',
  body: JSON.stringify({ is_public: true })
});

// After
const response = await fetch('/v2/decks/123', {
  method: 'PATCH',
  body: JSON.stringify({ visibility: 'public' })
});
```

## Examples

### Request with Version in URL
```http
GET /v1/decks/123 HTTP/1.1
Host: api.example.com
Accept: application/json
```

### Request with Accept-Version Header
```http
GET /decks/123 HTTP/1.1
Host: api.example.com
Accept: application/json
Accept-Version: 1.0.0
```

### Response with Version Information
```http
HTTP/1.1 200 OK
Content-Type: application/json
API-Version: 1.0.0

{
  "data": { ... },
  "meta": {
    "version": "1.0.0",
    "api_status": "stable",
    "documentation": "https://docs.example.com/v1"
  }
}
```

## Best Practices

### For API Consumers
- Always specify the API version in requests
- Monitor for deprecation headers
- Plan for version upgrades
- Test new versions in staging first

### For API Developers
- Maintain backward compatibility within major versions
- Document all breaking changes
- Provide migration guides
- Support multiple versions during transition periods
- Monitor version usage

### Versioning Don'ts
- Don't use query parameters for versioning
- Don't break backward compatibility in minor/patch versions
- Don't maintain too many versions
- Don't remove versions without notice

## Version Lifecycle

### Development (vX.Y.Z-dev)
- Pre-release versions for testing
- May contain breaking changes
- Not for production use

### Beta (vX.Y.0-beta.N)
- Feature complete
- May have bugs
- Breaking changes possible between beta versions

### Release Candidate (vX.Y.0-rc.N)
- No breaking changes from previous RCs
- Only bug fixes from this point
- Final testing before stable release

### Stable (vX.Y.Z)
- Production-ready
- Follows semantic versioning
- Supported until end of life

## Version Support Policy

### Active Support
- Bug fixes and security patches
- 12 months from release date
- Critical issues addressed within 72 hours

### Maintenance Support
- Security patches only
- 6 months after active support ends
- No new features or non-critical bug fixes

### End of Life
- No support provided
- No security updates
- Upgrade to a supported version required
