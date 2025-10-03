# Integration Test Report - Task 15

## Test Execution Date
Date: January 10, 2025

## Test Environment
- **Frontend**: React 19.2 with TypeScript
- **Backend**: FastAPI (Python)
- **Browser**: Testing required on Chrome, Firefox, Safari
- **Devices**: Desktop, Tablet, Mobile viewports

---

## Test Cases

### 1. Card Fetch and Display ✓
**Objective**: Verify cards fetch and display correctly with images

**Test Steps**:
1. Start the application
2. Navigate to the Deck Builder page
3. Observe card gallery loading

**Expected Results**:
- [ ] Cards load from API endpoint `/cards`
- [ ] All cards display with images
- [ ] Card names, elixir costs, and rarities are visible
- [ ] Rarity colors are correctly applied (Common: gray, Rare: orange, Epic: purple, Legendary: gold, Champion: gold)
- [ ] Loading spinner shows while fetching
- [ ] Image fallback works for broken images

**Status**: PENDING - Requires backend running

---

### 2. Filter Combinations ✓
**Objective**: Test all filter combinations work correctly

**Test Steps**:
1. Test name filter (search for "Knight")
2. Test elixir cost filter (select 3)
3. Test rarity filter (select "Epic")
4. Test type filter (select "Troop")
5. Test multiple filters combined
6. Test clear filters button

**Expected Results**:
- [ ] Name filter shows only matching cards (case-insensitive)
- [ ] Elixir filter shows only cards with exact cost
- [ ] Rarity filter shows only cards of selected rarity
- [ ] Type filter shows only cards of selected type
- [ ] Multiple filters work with AND logic
- [ ] Clear filters button resets all filters
- [ ] "No cards found" message appears when no matches
- [ ] Active filter count badge displays correctly

**Status**: PENDING - Requires backend running

---

### 3. Adding 8 Cards to Deck ✓
**Objective**: Test adding 8 cards to deck and enforcing limit

**Test Steps**:
1. Click on a card in the gallery
2. Click "Add to Deck" button
3. Repeat for 8 different cards
4. Try to add a 9th card

**Expected Results**:
- [ ] First card adds to slot 1
- [ ] Subsequent cards fill slots 2-8 in order
- [ ] After 8 cards, "Add to Deck" is disabled or shows error
- [ ] Error message: "Deck is full (8/8 cards)"
- [ ] Visual feedback on successful add (animation/highlight)
- [ ] Average elixir updates after each addition

**Status**: PENDING - Requires backend running

---

### 4. Removing Cards from Deck ✓
**Objective**: Test removing cards from deck leaves empty slots

**Test Steps**:
1. Add 8 cards to deck
2. Click on a card in deck slot 3
3. Click "Remove from Deck"
4. Verify slot 3 is now empty
5. Add a new card

**Expected Results**:
- [ ] Clicking deck slot shows options menu
- [ ] "Remove from Deck" button appears
- [ ] Card is removed and slot shows empty state (dashed border, "+" icon)
- [ ] Average elixir recalculates
- [ ] New cards fill the first empty slot
- [ ] Evolution status is cleared when card removed

**Status**: PENDING - Requires backend running

---

### 5. Evolution Slot Management ✓
**Objective**: Test marking 2 evolution slots and enforcing limit

**Test Steps**:
1. Add 8 cards to deck
2. Click on deck slot 1, select "Toggle Evolution"
3. Verify evolution badge appears
4. Click on deck slot 2, select "Toggle Evolution"
5. Try to mark deck slot 3 as evolution

**Expected Results**:
- [ ] First evolution toggle shows evolution image (if available)
- [ ] Evolution star badge (⭐) appears on card
- [ ] Second evolution toggle works
- [ ] Third evolution toggle is disabled
- [ ] Error message: "Maximum 2 evolution slots allowed"
- [ ] Can untoggle evolution to free up slot
- [ ] Evolution image displays correctly

**Status**: PENDING - Requires backend running

---

### 6. Average Elixir Calculation ✓
**Objective**: Test average elixir calculation with various card combinations

**Test Cases**:
- Empty deck: 0.0
- 1 card (3 elixir): 3.0
- 2 cards (3, 5 elixir): 4.0
- 8 cards (2, 3, 3, 4, 4, 5, 6, 7): 4.3
- Remove card and verify recalculation

**Expected Results**:
- [ ] Empty deck shows 0.0
- [ ] Single card shows correct value
- [ ] Multiple cards calculate average correctly
- [ ] Result rounded to 1 decimal place
- [ ] Updates in real-time when cards added/removed
- [ ] Display format: "X.X" (e.g., "4.3")

**Status**: PENDING - Requires backend running

---

### 7. Saving Deck ✓
**Objective**: Test saving deck with valid name

**Test Steps**:
1. Build a complete deck (8 cards)
2. Click "Save Deck" button
3. Enter deck name "Test Deck 1"
4. Confirm save

**Expected Results**:
- [ ] Save button is disabled until 8 cards added
- [ ] Name prompt appears when clicking save
- [ ] Deck saves via POST `/decks` endpoint
- [ ] Success notification: "Deck saved successfully!"
- [ ] Deck appears in saved decks list
- [ ] Evolution slots are preserved
- [ ] Average elixir is saved correctly

**Status**: PENDING - Requires backend running

---

### 8. Loading Saved Deck ✓
**Objective**: Test loading saved deck into builder

**Test Steps**:
1. Navigate to "Saved Decks" page
2. Click "Load Deck" on a saved deck
3. Verify navigation to Deck Builder
4. Verify deck is loaded correctly

