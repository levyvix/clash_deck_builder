# Requirements Document

## Introduction

The Clash Royale Deck Builder frontend currently has skeleton React components but lacks the core implementation needed for a functional user interface. This feature will implement a complete, working frontend that displays all Clash Royale cards with images, provides filtering capabilities, enables deck building with drag-and-drop or click interactions, and manages saved decks. The implementation will connect to the backend API endpoints and provide a polished user experience.

## Requirements

### Requirement 1: Card Gallery Display

**User Story:** As a player, I want to see all available Clash Royale cards with their images displayed in a grid, so that I can browse and select cards for my deck.

#### Acceptance Criteria

1. WHEN the application loads THEN the system SHALL fetch all cards from the GET /cards endpoint
2. WHEN cards are fetched successfully THEN the system SHALL display them in a responsive grid layout
3. WHEN a card is displayed THEN it SHALL show the card image, name, elixir cost, and rarity
4. WHEN card images fail to load THEN the system SHALL display a placeholder or fallback image
5. WHEN the API call fails THEN the system SHALL display an error message to the user
6. WHEN cards are loading THEN the system SHALL display a loading indicator

### Requirement 2: Card Filtering System

**User Story:** As a player, I want to filter cards by elixir cost, name, rarity, and type, so that I can quickly find specific cards for my deck strategy.

#### Acceptance Criteria

1. WHEN I enter text in the name filter THEN the system SHALL show only cards whose names contain that text (case-insensitive)
2. WHEN I select an elixir cost filter THEN the system SHALL show only cards with that exact elixir cost
3. WHEN I select a rarity filter THEN the system SHALL show only cards of that rarity (Common, Rare, Epic, Legendary, Champion)
4. WHEN I select a type filter THEN the system SHALL show only cards of that type (Troop, Building, Spell)
5. WHEN multiple filters are active THEN the system SHALL show only cards that match ALL active filters
6. WHEN I clear filters THEN the system SHALL display all cards again
7. WHEN no cards match the filters THEN the system SHALL display a "No cards found" message

### Requirement 3: Deck Building Interface

**User Story:** As a player, I want to add cards to my deck by clicking on them and see options to manage deck slots, so that I can build a deck of exactly 8 cards with precise control.

#### Acceptance Criteria

1. WHEN I click on a card in the gallery THEN the system SHALL show an option to "Add to Deck"
2. WHEN I select "Add to Deck" THEN the system SHALL add the card to the next empty slot in my current deck if the deck has fewer than 8 cards
3. WHEN my deck has 8 cards THEN the system SHALL prevent adding more cards and display a message
4. WHEN I click on a card in my deck THEN the system SHALL show an option to "Remove from Deck"
5. WHEN I select "Remove from Deck" THEN the system SHALL remove the card and leave that slot empty
6. WHEN cards are added or removed THEN the system SHALL automatically recalculate and display the average elixir cost
7. WHEN my deck is empty THEN the average elixir SHALL display as 0.0
8. WHEN calculating average elixir THEN the system SHALL round to one decimal place
9. WHEN I add a card THEN the system SHALL provide visual feedback (animation or highlight)
10. WHEN the deck has empty slots THEN they SHALL be visually indicated as empty positions

### Requirement 4: Evolution Slot Management

**User Story:** As a player, I want to designate up to 2 cards in my deck as evolution slots, so that I can plan my deck strategy with evolutions.

#### Acceptance Criteria

1. WHEN a card is in my deck THEN I SHALL be able to mark it as an evolution slot
2. WHEN I mark a card as evolution THEN the system SHALL display the evolution image if available
3. WHEN 2 cards are already marked as evolution THEN the system SHALL prevent marking additional cards
4. WHEN I unmark an evolution card THEN the system SHALL display the regular card image
5. WHEN a card with evolution is removed from the deck THEN its evolution status SHALL be cleared
6. WHEN evolution slots are used THEN they SHALL be visually distinct from regular cards

### Requirement 5: Deck Saving and Management

