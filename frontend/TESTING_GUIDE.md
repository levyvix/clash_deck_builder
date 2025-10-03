# Testing Guide - Clash Royale Deck Builder

## Overview
This document provides comprehensive testing instructions for Task 15: Final Integration and Testing. It covers automated tests, manual testing procedures, and verification of all requirements.

---

## Quick Start

### 1. Start the Backend
```bash
cd backend
uv run uvicorn src.main:app --reload
```
Verify backend is running: http://localhost:8000/health

### 2. Start the Frontend
```bash
cd frontend
npm start
```
Application opens at: http://localhost:3000

### 3. Run Automated Tests (Optional)
```bash
cd frontend
npm test -- --watchAll=false
```

---

## Testing Documents

### 1. INTEGRATION_TEST_REPORT.md
- Comprehensive test plan with all 13 test categories
- Detailed expected results for each test case
- Status tracking for test execution
- Known issues log
- Test summary and next steps

### 2. MANUAL_TEST_CHECKLIST.md
- Step-by-step manual testing checklist
- 130+ individual test cases
- Pass/fail checkboxes for each test
- Space for notes and observations
- Issues tracking table
- Sign-off section

### 3. integration.test.tsx
- Automated unit and integration tests
- Tests for all major components
- Mock API responses
- Error scenario testing

---

## Test Categories

### ✅ 1. Card Fetch and Display
**What to test**:
- Cards load from API
- Images display correctly
- Card details (name, elixir, rarity) visible
- Rarity colors applied correctly
- Loading states
- Error handling

**How to test**:
1. Open application
2. Observe loading spinner
3. Wait for cards to load
4. Verify all cards display with images
5. Check rarity color coding
6. Test image fallback by breaking an image URL

---

### ✅ 2. Filter Combinations
**What to test**:
- Name filter (case-insensitive)
- Elixir cost filter
- Rarity filter
- Type filter
- Multiple filters combined (AND logic)
- Clear filters functionality
- Active filter count badge
- "No cards found" message

**How to test**:
1. Test each filter individually
2. Combine multiple filters
3. Verify AND logic (all filters must match)
4. Test edge cases (no matches)
5. Verify clear filters resets all
6. Check filter count badge updates

---

### ✅ 3. Adding 8 Cards to Deck
**What to test**:
- Cards add to first empty slot
- Maximum 8 cards enforced
- Visual feedback on add
- Average elixir updates
- Error message when deck full

**How to test**:
1. Click on cards in gallery
2. Click "Add to Deck"
3. Verify cards fill slots 1-8 in order
4. Try to add 9th card
5. Verify error message
6. Check average elixir updates

---

### ✅ 4. Removing Cards from Deck
**What to test**:
- Click deck slot shows options
- Remove card clears slot
- Empty slot visual (dashed border, + icon)
- Average elixir recalculates
- New cards fill first empty slot
- Evolution status cleared on remove

**How to test**:
1. Build full deck
2. Click on a deck slot
3. Click "Remove from Deck"
4. Verify slot shows empty state
5. Add new card, verify it fills empty slot
6. Remove evolution card, verify status cleared

---

### ✅ 5. Evolution Slot Management
**What to test**:
- Toggle evolution shows evolution image
- Evolution badge (⭐) appears
- Maximum 2 evolutions enforced
- Can untoggle evolution
- Error message when limit reached

**How to test**:
1. Build full deck
2. Toggle evolution on slot 1
3. Toggle evolution on slot 2
4. Try to toggle slot 3 (should fail)
5. Untoggle slot 1
6. Toggle slot 3 (should work now)

---

### ✅ 6. Average Elixir Calculation
**What to test**:
- Empty deck: 0.0
- Correct calculation for various combinations
- Rounded to 1 decimal place
- Updates in real-time
- Format: X.X (e.g., "4.3")

**Test cases**:
- Empty: 0.0
- 1 card (3 elixir): 3.0
- 2 cards (3, 5): 4.0
- 8 cards (2,3,3,4,4,5,6,7): 4.3

