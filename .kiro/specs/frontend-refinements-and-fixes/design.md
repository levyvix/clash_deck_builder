# Design Document

## Overview

This design document outlines the technical approach for refining the Clash Royale Deck Builder frontend with Material Design principles, implementing drag-and-drop functionality, fixing API endpoint bugs, preventing duplicate cards in decks, and containerizing the frontend with Docker. The solution focuses on enhancing user experience through smooth animations, intuitive interactions, and proper error handling while maintaining code quality and performance.

## Architecture

### Component Architecture

```
App (Root)
├── Router
│   ├── DeckBuilder (/)
│   │   ├── CardFilters
│   │   ├── CardGallery
│   │   │   └── CardDisplay (draggable)
│   │   ├── DeckArea
│   │   │   └── DeckSlot (droppable)
│   │   └── DeckStats
│   │   └── SaveDeckDialog
│   └── SavedDecks (/saved-decks)
│       └── DeckCard (clickable)
└── Notification (global)
```

### State Management

- **Local Component State**: For UI-specific state (hover, drag preview, dialog open/close)
- **Lifted State**: Deck data, cards, and notifications managed in App component
- **Derived State**: Average elixir, deck completion status, card availability

### API Layer

- **Service Module**: `services/api.ts` handles all HTTP requests
- **Error Handling**: Centralized error parsing and user-friendly messages
- **Retry Logic**: Automatic retry for network failures
- **Endpoint Verification**: Ensure all endpoints match backend routes exactly

## Components and Interfaces

### 1. Material Design System

#### Design Tokens (CSS Variables)

```css
/* Elevation Shadows */
--elevation-1: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
--elevation-2: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
--elevation-3: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23);
--elevation-4: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
--elevation-5: 0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22);

/* Motion Curves */
--ease-standard: cubic-bezier(0.4, 0.0, 0.2, 1);
--ease-decelerate: cubic-bezier(0.0, 0.0, 0.2, 1);
--ease-accelerate: cubic-bezier(0.4, 0.0, 1, 1);

/* Durations */
--duration-short: 200ms;
--duration-medium: 300ms;
--duration-long: 400ms;

/* Spacing (8px grid) */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
```

#### Button Styles

- **Contained**: Elevated background, primary color, white text
- **Outlined**: Border, transparent background, primary color text
- **Text**: No border, transparent background, primary color text
- **Ripple Effect**: Pseudo-element animation on click

#### Card Styling

- Base elevation: `--elevation-2`
- Hover elevation: `--elevation-4`
- Transition: `box-shadow var(--duration-short) var(--ease-standard)`
- Border radius: 8px
- Padding: `var(--spacing-md)`

### 2. Drag and Drop System

#### HTML5 Drag and Drop API

**Draggable Cards (CardDisplay)**

```typescript
interface DragData {
  cardId: number;
  sourceType: 'gallery' | 'deck';
  sourceIndex?: number; // For deck slots
}

// On drag start
const handleDragStart = (e: React.DragEvent, card: Card, sourceType: 'gallery' | 'deck', sourceIndex?: number) => {
  const dragData: DragData = { cardId: card.id, sourceType, sourceIndex };
  e.dataTransfer.setData('application/json', JSON.stringify(dragData));
  e.dataTransfer.effectAllowed = 'move';
  
  // Create ghost image
  const ghost = createGhostElement(card);
  e.dataTransfer.setDragImage(ghost, 50, 70);
  
  // Add dragging class for visual feedback
  e.currentTarget.classList.add('dragging');
};

const handleDragEnd = (e: React.DragEvent) => {
  e.currentTarget.classList.remove('dragging');
};
```

**Drop Targets (DeckSlot)**

```typescript
const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault(); // Allow drop
  e.dataTransfer.dropEffect = 'move';
  
  // Highlight drop target
  e.currentTarget.classList.add('drag-over');
};

const handleDragLeave = (e: React.DragEvent) => {
  e.currentTarget.classList.remove('drag-over');
};

const handleDrop = (e: React.DragEvent, targetSlotIndex: number) => {
  e.preventDefault();
  e.currentTarget.classList.remove('drag-over');
  
  const dragData: DragData = JSON.parse(e.dataTransfer.getData('application/json'));
  
  if (dragData.sourceType === 'gallery') {
    // Add card from gallery to deck slot
    onAddCardToSlot(dragData.cardId, targetSlotIndex);
  } else if (dragData.sourceType === 'deck') {
    // Swap cards between deck slots
    onSwapCards(dragData.sourceIndex!, targetSlotIndex);
  }
};
```

**Remove Drop Zone**

