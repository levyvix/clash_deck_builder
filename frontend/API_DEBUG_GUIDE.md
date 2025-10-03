# API Endpoint Debugging Guide

## Overview
This document describes the debugging features added to help diagnose API endpoint configuration issues.

## Features Implemented

### 1. Automatic Logging on Module Load
When the API service module loads, it automatically logs:
- ✅ API Base URL being used
- ✅ Current environment (development/production)
- ✅ Value of REACT_APP_API_BASE_URL from environment

**Example Console Output:**
```
🔧 API Service Initialized
📍 API_BASE_URL: http://localhost:8000
🌍 Environment: development
⚙️  REACT_APP_API_BASE_URL from env: http://localhost:8000
```

### 2. Enhanced API Call Logging
Every API call now logs:
- ✅ Full URL being called
- ✅ Request payload (for POST/PUT)
- ✅ Response status
- ✅ Detailed error information on failure

**Example Console Output:**
```
🃏 Fetching cards from: http://localhost:8000/cards/cards
✅ Cards response status: 200

💾 Creating deck at: http://localhost:8000/decks
📦 Payload: {
  "name": "My Deck",
  "cards": [...]
}
✅ Create deck response status: 201
```

### 3. Endpoint Verification Function
A comprehensive `verifyEndpoints()` function tests all API endpoints:
- ✅ Tests health check endpoint
- ✅ Tests cards endpoint
- ✅ Tests decks endpoint (GET and POST)
- ✅ Shows response time for each endpoint
- ✅ Shows response status and content type
- ✅ Provides helpful error messages

**Automatically runs on app initialization in development mode.**

**Example Console Output:**
```
🔍 ===== API ENDPOINT VERIFICATION =====
Base URL: http://localhost:8000
Timestamp: 2025-03-10T12:00:00.000Z
========================================

📡 Testing: Health Check
   Method: GET
   URL: http://localhost:8000/health
   ✅ Status: 200 OK
   ⏱️  Duration: 45.23ms
   📦 Content-Type: application/json
   📊 Response: Object with keys: status, message

📡 Testing: Fetch Cards
   Method: GET
   URL: http://localhost:8000/cards/cards
   ✅ Status: 200 OK
   ⏱️  Duration: 123.45ms
   📦 Content-Type: application/json
   📊 Response: Array with 109 items

📡 Testing: Fetch Decks
   Method: GET
   URL: http://localhost:8000/decks
   ✅ Status: 200 OK
   ⏱️  Duration: 67.89ms
   📦 Content-Type: application/json
   📊 Response: Array with 5 items

========================================
✅ Endpoint verification complete
========================================
```

## How to Use

### Viewing Debug Information

1. **Open Browser Developer Tools**
   - Chrome/Edge: Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)
   - Firefox: Press F12 or Ctrl+Shift+K (Cmd+Option+K on Mac)

2. **Go to Console Tab**
   - All debug information will be displayed here

3. **Start the Application**
   ```bash
   cd frontend
   npm start
   ```

4. **Check Console Output**
   - Look for the API initialization logs
   - Look for the endpoint verification results
   - Monitor API calls as you interact with the app

### Manually Running Endpoint Verification

You can manually trigger endpoint verification from the browser console:

```javascript
// Import and run verification
import { verifyEndpoints } from './services/api';
verifyEndpoints();
```

Or add a button in the UI temporarily:

```tsx
import { verifyEndpoints } from './services/api';

<button onClick={() => verifyEndpoints()}>
  Test API Endpoints
</button>
```

### Checking Network Tab

1. **Open Developer Tools → Network Tab**
2. **Filter by "Fetch/XHR"**
3. **Interact with the app** (load cards, save deck, etc.)
4. **Click on any request** to see:
   - Full request URL
   - Request headers
   - Request payload
   - Response status
   - Response body

## Common Issues and Solutions

### Issue: "Cannot connect to server"
**Symptoms:** Network errors in console, red error messages

**Solutions:**
1. Check if backend is running:
   ```bash
   cd backend
   uv run uvicorn main:app --reload
   ```

2. Verify backend is accessible:
   - Open http://localhost:8000/health in browser
   - Should see: `{"status": "healthy"}`

3. Check CORS configuration in backend

### Issue: "404 Not Found"
**Symptoms:** API calls return 404 status

**Solutions:**
1. Verify API_BASE_URL in console logs
2. Check backend route definitions
3. Ensure backend is running on correct port
4. Check for typos in endpoint paths

### Issue: Wrong API Base URL
**Symptoms:** API calls go to wrong server

**Solutions:**
1. Check `.env` file in frontend directory:
   ```
   REACT_APP_API_BASE_URL=http://localhost:8000
   ```

2. Restart development server after changing .env:
   ```bash
   # Stop server (Ctrl+C)
   npm start
   ```

3. Verify in console that correct URL is loaded

### Issue: CORS Errors
**Symptoms:** "Access-Control-Allow-Origin" errors

**Solutions:**
1. Check backend CORS middleware configuration
2. Ensure backend allows requests from frontend origin
3. Check if credentials are being sent correctly

## Environment Configuration

### Development (.env.local)
```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

### Docker Development (.env.docker)
```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

### Production
```env
REACT_APP_API_BASE_URL=https://your-api-domain.com
```

## Disabling Debug Logs

To disable debug logs in production, the endpoint verification only runs in development mode:

```typescript
if (process.env.NODE_ENV === 'development') {
  verifyEndpoints();
}
```

To disable all debug logs, you can comment out the console.log statements in `api.ts`.

## Additional Tips

1. **Use Browser DevTools Network Tab** to see actual HTTP requests
2. **Check Response Headers** for CORS and content-type issues
3. **Monitor Console** for automatic debug information
4. **Test Backend Directly** using curl or Postman to isolate issues
5. **Check Backend Logs** for server-side errors

## Testing Checklist

- [ ] API service initializes with correct base URL
- [ ] Endpoint verification runs on app start
- [ ] All endpoints return expected status codes
- [ ] API calls show full URLs in console
- [ ] Error messages are clear and actionable
- [ ] Network tab shows correct request URLs
- [ ] Backend is accessible at configured URL
- [ ] CORS headers are present in responses
