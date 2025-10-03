# Error Handling Test Verification

This document provides manual test scenarios to verify the save deck error handling implementation.

## Test Scenarios

### 1. Test 404 Error (Endpoint Not Found)

**Setup:**
- Temporarily modify the API endpoint in `frontend/src/services/api.ts`
- Change `${API_BASE_URL}/decks` to `${API_BASE_URL}/decks-wrong`

**Steps:**
1. Build a complete deck (8 cards)
2. Click "Save Deck"
3. Enter a deck name
4. Click "Save"

**Expected Result:**
- Error notification appears with message: "Endpoint not found - check API configuration"
- Console shows 404 error details
- Deck is not saved

**Cleanup:**
- Restore the correct endpoint URL

---

### 2. Test 400 Validation Error

**Setup:**
- Backend should return 400 for invalid deck data
- This can be tested by modifying the payload temporarily

**Steps:**
1. Build a deck with less than 8 cards (if possible) or modify the payload in browser DevTools
2. Try to save the deck

**Expected Result:**
- Error notification appears with specific validation message from backend
- Example: "Deck must have exactly 8 cards" or similar validation message
- Console shows 400 error with details

---

### 3. Test Network Error

**Setup:**
- Stop the backend server
- Or disconnect from network
- Or use browser DevTools to simulate offline mode

**Steps:**
1. Build a complete deck (8 cards)
2. Click "Save Deck"
3. Enter a deck name
4. Click "Save"

**Expected Result:**
- Error notification appears with message: "Cannot connect to server"
- Console shows network error details
- Retry mechanism attempts to reconnect (check console logs)

---

### 4. Test Timeout Error

**Setup:**
- Use browser DevTools Network tab to throttle connection to "Slow 3G"
- Or temporarily increase timeout delay in backend

**Steps:**
1. Build a complete deck (8 cards)
2. Click "Save Deck"
3. Enter a deck name
4. Click "Save"
5. Wait for timeout (10 seconds)

**Expected Result:**
- Error notification appears with message: "Request timed out. Please try again."
- Console shows timeout error
- Request is aborted after 10 seconds

---

### 5. Test 500 Server Error

**Setup:**
- Temporarily modify backend to return 500 error
- Or cause a database error (e.g., stop MySQL)

**Steps:**
1. Build a complete deck (8 cards)
2. Click "Save Deck"
3. Enter a deck name
4. Click "Save"

**Expected Result:**
- Error notification appears with message: "Server error, please try again later."
- Console shows 500 error details
- User-friendly message doesn't expose internal error details

---

### 6. Test Successful Save (Baseline)

**Setup:**
- Ensure backend is running correctly
- Database is accessible

**Steps:**
1. Build a complete deck (8 cards)
2. Click "Save Deck"
3. Enter a deck name
4. Click "Save"

**Expected Result:**
- Success notification appears: "Deck saved successfully"
- Console shows 201 response
- Deck remains in builder (not cleared)
- Save dialog closes
- Saved decks list refreshes (if on saved decks page)

---

## Console Logging Verification

For all error scenarios, verify that console logs show:

1. **Request Details:**
   - Full URL being called
   - Request method (POST)
   - Payload structure and content

2. **Error Details:**
   - Error type (ApiError)
   - Status code (if applicable)
   - Error message
   - Whether it's a timeout or network error

3. **Retry Attempts:**
   - For network errors, should see retry attempts in console
   - Should show "retrying in Xms... (Y retries left)"

---

## Browser DevTools Testing

### Network Tab Verification

1. Open DevTools → Network tab
2. Attempt to save a deck
3. Verify:
   - Request URL is correct
   - Request method is POST
   - Request payload is properly formatted JSON
   - Response status code matches expected error
   - Response body contains error details

### Console Tab Verification

1. Open DevTools → Console tab
2. Look for detailed logging:
   - "🔍 ===== CREATE DECK REQUEST ====="
   - Payload structure
   - Response status
   - Error details (if any)

---

## Automated Test Execution

Run the Jest tests to verify error handling logic:

```bash
cd frontend
npm test -- api.test.ts
```

**Expected Results:**
- All tests should pass
- Tests cover: 404, 400, network error, timeout, 500, and success scenarios

---

## Error Message Checklist

Verify these specific error messages appear correctly:

- [ ] "Endpoint not found - check API configuration" (404)
- [ ] Specific validation message from backend (400)
- [ ] "Cannot connect to server" (network error)
- [ ] "Request timed out. Please try again." (timeout)
- [ ] "Server error, please try again later." (500)
- [ ] "Deck saved successfully" (201 success)

---

## Notes

- All error messages should be user-friendly (no technical jargon)
- Console logs should be detailed for debugging
- Notifications should auto-dismiss after a few seconds
- Error state should not break the UI
- User should be able to retry after an error