**User Story:** As a player, I want to save my current deck with a custom name, so that I can build and store multiple deck strategies.

#### Acceptance Criteria

1. WHEN I click save deck THEN the system SHALL prompt me for a deck name
2. WHEN I provide a deck name THEN the system SHALL save the deck via POST /decks endpoint
3. WHEN the deck is saved successfully THEN the system SHALL display a success message
4. WHEN I already have 20 saved decks THEN the system SHALL prevent saving and display an error message
5. WHEN saving fails THEN the system SHALL display an error message with details
6. WHEN a deck is saved THEN it SHALL include all 8 cards, evolution slots, and average elixir

### Requirement 6: Saved Decks View

**User Story:** As a player, I want to view all my saved decks in a list, so that I can manage and select decks to load or delete.

#### Acceptance Criteria

1. WHEN I navigate to the saved decks page THEN the system SHALL fetch all decks from GET /decks endpoint
2. WHEN decks are displayed THEN each SHALL show the deck name, card count, and average elixir
3. WHEN I click on a saved deck THEN the system SHALL load it into the deck builder
4. WHEN I click delete on a deck THEN the system SHALL prompt for confirmation
5. WHEN I confirm deletion THEN the system SHALL delete via DELETE /decks/{id} endpoint
6. WHEN I click rename on a deck THEN the system SHALL allow editing the name inline
7. WHEN I save a new name THEN the system SHALL update via PUT /decks/{id} endpoint

### Requirement 7: Responsive Design and Styling

**User Story:** As a player, I want the application to look polished and work on different screen sizes, so that I can use it on desktop or mobile devices.

#### Acceptance Criteria

1. WHEN viewing on desktop THEN the card gallery SHALL display in a multi-column grid
2. WHEN viewing on mobile THEN the card gallery SHALL adjust to fewer columns
3. WHEN viewing cards THEN rarity SHALL be indicated by color coding (Common: gray, Rare: orange, Epic: purple, Legendary: rainbow/gold, Champion: gold)
4. WHEN viewing the deck builder THEN it SHALL have a clear visual separation from the card gallery
5. WHEN interacting with buttons THEN they SHALL have hover and active states
6. WHEN errors occur THEN they SHALL be displayed in a visually distinct error banner

### Requirement 8: Application State Management

**User Story:** As a player, I want my current deck to persist while navigating between pages, so that I don't lose my work when viewing saved decks.

#### Acceptance Criteria

1. WHEN I build a deck and navigate to saved decks THEN my current deck SHALL remain in memory
2. WHEN I return to the deck builder THEN my current deck SHALL still be displayed
3. WHEN I load a saved deck THEN it SHALL replace my current deck
4. WHEN I refresh the page THEN my current unsaved deck SHALL be cleared (no persistence requirement)
5. WHEN the application state changes THEN the UI SHALL update reactively

### Requirement 9: Error Handling and User Feedback

**User Story:** As a player, I want clear feedback when actions succeed or fail, so that I understand what's happening in the application.

#### Acceptance Criteria

1. WHEN any API call fails THEN the system SHALL display a user-friendly error message
2. WHEN the backend is unreachable THEN the system SHALL display a "Cannot connect to server" message
3. WHEN an action succeeds THEN the system SHALL display a brief success notification
4. WHEN loading data THEN the system SHALL display loading spinners or skeleton screens
5. WHEN network requests timeout THEN the system SHALL display a timeout error message

### Requirement 10: Initial Setup and Dependencies

**User Story:** As a developer, I want all necessary frontend dependencies installed and configured, so that the application can run immediately.

#### Acceptance Criteria

1. WHEN setting up the project THEN all required npm packages SHALL be installed
2. WHEN the development server starts THEN it SHALL run on port 3000
3. WHEN the application loads THEN it SHALL connect to the backend API at the configured URL
4. WHEN environment variables are needed THEN they SHALL be properly configured in .env files
5. WHEN running npm start THEN the application SHALL open in the browser automatically
