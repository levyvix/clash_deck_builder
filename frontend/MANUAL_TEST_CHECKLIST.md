# Manual Test Checklist - Task 15
## Final Integration and Testing

**Date**: January 10, 2025  
**Tester**: _____________  
**Environment**: Development

---

## Prerequisites

### Backend Setup
```bash
cd backend
uv run uvicorn src.main:app --reload
```
**Backend URL**: http://localhost:8000  
**Status**: ⬜ Running ⬜ Not Running

### Frontend Setup
```bash
cd frontend
npm start
```
**Frontend URL**: http://localhost:3000  
**Status**: ⬜ Running ⬜ Not Running

### Database
**Status**: ⬜ Running ⬜ Not Running  
**Cards Loaded**: ⬜ Yes ⬜ No

---

## Test Execution

### 1. Card Fetch and Display ✓
**Requirement**: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Open application | Loading spinner appears | ⬜ Pass ⬜ Fail | |
| Wait for cards to load | All cards display in grid | ⬜ Pass ⬜ Fail | |
| Check card images | Images load correctly | ⬜ Pass ⬜ Fail | |
| Check card details | Name, elixir, rarity visible | ⬜ Pass ⬜ Fail | |
| Check rarity colors | Common=gray, Rare=orange, Epic=purple, Legendary=gold, Champion=gold | ⬜ Pass ⬜ Fail | |
| Break an image URL | Fallback placeholder shows | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 2. Filter Combinations ✓
**Requirement**: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Type "Knight" in name filter | Only cards with "Knight" in name show | ⬜ Pass ⬜ Fail | |
| Type "knight" (lowercase) | Same results (case-insensitive) | ⬜ Pass ⬜ Fail | |
| Select elixir cost "3" | Only 3-elixir cards show | ⬜ Pass ⬜ Fail | |
| Select rarity "Epic" | Only Epic cards show | ⬜ Pass ⬜ Fail | |
| Select type "Troop" | Only Troop cards show | ⬜ Pass ⬜ Fail | |
| Combine: name="Knight", elixir=3 | Only 3-elixir Knights show | ⬜ Pass ⬜ Fail | |
| Combine all 4 filters | Correct cards show (AND logic) | ⬜ Pass ⬜ Fail | |
| Set impossible filter combo | "No cards found" message | ⬜ Pass ⬜ Fail | |
| Check filter badge | Shows count of active filters | ⬜ Pass ⬜ Fail | |
| Click "Clear Filters" | All cards show again | ⬜ Pass ⬜ Fail | |
| Clear filters when none active | Button is disabled | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 3. Adding 8 Cards to Deck ✓
**Requirement**: 3.1, 3.2, 3.3, 3.9

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Click on first card | "Add to Deck" option appears | ⬜ Pass ⬜ Fail | |
| Click "Add to Deck" | Card appears in slot 1 | ⬜ Pass ⬜ Fail | |
| Add 7 more cards | Cards fill slots 2-8 | ⬜ Pass ⬜ Fail | |
| Check deck counter | Shows "8/8 cards" | ⬜ Pass ⬜ Fail | |
| Try to add 9th card | Error: "Deck is full" | ⬜ Pass ⬜ Fail | |
| Check visual feedback | Animation/highlight on add | ⬜ Pass ⬜ Fail | |
| Check average elixir | Updates after each card | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 4. Removing Cards from Deck ✓
**Requirement**: 3.4, 3.5, 3.10

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Build full deck (8 cards) | All slots filled | ⬜ Pass ⬜ Fail | |
| Click on deck slot 3 | Options menu appears | ⬜ Pass ⬜ Fail | |
| Click "Remove from Deck" | Card removed, slot shows empty | ⬜ Pass ⬜ Fail | |
| Check empty slot visual | Dashed border, "+" icon | ⬜ Pass ⬜ Fail | |
| Check average elixir | Recalculates correctly | ⬜ Pass ⬜ Fail | |
| Add new card | Fills first empty slot (slot 3) | ⬜ Pass ⬜ Fail | |
| Remove evolution card | Evolution status cleared | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 5. Evolution Slot Management ✓
**Requirement**: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Build full deck (8 cards) | All slots filled | ⬜ Pass ⬜ Fail | |
| Click slot 1, select "Toggle Evolution" | Evolution image shows (if available) | ⬜ Pass ⬜ Fail | |
| Check evolution badge | Star icon (⭐) appears | ⬜ Pass ⬜ Fail | |
| Click slot 2, toggle evolution | Second evolution works | ⬜ Pass ⬜ Fail | |
| Click slot 3, try to toggle | Error: "Maximum 2 evolution slots" | ⬜ Pass ⬜ Fail | |
| Toggle button disabled | Cannot click on slot 3 | ⬜ Pass ⬜ Fail | |
| Untoggle slot 1 evolution | Evolution badge removed | ⬜ Pass ⬜ Fail | |
| Toggle slot 3 evolution | Now works (under limit) | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 6. Average Elixir Calculation ✓
**Requirement**: 3.6, 3.7

