# Design Document

## Overview

The core frontend implementation will create a fully functional React-based web application for the Clash Royale Deck Builder. The design follows a component-based architecture with clear separation between UI components, state management, API integration, and styling. The application will provide an intuitive interface for browsing cards, building decks, and managing saved decks with real-time feedback and responsive design.

## Architecture

### Technology Stack
- **React 19.2+**: Component framework with hooks for state management
- **TypeScript**: Type-safe development with strict mode
- **React Router DOM**: Client-side routing for navigation
- **CSS3**: Styling with CSS Grid and Flexbox for responsive layouts
- **Fetch API**: HTTP client for backend communication

### Application Structure
```
frontend/src/
├── components/          # React UI components
│   ├── CardDisplay.tsx      # Individual card display
│   ├── CardGallery.tsx      # Grid of all cards
│   ├── CardFilters.tsx      # Filter controls
│   ├── DeckBuilder.tsx      # Main deck building interface
│   ├── DeckSlot.tsx         # Individual deck slot (new)
│   ├── SavedDecks.tsx       # Saved decks list view
│   └── Notification.tsx     # Toast/banner notifications (new)
├── services/           # API and business logic
│   ├── api.ts              # Backend API client
│   └── deckCalculations.ts # Deck utility functions (new)
├── types/              # TypeScript type definitions (new)
│   └── index.ts            # Shared types
├── styles/             # CSS stylesheets (new)
│   ├── App.css
│   ├── CardDisplay.css
│   ├── CardGallery.css
│   ├── DeckBuilder.css
│   └── variables.css       # CSS custom properties
├── App.tsx             # Main application component
└── index.tsx           # Application entry point
```

## Components and Interfaces

### 1. Type Definitions (types/index.ts)

```typescript
export interface Card {
  id: number;
  name: string;
  elixir_cost: number;
  rarity: 'Common' | 'Rare' | 'Epic' | 'Legendary' | 'Champion';
  type: 'Troop' | 'Spell' | 'Building';
  arena?: string;
  image_url: string;
  image_url_evo?: string;
}

export interface DeckSlot {
  card: Card | null;
  isEvolution: boolean;
}

export interface Deck {
  id?: number;
  name: string;
  slots: DeckSlot[];  // Always 8 slots
  average_elixir: number;
  created_at?: string;
  updated_at?: string;
}

export interface FilterState {
  name: string;
  elixirCost: number | null;
  rarity: string | null;
  type: string | null;
}

export type NotificationType = 'success' | 'error' | 'info';

export interface Notification {
  id: string;
  message: string;
  type: NotificationType;
}
```

### 2. CardDisplay Component

**Purpose**: Display a single card with its image, stats, and rarity styling.

**Props**:
```typescript
interface CardDisplayProps {
  card: Card;
  isEvolution?: boolean;
  onClick?: () => void;
  showOptions?: boolean;
  onAddToDeck?: () => void;
  onRemoveFromDeck?: () => void;
  inDeck?: boolean;
}
```

**Behavior**:
- Displays card image (evolution image if `isEvolution` is true)
- Shows card name, elixir cost, and rarity
- Applies rarity-based color coding via CSS classes
- Shows action buttons when clicked (Add to Deck / Remove from Deck)
- Handles image loading errors with fallback placeholder

**Styling**:
- Rarity colors: Common (gray), Rare (orange), Epic (purple), Legendary (gold gradient), Champion (gold)
- Card dimensions: 120px width, auto height
- Hover effect: slight scale and shadow
- Click effect: pulse animation

### 3. CardGallery Component

**Purpose**: Display all cards in a filterable, responsive grid.

**Props**:
```typescript
interface CardGalleryProps {
  cards: Card[];
  filters: FilterState;
  onCardClick: (card: Card) => void;
  selectedCard: Card | null;
  onAddToDeck: (card: Card) => void;
}
```

**State**:
- `filteredCards`: Computed from cards and filters
- `selectedCard`: Currently clicked card showing options

**Behavior**:
- Filters cards based on active filters (name, elixir, rarity, type)
- Displays cards in CSS Grid (responsive: 6 columns desktop, 3 tablet, 2 mobile)
- Shows "No cards found" when filters return empty
- Displays loading skeleton while fetching
- Shows action menu overlay when card is clicked