---

### ✅ 7. Saving Deck
**What to test**:
- Save button disabled until 8 cards
- Name prompt appears
- Deck saves via API
- Success notification
- Deck appears in saved decks
- Evolution slots preserved
- Average elixir saved

**How to test**:
1. Build deck with < 8 cards, verify button disabled
2. Complete deck to 8 cards
3. Click "Save Deck"
4. Enter name "Test Deck 1"
5. Verify success notification
6. Navigate to Saved Decks
7. Verify deck appears with correct details

---

### ✅ 8. Loading Saved Deck
**What to test**:
- Click "Load Deck" navigates to builder
- All 8 cards loaded correctly
- Evolution slots restored
- Average elixir correct
- Success notification
- Current deck replaced

**How to test**:
1. Navigate to Saved Decks
2. Click "Load Deck" on a deck
3. Verify navigation to builder
4. Verify all cards loaded
5. Verify evolution slots
6. Check notification

---

### ✅ 9. Renaming Deck
**What to test**:
- Inline input appears
- Pre-filled with current name
- Save button updates name
- Cancel button discards changes
- Enter key saves
- Escape key cancels
- Empty name validation

**How to test**:
1. Navigate to Saved Decks
2. Click "Rename"
3. Type new name
4. Click save (✓)
5. Verify name updates
6. Test Enter and Escape keys
7. Try to save empty name

---

### ✅ 10. Deleting Deck
**What to test**:
- Confirmation dialog appears
- Cancel keeps deck
- Delete removes deck
- Success notification
- Deck removed from list

**How to test**:
1. Navigate to Saved Decks
2. Click "Delete"
3. Verify confirmation dialog
4. Click "Cancel", verify deck remains
5. Click "Delete" again
6. Click "Delete" in confirmation
7. Verify deck removed

---

### ✅ 11. Error Scenarios
**What to test**:
- Backend down: "Cannot connect to server"
- Network timeout: "Request timed out"
- Server error (5xx): "Server error, please try again"
- Client error (4xx): Specific error message
- Error boundaries catch component errors
- Retry functionality works

**How to test**:
1. Stop backend, refresh app
2. Simulate slow network in DevTools
3. Trigger various error conditions
4. Verify error messages
5. Test retry functionality
6. Verify app doesn't crash

---

### ✅ 12. Browser Compatibility
**What to test**:
- Chrome: All features work
- Firefox: All features work
- Safari: All features work (if available)
- CSS renders consistently
- No console errors
- Animations smooth

**How to test**:
1. Open app in each browser
2. Perform basic operations
3. Check console for errors
4. Verify CSS rendering
5. Test animations

---

### ✅ 13. Responsive Design
**What to test**:
- Desktop (>1200px): 6 column grid, 2x4 deck slots
- Tablet (768-1200px): 4 column grid, 2x4 deck slots
- Mobile (<768px): 2 column grid, stacked layout
- Touch targets ≥ 44x44px
- No horizontal scrolling
- Text remains readable

**How to test**:
1. Open DevTools responsive mode
2. Test at 1920x1080 (desktop)
3. Test at 768x1024 (tablet)
4. Test at 375x667 (mobile)
5. Verify layouts adjust correctly
6. Test touch interactions

---

## Automated Testing

### Running Tests
```bash
cd frontend
npm test -- --watchAll=false
```

### Test Coverage
The automated tests cover:
- Component rendering
- User interactions
- API integration (mocked)
- Error handling
- State management
- Filter logic
- Calculations

### Test Files
- `src/tests/integration.test.tsx` - Main integration tests
- `src/App.test.tsx` - App component tests (if exists)
- `src/components/*.test.tsx` - Component-specific tests (if exist)

---

## Manual Testing

### Prerequisites
1. Backend running on port 8000
2. Frontend running on port 3000
3. Database populated with card data
4. Clean browser cache

