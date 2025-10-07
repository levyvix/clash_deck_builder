# Evolution Cards

The evolution card system allows users to mark specific cards in their deck for evolution, adding strategic depth to deck building.

## Overview

- Maximum 2 evolution slots per deck
- Only cards with evolution variants can be marked
- Visual indicators show evolution status
- Evolution data stored separately in database

## Identifying Evolution Cards

Cards with evolution capability have a non-null `image_url_evo` field:

```typescript
interface Card {
  id: number;
  name: string;
  image_url: string;          // Base card image
  image_url_evo: string | null;  // Evolution image (null if no evolution)
}

// Check if card can evolve
function canEvolve(card: Card): boolean {
  return card.image_url_evo !== null;
}
```

## Evolution Service

```typescript
// src/services/evolutionService.ts
export const evolutionService = {
  canEvolve(card: Card): boolean {
    return card.image_url_evo !== null;
  },

  getEvolutionCards(cards: Card[]): Card[] {
    return cards.filter(card => this.canEvolve(card));
  },

  validateEvolutionSlots(slots: DeckSlot[]): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    const evolutionSlots = slots.filter(s => s.isEvolution);

    if (evolutionSlots.length > 2) {
      errors.push('Maximum 2 evolution slots allowed');
    }

    evolutionSlots.forEach(slot => {
      if (!this.canEvolve(slot.card)) {
        errors.push(`${slot.card.name} cannot evolve`);
      }
    });

    return { valid: errors.length === 0, errors };
  }
};
```

## UI Components

### Evolution Badge

```typescript
function DeckSlot({ slot, onToggleEvolution }: Props) {
  return (
    <div className="deck-slot">
      <img src={slot.isEvolution ? slot.card.image_url_evo : slot.card.image_url} />

      {slot.isEvolution && (
        <div className="evolution-badge">EVO</div>
      )}

      {evolutionService.canEvolve(slot.card) && (
        <button onClick={onToggleEvolution}>
          {slot.isEvolution ? 'Remove Evolution' : 'Mark as Evolution'}
        </button>
      )}
    </div>
  );
}
```

### Evolution Filter

```typescript
function CardGallery() {
  const [showEvolutionOnly, setShowEvolutionOnly] = useState(false);

  const filteredCards = useMemo(() => {
    if (showEvolutionOnly) {
      return cards.filter(card => evolutionService.canEvolve(card));
    }
    return cards;
  }, [cards, showEvolutionOnly]);

  return (
    <div>
      <label>
        <input
          type="checkbox"
          checked={showEvolutionOnly}
          onChange={e => setShowEvolutionOnly(e.target.checked)}
        />
        Evolution Cards Only
      </label>

      {filteredCards.map(card => <CardDisplay key={card.id} card={card} />)}
    </div>
  );
}
```

## Backend Storage

### Database Format

```sql
CREATE TABLE decks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cards JSON NOT NULL,  -- [1, 2, 3, 4, 5, 6, 7, 8]
    evolution_slots JSON,  -- [1, 3]  (max 2)
    CONSTRAINT chk_evolution_slots_limit CHECK (JSON_LENGTH(evolution_slots) <= 2)
);
```

### Validation

```python
def validate_evolution_slots(cards: List[int], evolution_slots: List[int]) -> bool:
    # Evolution slots must be subset of cards
    if not all(evo_id in cards for evo_id in evolution_slots):
        raise ValueError("Evolution slots must be in main card list")

    # Maximum 2 evolution slots
    if len(evolution_slots) > 2:
        raise ValueError("Maximum 2 evolution slots allowed")

    # Cards must have evolution capability
    card_service = CardService()
    for evo_id in evolution_slots:
        card = card_service.get_card_by_id(evo_id)
        if card.image_url_evo is None:
            raise ValueError(f"Card {card.name} cannot evolve")

    return True
```

## Styling

```css
/* Evolution badge */
.evolution-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Evolution card glow */
.deck-slot--evolution {
  box-shadow: 0 0 12px rgba(102, 126, 234, 0.6);
  border: 2px solid #667eea;
}

/* Evolution toggle button */
.evolution-toggle {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-sm);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.evolution-toggle:hover {
  background: var(--color-primary-dark);
}

.evolution-toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

## Testing

```typescript
describe('Evolution Cards', () => {
  it('identifies evolution capable cards', () => {
    const evoCard = { id: 1, name: 'Knight', image_url_evo: 'url' };
    const normalCard = { id: 2, name: 'Fireball', image_url_evo: null };

    expect(evolutionService.canEvolve(evoCard)).toBe(true);
    expect(evolutionService.canEvolve(normalCard)).toBe(false);
  });

  it('enforces 2 evolution slot limit', () => {
    const slots = [
      { card: mockEvoCard(), isEvolution: true },
      { card: mockEvoCard(), isEvolution: true },
      { card: mockEvoCard(), isEvolution: true },  // 3rd - invalid
    ];

    const result = evolutionService.validateEvolutionSlots(slots);
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Maximum 2 evolution slots allowed');
  });

  it('prevents marking non-evolution cards', () => {
    const slot = { card: { image_url_evo: null }, isEvolution: true };

    const result = evolutionService.validateEvolutionSlots([slot]);
    expect(result.valid).toBe(false);
  });
});
```

## Current Evolution Cards

As of 2024, these cards have evolution variants:

- Knight
- Archers
- Skeletons
- Bats
- Firecracker
- Mortar
- Valkyrie
- And more...

Check `image_url_evo` field in card data for complete list.

## Related Documentation

- [Deck Management](deck-management.md) - Overall deck system
- [Cards API](../api/cards.md) - Card data structure
- [Frontend Architecture](../architecture/frontend.md) - Component design
