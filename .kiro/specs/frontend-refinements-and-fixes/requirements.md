# Requirements Document

## Introduction

This feature focuses on refining the Clash Royale Deck Builder frontend with Material Design principles, smooth animations, drag-and-drop functionality, bug fixes for duplicate cards and API endpoints, and Docker containerization. The goal is to create a polished, professional user experience with intuitive interactions and proper error handling.

## Requirements

### Requirement 1: Material Design Implementation

**User Story:** As a user, I want the application to follow Material Design principles, so that the interface feels modern, consistent, and professional.

#### Acceptance Criteria

1. WHEN the application loads THEN all components SHALL use Material Design elevation, shadows, and spacing
2. WHEN cards are displayed THEN they SHALL have proper Material Design card styling with elevation levels
3. WHEN buttons are rendered THEN they SHALL follow Material Design button styles (contained, outlined, text)
4. WHEN interactive elements are hovered THEN they SHALL show Material Design ripple effects
5. WHEN transitions occur THEN they SHALL use Material Design motion curves (ease-in-out, duration 200-300ms)
6. WHEN the rarity text is displayed on cards THEN the font size SHALL be reduced to prevent clipping
7. WHEN the elixir cost is displayed on cards THEN it SHALL use a droplet icon instead of a lightning icon

### Requirement 2: Drag and Drop Functionality

**User Story:** As a user, I want to drag cards from the gallery to my deck and drag them out to remove them, so that deck building feels intuitive and natural.

#### Acceptance Criteria

1. WHEN I click and drag a card from the gallery THEN the card SHALL follow my cursor with visual feedback
2. WHEN I drag a card over an empty deck slot THEN the slot SHALL highlight to indicate it's a valid drop target
3. WHEN I drop a card on an empty deck slot THEN the card SHALL be added to that slot with a smooth animation
4. WHEN I drag a card from a deck slot THEN the card SHALL follow my cursor
5. WHEN I drag a card outside the deck area THEN the card SHALL be removed from the deck with a fade-out animation
6. WHEN I drop a card on an occupied deck slot THEN the cards SHALL swap positions
7. WHEN dragging is in progress THEN a ghost/preview image SHALL follow the cursor
8. WHEN a drag operation completes THEN the UI SHALL update immediately with smooth transitions

### Requirement 3: Duplicate Card Prevention

**User Story:** As a user, I want to be prevented from adding the same card multiple times to my deck, so that my deck follows Clash Royale rules.

#### Acceptance Criteria

1. WHEN a card is added to the deck THEN that card SHALL be visually marked as "in deck" in the gallery
2. WHEN a card is already in the deck THEN clicking or dragging it SHALL show a notification "Card already in deck"
3. WHEN a card is in the deck THEN it SHALL have a disabled/dimmed appearance in the gallery
4. WHEN a card is removed from the deck THEN it SHALL become available again in the gallery
5. WHEN the deck is cleared THEN all cards SHALL become available in the gallery

### Requirement 4: Save Deck API Fix

**User Story:** As a user, I want to successfully save my deck with a name, so that I can access it later.

#### Acceptance Criteria

1. WHEN I click save deck THEN the system SHALL call the correct API endpoint (POST /api/decks)
2. WHEN the save request is made THEN it SHALL include the deck name and all 8 cards with evolution flags
3. WHEN the save succeeds THEN the system SHALL show a success notification "Deck saved successfully"
4. WHEN the save fails with 404 THEN the system SHALL check the API endpoint configuration
5. WHEN the save fails with network error THEN the system SHALL show "Cannot connect to server"
6. WHEN the save fails with validation error THEN the system SHALL show the specific error message
7. WHEN a deck is saved THEN the deck list SHALL refresh to show the new deck

### Requirement 5: Saved Decks Page Fix

**User Story:** As a user, I want to view my saved decks without errors, so that I can manage and load them.

#### Acceptance Criteria