**Layout**:
- Grid with gap: 16px
- Responsive breakpoints: 1200px, 768px, 480px

### 4. CardFilters Component

**Purpose**: Provide UI controls for filtering cards.

**Props**:
```typescript
interface CardFiltersProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  onClearFilters: () => void;
}
```

**Controls**:
- Text input for name search (debounced 300ms)
- Dropdown for elixir cost (0-10, "All")
- Dropdown for rarity (All, Common, Rare, Epic, Legendary, Champion)
- Dropdown for type (All, Troop, Spell, Building)
- Clear filters button

**Behavior**:
- Updates filters on change
- Shows active filter count badge
- Disables clear button when no filters active

### 5. DeckSlot Component (New)

**Purpose**: Represent a single slot in the 8-card deck.

**Props**:
```typescript
interface DeckSlotProps {
  slot: DeckSlot;
  slotIndex: number;
  onCardClick: (slotIndex: number) => void;
  onRemoveCard: (slotIndex: number) => void;
  onToggleEvolution: (slotIndex: number) => void;
  canAddEvolution: boolean;
  showOptions: boolean;
}
```

**Behavior**:
- Displays card if slot is filled, otherwise shows empty slot placeholder
- Shows evolution badge if `isEvolution` is true
- Clicking filled slot shows options: Remove, Toggle Evolution
- Empty slots show dashed border and "+" icon
- Evolution toggle disabled if 2 evolutions already exist

**Styling**:
- Fixed size: 100px x 140px
- Empty slot: dashed border, gray background
- Evolution indicator: star icon overlay

### 6. DeckBuilder Component (Enhanced)

**Purpose**: Main interface for building and managing the current deck.

**State**:
```typescript
const [currentDeck, setCurrentDeck] = useState<DeckSlot[]>(
  Array(8).fill({ card: null, isEvolution: false })
);
const [cards, setCards] = useState<Card[]>([]);
const [filters, setFilters] = useState<FilterState>({
  name: '', elixirCost: null, rarity: null, type: null
});
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [selectedGalleryCard, setSelectedGalleryCard] = useState<Card | null>(null);
const [selectedDeckSlot, setSelectedDeckSlot] = useState<number | null>(null);
```

**Computed Values**:
- `averageElixir`: Calculated from non-empty slots
- `evolutionCount`: Count of slots with `isEvolution: true`
- `emptySlotCount`: Count of slots with `card: null`

**Methods**:
```typescript
const addCardToDeck = (card: Card) => {
  // Find first empty slot and add card
  // Close options menu
  // Show success notification
};

const removeCardFromDeck = (slotIndex: number) => {
  // Set slot to { card: null, isEvolution: false }
  // Recalculate average elixir
  // Show success notification
};

const toggleEvolution = (slotIndex: number) => {
  // Toggle isEvolution if under 2 evolution limit
  // Show error if limit reached
};

const saveDeck = async (deckName: string) => {
  // Validate deck has 8 cards
  // Call API to save deck
  // Show success/error notification
};

const calculateAverageElixir = (slots: DeckSlot[]): number => {
  // Sum elixir costs of non-empty slots
  // Divide by number of cards
  // Round to 1 decimal place
};
```

**Layout**:
- Top section: Deck slots (8 slots in 2 rows of 4)
- Middle section: Deck stats (average elixir, card count)
- Bottom section: Save deck button
- Right section: Card gallery with filters

### 7. SavedDecks Component (Enhanced)

**Purpose**: Display and manage saved decks.

**Props**:
```typescript
interface SavedDecksProps {
  decks: Deck[];
  onSelectDeck: (deck: Deck) => void;
  onRenameDeck: (deckId: number, newName: string) => void;
  onDeleteDeck: (deckId: number) => void;
}
```

**State**:
- `editingDeckId`: ID of deck being renamed
- `editingName`: Temporary name during edit

**Behavior**:
- Displays decks in a list/grid
- Each deck shows: name, 8 card thumbnails, average elixir
- Click deck to load into builder
- Rename: inline edit with save/cancel
- Delete: confirmation modal before deletion
- Shows "No saved decks" when empty

### 8. Notification Component (New)

**Purpose**: Display toast notifications for user feedback.

