# Implementation Plan

- [x] 1. Add Material Design CSS variables and base styles





  - Create or update `frontend/src/styles/material-design.css` with elevation shadows, motion curves, durations, and spacing variables
  - Import material design styles in `frontend/src/index.css`
  - Update button styles to use Material Design patterns (contained, outlined, text)
  - Add ripple effect styles for interactive elements
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Fix rarity text clipping and update elixir icon







  - Update `frontend/src/styles/CardDisplay.css` to reduce rarity font size to 0.75rem
  - Add text overflow handling (ellipsis, max-width) for rarity text
  - Replace lightning icon (⚡) with droplet icon (💧) in `frontend/src/components/CardDisplay.tsx`
  - Test rarity text display for all rarity types (Common, Rare, Epic, Legendary, Champion)
  - _Requirements: 1.6, 1.7_

- [x] 3. Implement duplicate card prevention logic




  - Add `cardsInDeck: Set<number>` state to `frontend/src/components/DeckBuilder.tsx`
  - Update `addCardToDeck` function to check if card ID exists in `cardsInDeck` set
  - Show notification "Card already in deck" when attempting to add duplicate
  - Update `removeCardFromDeck` function to remove card ID from `cardsInDeck` set
  - Pass `cardsInDeck` set to CardGallery component
  - _Requirements: 3.1, 3.4, 3.5_

- [x] 4. Add visual feedback for cards in deck





  - Update `frontend/src/components/CardDisplay.tsx` to accept `inDeck` and `disabled` props
  - Add CSS class `.card-display--in-deck` with opacity 0.5 and pointer-events none
  - Add "✓ In Deck" overlay badge using ::after pseudo-element
  - Update `frontend/src/components/CardGallery.tsx` to pass `inDeck={cardsInDeck.has(card.id)}` to each CardDisplay
  - _Requirements: 3.2, 3.3_

- [x] 5. Implement drag and drop for gallery cards




  - Add `draggable={true}` attribute to CardDisplay component when rendered in gallery
  - Implement `handleDragStart` in CardDisplay to set drag data with card ID and source type 'gallery'
  - Create ghost element for drag preview using `setDragImage`
  - Add `dragging` CSS class during drag operation
  - Implement `handleDragEnd` to remove dragging class
  - _Requirements: 2.1, 2.7_
-

- [x] 6. Implement drop zones in deck slots




  - Update `frontend/src/components/DeckSlot.tsx` to handle `onDragOver`, `onDragLeave`, and `onDrop` events
  - Add `drag-over` CSS class to highlight valid drop targets
  - Implement drop handler to parse drag data and call `onAddCardToSlot` callback
  - Add visual feedback (border highlight) when dragging over empty slot
  - _Requirements: 2.2, 2.3_

- [x] 7. Implement drag from deck slots





  - Make DeckSlot draggable when it contains a card
  - Implement `handleDragStart` in DeckSlot to set drag data with card ID, source type 'deck', and slot index
  - Implement card swapping logic when dropping deck card on another deck slot
  - _Requirements: 2.4, 2.6_

- [x] 8. Create remove drop zone





  - Create `frontend/src/components/RemoveDropZone.tsx` component
  - Position drop zone outside deck area (below or to the side)
  - Implement drop handler to remove card from deck when dropped
  - Add visual feedback (trash icon, highlight on drag over)
  - Add fade-out animation when card is removed
  - _Requirements: 2.5_

- [x] 9. Add smooth animations for card operations





  - Create `frontend/src/styles/animations.css` with keyframe animations
  - Implement `cardAddToDeck` animation (scale + fade-in, 300ms)
  - Implement `cardRemoveFromDeck` animation (scale + fade-out, 300ms)
  - Add animation classes to DeckSlot when cards are added/removed
  - Use animation state management (entering/leaving classes)
  - _Requirements: 7.1, 7.2_


- [x] 10. Add hover and transition animations




  - Update CardDisplay hover styles with elevation change and translateY
  - Add transition properties (box-shadow, transform) with 200ms duration
  - Implement staggered fade-in for gallery cards when filters change
  - Add shimmer animation for skeleton loaders
  - _Requirements: 7.3, 7.4, 7.8_

- [x] 11. Add notification animations





  - Update `frontend/src/styles/Notification.css` with slide-in/slide-out animations
  - Implement `slideInRight` keyframe (250ms)
  - Implement `slideOutRight` keyframe (250ms)
  - Add entering/leaving classes to notification component
  - _Requirements: 7.5, 7.6_


