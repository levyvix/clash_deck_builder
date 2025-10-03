# Implementation Plan

- [x] 1. Add Material Design CSS variables and base styles




  - Create or update `frontend/src/styles/material-design.css` with elevation shadows, motion curves, durations, and spacing variables
  - Import material design styles in `frontend/src/index.css`
  - Update button styles to use Material Design patterns (contained, outlined, text)
  - Add ripple effect styles for interactive elements
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 2. Fix rarity text clipping and update elixir icon


  - Update `frontend/src/styles/CardDisplay.css` to reduce rarity font size to 0.75rem
  - Add text overflow handling (ellipsis, max-width) for rarity text
  - Replace lightning icon (⚡) with droplet icon (💧) in `frontend/src/components/CardDisplay.tsx`
  - Test rarity text display for all rarity types (Common, Rare, Epic, Legendary, Champion)
  - _Requirements: 1.6, 1.7_

- [ ] 3. Implement duplicate card prevention logic
  - Add `cardsInDeck: Set<number>` state to `frontend/src/components/DeckBuilder.tsx`
  - Update `addCardToDeck` function to check if card ID exists in `cardsInDeck` set
  - Show notification "Card already in deck" when attempting to add duplicate
  - Update `removeCardFromDeck` function to remove card ID from `cardsInDeck` set
  - Pass `cardsInDeck` set to CardGallery component
  - _Requirements: 3.1, 3.4, 3.5_

- [ ] 4. Add visual feedback for cards in deck
  - Update `frontend/src/components/CardDisplay.tsx` to accept `inDeck` and `disabled` props
  - Add CSS class `.card-display--in-deck` with opacity 0.5 and pointer-events none
  - Add "✓ In Deck" overlay badge using ::after pseudo-element
  - Update `frontend/src/components/CardGallery.tsx` to pass `inDeck={cardsInDeck.has(card.id)}` to each CardDisplay
  - _Requirements: 3.2, 3.3_

- [ ] 5. Implement drag and drop for gallery cards
  - Add `draggable={true}` attribute to CardDisplay component when rendered in gallery
  - Implement `handleDragStart` in CardDisplay to set drag data with card ID and source type 'gallery'
  - Create ghost element for drag preview using `setDragImage`
  - Add `dragging` CSS class during drag operation
  - Implement `handleDragEnd` to remove dragging class
  - _Requirements: 2.1, 2.7_

- [ ] 6. Implement drop zones in deck slots
  - Update `frontend/src/components/DeckSlot.tsx` to handle `onDragOver`, `onDragLeave`, and `onDrop` events
  - Add `drag-over` CSS class to highlight valid drop targets
  - Implement drop handler to parse drag data and call `onAddCardToSlot` callback
  - Add visual feedback (border highlight) when dragging over empty slot
  - _Requirements: 2.2, 2.3_

- [ ] 7. Implement drag from deck slots
  - Make DeckSlot draggable when it contains a card
  - Implement `handleDragStart` in DeckSlot to set drag data with card ID, source type 'deck', and slot index
  - Implement card swapping logic when dropping deck card on another deck slot
  - _Requirements: 2.4, 2.6_

- [ ] 8. Create remove drop zone
  - Create `frontend/src/components/RemoveDropZone.tsx` component
  - Position drop zone outside deck area (below or to the side)
  - Implement drop handler to remove card from deck when dropped
  - Add visual feedback (trash icon, highlight on drag over)
  - Add fade-out animation when card is removed
  - _Requirements: 2.5_

- [ ] 9. Add smooth animations for card operations
  - Create `frontend/src/styles/animations.css` with keyframe animations
  - Implement `cardAddToDeck` animation (scale + fade-in, 300ms)
  - Implement `cardRemoveFromDeck` animation (scale + fade-out, 300ms)
  - Add animation classes to DeckSlot when cards are added/removed
  - Use animation state management (entering/leaving classes)
  - _Requirements: 7.1, 7.2_

- [ ] 10. Add hover and transition animations
  - Update CardDisplay hover styles with elevation change and translateY
  - Add transition properties (box-shadow, transform) with 200ms duration
  - Implement staggered fade-in for gallery cards when filters change
  - Add shimmer animation for skeleton loaders
  - _Requirements: 7.3, 7.4, 7.8_

- [ ] 11. Add notification animations
  - Update `frontend/src/styles/Notification.css` with slide-in/slide-out animations
  - Implement `slideInRight` keyframe (250ms)
  - Implement `slideOutRight` keyframe (250ms)
  - Add entering/leaving classes to notification component
  - _Requirements: 7.5, 7.6_

