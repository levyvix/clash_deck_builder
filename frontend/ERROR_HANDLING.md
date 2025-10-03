# Error Handling Implementation

This document describes the comprehensive error handling implemented across the Clash Royale Deck Builder frontend application.

## Overview

The application now has robust error handling that covers:
- Network failures
- API errors (4xx and 5xx responses)
- Timeout errors
- Component-level errors (via Error Boundaries)

## API Error Handling

### Custom ApiError Class

A custom `ApiError` class has been created in `services/api.ts` that categorizes errors:

```typescript
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public isTimeout: boolean = false,
    public isNetworkError: boolean = false
  )
}
```

### Error Categories

1. **Network Errors** (`isNetworkError: true`)
   - Displayed as: "Cannot connect to server"
   - Occurs when: Backend is unreachable or network is down

2. **Timeout Errors** (`isTimeout: true`)
   - Displayed as: "Request timed out"
   - Occurs when: Request takes longer than 10 seconds

3. **4xx Client Errors** (`statusCode: 400-499`)
   - Displayed as: The specific error message from the API response
   - Occurs when: Invalid request, validation errors, not found, etc.

4. **5xx Server Errors** (`statusCode: 500-599`)
   - Displayed as: "Server error, please try again"
   - Occurs when: Backend server encounters an error

### API Functions with Error Handling

All API functions now use the enhanced error handling:
- `fetchCards()` - Get all cards
- `fetchDecks()` - Get saved decks
- `createDeck()` - Save a new deck
- `updateDeck()` - Update deck name
- `deleteDeck()` - Delete a deck

### Retry Logic

API calls automatically retry up to 3 times with exponential backoff for:
- Network errors (TypeError)
- Timeout errors (AbortError)

## Component Error Handling

### DeckBuilder Component

**Card Loading Errors:**
- Try-catch block around `fetchCards()`
- Displays appropriate error message based on error type
- Shows retry button
- Adds notification to alert user

**Deck Saving Errors:**
- Try-catch block around `createDeck()`
- Displays specific error messages
- Keeps save dialog open on error
- Allows user to retry

### SavedDecks Component

**Deck Loading Errors:**
- Try-catch block around `fetchDecks()`
- Displays error message with retry button
- Notifies user via notification system

**Deck Update Errors:**
- Try-catch block around `updateDeck()`
- Displays specific error messages
- Notifies user of failure

**Deck Delete Errors:**
- Try-catch block around `deleteDeck()`
- Displays specific error messages
- Keeps confirmation dialog open on error

## Error Boundary

### ErrorBoundary Component

A React Error Boundary component has been implemented to catch component-level errors:

**Location:** `components/ErrorBoundary.tsx`

**Features:**
- Catches JavaScript errors anywhere in the child component tree
- Logs error details to console
- Displays user-friendly error UI
- Provides "Refresh Page" and "Try Again" buttons
- Shows error details in collapsible section (for debugging)

**Usage:**
Error boundaries wrap:
- The entire Routes component
- Individual route components (DeckBuilder, SavedDecks)

This provides multiple layers of error protection.

### Error Boundary UI

When an error is caught, users see:
- Clear error title: "Oops! Something went wrong"
- Helpful message explaining the situation
- Action buttons to recover
- Optional error details for debugging

## User Notifications

All errors trigger user notifications via the Notification component:
- **Error notifications** (red): For failures
- **Success notifications** (green): For successful operations
- **Info notifications** (blue): For informational messages

Notifications:
- Auto-dismiss after 3 seconds
- Can be manually dismissed
- Stack vertically in top-right corner

## Error Messages

### User-Friendly Messages

All error messages are written in plain language:

| Error Type | Message |
|------------|---------|
| Network failure | "Cannot connect to server. Please check your connection." |
| Timeout | "Request timed out. Please try again." |
| Server error (5xx) | "Server error, please try again later." |
| Client error (4xx) | Specific message from API |
| Component error | "Oops! Something went wrong" |

### Error Recovery

Users can recover from errors through:
1. **Retry buttons** - Reload data or retry operation
2. **Refresh page** - Full page reload
3. **Try again** - Reset error boundary state
4. **Manual actions** - Close dialogs and try different approach

## Testing Error Handling

To test error handling:

1. **Network Errors:**
   - Stop the backend server
   - Try to load cards or decks
   - Expected: "Cannot connect to server" message

2. **Timeout Errors:**
   - Simulate slow network (browser dev tools)
   - Make API request
   - Expected: "Request timed out" message after 10 seconds

3. **Server Errors:**
   - Modify backend to return 500 error
   - Make API request
   - Expected: "Server error, please try again" message

4. **Client Errors:**
   - Try to save deck with invalid data
   - Expected: Specific error message from API

5. **Component Errors:**
   - Trigger a JavaScript error in a component
   - Expected: Error boundary catches and displays error UI

## Best Practices Implemented

1. ✅ All API calls wrapped in try-catch blocks
2. ✅ Specific error messages for different error types
3. ✅ User-friendly error messages (no technical jargon)
4. ✅ Retry mechanisms for transient failures
5. ✅ Error boundaries for component-level errors
6. ✅ Consistent error notification system
7. ✅ Error logging to console for debugging
8. ✅ Graceful degradation (app remains functional)
9. ✅ Clear recovery paths for users
10. ✅ Timeout handling for long-running requests

## Future Enhancements

Potential improvements for error handling:
- Error tracking service integration (e.g., Sentry)
- Offline mode detection and messaging
- More granular retry strategies
- Error analytics and monitoring
- Custom error pages for different error types