- [x] 12. Add save button pulse animation



  - Create pulse animation keyframe in animations.css
  - Add `.save-button--ready` class when deck has 8 cards
  - Implement pulse animation (2s infinite) with scale and shadow changes
  - _Requirements: 7.7_

- [x] 13. Debug and fix API endpoint configuration




  - Add console.log to verify `REACT_APP_API_BASE_URL` in `frontend/src/services/api.ts`
  - Create `verifyEndpoints` function to test all API endpoints
  - Call `verifyEndpoints` on app initialization for debugging
  - Check `.env` files to ensure correct API base URL
  - Test API calls in browser network tab to see actual URLs being called
  - _Requirements: 4.5, 5.4, 8.1, 8.6_

- [x] 14. Fix save deck API payload format





  - Update `createDeck` function in `frontend/src/services/api.ts` to match backend expected format
  - Ensure payload has `name` (string) and `cards` (array of objects with `card_id` and `is_evolution`)
  - Add console.log to show payload before sending
  - Verify Content-Type header is set to application/json
  - Test save deck functionality and verify 201 response
  - _Requirements: 4.1, 4.2, 8.2, 8.5_

- [x] 15. Fix save deck success handling




  - Update DeckBuilder to show success notification "Deck saved successfully" on 201 response
  - Clear deck or keep current deck based on UX decision
  - Refresh saved decks list after successful save
  - _Requirements: 4.3, 4.7_

- [x] 16. Fix save deck error handling






  - Add specific error handling for 404 responses (endpoint not found)
  - Add error handling for validation errors (400) with specific message display
  - Add error handling for network errors with "Cannot connect to server" message
  - Test error scenarios and verify user-friendly messages
  - _Requirements: 4.4, 4.5, 4.6, 8.3, 8.4_

- [x] 17. Fix saved decks page API call







  - Verify `fetchDecks` function in `frontend/src/services/api.ts` calls correct endpoint (GET /decks)
  - Add console.log to show full request URL
  - Test endpoint in browser or Postman to verify backend is responding
  - _Requirements: 5.1, 8.5_

- [x] 18. Fix saved decks page error handling

  - Update SavedDecks component to handle 404 errors with specific message
  - Implement retry button functionality to re-fetch decks
  - Show "Cannot connect to server" for network errors
  - Show "No saved decks yet" when response is empty array
  - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6_


- [x] 19. Create frontend Dockerfile




  - Create `frontend/Dockerfile` with multi-stage build (node build stage + nginx serve stage)
  - Install dependencies with `npm ci` in build stage
  - Run `npm run build` to create production build
  - Copy build output to nginx html directory in production stage
  - Add EXPOSE 80 directive
  - _Requirements: 6.1, 6.2, 6.3, 6.4_
-

- [x] 20. Create nginx configuration for frontend

  - Create `frontend/nginx.conf` with SPA routing (serve index.html for all routes)
  - Add gzip compression configuration
  - Add static asset caching headers
  - Configure proxy for /api/ requests to backend service
  - _Requirements: 6.5_

- [x] 21. Create frontend .dockerignore file

  - Create `frontend/.dockerignore` to exclude node_modules, build, .git, .env.local
  - Add other unnecessary files (coverage, .vscode, README.md)
  - _Requirements: 6.8_

- [x] 22. Add frontend service to docker-compose




  - Update `docker-compose.yml` to add frontend service
  - Configure build context and dockerfile path
  - Map port 3000:80 for frontend access
  - Add environment variable for REACT_APP_API_BASE_URL
  - Add depends_on backend service
  - Configure networking to connect frontend and backend


  - _Requirements: 6.5, 6.6_



- [x] 23. Implement runtime environment variable support

  - Create `frontend/public/env-config.js` template for runtime env vars
  - Update `frontend/public/index.html` to include env-config.js script
  - Create `frontend/src/config.ts` to read from window.ENV or process.env
  - Update api.ts to use config.ts for API_BASE_URL
  - _Requirements: 6.7_

- [x] 24. Add health check to frontend Dockerfile


  - Add HEALTHCHECK directive to Dockerfile
  - Configure health check to wget localhost every 30s
  - Set timeout, start-period, and retries
  - _Requirements: 6.4_