- [ ] 12. Add save button pulse animation
  - Create pulse animation keyframe in animations.css
  - Add `.save-button--ready` class when deck has 8 cards
  - Implement pulse animation (2s infinite) with scale and shadow changes
  - _Requirements: 7.7_

- [ ] 13. Debug and fix API endpoint configuration
  - Add console.log to verify `REACT_APP_API_BASE_URL` in `frontend/src/services/api.ts`
  - Create `verifyEndpoints` function to test all API endpoints
  - Call `verifyEndpoints` on app initialization for debugging
  - Check `.env` files to ensure correct API base URL
  - Test API calls in browser network tab to see actual URLs being called
  - _Requirements: 4.5, 5.4, 8.1, 8.6_

- [ ] 14. Fix save deck API payload format
  - Update `createDeck` function in `frontend/src/services/api.ts` to match backend expected format
  - Ensure payload has `name` (string) and `cards` (array of objects with `card_id` and `is_evolution`)
  - Add console.log to show payload before sending
  - Verify Content-Type header is set to application/json
  - Test save deck functionality and verify 201 response
  - _Requirements: 4.1, 4.2, 8.2, 8.5_

- [ ] 15. Fix save deck success handling
  - Update DeckBuilder to show success notification "Deck saved successfully" on 201 response
  - Clear deck or keep current deck based on UX decision
  - Refresh saved decks list after successful save
  - _Requirements: 4.3, 4.7_

- [ ] 16. Fix save deck error handling
  - Add specific error handling for 404 responses (endpoint not found)
  - Add error handling for validation errors (400) with specific message display
  - Add error handling for network errors with "Cannot connect to server" message
  - Test error scenarios and verify user-friendly messages
  - _Requirements: 4.4, 4.5, 4.6, 8.3, 8.4_

- [ ] 17. Fix saved decks page API call
  - Verify `fetchDecks` function in `frontend/src/services/api.ts` calls correct endpoint (GET /decks)
  - Add console.log to show full request URL
  - Test endpoint in browser or Postman to verify backend is responding
  - _Requirements: 5.1, 8.5_

- [ ] 18. Fix saved decks page error handling
  - Update SavedDecks component to handle 404 errors with specific message
  - Implement retry button functionality to re-fetch decks
  - Show "Cannot connect to server" for network errors
  - Show "No saved decks yet" when response is empty array
  - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 19. Create frontend Dockerfile
  - Create `frontend/Dockerfile` with multi-stage build (node build stage + nginx serve stage)
  - Install dependencies with `npm ci` in build stage
  - Run `npm run build` to create production build
  - Copy build output to nginx html directory in production stage
  - Add EXPOSE 80 directive
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 20. Create nginx configuration for frontend
  - Create `frontend/nginx.conf` with SPA routing (serve index.html for all routes)
  - Add gzip compression configuration
  - Add static asset caching headers
  - Configure proxy for /api/ requests to backend service
  - _Requirements: 6.5_

- [ ] 21. Create frontend .dockerignore file
  - Create `frontend/.dockerignore` to exclude node_modules, build, .git, .env.local
  - Add other unnecessary files (coverage, .vscode, README.md)
  - _Requirements: 6.8_

- [ ] 22. Add frontend service to docker-compose
  - Update `docker-compose.yml` to add frontend service
  - Configure build context and dockerfile path
  - Map port 3000:80 for frontend access
  - Add environment variable for REACT_APP_API_BASE_URL
  - Add depends_on backend service
  - Configure networking to connect frontend and backend
  - _Requirements: 6.5, 6.6_

- [ ] 23. Implement runtime environment variable support
  - Create `frontend/public/env-config.js` template for runtime env vars
  - Update `frontend/public/index.html` to include env-config.js script
  - Create `frontend/src/config.ts` to read from window.ENV or process.env
  - Update api.ts to use config.ts for API_BASE_URL
  - _Requirements: 6.7_

- [ ] 24. Add health check to frontend Dockerfile
  - Add HEALTHCHECK directive to Dockerfile
  - Configure health check to wget localhost every 30s
  - Set timeout, start-period, and retries
  - _Requirements: 6.4_

- [ ] 25. Test Docker build and run
  - Build frontend Docker image locally
  - Run frontend container and verify it starts
  - Test accessing frontend on configured port
  - Verify frontend can connect to backend API
  - Test with docker-compose up to ensure all services work together
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
