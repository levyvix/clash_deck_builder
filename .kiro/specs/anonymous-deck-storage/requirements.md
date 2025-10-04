# Requirements Document

## Introduction

This feature restores the "Saved Decks" functionality for anonymous users by implementing browser-based local storage. When Google authentication was added, the saved decks tab was removed, but anonymous users still need the ability to save and manage their decks locally without requiring authentication. This feature ensures that users can build, save, and manage decks whether they're signed in or not, with data persisting in the browser's local storage for anonymous users.

## Requirements

### Requirement 1

**User Story:** As an anonymous user, I want to see a "Saved Decks" tab in the navigation, so that I can access my locally saved decks without needing to authenticate.

#### Acceptance Criteria

1. WHEN an anonymous user visits the application THEN the navigation SHALL display a "Saved Decks" tab alongside existing tabs
2. WHEN an anonymous user clicks the "Saved Decks" tab THEN the system SHALL display the saved decks interface
3. IF a user is authenticated THEN the "Saved Decks" tab SHALL still be visible and functional for backward compatibility

### Requirement 2

**User Story:** As an anonymous user, I want to save decks to my browser's local storage, so that my decks persist between sessions without requiring an account.

#### Acceptance Criteria

1. WHEN an anonymous user creates a deck and clicks save THEN the system SHALL store the deck data in browser localStorage
2. WHEN an anonymous user saves a deck THEN the system SHALL assign a unique identifier to the deck
3. WHEN an anonymous user saves a deck THEN the system SHALL include deck name, cards, and creation timestamp
4. IF localStorage is not available THEN the system SHALL display an appropriate error message
5. WHEN an anonymous user reaches the maximum of 20 saved decks THEN the system SHALL prevent saving additional decks and display a warning

### Requirement 3

**User Story:** As an anonymous user, I want to view all my locally saved decks in a list, so that I can easily browse and select decks I've created.

#### Acceptance Criteria

1. WHEN an anonymous user opens the Saved Decks tab THEN the system SHALL display all decks stored in localStorage
2. WHEN displaying saved decks THEN the system SHALL show deck name, card count, average elixir cost, and creation date
3. WHEN no decks are saved THEN the system SHALL display a message encouraging the user to create their first deck
4. WHEN decks are displayed THEN they SHALL be sorted by creation date with newest first

### Requirement 4

**User Story:** As an anonymous user, I want to load a saved deck into the deck builder, so that I can modify or use existing decks.

#### Acceptance Criteria

1. WHEN an anonymous user clicks on a saved deck THEN the system SHALL load the deck into the deck builder interface
2. WHEN a deck is loaded THEN the system SHALL populate all card slots with the saved cards
3. WHEN a deck is loaded THEN the system SHALL update the average elixir calculation
4. WHEN a deck is loaded THEN the system SHALL navigate to the deck builder tab

### Requirement 5

**User Story:** As an anonymous user, I want to rename my saved decks, so that I can organize them with meaningful names.

#### Acceptance Criteria

1. WHEN an anonymous user clicks a rename option on a saved deck THEN the system SHALL display an editable text field
2. WHEN an anonymous user enters a new deck name and confirms THEN the system SHALL update the deck name in localStorage
3. WHEN an anonymous user cancels renaming THEN the system SHALL revert to the original name
4. IF a user enters an empty name THEN the system SHALL prevent saving and display a validation message

### Requirement 6

**User Story:** As an anonymous user, I want to delete saved decks I no longer need, so that I can manage my deck collection.

#### Acceptance Criteria

1. WHEN an anonymous user clicks delete on a saved deck THEN the system SHALL prompt for confirmation
2. WHEN an anonymous user confirms deletion THEN the system SHALL remove the deck from localStorage
3. WHEN an anonymous user cancels deletion THEN the system SHALL keep the deck unchanged
4. WHEN a deck is deleted THEN the system SHALL update the displayed deck list immediately

### Requirement 7

**User Story:** As an anonymous user, I want my deck data to be compatible with the authenticated user system, so that I can potentially migrate my data if I decide to create an account later.

#### Acceptance Criteria

1. WHEN storing deck data THEN the system SHALL use a format compatible with the existing deck data structure
2. WHEN storing deck data THEN the system SHALL include all fields necessary for potential future migration
3. IF a user signs in after using anonymous storage THEN the system SHALL maintain both local and server-based decks separately
4. WHEN displaying decks for authenticated users THEN the system SHALL clearly distinguish between local and server-stored decks

### Requirement 8

**User Story:** As a user, I want the saved decks functionality to work consistently whether I'm authenticated or not, so that I have a seamless experience regardless of my login status.

#### Acceptance Criteria

1. WHEN switching between authenticated and anonymous states THEN the saved decks interface SHALL remain functional
2. WHEN an authenticated user also has local decks THEN the system SHALL display both local and server decks in the same interface
3. WHEN displaying mixed deck sources THEN the system SHALL indicate which decks are stored locally vs on the server
4. WHEN the user's authentication state changes THEN the system SHALL refresh the saved decks display appropriately