- [x] 25. Test Docker build and run




  - Build frontend Docker image locally
  - Run frontend container and verify it starts
  - Test accessing frontend on configured port
  - Verify frontend can connect to backend API
  - Test with docker-compose up to ensure all services work together
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 26. Implement filter sorting controls









  - Add SortConfig interface and state management to `frontend/src/components/DeckBuilder.tsx`
  - Create SortControls component with ascending/descending buttons for name, elixir, rarity, arena
  - Implement sortCards function with proper handling for numeric, string, and rarity hierarchy sorting
  - Add sort icons (↑↓) and active state styling for sort buttons
  - Integrate sort controls with existing filter system
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 27. Fix saved decks visual contrast








  - Update `frontend/src/styles/SavedDecks.css` with high contrast colors
  - Set deck names to dark gray (#212121) for visibility
  - Set elixir cost to blue (#1976d2) and card count to green (#388e3
  - Add proper hover states that maintain text visibility
  - Test color contrast ratios meet accessibility standards
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 28. Fix card selection animation glitches









  - Add AnimationState interface and state management to DeckBuilder
  - Implement addCardWithAnimation function that prevents multiple animations on same card
  - Update card animation CSS to prevent flickering (remove default transitions)
  - Add animation state cleanup after animation completes
  - Test that cards don't disappear during selection and timing is consistent
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 29. Fix card opacity issues








  - Implement replaceCardInSlot function that clears animation states
  - Add getCardOpacity function that ensures full opacity unless explicitly animating
  - Update card rendering to use dynamic opacity calculation
  - Test that replaced cards display with full opacity immediately
  - Verify opacity states are properly managed during card swaps
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 30. Implement evolution card detection









  - Create EVOLUTION_CAPABLE_CARDS set or integrate with API data
  - Add canCardEvolve function to check evolution capability
  - Update DeckSlot component to conditionally show evolution toggle
  - Extend Card interface to include can_evolve field if available from API
  - Test that evolution toggle only appears for evolution-capable cards
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
-

- [x] 31. Implement automatic evolution for first two slots








  - Create updateEvolutionStates function that auto-marks first two slots as evolution
  - Update addCardToSlot function to call updateEvolutionStates
  - Update swapCards function to recalculate evolution states after swap
  - Modify drag and drop handlers to trigger evolution state updates
  - Test that cards in positions 1-2 are automatically marked as evolution if capable
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

- [x] 32. Add blue outline styling to deck slots










  - Update `frontend/src/styles/DeckSlot.css` with blue outline for empty slots
  - Add drag-over state with darker blue and glow effect
  - Add subtle blue outline for filled slots
  - Add green outline when deck is complete
  - Implement getDeckSlotClasses function for dynamic class application
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 33. Update page title and HTML head metadata









  - Update `frontend/public/index.html` to set title as "Clash Royale Deck Builder"
  - Add proper meta description for SEO
  - Add Open Graph meta tags for social sharing
  - Update manifest.json with correct app name and description
  - _Requirements: 16.1, 16.4_

- [x] 34. Create and implement Clash Royale themed favicon









  - Create or source Clash Royale themed favicon in ICO format (16x16, 32x32, 48x48)
  - Create PNG icons for mobile (192x192, 512x512)
  - Replace default favicon.ico in `frontend/public/` directory
  - Add apple-touch-icon link in HTML head
  - Update manifest.json with new icon paths
  - _Requirements: 16.2, 16.3_

- [ ] 35. Implement dynamic page title management




  - Create `frontend/src/hooks/useDocumentTitle.ts` hook for title management
  - Update DeckBuilder component to set title "Clash Royale Deck Builder"
  - Update SavedDecks component to set title "Saved Decks - Clash Royale Deck Builder"
  - Test that browser tab titles update correctly when navigating
  - _Requirements: 16.1, 16.4_

- [x] 36. Filter out 0 elixir cards from API data










  - Update `frontend/src/services/api.ts` fetchCards function to filter elixir_cost > 0
  - Create processCardData function to handle card filtering
  - Add console logging to show how many cards were filtered out
  - Test that 0 elixir cards don't appear in card gallery
  - _Requirements: 17.1, 17.4_

- [ ] 37. Update card filters to exclude 0 elixir range




  - Update `frontend/src/components/CardFilters.tsx` to set minimum elixir to 1
  - Calculate minElixir from filtered cards (excluding 0)
  - Update elixir range slider to start from 1 instead of 0
  - Update filter state initialization to use elixirMin: 1
  - _Requirements: 17.2, 17.3_

- [ ] 38. Add card validation and safety filtering




  - Create `frontend/src/utils/cardValidation.ts` with validateCard and filterValidCards functions
  - Add client-side validation to ensure elixir_cost is between 1-10
  - Add validation for required fields (id, name, rarity, image_url)
  - Implement safety filtering in CardGallery component as backup
  - Add error logging for invalid cards
  - _Requirements: 17.4, 17.5_