**Props**:
```typescript
interface NotificationProps {
  notifications: Notification[];
  onDismiss: (id: string) => void;
}
```

**Behavior**:
- Displays notifications in top-right corner
- Auto-dismiss after 3 seconds
- Manual dismiss with X button
- Stacks multiple notifications
- Color-coded by type (success: green, error: red, info: blue)

### 9. App Component (Enhanced)

**Purpose**: Root component managing routing and global state.

**State**:
```typescript
const [savedDecks, setSavedDecks] = useState<Deck[]>([]);
const [notifications, setNotifications] = useState<Notification[]>([]);
const [currentDeck, setCurrentDeck] = useState<DeckSlot[]>(
  Array(8).fill({ card: null, isEvolution: false })
);
```

**Methods**:
```typescript
const addNotification = (message: string, type: NotificationType) => {
  // Add notification with unique ID
  // Auto-remove after 3 seconds
};

const loadDeckIntoBuilder = (deck: Deck) => {
  // Set currentDeck from saved deck
  // Navigate to deck builder
  // Show success notification
};
```

**Routes**:
- `/`: DeckBuilder component
- `/saved-decks`: SavedDecks component

## Data Models

### Card Model
Matches backend API response:
```typescript
{
  id: number;
  name: string;
  elixir_cost: number;
  rarity: string;
  type: string;
  arena?: string;
  image_url: string;
  image_url_evo?: string;
}
```

### Deck Model for API
When saving/updating decks:
```typescript
{
  name: string;
  cards: Card[];  // Array of 8 cards
  evolution_slots: number[];  // Array of card IDs marked as evolution (max 2)
  average_elixir: number;
}
```

## API Integration

### Service Layer (services/api.ts)

**Enhanced Methods**:
```typescript
export const fetchCards = async (): Promise<Card[]> => {
  // GET /cards
  // Returns array of Card objects
  // Throws error on failure
};

export const fetchDecks = async (): Promise<Deck[]> => {
  // GET /decks
  // Returns array of saved decks
  // Transforms API response to Deck type
};

export const createDeck = async (deck: Omit<Deck, 'id'>): Promise<Deck> => {
  // POST /decks
  // Sends deck data
  // Returns created deck with ID
};

export const updateDeck = async (deckId: number, deck: Partial<Deck>): Promise<Deck> => {
  // PUT /decks/{deckId}
  // Updates deck
  // Returns updated deck
};

export const deleteDeck = async (deckId: number): Promise<void> => {
  // DELETE /decks/{deckId}
  // Returns void on success
};
```

**Error Handling**:
- Network errors: "Cannot connect to server"
- 4xx errors: Display error message from response
- 5xx errors: "Server error, please try again"
- Timeout: "Request timed out"

### Utility Functions (services/deckCalculations.ts)

```typescript
export const calculateAverageElixir = (slots: DeckSlot[]): number => {
  const cards = slots.filter(slot => slot.card !== null);
  if (cards.length === 0) return 0;
  const total = cards.reduce((sum, slot) => sum + slot.card!.elixir_cost, 0);
  return Math.round((total / cards.length) * 10) / 10;
};

export const canAddEvolution = (slots: DeckSlot[]): boolean => {
  const evolutionCount = slots.filter(slot => slot.isEvolution).length;
  return evolutionCount < 2;
};

export const isDeckComplete = (slots: DeckSlot[]): boolean => {
  return slots.every(slot => slot.card !== null);
};

export const getEmptySlotIndex = (slots: DeckSlot[]): number => {
  return slots.findIndex(slot => slot.card === null);
};
```

## Styling Strategy

### CSS Variables (styles/variables.css)
```css
:root {
  /* Colors */
  --color-common: #808080;
  --color-rare: #ff8c00;
  --color-epic: #9370db;
  --color-legendary: linear-gradient(135deg, #ffd700, #ff8c00);
  --color-champion: #ffd700;
  
  --color-primary: #4a90e2;
  --color-success: #4caf50;
  --color-error: #f44336;
  --color-warning: #ff9800;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 20px;
  
  /* Borders */
  --border-radius: 8px;
  --border-radius-sm: 4px;
}
```

### Responsive Breakpoints
- Desktop: > 1200px (6 columns)
- Tablet: 768px - 1200px (4 columns)
- Mobile: < 768px (2 columns)

