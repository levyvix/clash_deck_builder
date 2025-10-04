/**
 * Integration test for LocalStorageService with real deck data
 */

import { LocalStorageService, LocalStorageError } from './localStorageService';
import { Deck, DeckSlot, Card } from '../types';

describe('LocalStorageService Integration', () => {
  let service: LocalStorageService;
  let mockStorage: Record<string, string>;

  beforeEach(() => {
    // Create a simple storage mock
    mockStorage = {};
    
    const storageMock = {
      getItem: (key: string) => mockStorage[key] || null,
      setItem: (key: string, value: string) => {
        mockStorage[key] = value;
      },
      removeItem: (key: string) => {
        delete mockStorage[key];
      },
      clear: () => {
        mockStorage = {};
      },
    };

    Object.defineProperty(window, 'localStorage', {
      value: storageMock,
      writable: true,
      configurable: true,
    });

    Object.defineProperty(window, 'Storage', {
      value: function Storage() {},
      writable: true,
      configurable: true,
    });

    service = new LocalStorageService();
  });

  test('should handle deck with mixed card types and evolution slots', async () => {
    // Create realistic deck data with different card types
    const cards: Card[] = [
      { id: 1, name: 'Knight', elixir_cost: 3, rarity: 'Common', type: 'Troop', image_url: 'knight.jpg' },
      { id: 2, name: 'Archers', elixir_cost: 3, rarity: 'Common', type: 'Troop', image_url: 'archers.jpg' },
      { id: 3, name: 'Fireball', elixir_cost: 4, rarity: 'Rare', type: 'Spell', image_url: 'fireball.jpg' },
      { id: 4, name: 'Cannon', elixir_cost: 3, rarity: 'Common', type: 'Building', image_url: 'cannon.jpg' },
      { id: 5, name: 'Giant', elixir_cost: 5, rarity: 'Rare', type: 'Troop', image_url: 'giant.jpg' },
      { id: 6, name: 'Wizard', elixir_cost: 5, rarity: 'Rare', type: 'Troop', image_url: 'wizard.jpg' },
      { id: 7, name: 'Arrows', elixir_cost: 3, rarity: 'Common', type: 'Spell', image_url: 'arrows.jpg' },
      { id: 8, name: 'Minions', elixir_cost: 3, rarity: 'Common', type: 'Troop', image_url: 'minions.jpg' },
    ];

    const slots: DeckSlot[] = cards.map((card, index) => ({
      card,
      isEvolution: index < 2, // First two cards are evolution cards
    }));

    const deckData: Omit<Deck, 'id'> = {
      name: 'Mixed Deck',
      slots,
      average_elixir: 3.6,
    };

    // Save the deck
    const savedDeck = await service.saveLocalDeck(deckData);
    
    expect(savedDeck.id).toBeDefined();
    expect(savedDeck.name).toBe('Mixed Deck');
    expect(savedDeck.slots).toHaveLength(8);
    expect(savedDeck.slots[0].isEvolution).toBe(true);
    expect(savedDeck.slots[2].isEvolution).toBe(false);
    expect(savedDeck.storageType).toBe('local');

    // Retrieve and verify
    const decks = await service.getLocalDecks();
    expect(decks).toHaveLength(1);
    expect(decks[0].slots[0].card?.name).toBe('Knight');
    expect(decks[0].slots[0].isEvolution).toBe(true);
  });

  test('should handle deck limit enforcement', async () => {
    // Create 20 decks (the maximum)
    const promises = [];
    for (let i = 0; i < 20; i++) {
      const deckData: Omit<Deck, 'id'> = {
        name: `Deck ${i + 1}`,
        slots: Array(8).fill({
          card: { id: 1, name: 'Test Card', elixir_cost: 3, rarity: 'Common', type: 'Troop', image_url: 'test.jpg' },
          isEvolution: false,
        }),
        average_elixir: 3.0,
      };
      promises.push(service.saveLocalDeck(deckData));
    }

    await Promise.all(promises);

    // Verify we have 20 decks
    const decks = await service.getLocalDecks();
    expect(decks).toHaveLength(20);

    // Try to save the 21st deck - should fail
    const extraDeck: Omit<Deck, 'id'> = {
      name: 'Extra Deck',
      slots: Array(8).fill({
        card: { id: 1, name: 'Test Card', elixir_cost: 3, rarity: 'Common', type: 'Troop', image_url: 'test.jpg' },
        isEvolution: false,
      }),
      average_elixir: 3.0,
    };

    await expect(service.saveLocalDeck(extraDeck)).rejects.toThrow(LocalStorageError);
  });

  test('should handle empty slots in deck', async () => {
    // Create deck with some empty slots
    const slots: DeckSlot[] = [
      { card: { id: 1, name: 'Knight', elixir_cost: 3, rarity: 'Common', type: 'Troop', image_url: 'knight.jpg' }, isEvolution: false },
      { card: null, isEvolution: false },
      { card: { id: 2, name: 'Archers', elixir_cost: 3, rarity: 'Common', type: 'Troop', image_url: 'archers.jpg' }, isEvolution: true },
      { card: null, isEvolution: false },
      { card: null, isEvolution: false },
      { card: null, isEvolution: false },
      { card: null, isEvolution: false },
      { card: null, isEvolution: false },
    ];

    const deckData: Omit<Deck, 'id'> = {
      name: 'Partial Deck',
      slots,
      average_elixir: 2.0,
    };

    const savedDeck = await service.saveLocalDeck(deckData);
    
    expect(savedDeck.slots[0].card?.name).toBe('Knight');
    expect(savedDeck.slots[1].card).toBeNull();
    expect(savedDeck.slots[2].isEvolution).toBe(true);

    // Retrieve and verify null cards are preserved
    const decks = await service.getLocalDecks();
    expect(decks[0].slots[1].card).toBeNull();
    expect(decks[0].slots[2].card?.name).toBe('Archers');
  });

  test('should validate deck data structure', async () => {
    // Test invalid deck name
    const invalidDeck1 = {
      name: '',
      slots: Array(8).fill({ card: null, isEvolution: false }),
      average_elixir: 3.0,
    };

    await expect(service.saveLocalDeck(invalidDeck1)).rejects.toThrow('Invalid deck data provided');

    // Test invalid slots count
    const invalidDeck2 = {
      name: 'Test Deck',
      slots: Array(7).fill({ card: null, isEvolution: false }), // Only 7 slots
      average_elixir: 3.0,
    };

    await expect(service.saveLocalDeck(invalidDeck2)).rejects.toThrow('Invalid deck data provided');

    // Test invalid slot structure
    const invalidDeck3 = {
      name: 'Test Deck',
      slots: Array(8).fill({ card: null }), // Missing isEvolution
      average_elixir: 3.0,
    };

    await expect(service.saveLocalDeck(invalidDeck3)).rejects.toThrow('Invalid deck data provided');
  });
});