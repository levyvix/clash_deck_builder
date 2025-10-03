# Task 14 Verification: Fix Save Deck API Payload Format

## Implementation Summary

### Changes Made

#### 1. Updated `frontend/src/services/api.ts`

**Added DeckPayload Interface:**
```typescript
export interface DeckPayload {
  name: string;
  cards: any[]; // Full card objects
  evolution_slots?: any[]; // Full card objects
  average_elixir?: number;
}
```

**Enhanced createDeck Function:**
- Added comprehensive console logging to show payload structure before sending
- Logs include:
  - Request URL
  - Deck name
  - Card count
  - Evolution slots count
  - Average elixir
  - Full JSON payload
- Added success logging for 201 responses
- Enhanced error logging with full payload details
- Verified Content-Type header is set to 'application/json' (already configured in fetchWithTimeout)

#### 2. Updated `frontend/src/components/DeckBuilder.tsx`

**Fixed Payload Format:**
- Changed from sending card IDs to sending full card objects
- Before: `cards: currentDeck.map(slot => slot.card!.id)`
- After: `cards: currentDeck.map(slot => slot.card!)`
- Before: `evolution_slots: currentDeck.filter(slot => slot.isEvolution).map(slot => slot.card!.id)`
- After: `evolution_slots: currentDeck.filter(slot => slot.isEvolution).map(slot => slot.card!)`

## Task Requirements Verification

### ✅ Requirement 4.1: Correct API Endpoint
- The createDeck function calls `POST ${API_BASE_URL}/decks`
- This matches the backend endpoint defined in `backend/src/api/decks.py`

### ✅ Requirement 4.2: Correct Payload Format
- Payload now includes:
  - `name`: string (deck name)
  - `cards`: array of full Card objects (not just IDs)
  - `evolution_slots`: array of full Card objects (not just IDs)
  - `average_elixir`: number (calculated average)
- This matches the backend Deck model expectations

### ✅ Requirement 8.2: Console Logging
- Added comprehensive console.log statements showing:
  - Full request URL
  - Payload structure breakdown
  - Complete JSON payload
  - Response status
  - Success/error messages

### ✅ Requirement 8.5: Content-Type Header
- Content-Type header is set to 'application/json' in fetchWithTimeout function
- This is applied to all API requests including createDeck

## Backend Expected Format

According to `backend/src/models/deck.py`, the Deck model expects:

```python
class Deck(BaseModel):
    name: str  # Required
    cards: List[Card]  # Required - exactly 8 cards
    evolution_slots: List[Card]  # Optional - max 2 cards
    average_elixir: Optional[float]  # Optional - auto-calculated if not provided
```

Each Card object should have:
```python
class Card(BaseModel):
    id: int
    name: str
    elixir_cost: int
    rarity: str
    type: str
    arena: str
    image_url: str
    image_url_evo: Optional[str]
```

## Testing Instructions

### Manual Testing Steps:

1. **Start the backend server:**
   ```bash
   cd backend
   uv run uvicorn main:app --reload
   ```

2. **Start the frontend development server:**
   ```bash
   cd frontend
   npm start
   ```

3. **Test the save deck functionality:**
   - Open the application in browser (http://localhost:3000)
   - Add 8 cards to the deck
   - Click "Save Deck" button
   - Enter a deck name
   - Click "Save"
   - Open browser console (F12) to see detailed logging

4. **Verify console output shows:**
   - "🔍 ===== CREATE DECK REQUEST ====="
   - URL: http://localhost:8000/decks
   - Payload structure with card count
   - Full JSON payload with card objects
   - Response status: 201 (on success)
   - "🎉 Deck created successfully!" (on success)

5. **Verify backend response:**
   - Should return 201 status code
   - Should return the created deck with an ID
   - Frontend should show "Deck saved successfully!" notification

### Expected Console Output Example:

```
🔍 ===== CREATE DECK REQUEST =====
📍 URL: http://localhost:8000/decks
📦 Payload Structure:
   - name: My Test Deck
   - cards count: 8
   - evolution_slots count: 2
   - average_elixir: 3.5

📄 Full Payload:
{
  "name": "My Test Deck",
  "cards": [
    {
      "id": 26000000,
      "name": "Knight",
      "elixir_cost": 3,
      "rarity": "Common",
      ...
    },
    ...
  ],
  "evolution_slots": [
    {
      "id": 26000001,
      "name": "Archers",
      ...
    }
  ],
  "average_elixir": 3.5
}
=====================================

✅ Create deck response status: 201
🎉 Deck created successfully!
```

## Error Scenarios to Test:

1. **Network Error:**
   - Stop backend server
   - Try to save deck
   - Should show: "Cannot connect to server"

2. **Validation Error:**
   - Try to save deck with less than 8 cards
   - Should show validation error from backend

3. **Timeout:**
   - Simulate slow network
   - Should show: "Request timed out"

## Next Steps

After verifying this task works correctly:
- Move to Task 15: Fix save deck success handling
- Move to Task 16: Fix save deck error handling
- Move to Task 17: Fix saved decks page API call

## Notes

- The backend expects full Card objects, not just IDs
- The backend will auto-calculate average_elixir if not provided, but we're sending it anyway
- The backend validates that the deck has exactly 8 cards
- The backend validates that evolution_slots has at most 2 cards
- The backend validates that evolution slot cards are also in the main deck
