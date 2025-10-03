# Implementation Plan

- [x] 1. Setup project dependencies and structure





  - Install required npm packages if missing (react-router-dom, typescript types)
  - Create types directory and index.ts with all TypeScript interfaces
  - Create styles directory with variables.css for CSS custom properties
  - Verify .env file has REACT_APP_API_BASE_URL configured
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 2. Implement shared TypeScript types




  - Create types/index.ts with Card, DeckSlot, Deck, FilterState, Notification interfaces
  - Export all types for use across components
  - _Requirements: 10.1_

- [x] 3. Create utility functions for deck calculations




  - Create services/deckCalculations.ts file
  - Implement calculateAverageElixir function with rounding to 1 decimal
  - Implement canAddEvolution function to check evolution limit
  - Implement isDeckComplete function to validate 8 cards
  - Implement getEmptySlotIndex function to find next empty slot
  - _Requirements: 3.6, 3.7, 4.6_

- [x] 4. Implement CSS variables and base styles





  - Create styles/variables.css with color, spacing, typography, and border variables
  - Define rarity colors (Common: gray, Rare: orange, Epic: purple, Legendary: gold, Champion: gold)
  - Define responsive breakpoints
  - _Requirements: 7.3, 7.1, 7.2_
-

- [x] 5. Build CardDisplay component with styling




  - Create CardDisplay.tsx with props for card, isEvolution, onClick, showOptions, onAddToDeck, onRemoveFromDeck, inDeck
  - Display card image (use evolution image if isEvolution is true)
  - Show card name, elixir cost, and rarity
  - Implement image error handling with fallback placeholder
  - Create styles/CardDisplay.css with rarity-based color classes
  - Add hover and click animations
  - Show action buttons (Add to Deck / Remove from Deck) when showOptions is true
  - _Requirements: 1.3, 1.4, 7.3_

- [x] 6. Build CardGallery component with grid layout




  - Create CardGallery.tsx with props for cards, filters, onCardClick, selectedCard, onAddToDeck
  - Implement card filtering logic (name, elixir cost, rarity, type)
  - Display filtered cards in CSS Grid layout
  - Create styles/CardGallery.css with responsive grid (6 cols desktop, 4 tablet, 2 mobile)
  - Show "No cards found" message when filters return empty
  - Display loading skeleton while fetching cards
  - Show action menu overlay when card is clicked
  - _Requirements: 1.2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 7.1, 7.2_
- [x] 7. Build CardFilters component




- [ ] 7. Build CardFilters component

  - Create CardFilters.tsx with props for filters, onFilterChange, onClearFilters
  - Implement text input for name search with 300ms debounce
  - Implement dropdown for elixir cost (0-10, "All")
  - Implement dropdown for rarity (All, Common, Rare, Epic, Legendary, Champion)
  - Implement dropdown for type (All, Troop, Spell, Building)
  - Add clear filters button
  - Show active filter count badge
  - Disable clear button when no filters active
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 8. Build DeckSlot component




  - Create DeckSlot.tsx with props for slot, slotIndex, onCardClick, onRemoveCard, onToggleEvolution, canAddEvolution, showOptions
  - Display card if slot is filled, otherwise show empty slot placeholder with dashed border
  - Show evolution badge/star icon if isEvolution is true
  - Implement click handler to show options menu
  - Show options: Remove from Deck, Toggle Evolution (disabled if evolution limit reached)
  - Create styles/DeckSlot.css with fixed size (100px x 140px)
  - Style empty slots with dashed border and "+" icon
  - _Requirements: 3.2, 3.4, 3.5, 3.10, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
-

- [x] 9. Build Notification component




  - Create Notification.tsx with props for notifications array and onDismiss
  - Display notifications in top-right corner stacked vertically
  - Implement auto-dismiss after 3 seconds
  - Add manual dismiss button (X)
  - Apply color coding by type (success: green, error: red, info: blue)
  - Create styles/Notification.css with positioning and animations
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 10. Enhance DeckBuilder component with full functionality




  - Update DeckBuilder.tsx to use DeckSlot array (8 slots initialized as empty)
  - Implement state for currentDeck, cards, filters, loading, error, selectedGalleryCard, selectedDeckSlot
  - Fetch cards from API on component mount using fetchCards
  - Implement addCardToDeck function to find first empty slot and add card
  - Implement removeCardFromDeck function to clear slot
  - Implement toggleEvolution function with 2-evolution limit check
  - Calculate and display average elixir in real-time
  - Implement saveDeck function with validation (must have 8 cards)
  - Create styles/DeckBuilder.css with layout (deck slots in 2 rows of 4, stats section, card gallery)
  - Display loading state while fetching cards
  - Display error state if fetch fails
  - Show success/error notifications for user actions
  - _Requirements: 1.1, 1.5, 1.6, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 9.1, 9.3, 9.4_




- [ ] 11. Enhance SavedDecks component

  - Update SavedDecks.tsx to display decks in grid/list layout
  - Show deck name, 8 card thumbnails, and average elixir for each deck
  - Implement click handler to load deck into builder
  - Implement inline rename with save/cancel buttons
  - Implement delete with confirmation dialog
  - Show "No saved decks" message when empty
  - Fetch decks from API on component mount



  - Display loading state while fetching
  - Display error state if fetch fails
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 9.1_

- [ ] 12. Enhance App component with global state and routing

  - Update App.tsx to manage savedDecks and notifications state
  - Implement addNotification function with auto-dismiss after 3 seconds
  - Implement loadDeckIntoBuilder function to set currentDeck from saved deck

  - Pass currentDeck state to DeckBuilder via props
  - Pass notifications to Notification component
  - Ensure routing works correctly between "/" and "/saved-decks"
  - Update App.css with global styles and layout
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2_


- [x] 13. Implement error handling across all components


  - Add try-catch blocks around all API calls
  - Display user-friendly error messages for network failures ("Cannot connect to server")
  - Display error messages for 4xx responses (use response message)
  - Display error messages for 5xx responses ("Server error, please try again")
  - Display timeout error messages ("Request timed out")
  - Add error boundaries for component-level errors
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_



- [x] 14. Add responsive design and polish



  - Test and adjust responsive breakpoints (1200px, 768px, 480px)
  - Verify card gallery grid adjusts correctly on different screen sizes
  - Ensure deck builder layout works on mobile (stack vertically if needed)
  - Test all interactions on touch devices
  - Add loading spinners/skeletons for better UX
  - Verify all rarity colors display correctly
  - Test image loading and fallback behavior
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_





- [ ] 15. Final integration and testing

  - Verify cards fetch and display correctly with images
  - Test all filter combinations work correctly
  - Test adding 8 cards to deck and enforcing limit
  - Test removing cards from deck leaves empty slots
  - Test marking 2 evolution slots and enforcing limit
  - Test average elixir calculation with various card combinations
  - Test saving deck with valid name
  - Test loading saved deck into builder
  - Test renaming deck
  - Test deleting deck with confirmation
  - Test error scenarios (backend down, network failure)
  - Test on multiple browsers (Chrome, Firefox, Safari)
  - Verify responsive behavior on mobile, tablet, desktop
  - _Requirements: All requirements_
