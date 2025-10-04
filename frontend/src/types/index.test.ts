/**
 * Tests for type definitions and type guards
 */

import {
  Deck,
  UnifiedDeck,
  LocalDeck,
  ServerDeck,
  isLocalDeck,
  isServerDeck,
  isLocalDeckId,
  isServerDeckId,
  hasStorageType,
  DeckInput,
  DeckUpdate,
  StorageStats
} from './index';

describe('Type Definitions', () => {
  describe('Type Guards', () => {
    test('isLocalDeck should correctly identify local decks', () => {
      const localDeck: LocalDeck = {
        id: 'local_123456_abc',
        name: 'Test Local Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'local',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      const serverDeck: ServerDeck = {
        id: 123,
        name: 'Test Server Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'server'
      };

      expect(isLocalDeck(localDeck)).toBe(true);
      expect(isLocalDeck(serverDeck)).toBe(false);
    });

    test('isServerDeck should correctly identify server decks', () => {
      const localDeck: LocalDeck = {
        id: 'local_123456_abc',
        name: 'Test Local Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'local',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      const serverDeck: ServerDeck = {
        id: 123,
        name: 'Test Server Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'server'
      };

      expect(isServerDeck(serverDeck)).toBe(true);
      expect(isServerDeck(localDeck)).toBe(false);
    });

    test('isLocalDeckId should correctly identify local deck IDs', () => {
      expect(isLocalDeckId('local_123456_abc')).toBe(true);
      expect(isLocalDeckId('local_789_def')).toBe(true);
      expect(isLocalDeckId(123)).toBe(false);
      expect(isLocalDeckId('regular_string')).toBe(false);
    });

    test('isServerDeckId should correctly identify server deck IDs', () => {
      expect(isServerDeckId(123)).toBe(true);
      expect(isServerDeckId('local_123456_abc')).toBe(false);
      expect(isServerDeckId('regular_string')).toBe(true); // Non-local strings are considered server IDs
    });

    test('hasStorageType should correctly identify decks with storage type', () => {
      const deckWithStorageType = {
        id: 123,
        name: 'Test Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'server' as const
      };

      const deckWithoutStorageType = {
        id: 123,
        name: 'Test Deck',
        slots: [],
        average_elixir: 3.5
      };

      expect(hasStorageType(deckWithStorageType)).toBe(true);
      expect(hasStorageType(deckWithoutStorageType)).toBe(false);
    });
  });

  describe('Type Compatibility', () => {
    test('Deck interface should support both numeric and string IDs', () => {
      const numericIdDeck: Deck = {
        id: 123,
        name: 'Numeric ID Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'server'
      };

      const stringIdDeck: Deck = {
        id: 'local_123456_abc',
        name: 'String ID Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'local'
      };

      // These should compile without errors
      expect(typeof numericIdDeck.id).toBe('number');
      expect(typeof stringIdDeck.id).toBe('string');
    });

    test('UnifiedDeck should work with both local and server decks', () => {
      const localUnifiedDeck: UnifiedDeck = {
        id: 'local_123456_abc',
        name: 'Local Unified Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'local'
      };

      const serverUnifiedDeck: UnifiedDeck = {
        id: 123,
        name: 'Server Unified Deck',
        slots: [],
        average_elixir: 3.5,
        storageType: 'server'
      };

      expect(localUnifiedDeck.storageType).toBe('local');
      expect(serverUnifiedDeck.storageType).toBe('server');
    });

    test('DeckInput should exclude ID and storage-specific fields', () => {
      const deckInput: DeckInput = {
        name: 'New Deck',
        slots: [],
        average_elixir: 3.5
      };

      // These properties should not be allowed on DeckInput
      // @ts-expect-error - id should not be allowed
      const invalidInput1: DeckInput = { ...deckInput, id: 123 };
      
      // @ts-expect-error - storageType should not be allowed
      const invalidInput2: DeckInput = { ...deckInput, storageType: 'local' };

      expect(deckInput.name).toBe('New Deck');
    });

    test('DeckUpdate should allow partial updates without ID and storageType', () => {
      const deckUpdate: DeckUpdate = {
        name: 'Updated Name'
      };

      const fullUpdate: DeckUpdate = {
        name: 'Updated Name',
        slots: [],
        average_elixir: 4.0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      // These properties should not be allowed on DeckUpdate
      // @ts-expect-error - id should not be allowed
      const invalidUpdate1: DeckUpdate = { ...deckUpdate, id: 123 };
      
      // @ts-expect-error - storageType should not be allowed
      const invalidUpdate2: DeckUpdate = { ...deckUpdate, storageType: 'local' };

      expect(deckUpdate.name).toBe('Updated Name');
      expect(fullUpdate.average_elixir).toBe(4.0);
    });
  });

  describe('Storage Statistics Types', () => {
    test('StorageStats should have correct structure', () => {
      const stats: StorageStats = {
        local: {
          deckCount: 5,
          maxDecks: 20,
          storageUsed: 1024,
          available: true
        },
        server: {
          deckCount: 10,
          available: true
        },
        total: 15,
        storageType: 'mixed'
      };

      expect(stats.local.deckCount).toBe(5);
      expect(stats.server.deckCount).toBe(10);
      expect(stats.total).toBe(15);
      expect(stats.storageType).toBe('mixed');
    });
  });
});