| Test Case | Cards | Expected Avg | Actual Avg | Status |
|-----------|-------|--------------|------------|--------|
| Empty deck | None | 0.0 | _____ | ⬜ Pass ⬜ Fail |
| 1 card | 3 elixir | 3.0 | _____ | ⬜ Pass ⬜ Fail |
| 2 cards | 3, 5 elixir | 4.0 | _____ | ⬜ Pass ⬜ Fail |
| 8 cards | 2,3,3,4,4,5,6,7 | 4.3 | _____ | ⬜ Pass ⬜ Fail |
| Remove 1 card | 7 cards remaining | _____ | _____ | ⬜ Pass ⬜ Fail |
| Format check | Any deck | X.X format | _____ | ⬜ Pass ⬜ Fail |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 7. Saving Deck ✓
**Requirement**: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Check "Save Deck" button | Disabled with < 8 cards | ⬜ Pass ⬜ Fail | |
| Build full deck (8 cards) | "Save Deck" button enabled | ⬜ Pass ⬜ Fail | |
| Click "Save Deck" | Name prompt appears | ⬜ Pass ⬜ Fail | |
| Enter "Test Deck 1" | Name accepted | ⬜ Pass ⬜ Fail | |
| Confirm save | Success notification appears | ⬜ Pass ⬜ Fail | |
| Check notification message | "Deck saved successfully!" | ⬜ Pass ⬜ Fail | |
| Navigate to Saved Decks | Deck appears in list | ⬜ Pass ⬜ Fail | |
| Check saved deck details | 8 cards, correct avg elixir | ⬜ Pass ⬜ Fail | |
| Check evolution slots | Preserved correctly | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 8. Loading Saved Deck ✓
**Requirement**: 6.1, 6.3

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Navigate to "Saved Decks" | List of saved decks shows | ⬜ Pass ⬜ Fail | |
| Click "Load Deck" on a deck | Navigates to Deck Builder | ⬜ Pass ⬜ Fail | |
| Check deck slots | All 8 cards loaded correctly | ⬜ Pass ⬜ Fail | |
| Check evolution slots | Evolution status restored | ⬜ Pass ⬜ Fail | |
| Check average elixir | Displays correctly | ⬜ Pass ⬜ Fail | |
| Check notification | "Loaded deck: [name]" | ⬜ Pass ⬜ Fail | |
| Build different deck | Previous deck replaced | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 9. Renaming Deck ✓
**Requirement**: 6.6, 6.7

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Navigate to "Saved Decks" | Decks list shows | ⬜ Pass ⬜ Fail | |
| Click "Rename" on a deck | Inline input appears | ⬜ Pass ⬜ Fail | |
| Check input value | Pre-filled with current name | ⬜ Pass ⬜ Fail | |
| Type "Updated Deck Name" | Input updates | ⬜ Pass ⬜ Fail | |
| Click save button (✓) | Name updates | ⬜ Pass ⬜ Fail | |
| Check notification | "Deck renamed successfully" | ⬜ Pass ⬜ Fail | |
| Click "Rename", press Escape | Edit cancelled | ⬜ Pass ⬜ Fail | |
| Click "Rename", press Enter | Name saved | ⬜ Pass ⬜ Fail | |
| Try to save empty name | Error: "Deck name cannot be empty" | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 10. Deleting Deck ✓
**Requirement**: 6.4, 6.5

| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Navigate to "Saved Decks" | Decks list shows | ⬜ Pass ⬜ Fail | |
| Click "Delete" on a deck | Confirmation dialog appears | ⬜ Pass ⬜ Fail | |
| Check confirmation message | "Delete this deck?" | ⬜ Pass ⬜ Fail | |
| Click "Cancel" | Dialog closes, deck remains | ⬜ Pass ⬜ Fail | |
| Click "Delete" again | Confirmation appears again | ⬜ Pass ⬜ Fail | |
| Click "Delete" in confirmation | Deck removed from list | ⬜ Pass ⬜ Fail | |
| Check notification | "Deck deleted successfully" | ⬜ Pass ⬜ Fail | |
| Refresh page | Deck still deleted | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 11. Error Scenarios ✓
**Requirement**: 9.1, 9.2, 9.3, 9.4, 9.5

#### 11.1 Backend Down
| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Stop backend server | - | ⬜ Done | |
| Refresh application | Error message appears | ⬜ Pass ⬜ Fail | |
| Check error message | "Cannot connect to server" | ⬜ Pass ⬜ Fail | |
| Check retry button | Button appears | ⬜ Pass ⬜ Fail | |
| Check application state | No crash, error boundary works | ⬜ Pass ⬜ Fail | |
| Start backend | - | ⬜ Done | |
| Click retry | Cards load successfully | ⬜ Pass ⬜ Fail | |

#### 11.2 Network Timeout
| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Simulate slow network (DevTools) | - | ⬜ Done | |
| Try to save deck | Loading spinner shows | ⬜ Pass ⬜ Fail | |
| Wait for timeout | Error: "Request timed out" | ⬜ Pass ⬜ Fail | |
| Check retry option | User can retry | ⬜ Pass ⬜ Fail | |

#### 11.3 Server Error (5xx)
| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Trigger 500 error (if possible) | - | ⬜ Done | |
| Observe error handling | Error notification displays | ⬜ Pass ⬜ Fail | |
| Check error message | "Server error, please try again" | ⬜ Pass ⬜ Fail | |
| Check application state | Remains functional | ⬜ Pass ⬜ Fail | |

#### 11.4 Client Error (4xx)
| Test Step | Expected Result | Status | Notes |
|-----------|----------------|--------|-------|
| Save 20 decks | - | ⬜ Done | |
| Try to save 21st deck | Error message from API | ⬜ Pass ⬜ Fail | |
| Check error notification | Specific error displays | ⬜ Pass ⬜ Fail | |
| Check retry option | User can correct and retry | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 12. Browser Compatibility ✓

#### Chrome
| Feature | Status | Notes |
|---------|--------|-------|
| Card display | ⬜ Pass ⬜ Fail | |
| Filters | ⬜ Pass ⬜ Fail | |
| Deck building | ⬜ Pass ⬜ Fail | |
| Save/Load | ⬜ Pass ⬜ Fail | |
| CSS rendering | ⬜ Pass ⬜ Fail | |
| Animations | ⬜ Pass ⬜ Fail | |
| Console errors | ⬜ None ⬜ Some | |

#### Firefox
| Feature | Status | Notes |
|---------|--------|-------|
| Card display | ⬜ Pass ⬜ Fail | |
| Filters | ⬜ Pass ⬜ Fail | |
| Deck building | ⬜ Pass ⬜ Fail | |
| Save/Load | ⬜ Pass ⬜ Fail | |
| CSS rendering | ⬜ Pass ⬜ Fail | |
| Animations | ⬜ Pass ⬜ Fail | |
| Console errors | ⬜ None ⬜ Some | |

#### Safari (if available)
| Feature | Status | Notes |
|---------|--------|-------|
| Card display | ⬜ Pass ⬜ Fail ⬜ N/A | |
| Filters | ⬜ Pass ⬜ Fail ⬜ N/A | |
| Deck building | ⬜ Pass ⬜ Fail ⬜ N/A | |
| Save/Load | ⬜ Pass ⬜ Fail ⬜ N/A | |
| CSS rendering | ⬜ Pass ⬜ Fail ⬜ N/A | |
| Animations | ⬜ Pass ⬜ Fail ⬜ N/A | |
| Console errors | ⬜ None ⬜ Some ⬜ N/A | |

