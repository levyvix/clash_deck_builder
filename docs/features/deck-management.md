# Deck Management

Complete guide to the deck management system in the Clash Royale Deck Builder.

## Overview

Users can build, save, and manage Clash Royale decks with these features:
- Build decks with exactly 8 cards
- Save up to 20 decks per user
- Mark up to 2 cards as evolution slots
- View, edit, and delete saved decks
- Automatic average elixir cost calculation

## Data Formats

### Frontend Format

```typescript
interface DeckSlot {
  card: Card;
  isEvolution: boolean;
}

interface Deck {
  id?: number;
  name: string;
  slots: DeckSlot[];  // Array of 8 slots
  averageElixir?: number;
}
```

### Backend Format

```json
{
  "id": 123,
  "name": "My Deck",
  "cards": [26000000, 26000001, ...],  // 8 card IDs
  "evolution_slots": [26000001],       // 0-2 card IDs
  "average_elixir": 3.5
}
```

### Transformation

```typescript
// Frontend ’ Backend
function transformDeckForBackend(deck: Deck) {
  return {
    name: deck.name,
    cards: deck.slots.map(slot => slot.card.id),
    evolution_slots: deck.slots
      .filter(slot => slot.isEvolution)
      .map(slot => slot.card.id)
  };
}

// Backend ’ Frontend
function transformDeckForFrontend(backendDeck, allCards) {
  const cardMap = new Map(allCards.map(c => [c.id, c]));

  return {
    id: backendDeck.id,
    name: backendDeck.name,
    averageElixir: backendDeck.average_elixir,
    slots: backendDeck.cards.map(cardId => ({
      card: cardMap.get(cardId),
      isEvolution: backendDeck.evolution_slots.includes(cardId)
    }))
  };
}
```

## Operations

### Create Deck

**Frontend:**
```typescript
async function saveDeck() {
  if (deckSlots.filter(s => s.card).length !== 8) {
    showError('Deck must have 8 cards');
    return;
  }

  const backendDeck = transformDeckForBackend({ name: deckName, slots: deckSlots });
  const savedDeck = await createDeck(backendDeck);
  showSuccess('Deck saved!');
}
```

**Backend:**
```python
async def create_deck(self, deck: Deck, user: User) -> Deck:
    if len(await self.get_user_decks(user)) >= 20:
        raise DeckLimitExceededError("Maximum 20 decks allowed")

    cards = self.card_service.get_cards_by_ids(deck.cards)
    deck.average_elixir = sum(c.elixir_cost for c in cards) / 8

    # Save to database
    cursor.execute("""
        INSERT INTO decks (user_id, name, cards, evolution_slots, average_elixir)
        VALUES (%s, %s, %s, %s, %s)
    """, (user.id, deck.name, json.dumps(deck.cards),
          json.dumps(deck.evolution_slots), deck.average_elixir))

    return deck
```

## Business Rules

- Exactly 8 cards required
- Maximum 20 decks per user
- Up to 2 evolution slots
- Evolution cards must be in main card list
- Average elixir auto-calculated

## Storage

### Anonymous Users
```typescript
// localStorage
localStorage.setItem('decks', JSON.stringify(decks));
```

### Authenticated Users
```typescript
// Server API
await fetch('/api/decks', { method: 'POST', body: JSON.stringify(deck) });
```

### Migration on Login
```typescript
// Migrate local decks to server when user logs in
const localDecks = localStorage.getItem('decks');
for (const deck of localDecks) {
  await createDeck(deck);
}
localStorage.removeItem('decks');
```

## Related Documentation

- [Evolution Cards](evolution-cards.md)
- [Anonymous Mode](anonymous-mode.md)
- [Decks API](../api/decks.md)