```typescript
// Special drop zone outside deck area for removing cards
const RemoveDropZone: React.FC = () => {
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const dragData: DragData = JSON.parse(e.dataTransfer.getData('application/json'));
    
    if (dragData.sourceType === 'deck' && dragData.sourceIndex !== undefined) {
      onRemoveCardFromDeck(dragData.sourceIndex);
    }
  };
  
  return (
    <div 
      className="remove-drop-zone"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      🗑️ Drag here to remove
    </div>
  );
};
```

### 3. Duplicate Card Prevention

#### Card Tracking State

```typescript
interface DeckBuilderState {
  deck: DeckSlot[]; // 8 slots
  cardsInDeck: Set<number>; // Track card IDs currently in deck
}

// When adding a card
const addCardToDeck = (card: Card, slotIndex: number) => {
  if (cardsInDeck.has(card.id)) {
    showNotification('Card already in deck', 'error');
    return;
  }
  
  // Add card to slot
  const newDeck = [...deck];
  newDeck[slotIndex] = { card, isEvolution: false };
  
  // Update tracking set
  const newCardsInDeck = new Set(cardsInDeck);
  newCardsInDeck.add(card.id);
  
  setDeck(newDeck);
  setCardsInDeck(newCardsInDeck);
};

// When removing a card
const removeCardFromDeck = (slotIndex: number) => {
  const cardId = deck[slotIndex]?.card?.id;
  if (!cardId) return;
  
  // Remove from slot
  const newDeck = [...deck];
  newDeck[slotIndex] = null;
  
  // Update tracking set
  const newCardsInDeck = new Set(cardsInDeck);
  newCardsInDeck.delete(cardId);
  
  setDeck(newDeck);
  setCardsInDeck(newCardsInDeck);
};
```

#### Visual Feedback in Gallery

```typescript
// In CardGallery component
const isCardInDeck = (cardId: number): boolean => {
  return cardsInDeck.has(cardId);
};

// Pass to CardDisplay
<CardDisplay
  card={card}
  inDeck={isCardInDeck(card.id)}
  disabled={isCardInDeck(card.id)}
  // ... other props
/>
```

```css
/* CardDisplay.css */
.card-display--in-deck {
  opacity: 0.5;
  pointer-events: none;
  position: relative;
}

.card-display--in-deck::after {
  content: '✓ In Deck';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(76, 175, 80, 0.9);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 600;
}
```

### 4. API Endpoint Fixes

#### Current Issues

1. **Save Deck**: Frontend calls `/decks` but may have incorrect payload format
2. **Fetch Decks**: Frontend calls `/decks` but gets 404

#### Root Cause Analysis

Based on backend code review:
- Backend routes are correctly defined at `/decks` (POST, GET)
- Issue likely: API base URL misconfiguration or CORS

#### Solution

**Verify API Base URL**

```typescript
// services/api.ts
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Add debug logging
console.log('API Base URL:', API_BASE_URL);

// Add endpoint verification function
export const verifyEndpoints = async () => {
  const endpoints = [
    { name: 'Health', url: `${API_BASE_URL}/health` },
    { name: 'Cards', url: `${API_BASE_URL}/cards/cards` },
    { name: 'Decks', url: `${API_BASE_URL}/decks` },
  ];
  
  for (const endpoint of endpoints) {
    try {
      const response = await fetch(endpoint.url);
      console.log(`${endpoint.name}: ${response.status}`);
    } catch (error) {
      console.error(`${endpoint.name}: Failed`, error);
    }
  }
};
```

**Fix Deck Payload Format**

```typescript
// Ensure payload matches backend Deck model
interface DeckPayload {
  name: string;
  cards: Array<{
    card_id: number;
    is_evolution: boolean;
  }>;
}

export const createDeck = async (deckName: string, deckSlots: DeckSlot[]) => {
  const payload: DeckPayload = {
    name: deckName,
    cards: deckSlots
      .filter(slot => slot !== null)
      .map(slot => ({
        card_id: slot.card.id,
        is_evolution: slot.isEvolution
      }))
  };
  
  console.log('Creating deck with payload:', payload);
  
  const response = await fetchWithTimeout(`${API_BASE_URL}/decks`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  
  return await handleApiResponse(response);
};
```

### 5. Smooth Animations

#### Animation Library

Use CSS transitions and keyframe animations (no external library needed)

#### Key Animations

**Card Add Animation**

```css
@keyframes cardAddToDeck {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(-20px);
  }
  60% {
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.deck-slot__card--entering {
  animation: cardAddToDeck var(--duration-medium) var(--ease-decelerate);
}
```

**Card Remove Animation**

```css
@keyframes cardRemoveFromDeck {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
}

.deck-slot__card--leaving {
  animation: cardRemoveFromDeck var(--duration-medium) var(--ease-accelerate);
}
```

**Gallery Filter Animation**