**Overall**: ⬜ PASS ⬜ FAIL

---

### 13. Responsive Design ✓
**Requirement**: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6

#### Desktop (1920x1080)
| Feature | Expected | Status | Notes |
|---------|----------|--------|-------|
| Card gallery columns | 6 columns | ⬜ Pass ⬜ Fail | |
| Deck slots layout | 2 rows of 4 | ⬜ Pass ⬜ Fail | |
| All controls visible | Yes | ⬜ Pass ⬜ Fail | |
| Filters layout | Sidebar or top | ⬜ Pass ⬜ Fail | |
| Navigation | Accessible | ⬜ Pass ⬜ Fail | |

#### Tablet (768x1024)
| Feature | Expected | Status | Notes |
|---------|----------|--------|-------|
| Card gallery columns | 4 columns | ⬜ Pass ⬜ Fail | |
| Deck slots layout | 2 rows of 4 | ⬜ Pass ⬜ Fail | |
| Navigation | Accessible | ⬜ Pass ⬜ Fail | |
| Touch interactions | Work correctly | ⬜ Pass ⬜ Fail | |
| Filters | Stack or collapse | ⬜ Pass ⬜ Fail | |

#### Mobile (375x667)
| Feature | Expected | Status | Notes |
|---------|----------|--------|-------|
| Card gallery columns | 2 columns | ⬜ Pass ⬜ Fail | |
| Deck slots layout | Stack or 2x4 | ⬜ Pass ⬜ Fail | |
| Filters | Stack vertically | ⬜ Pass ⬜ Fail | |
| Touch targets | ≥ 44x44px | ⬜ Pass ⬜ Fail | |
| Horizontal scroll | None | ⬜ Pass ⬜ Fail | |
| Text readability | Clear | ⬜ Pass ⬜ Fail | |
| Navigation | Accessible | ⬜ Pass ⬜ Fail | |

**Overall**: ⬜ PASS ⬜ FAIL

---

## Test Summary

| Category | Status | Pass Rate |
|----------|--------|-----------|
| 1. Card Fetch and Display | ⬜ PASS ⬜ FAIL | ___/6 |
| 2. Filter Combinations | ⬜ PASS ⬜ FAIL | ___/11 |
| 3. Adding Cards to Deck | ⬜ PASS ⬜ FAIL | ___/7 |
| 4. Removing Cards | ⬜ PASS ⬜ FAIL | ___/7 |
| 5. Evolution Slots | ⬜ PASS ⬜ FAIL | ___/8 |
| 6. Average Elixir | ⬜ PASS ⬜ FAIL | ___/6 |
| 7. Saving Deck | ⬜ PASS ⬜ FAIL | ___/9 |
| 8. Loading Deck | ⬜ PASS ⬜ FAIL | ___/7 |
| 9. Renaming Deck | ⬜ PASS ⬜ FAIL | ___/9 |
| 10. Deleting Deck | ⬜ PASS ⬜ FAIL | ___/8 |
| 11. Error Scenarios | ⬜ PASS ⬜ FAIL | ___/15 |
| 12. Browser Compatibility | ⬜ PASS ⬜ FAIL | ___/21 |
| 13. Responsive Design | ⬜ PASS ⬜ FAIL | ___/16 |

**Total Tests**: 130  
**Passed**: _____  
**Failed**: _____  
**Pass Rate**: _____%

---

## Issues Found

| # | Category | Description | Severity | Status |
|---|----------|-------------|----------|--------|
| 1 | | | ⬜ Critical ⬜ High ⬜ Medium ⬜ Low | ⬜ Open ⬜ Fixed |
| 2 | | | ⬜ Critical ⬜ High ⬜ Medium ⬜ Low | ⬜ Open ⬜ Fixed |
| 3 | | | ⬜ Critical ⬜ High ⬜ Medium ⬜ Low | ⬜ Open ⬜ Fixed |

---

## Sign-off

**Tester**: ________________  
**Date**: ________________  
**Overall Result**: ⬜ PASS ⬜ FAIL  

**Notes**:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