1. WHEN I navigate to saved decks page THEN the system SHALL call the correct API endpoint (GET /api/decks)
2. WHEN the fetch succeeds THEN all saved decks SHALL be displayed in a grid layout
3. WHEN the fetch fails with 404 THEN the system SHALL verify the API endpoint exists in the backend
4. WHEN the fetch fails with network error THEN the system SHALL show "Cannot connect to server" with retry button
5. WHEN no decks exist THEN the system SHALL show "No saved decks yet" message
6. WHEN the retry button is clicked THEN the system SHALL attempt to fetch decks again

### Requirement 6: Frontend Docker Containerization

**User Story:** As a developer, I want the frontend to run in a Docker container, so that the entire application can be deployed consistently.

#### Acceptance Criteria

1. WHEN the frontend Dockerfile is created THEN it SHALL use a multi-stage build (build stage + nginx stage)
2. WHEN the frontend container builds THEN it SHALL install dependencies and create an optimized production build
3. WHEN the frontend container runs THEN it SHALL serve the static files via nginx
4. WHEN the frontend container starts THEN it SHALL be accessible on the configured port
5. WHEN docker-compose is used THEN the frontend service SHALL be defined with proper networking
6. WHEN the frontend connects to backend THEN it SHALL use the correct API URL from environment variables
7. WHEN environment variables change THEN the container SHALL support runtime configuration
8. WHEN the container is built THEN it SHALL include a .dockerignore file to exclude node_modules and build artifacts

### Requirement 7: Smooth Animations and Transitions

**User Story:** As a user, I want smooth animations throughout the application, so that interactions feel polished and responsive.

#### Acceptance Criteria

1. WHEN a card is added to the deck THEN it SHALL animate with a scale and fade-in effect (300ms)
2. WHEN a card is removed from the deck THEN it SHALL animate with a scale and fade-out effect (300ms)
3. WHEN filters are applied THEN the card gallery SHALL update with a staggered fade-in animation
4. WHEN hovering over cards THEN they SHALL lift with a smooth elevation change (200ms)
5. WHEN notifications appear THEN they SHALL slide in from the top-right (250ms)
6. WHEN notifications dismiss THEN they SHALL slide out to the right (250ms)
7. WHEN the deck is complete THEN the save button SHALL pulse with a subtle animation
8. WHEN loading states occur THEN skeleton loaders SHALL have a shimmer animation

### Requirement 8: API Service Layer Verification

**User Story:** As a developer, I want to verify the API service layer is correctly configured, so that all endpoints work properly.

#### Acceptance Criteria

1. WHEN the API service is initialized THEN it SHALL use the base URL from environment variables
2. WHEN API calls are made THEN they SHALL include proper headers (Content-Type: application/json)
3. WHEN the backend returns errors THEN the frontend SHALL parse and display them correctly
4. WHEN network errors occur THEN the frontend SHALL handle them gracefully
5. WHEN the API endpoints are called THEN they SHALL match the backend route definitions exactly
6. WHEN debugging API issues THEN console logs SHALL show the full request URL and payload

### Requirement 9: Filter Sorting Controls

**User Story:** As a user, I want to sort filtered results in ascending or descending order, so that I can find cards more efficiently.

#### Acceptance Criteria

1. WHEN filters are displayed THEN there SHALL be ascending/descending toggle buttons for sortable fields
2. WHEN I click ascending sort THEN cards SHALL be sorted from lowest to highest value
3. WHEN I click descending sort THEN cards SHALL be sorted from highest to lowest value
4. WHEN sorting by elixir cost THEN cards SHALL be ordered numerically (1, 2, 3... or 10, 9, 8...)
5. WHEN sorting by name THEN cards SHALL be ordered alphabetically (A-Z or Z-A)
6. WHEN sorting by rarity THEN cards SHALL be ordered by rarity hierarchy (Common, Rare, Epic, Legendary, Champion)
7. WHEN a sort direction is active THEN the corresponding button SHALL show visual feedback (highlighted/pressed state)

