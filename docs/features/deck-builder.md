# Deck Builder Feature

## Overview
The Deck Builder is the core feature of the application, allowing users to create, manage, and optimize their Clash Royale decks.

## User Flows

### Creating a New Deck
1. User clicks "New Deck" button
2. System generates an empty deck with a default name
3. User can:
   - Drag and drop cards into deck slots
   - Search/filter cards using the search bar
   - View card details on hover
   - Save the deck when complete

### Editing a Deck
1. User selects a deck from their collection
2. System loads the deck into the builder interface
3. User can:
   - Add/remove cards
   - Change evolution cards
   - Rename the deck
   - Save changes or discard

### Deck Validation
- Maximum 8 cards per deck
- Maximum 2 evolution cards
- No duplicate cards
- Must include at least 1 troop card

## Business Rules

### Card Slots
- **Total Slots**: 8 cards per deck
- **Evolution Slots**: Up to 2 cards can be marked as evolved
- **Card Levels**: Each card has a level (1-14)

### Elixir Calculation
- Average elixir cost is calculated as:
  ```
  total_elixir = sum(card.elixir for card in deck.cards)
  average_elixir = round(total_elixir / 8, 1)
  ```
- Displayed to 1 decimal place
- Rounded using standard rounding rules

### Evolution System
- Users can select up to 2 cards to be evolved
- Only cards with evolution versions can be evolved
- Evolving a card increases its level by 1 for stats calculation

## API Endpoints

### Get All Cards
```http
GET /api/cards
```

### Create Deck
```http
POST /api/decks
```

### Update Deck
```http
PUT /api/decks/{deck_id}
```

## UI Components

### Card Browser
- Grid layout of all available cards
- Filter by:
  - Elixir cost (1-7+)
  - Rarity (Common, Rare, Epic, Legendary, Champion)
  - Type (Troop, Spell, Building)
  - Arena
- Search by name
- Sort options (Elixir, Rarity, Name)

### Deck Display
- Visual representation of the deck
- Shows card levels and evolution status
- Displays average elixir cost
- Visual indicators for:
  - Missing cards
  - Invalid deck configurations
  - Evolution slots used

## State Management

### Frontend State
```typescript
interface DeckState {
  id?: string;
  name: string;
  cards: Array<{
    id: number;
    level: number;
    isEvolution: boolean;
  }>;
  averageElixir: number;
  isValid: boolean;
  lastSaved: Date | null;
}
```

### Validation Rules
```typescript
function validateDeck(deck: DeckState): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  
  if (deck.cards.length !== 8) {
    errors.push('Deck must contain exactly 8 cards');
  }
  
  const evolutionCount = deck.cards.filter(c => c.isEvolution).length;
  if (evolutionCount > 2) {
    errors.push('Maximum of 2 evolution cards allowed');
  }
  
  // Check for duplicate cards
  const cardIds = deck.cards.map(c => c.id);
  if (new Set(cardIds).size !== cardIds.length) {
    errors.push('Duplicate cards are not allowed');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}
```

## Performance Considerations

### Card Images
- Lazy loading of card images
- Preloading of commonly used cards
- Responsive images with appropriate sizes

### State Updates
- Debounced auto-save (2s delay after last change)
- Optimistic UI updates
- Background sync for offline support

## Accessibility

### Keyboard Navigation
- Tab through interactive elements
- Keyboard shortcuts for common actions
- Screen reader support for all controls

### ARIA Labels
- Card names and rarities
- Interactive elements
- Error messages and status updates

## Testing Strategy

### Unit Tests
- Deck validation logic
- Elixir calculation
- Evolution rules

### Integration Tests
- Drag and drop functionality
- Filter and search
- Save/load operations

### E2E Tests
- Complete deck creation flow
- Error scenarios
- Cross-browser testing

## Future Enhancements

### Deck Sharing
- Generate shareable links
- Embeddable deck widgets
- Social media integration

### Deck Analysis
- Win rate prediction
- Card synergy scoring
- Counter recommendations

### Import/Export
- Copy deck links
- Export as image
- Import from game screenshots (OCR)