**Expected Results**:
- [ ] Clicking "Load Deck" navigates to builder
- [ ] All 8 cards appear in correct slots
- [ ] Evolution slots are restored
- [ ] Average elixir displays correctly
- [ ] Success notification: "Loaded deck: [name]"
- [ ] Current deck state is replaced

**Status**: PENDING - Requires backend running

---

### 9. Renaming Deck ✓
**Objective**: Test renaming deck

**Test Steps**:
1. Navigate to "Saved Decks" page
2. Click "Rename" on a deck
3. Enter new name "Updated Deck Name"
4. Click save (✓) button
5. Verify name updates

**Expected Results**:
- [ ] Clicking "Rename" shows inline input field
- [ ] Input is pre-filled with current name
- [ ] Save button (✓) updates name via PUT `/decks/{id}`
- [ ] Cancel button (✕) discards changes
- [ ] Enter key saves, Escape key cancels
- [ ] Success notification: "Deck renamed successfully"
- [ ] Empty name shows error: "Deck name cannot be empty"

**Status**: PENDING - Requires backend running

---

### 10. Deleting Deck ✓
**Objective**: Test deleting deck with confirmation

**Test Steps**:
1. Navigate to "Saved Decks" page
2. Click "Delete" on a deck
3. Verify confirmation dialog appears
4. Click "Cancel" - verify deck remains
5. Click "Delete" again
6. Click "Delete" in confirmation - verify deck removed

**Expected Results**:
- [ ] Clicking "Delete" shows confirmation overlay
- [ ] Confirmation message: "Delete this deck?"
- [ ] "Cancel" button closes dialog without deleting
- [ ] "Delete" button removes deck via DELETE `/decks/{id}`
- [ ] Deck disappears from list
- [ ] Success notification: "Deck deleted successfully"

**Status**: PENDING - Requires backend running

---

### 11. Error Scenarios ✓
**Objective**: Test error scenarios (backend down, network failure)

**Test Cases**:

#### 11.1 Backend Down
1. Stop backend server
2. Refresh application
3. Observe error handling

**Expected Results**:
- [ ] Error message: "Cannot connect to server. Please check your connection."
- [ ] Retry button appears
- [ ] No application crash
- [ ] Error boundary catches component errors

#### 11.2 Network Timeout
1. Simulate slow network
2. Attempt to save deck

**Expected Results**:
- [ ] Timeout error: "Request timed out. Please try again."
- [ ] Loading spinner shows during request
- [ ] User can retry action

#### 11.3 Server Error (5xx)
1. Trigger 500 error from backend
2. Observe error handling

**Expected Results**:
- [ ] Error message: "Server error, please try again later."
- [ ] Error notification displays
- [ ] Application remains functional

#### 11.4 Client Error (4xx)
1. Attempt invalid operation (e.g., save 21st deck)
2. Observe error handling

**Expected Results**:
- [ ] Specific error message from API response
- [ ] Error notification displays
- [ ] User can correct and retry

**Status**: PENDING - Requires backend running

---

### 12. Browser Compatibility ✓
**Objective**: Test on multiple browsers (Chrome, Firefox, Safari)

**Test Steps**:
1. Open application in Chrome
2. Perform basic operations (add cards, save deck)
3. Repeat in Firefox
4. Repeat in Safari (if available)

**Expected Results**:
- [ ] Chrome: All features work correctly
- [ ] Firefox: All features work correctly
- [ ] Safari: All features work correctly
- [ ] CSS renders consistently
- [ ] No console errors
- [ ] Animations work smoothly

**Status**: PENDING - Manual testing required

---

### 13. Responsive Design ✓
**Objective**: Verify responsive behavior on mobile, tablet, desktop

**Test Steps**:
1. Open application in desktop viewport (1920x1080)
2. Resize to tablet viewport (768x1024)
3. Resize to mobile viewport (375x667)
4. Test all interactions at each size

**Expected Results**:

#### Desktop (> 1200px)
- [ ] Card gallery: 6 columns
- [ ] Deck slots: 2 rows of 4
- [ ] All controls visible
- [ ] Filters in sidebar or top section

#### Tablet (768px - 1200px)
- [ ] Card gallery: 4 columns
- [ ] Deck slots: 2 rows of 4
- [ ] Navigation remains accessible
- [ ] Touch interactions work

#### Mobile (< 768px)
- [ ] Card gallery: 2 columns
- [ ] Deck slots: Stack vertically or 2x4 grid
- [ ] Filters collapse or stack
- [ ] Touch targets are large enough (44x44px minimum)
- [ ] No horizontal scrolling
- [ ] Text remains readable

**Status**: PENDING - Manual testing required

---

## Test Execution Instructions

### Prerequisites
1. Start backend server:
   ```bash
   cd backend
   uv run uvicorn src.main:app --reload
   ```

2. Start frontend development server:
   ```bash
   cd frontend
   npm start
   ```

3. Ensure database is running and populated with card data

### Automated Testing
Run the test suite:
```bash
cd frontend
npm test -- --run
```

### Manual Testing
1. Follow each test case in order
2. Check off completed items
3. Document any failures or issues
4. Take screenshots of visual bugs
5. Test on multiple browsers and devices

---

## Known Issues
- None identified yet

---

## Test Summary

**Total Test Cases**: 13
**Passed**: 0
**Failed**: 0
**Pending**: 13

**Overall Status**: PENDING - Awaiting backend availability

---

## Next Steps
1. Start backend server
2. Execute all test cases systematically
3. Document results
4. Fix any identified issues
5. Re-test failed cases
6. Mark task as complete when all tests pass