### Requirement 10: Saved Decks Visual Fixes

**User Story:** As a user, I want to clearly see my saved deck information, so that I can identify and select the right deck.

#### Acceptance Criteria

1. WHEN viewing saved decks THEN deck names SHALL be visible with sufficient color contrast
2. WHEN viewing saved decks THEN average elixir cost SHALL be visible with sufficient color contrast
3. WHEN viewing saved decks THEN card count SHALL be visible with sufficient color contrast
4. WHEN saved deck text is displayed THEN it SHALL use dark colors on light background for readability
5. WHEN hovering over saved decks THEN text SHALL remain clearly visible

### Requirement 11: Card Selection Animation Fixes

**User Story:** As a user, I want smooth card selection animations without visual glitches, so that the interface feels polished.

#### Acceptance Criteria

1. WHEN I click on a card THEN the card SHALL NOT disappear momentarily during selection
2. WHEN adding cards to deck THEN each subsequent card SHALL animate consistently without increasing delay
3. WHEN a card is selected THEN the animation SHALL complete smoothly without flickering
4. WHEN multiple cards are added quickly THEN animations SHALL not interfere with each other
5. WHEN the deck has more cards THEN new card animations SHALL maintain the same timing

### Requirement 12: Card Opacity and State Management

**User Story:** As a user, I want cards to display with proper opacity states, so that I can clearly see which cards are available.

#### Acceptance Criteria

1. WHEN I remove a card from the deck THEN the replacement card SHALL display with full opacity
2. WHEN I add a card to fill an empty slot THEN the card SHALL display with full opacity immediately
3. WHEN cards are swapped in deck slots THEN both cards SHALL maintain proper opacity
4. WHEN a card is moved between slots THEN it SHALL not retain any opacity effects from previous states
5. WHEN the deck is cleared THEN all replacement cards SHALL display with full opacity

### Requirement 13: Evolution Card Logic Enhancement

**User Story:** As a user, I want evolution marking to only work with cards that actually support evolution, so that I don't make invalid deck configurations.

#### Acceptance Criteria

1. WHEN a card does not support evolution THEN the evolution toggle SHALL NOT be available
2. WHEN a card supports evolution THEN the evolution toggle SHALL be visible and functional
3. WHEN displaying evolution options THEN the system SHALL first check if the card has evolution capability
4. WHEN a non-evolution card is in deck THEN no evolution UI elements SHALL be shown for that card
5. WHEN loading card data THEN the system SHALL identify which cards support evolution

### Requirement 14: Automatic Evolution for First Two Slots

**User Story:** As a user, I want the first two deck slots to automatically handle evolution states, so that deck building follows optimal patterns.

#### Acceptance Criteria

1. WHEN the first two slots are filled THEN those cards SHALL be automatically marked as evolution IF they support it
2. WHEN I drag a card to slot 1 or 2 THEN it SHALL be automatically marked as evolution IF it supports evolution
3. WHEN I drag a card from slot 1 or 2 to another slot THEN it SHALL be automatically unmarked as evolution
4. WHEN I swap cards between slots 1-2 and slots 3-8 THEN evolution states SHALL update automatically
5. WHEN a card in slot 1 or 2 doesn't support evolution THEN it SHALL remain unmarked
6. WHEN cards are rearranged THEN only cards in positions 1 and 2 SHALL be eligible for automatic evolution marking

### Requirement 15: Deck Slot Visual Enhancement

**User Story:** As a user, I want clear visual indicators for deck slots, so that I can easily see where to place cards.

#### Acceptance Criteria

1. WHEN deck slots are empty THEN they SHALL display a blue outline border
2. WHEN hovering over empty slots during drag THEN the blue outline SHALL become more prominent
3. WHEN slots contain cards THEN the blue outline SHALL be subtle or hidden
4. WHEN dragging cards over slots THEN the blue outline SHALL provide clear drop target feedback
5. WHEN the deck is complete THEN slot outlines SHALL indicate the deck is full
