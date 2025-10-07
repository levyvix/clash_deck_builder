# API Rate Limiting

This document outlines the rate limiting strategy for the Clash Royale Deck Builder API to ensure fair usage and protect the service from abuse.

## Rate Limits

| Resource | Limit | Window |
|----------|-------|--------|
| Public Endpoints | 100 requests | 1 minute |
| Authenticated Endpoints | 200 requests | 1 minute |
| Authentication Endpoints | 10 requests | 5 minutes |
| File Uploads | 20 requests | 1 hour |

## Rate Limit Headers

Responses include the following headers:

- `X-RateLimit-Limit`: Total number of requests allowed in the time window
- `X-RateLimit-Remaining`: Remaining number of requests in the current window
- `X-RateLimit-Reset`: Time (in UTC epoch seconds) when the current window resets
- `Retry-After`: Only present when rate limited, indicates seconds to wait before retrying

## Example Response Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1738281600
```

## Handling Rate Limits

When a rate limit is exceeded, the API will respond with:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Too many requests. Please try again in 60 seconds.",
    "retry_after": 60
  }
}
```

### Best Practices for Clients

1. **Monitor Rate Limit Headers**
   - Always check `X-RateLimit-Remaining` to avoid hitting limits
   - Use `X-RateLimit-Reset` to calculate when to retry

2. **Implement Exponential Backoff**
   ```javascript
   async function makeRequestWithRetry(url, options = {}, retries = 3, backoff = 1000) {
     try {
       const response = await fetch(url, options);
       
       if (response.status === 429) {
         const retryAfter = response.headers.get('Retry-After') || backoff / 1000;
         if (retries > 0) {
           await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
           return makeRequestWithRetry(url, options, retries - 1, backoff * 2);
         }
       }
       
       return response;
     } catch (error) {
       if (retries > 0) {
         await new Promise(resolve => setTimeout(resolve, backoff));
         return makeRequestWithRetry(url, options, retries - 1, backoff * 2);
       }
       throw error;
     }
   }
   ```

3. **Cache Responses**
   - Cache responses when possible to reduce API calls
   - Use appropriate cache headers (`ETag`, `Last-Modified`)

## Increasing Rate Limits

For applications that require higher rate limits, please contact support with:

1. Your application name and purpose
2. Expected request volume
3. Authentication method (API key, OAuth, etc.)

## Monitoring

Rate limit usage is logged and monitored. Excessive rate limiting may result in temporary or permanent restrictions.

## Testing Rate Limits

To test rate limiting in development:

```bash
# Using curl to test rate limits
for i in {1..110}; do
  curl -v "http://localhost:8000/api/endpoint" \
    -H "Authorization: Bearer $TOKEN"
  echo "Request $i"
done
```

## Rate Limit Categories

### 1. Public Endpoints
- Card listings
- Public deck views
- Health checks

### 2. Authenticated Endpoints
- User profile
- Deck management
- Card collections

### 3. Authentication Endpoints
- Login
- Token refresh
- OAuth callbacks

### 4. High-Cost Operations
- Complex searches
- Batch operations
- File processing

## Implementation Details

### Server-Side
- Uses Redis for distributed rate limiting
- Sliding window algorithm for accurate counting
- IP-based and user-based limits

### Client-Side
- Built-in retry mechanism in the SDK
- Automatic backoff for failed requests
- Configuration options for customizing behavior

## Troubleshooting

### Common Issues
1. **Unexpected Rate Limiting**
   - Check for multiple clients making requests
   - Verify authentication is working correctly
   - Look for background processes making requests

2. **High Latency**
   - May indicate you're approaching rate limits
   - Check response headers for rate limit information
   - Implement client-side caching

3. **429 Errors in Production**
   - Review your application's request patterns
   - Consider implementing request queuing
   - Contact support if limits are too restrictive

## Best Practices

1. **Client Libraries**
   - Use official SDKs which handle rate limiting automatically
   - Keep SDKs updated to benefit from improvements

2. **Batching**
   - Combine multiple operations into a single request when possible
   - Use the batch API endpoints

3. **Webhooks**
   - Prefer webhooks over polling where appropriate
   - Handle webhook retries properly