### Component-Specific Styles
Each component has its own CSS file with scoped class names:
- `.card-display`, `.card-display--common`, `.card-display--rare`, etc.
- `.deck-slot`, `.deck-slot--empty`, `.deck-slot--evolution`
- `.card-gallery`, `.card-gallery__grid`
- `.notification`, `.notification--success`, `.notification--error`

## Error Handling

### Error Scenarios

1. **API Connection Failure**
   - Display: "Cannot connect to server. Please check your connection."
   - Action: Retry button

2. **Card Fetch Failure**
   - Display: "Failed to load cards. Please refresh the page."
   - Action: Refresh button

3. **Deck Save Failure**
   - Display: Error message from API or "Failed to save deck"
   - Action: Retry save

4. **Deck Limit Reached**
   - Display: "You have reached the maximum of 20 saved decks. Delete a deck to save a new one."
   - Action: Navigate to saved decks

5. **Image Load Failure**
   - Display: Placeholder image with card name
   - Action: None (graceful degradation)

### Loading States
- Cards loading: Skeleton grid (8 placeholder cards)
- Decks loading: Spinner
- Save in progress: Disabled button with spinner

## Testing Strategy

### Component Testing
- **CardDisplay**: Renders correctly, handles click events, shows evolution image
- **CardGallery**: Filters work correctly, displays cards, handles empty state
- **DeckSlot**: Shows empty/filled state, handles remove action
- **DeckBuilder**: Adds/removes cards, calculates elixir, enforces 8-card limit

### Integration Testing
- **API Integration**: Mock API responses, test error handling
- **Deck Building Flow**: Add 8 cards, save deck, verify in saved decks
- **Filter Flow**: Apply filters, verify correct cards shown

### Manual Testing Checklist
- [ ] Cards display with images
- [ ] Filters work for all combinations
- [ ] Can build deck with 8 cards
- [ ] Can mark 2 evolution slots
- [ ] Average elixir calculates correctly
- [ ] Can save deck with name
- [ ] Can load saved deck
- [ ] Can rename deck
- [ ] Can delete deck
- [ ] Error messages display correctly
- [ ] Responsive on mobile/tablet/desktop

## Performance Considerations

### Optimization Strategies
1. **Memoization**: Use `useMemo` for filtered cards and average elixir calculation
2. **Debouncing**: Debounce name filter input (300ms)
3. **Lazy Loading**: Consider virtualizing card gallery if > 100 cards
4. **Image Optimization**: Use browser caching for card images
5. **Code Splitting**: Split routes with React.lazy if needed

### Initial Load Performance
- Target: < 2 seconds to interactive
- Minimize bundle size
- Optimize images (already handled by external CDN)

## Accessibility

### ARIA Labels
- Card buttons: `aria-label="Add {cardName} to deck"`
- Deck slots: `aria-label="Deck slot {index}"`
- Filter controls: Proper labels for all inputs

### Keyboard Navigation
- Tab through cards and deck slots
- Enter/Space to select cards
- Escape to close options menu

### Screen Reader Support
- Announce when cards added/removed
- Announce average elixir changes
- Announce notifications

## Deployment Considerations

### Environment Configuration
- `.env` file with `REACT_APP_API_BASE_URL`
- Default to `http://localhost:8000` for development
- Production URL to be configured

### Build Process
```bash
npm install
npm run build
# Outputs to frontend/build/
```

### Dependencies to Install
```json
{
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "react-router-dom": "^6.x",
    "typescript": "^5.x"
  }
}
```

## Implementation Notes

### Phase 1: Core Display (Priority 1)
- CardDisplay component with styling
- CardGallery with basic grid
- Fetch and display cards from API
- Loading and error states

### Phase 2: Filtering (Priority 2)
- CardFilters component
- Filter logic implementation
- Clear filters functionality

### Phase 3: Deck Building (Priority 3)
- DeckSlot component
- Add/remove card functionality
- Average elixir calculation
- Evolution slot management

### Phase 4: Deck Management (Priority 4)
- Save deck functionality
- SavedDecks component
- Load/rename/delete operations

### Phase 5: Polish (Priority 5)
- Notification system
- Responsive design refinements
- Accessibility improvements
- Performance optimizations