### Testing Process
1. Print or open `MANUAL_TEST_CHECKLIST.md`
2. Follow each test case in order
3. Check off completed items
4. Document any failures
5. Take screenshots of issues
6. Fill in the issues table
7. Calculate pass rate
8. Sign off when complete

### Tips
- Test in a clean browser session
- Clear localStorage between major tests
- Use browser DevTools to inspect network requests
- Check console for errors
- Test edge cases and error conditions
- Verify data persistence (refresh page)

---

## Verification Checklist

### Before Testing
- [ ] Backend is running and healthy
- [ ] Frontend is running
- [ ] Database has card data
- [ ] Browser cache cleared
- [ ] DevTools open for debugging

### During Testing
- [ ] Follow test cases in order
- [ ] Document all failures
- [ ] Take screenshots of issues
- [ ] Note any unexpected behavior
- [ ] Test edge cases
- [ ] Verify error messages

### After Testing
- [ ] All test cases executed
- [ ] Pass/fail status recorded
- [ ] Issues documented
- [ ] Screenshots attached
- [ ] Pass rate calculated
- [ ] Sign-off completed

---

## Common Issues and Solutions

### Issue: Cards not loading
**Solution**: 
- Check backend is running
- Verify API endpoint in .env
- Check browser console for errors
- Verify CORS settings

### Issue: Images not displaying
**Solution**:
- Check image URLs in database
- Verify external CDN is accessible
- Test fallback placeholder

### Issue: Filters not working
**Solution**:
- Check filter state updates
- Verify filter logic (AND vs OR)
- Test debounce timing (300ms)

### Issue: Deck not saving
**Solution**:
- Verify 8 cards in deck
- Check backend API response
- Verify database connection
- Check for validation errors

### Issue: Responsive layout broken
**Solution**:
- Check CSS media queries
- Verify viewport meta tag
- Test in different browsers
- Check for CSS conflicts

---

## Performance Testing

### Metrics to Check
- Initial load time: < 2 seconds
- Card gallery render: < 500ms
- Filter response: < 300ms (debounced)
- Deck save: < 1 second
- Navigation: < 200ms

### Tools
- Chrome DevTools Performance tab
- Lighthouse audit
- Network tab for API calls
- React DevTools Profiler

---

## Accessibility Testing

### Checklist
- [ ] Keyboard navigation works
- [ ] Tab order is logical
- [ ] ARIA labels present
- [ ] Screen reader compatible
- [ ] Color contrast sufficient
- [ ] Focus indicators visible
- [ ] Error messages announced

### Tools
- Chrome DevTools Accessibility tab
- axe DevTools extension
- WAVE browser extension
- Screen reader (NVDA, JAWS, VoiceOver)

---

## Security Testing

### Checklist
- [ ] No sensitive data in console
- [ ] API keys not exposed
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Input validation
- [ ] SQL injection prevention (backend)

---

## Completion Criteria

Task 15 is complete when:
- [ ] All 130+ manual test cases pass
- [ ] Automated tests pass
- [ ] No critical or high severity bugs
- [ ] All requirements verified
- [ ] Browser compatibility confirmed
- [ ] Responsive design verified
- [ ] Error handling tested
- [ ] Performance acceptable
- [ ] Accessibility verified
- [ ] Documentation complete

---

## Next Steps After Testing

1. **If all tests pass**:
   - Mark task 15 as complete
   - Update task status in tasks.md
   - Document any minor issues for future improvement
   - Celebrate! 🎉

2. **If tests fail**:
   - Document all failures
   - Prioritize by severity
   - Fix critical issues first
   - Re-test after fixes
   - Repeat until all tests pass

3. **Final steps**:
   - Update INTEGRATION_TEST_REPORT.md with results
   - Archive test artifacts
   - Prepare for deployment
   - Update project documentation

---

## Contact

For questions or issues during testing:
- Check project README.md
- Review component documentation
- Check API documentation in docs/api.md
- Review error handling guide in ERROR_HANDLING.md

---

**Last Updated**: January 10, 2025  
**Version**: 1.0  
**Status**: Ready for Testing