```css
@keyframes fadeInStagger {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-gallery__card {
  animation: fadeInStagger var(--duration-short) var(--ease-standard);
  animation-fill-mode: both;
}

/* Stagger delay */
.card-gallery__card:nth-child(1) { animation-delay: 0ms; }
.card-gallery__card:nth-child(2) { animation-delay: 30ms; }
.card-gallery__card:nth-child(3) { animation-delay: 60ms; }
/* ... up to 20 items */
```

**Hover Elevation**

```css
.card-display {
  box-shadow: var(--elevation-2);
  transition: box-shadow var(--duration-short) var(--ease-standard),
              transform var(--duration-short) var(--ease-standard);
}

.card-display:hover {
  box-shadow: var(--elevation-4);
  transform: translateY(-4px);
}
```

**Notification Slide-In**

```css
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOutRight {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

.notification--entering {
  animation: slideInRight 250ms var(--ease-decelerate);
}

.notification--leaving {
  animation: slideOutRight 250ms var(--ease-accelerate);
}
```

**Save Button Pulse (when deck complete)**

```css
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: var(--elevation-2);
  }
  50% {
    transform: scale(1.05);
    box-shadow: var(--elevation-4);
  }
}

.save-button--ready {
  animation: pulse 2s var(--ease-standard) infinite;
}
```

**Skeleton Shimmer**

```css
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #e0e0e0 50%,
    #f0f0f0 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite linear;
}
```

### 6. Frontend Docker Container

#### Multi-Stage Dockerfile

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # SPA routing - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Docker Compose Integration

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - app-network
    restart: unless-stopped

  backend:
    # ... existing backend config
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

#### .dockerignore

```
node_modules
build
.env.local
.git
.gitignore
README.md
npm-debug.log
.DS_Store
coverage
.vscode
```

#### Environment Variable Handling

For runtime configuration (since React builds are static):

```javascript
// public/env-config.js
window.ENV = {
  REACT_APP_API_BASE_URL: '${REACT_APP_API_BASE_URL}'
};
```

```html
<!-- public/index.html -->
<script src="%PUBLIC_URL%/env-config.js"></script>
```

```typescript
// src/config.ts
const getEnvVar = (key: string, defaultValue: string): string => {
  // Check window.ENV first (runtime), then process.env (build-time)
  return (window as any).ENV?.[key] || process.env[key] || defaultValue;
};

export const API_BASE_URL = getEnvVar('REACT_APP_API_BASE_URL', 'http://localhost:8000');
```

### 7. Elixir Icon Update

Replace lightning icon (⚡) with droplet icon (💧) or custom SVG:

```typescript
// CardDisplay.tsx
<span className="card-display__elixir">
  <span className="card-display__elixir-icon">💧</span>
  {card.elixir_cost}
</span>
```

Or use custom SVG:

```typescript
const ElixirDropletIcon: React.FC = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
    <path d="M8 0C8 0 4 5 4 9C4 11.2091 5.79086 13 8 13C10.2091 13 12 11.2091 12 9C12 5 8 0 8 0Z" />
  </svg>
);
```

### 8. Rarity Text Fix

Reduce font size to prevent clipping:

```css
.card-display__rarity {
  font-size: 0.75rem; /* Reduced from 0.875rem */
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
```

## Data Models

### DeckSlot

```typescript
interface DeckSlot {
  card: Card | null;
  isEvolution: boolean;
}
```

### DragData

```typescript
interface DragData {
  cardId: number;
  sourceType: 'gallery' | 'deck';
  sourceIndex?: number;
}
```

### DeckPayload (API)

```typescript
interface DeckPayload {
  name: string;
  cards: Array<{
    card_id: number;
    is_evolution: boolean;
  }>;
}
```

## Error Handling

### API Error Categories

1. **Network Errors**: "Cannot connect to server"
2. **404 Errors**: "Endpoint not found - check API configuration"
3. **400 Errors**: Display specific validation message from backend
4. **500 Errors**: "Server error, please try again"
5. **Timeout Errors**: "Request timed out"

### Error Recovery

- **Retry Button**: For network failures
- **Fallback UI**: Show last known good state
- **Debug Mode**: Console logging for development

## Testing Strategy

### Unit Tests

- Drag and drop event handlers
- Duplicate card prevention logic
- API payload formatting
- Animation trigger conditions

### Integration Tests

- Complete drag-and-drop flow
- Save deck with API call
- Load saved decks
- Error handling scenarios

### Manual Testing

- Test drag and drop on touch devices
- Verify animations are smooth (60fps)
- Test API endpoints with network throttling
- Verify Docker container builds and runs
- Test responsive behavior

### Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Considerations

- **Animation Performance**: Use `transform` and `opacity` for GPU acceleration
- **Drag Preview**: Use lightweight ghost element
- **Re-renders**: Memoize expensive calculations
- **Image Loading**: Lazy load card images in gallery
- **Docker Image Size**: Multi-stage build reduces final image size
