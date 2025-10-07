# Error Handling Guide

This document outlines the error handling strategy for the Clash Royale Deck Builder application.

## Table of Contents
1. [Error Classification](#error-classification)
2. [Error Responses](#error-responses)
3. [Client-Side Handling](#client-side-handling)
4. [Server-Side Handling](#server-side-handling)
5. [Logging and Monitoring](#logging-and-monitoring)
6. [Error Recovery](#error-recovery)
7. [Testing Error Cases](#testing-error-cases)
8. [Best Practices](#best-practices)

## Error Classification

### 1. Client Errors (4xx)
- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Resource conflict
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded

### 2. Server Errors (5xx)
- **500 Internal Server Error**: Unhandled exception
- **502 Bad Gateway**: Upstream service error
- **503 Service Unavailable**: Service temporarily unavailable
- **504 Gateway Timeout**: Upstream service timeout

### 3. Business Logic Errors
- **Invalid State**: Operation not allowed in current state
- **Validation Failed**: Business rule violation
- **Quota Exceeded**: Usage limits reached
- **Maintenance Mode**: Service temporarily unavailable

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "deck_name",
        "message": "must be between 3 and 100 characters"
      }
    ],
    "request_id": "req_abc123",
    "documentation_url": "https://docs.example.com/errors/invalid-request"
  }
}
```

### Field Descriptions
- **code**: Machine-readable error code
- **message**: Human-readable error message
- **details**: Array of error details (optional)
- **request_id**: Unique identifier for the request
- **documentation_url**: Link to documentation (optional)

## Client-Side Handling

### Error Boundary (React)
```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

### API Client
```javascript
class ApiClient {
  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new ApiError(
          error.message || 'Something went wrong',
          response.status,
          error
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Network error', 0, { code: 'network_error' });
    }
  }
}
```

## Server-Side Handling

### Error Middleware (FastAPI)
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code if hasattr(exc, "code") else "http_error",
                "message": exc.detail,
                "request_id": request.state.request_id,
            }
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Validation failed",
                "details": [
                    {
                        "field": ".".join(str(loc) for loc in error["loc"]),
                        "message": error["msg"],
                    }
                    for error in exc.errors()
                ],
                "request_id": request.state.request_id,
            }
        },
    )
```

### Business Logic Errors
```python
class BusinessError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# Usage
raise BusinessError(
    code="insufficient_funds",
    message="Not enough credits to complete this operation",
    status_code=402
)
```

## Logging and Monitoring

### Structured Logging
```python
import logging
import json_log_formatter

formatter = json_log_formatter.JSONFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger('app')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
try:
    # Business logic
    pass
except Exception as e:
    logger.error("Failed to process request", 
        extra={
            'error': str(e),
            'type': type(e).__name__,
            'stack_trace': traceback.format_exc(),
            'request_id': request.state.request_id,
        }
    )
    raise
```

### Monitoring Integration
- Track error rates by type and endpoint
- Set up alerts for increased error rates
- Create dashboards for error trends
- Implement distributed tracing for error correlation

## Error Recovery

### Retry Logic
```javascript
async function withRetry(operation, maxRetries = 3, delay = 1000) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx) except 429
      if (error.status >= 400 && error.status < 500 && error.status !== 429) {
        break;
      }
      
      // Exponential backoff with jitter
      const backoff = delay * Math.pow(2, i) + Math.random() * 1000;
      await new Promise(resolve => setTimeout(resolve, backoff));
    }
  }
  
  throw lastError;
}
```

### Circuit Breaker
```javascript
class CircuitBreaker {
  constructor(failureThreshold = 5, resetTimeout = 30000) {
    this.failureThreshold = failureThreshold;
    this.resetTimeout = resetTimeout;
    this.failureCount = 0;
    this.lastFailure = null;
    this.state = 'CLOSED';
  }

  async execute(operation) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailure > this.resetTimeout) {
        this.state = 'HALF-OPEN';
      } else {
        throw new Error('Service unavailable');
      }
    }

    try {
      const result = await operation();
      if (this.state === 'HALF-OPEN') {
        this.reset();
      }
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  recordFailure() {
    this.failureCount++;
    this.lastFailure = Date.now();
    
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      setTimeout(() => this.state = 'HALF-OPEN', this.resetTimeout);
    }
  }

  reset() {
    this.failureCount = 0;
    this.lastFailure = null;
    this.state = 'CLOSED';
  }
}
```

## Testing Error Cases

### Unit Tests
```python
def test_insufficient_funds():
    with pytest.raises(BusinessError) as excinfo:
        process_payment(user_id=1, amount=1000)
    
    assert excinfo.value.code == "insufficient_funds"
    assert excinfo.value.status_code == 402
```

### Integration Tests
```javascript
describe('Deck API', () => {
  it('should return 400 for invalid deck data', async () => {
    const response = await request(app)
      .post('/api/decks')
      .send({ invalid: 'data' });
    
    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('validation_error');
  });
});
```

### E2E Tests
```javascript
describe('Deck Creation', () => {
  it('should show error for invalid deck', async () => {
    await page.goto('/decks/new');
    await page.click('button[type="submit"]');
    
    const errorMessage = await page.$eval(
      '.error-message',
      el => el.textContent
    );
    
    expect(errorMessage).toContain('Deck must have 8 cards');
  });
});
```

## Best Practices

### Do's
- Use specific error types for different error cases
- Include helpful error messages
- Log errors with sufficient context
- Handle errors at the appropriate level
- Provide recovery options when possible

### Don'ts
- Don't expose sensitive information in errors
- Don't swallow errors without logging
- Don't use exceptions for control flow
- Don't return 200 for error conditions
- Don't rely on generic error messages

### Performance Considerations
- Use Error objects instead of string errors
- Avoid creating stack traces for expected errors
- Use error boundaries to prevent UI crashes
- Implement proper error aggregation

### Security Considerations
- Sanitize error messages before displaying to users
- Don't leak stack traces in production
- Rate limit error responses
- Monitor for suspicious error patterns

## Error Codes Reference

### Authentication (1xxx)
- `1001`: Invalid credentials
- `1002`: Token expired
- `1003`: Insufficient permissions

### Validation (2xxx)
- `2001`: Required field missing
- `2002`: Invalid format
- `2003`: Out of range

### Business Logic (3xxx)
- `3001`: Insufficient funds
- `3002`: Resource not found
- `3003`: Operation not allowed

### System Errors (5xxx)
- `5001`: Service unavailable
- `5002`: Timeout
- `5003`: External service error
