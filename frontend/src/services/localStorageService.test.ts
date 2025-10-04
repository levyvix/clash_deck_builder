/**
 * Simple test to verify LocalStorageService basic functionality
 */

import { LocalStorageService } from './localStorageService';
import { Deck, DeckSlot, Card } from '../types';

// Mock card for testing
const mockCard: Card = {
  id: 1,
  name: 'Test Card',
  elixir_cost: 3,
  rarity: 'Common',
  type: 'Troop',
  image_url: 'test.jpg',
};

// Mock deck slot
const mockSlot: DeckSlot = {
  card: mockCard,
  isEvolution: false,
};

// Mock deck data
const mockDeckData: Omit<Deck, 'id'> = {
  name: 'Test Deck',
  slots: Array(8).fill(mockSlot),
  average_elixir: 3.5,
};

describe('LocalStorageService Basic Functionality', () => {
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

  test('should check localStorage availability', () => {
    expect(service.isLocalStorageAvailable()).toBe(true);
  });

  test('should generate unique IDs', () => {
    const id1 = service.getNextLocalId();
    const id2 = service.getNextLocalId();
    
    expect(id1).toMatch(/^local_\d+_[a-z0-9]+$/);
    expect(id2).toMatch(/^local_\d+_[a-z0-9]+$/);
    expect(id1).not.toBe(id2);
  });

  test('should save and retrieve a deck', async () => {
    const savedDeck = await service.saveLocalDeck(mockDeckData);
    
    expect(savedDeck.id).toBeDefined();
    expect(savedDeck.name).toBe(mockDeckData.name);
    expect(savedDeck.storageType).toBe('local');
    
    const decks = await service.getLocalDecks();
    expect(decks).toHaveLength(1);
    expect(decks[0].id).toBe(savedDeck.id);
  });

  test('should update a deck', async () => {
    const savedDeck = await service.saveLocalDeck(mockDeckData);
    const updatedDeck = await service.updateLocalDeck(savedDeck.id, { name: 'Updated Deck' });
    
    expect(updatedDeck.name).toBe('Updated Deck');
    expect(updatedDeck.id).toBe(savedDeck.id);
  });

  test('should delete a deck', async () => {
    const savedDeck = await service.saveLocalDeck(mockDeckData);
    
    await service.deleteLocalDeck(savedDeck.id);
    
    const decks = await service.getLocalDecks();
    expect(decks).toHaveLength(0);
  });

  test('should get storage stats', async () => {
    await service.saveLocalDeck(mockDeckData);
    
    const stats = await service.getStorageStats();
    
    expect(stats.deckCount).toBe(1);
    expect(stats.maxDecks).toBe(20);
    expect(stats.storageUsed).toBeGreaterThan(0);
    expect(stats.lastModified).toBeDefined();
  });
});