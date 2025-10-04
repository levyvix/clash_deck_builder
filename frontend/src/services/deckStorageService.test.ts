/**
 * Unit tests for DeckStorageService
 * 
 * Tests the unified interface for deck operations with both local and server storage.
 */

import { DeckStorageService, DeckStorageError } from './deckStorageService';
import { UnifiedDeck } from '../types';
import { localStorageService, LocalStorageError } from './localStorageService';
import * as api from './api';
import { Deck, DeckSlot, Card } from '../types';

// Mock dependencies
jest.mock('./localStorageService');
jest.mock('./api');

const mockLocalStorageService = localStorageService as jest.Mocked<typeof localStorageService>;
const mockApi = api as jest.Mocked<typeof api>;

// Test data
const mockCard: Card = {
  id: 1,
  name: 'Knight',
  elixir_cost: 3,
  rarity: 'Common',
  type: 'Troop',
  image_url: 'knight.png',
};

const mockDeckSlot: DeckSlot = {
  card: mockCard,
  isEvolution: false,
};

const mockDeck: Omit<Deck, 'id'> = {
  name: 'Test Deck',
  slots: Array(8).fill(mockDeckSlot),
  average_elixir: 3.0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockLocalDeck: UnifiedDeck = {
  ...mockDeck,
  id: 'local_123456_abc123',
  storageType: 'local',
};

const mockServerDeck: UnifiedDeck = {
  ...mockDeck,
  id: 1,
  storageType: 'server',
};

describe('DeckStorageService', () => {
  let service: DeckStorageService;
  let mockAuthProvider: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    mockAuthProvider = jest.fn();
    service = new DeckStorageService(mockAuthProvider);
  });

  describe('constructor', () => {
    it('should create service with auth provider', () => {
      expect(service).toBeInstanceOf(DeckStorageService);
    });
  });

  describe('getStorageType', () => {
    it('should return "local" for anonymous users', async () => {
      mockAuthProvider.mockReturnValue(false);
      
      const result = await service.getStorageType();
      
      expect(result).toBe('local');
    });

    it('should return "server" for authenticated users with no local decks', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockLocalStorageService.getLocalDecks.mockResolvedValue([]);
      
      const result = await service.getStorageType();
      
      expect(result).toBe('server');
    });

    it('should return "mixed" for authenticated users with local decks', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockLocalStorageService.getLocalDecks.mockResolvedValue([
        { ...mockLocalDeck, id: 'local_123', storageType: 'local' } as any
      ]);
      
      const result = await service.getStorageType();
      
      expect(result).toBe('mixed');
    });

    it('should return "server" when local storage fails for authenticated users', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockLocalStorageService.getLocalDecks.mockRejectedValue(new LocalStorageError('Storage unavailable', 'UNAVAILABLE'));
      
      const result = await service.getStorageType();
      
      expect(result).toBe('server');
    });
  });

  describe('isLocalDeck', () => {
    it('should return true for local deck IDs', () => {
      expect(service.isLocalDeck('local_123456_abc123')).toBe(true);
    });

    it('should return false for server deck IDs', () => {
      expect(service.isLocalDeck(1)).toBe(false);
      expect(service.isLocalDeck('123')).toBe(false);
    });
  });

  describe('getAllDecks', () => {
    it('should retrieve only local decks for anonymous users', async () => {
      mockAuthProvider.mockReturnValue(false);
      mockLocalStorageService.getLocalDecks.mockResolvedValue([
        { ...mockLocalDeck, id: 'local_123', storageType: 'local' } as any
      ]);
      
      const result = await service.getAllDecks();
      
      expect(result.localDecks).toHaveLength(1);
      expect(result.serverDecks).toHaveLength(0);
      expect(result.totalCount).toBe(1);
      expect(result.storageType).toBe('local');
    });

    it('should retrieve both local and server decks for authenticated users', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockLocalStorageService.getLocalDecks.mockResolvedValue([
        { ...mockLocalDeck, id: 'local_123', storageType: 'local' } as any
      ]);
      mockApi.fetchDecks.mockResolvedValue([mockServerDeck as any]);
      
      const result = await service.getAllDecks();
      
      expect(result.localDecks).toHaveLength(1);
      expect(result.serverDecks).toHaveLength(1);
      expect(result.totalCount).toBe(2);
      expect(result.storageType).toBe('mixed');
    });

    it('should handle local storage errors gracefully', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockLocalStorageService.getLocalDecks.mockRejectedValue(new LocalStorageError('Storage unavailable', 'UNAVAILABLE'));
      mockApi.fetchDecks.mockResolvedValue([mockServerDeck as any]);
      
      const result = await service.getAllDecks();
      
      expect(result.localDecks).toHaveLength(0);
      expect(result.serverDecks).toHaveLength(1);
      expect(result.totalCount).toBe(1);
    });

    it('should throw error when both storages fail for authenticated users', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockLocalStorageService.getLocalDecks.mockRejectedValue(new LocalStorageError('Local error', 'LOCAL_ERROR'));
      mockApi.fetchDecks.mockRejectedValue(new api.ApiError('Server error', 500));
      
      await expect(service.getAllDecks()).rejects.toThrow(DeckStorageError);
    });

    it('should handle non-critical local storage errors gracefully for anonymous users', async () => {
      mockAuthProvider.mockReturnValue(false);
      mockLocalStorageService.getLocalDecks.mockRejectedValue(new LocalStorageError('Local error', 'LOCAL_ERROR'));
      
      const result = await service.getAllDecks();
      expect(result).toEqual({
        localDecks: [],
        serverDecks: [],
        totalCount: 0,
        storageType: 'local'
      });
    });

    it('should handle all local storage errors gracefully for anonymous users', async () => {
      mockAuthProvider.mockReturnValue(false);
      mockLocalStorageService.getLocalDecks.mockRejectedValue(new LocalStorageError('Storage unavailable', 'STORAGE_UNAVAILABLE'));
      
      // Even critical errors should be handled gracefully to allow anonymous users to continue
      const result = await service.getAllDecks();
      expect(result).toEqual({
        localDecks: [],
        serverDecks: [],
        totalCount: 0,
        storageType: 'local'
      });
    });
  });

  describe('saveDeck', () => {
    it('should save to local storage for anonymous users', async () => {
      mockAuthProvider.mockReturnValue(false);
      mockLocalStorageService.saveLocalDeck.mockResolvedValue({
        ...mockLocalDeck,
        id: 'local_123',
        storageType: 'local'
      } as any);
      
      const result = await service.saveDeck(mockDeck);
      
      expect(mockLocalStorageService.saveLocalDeck).toHaveBeenCalledWith(mockDeck);
      expect(result.storageType).toBe('local');
      expect(result.id).toBe('local_123');
    });

    it('should save to server for authenticated users', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockApi.createDeck.mockResolvedValue({ ...mockServerDeck, id: 1 } as any);
      
      const result = await service.saveDeck(mockDeck);
      
      expect(mockApi.createDeck).toHaveBeenCalled();
      expect(result.storageType).toBe('server');
      expect(result.id).toBe(1);
    });

    it('should force local storage when forceLocal is true', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockLocalStorageService.saveLocalDeck.mockResolvedValue({
        ...mockLocalDeck,
        id: 'local_123',
        storageType: 'local'
      } as any);
      
      const result = await service.saveDeck(mockDeck, true);
      
      expect(mockLocalStorageService.saveLocalDeck).toHaveBeenCalledWith(mockDeck);
      expect(result.storageType).toBe('local');
    });

    it('should handle local storage errors', async () => {
      mockAuthProvider.mockReturnValue(false);
      mockLocalStorageService.saveLocalDeck.mockRejectedValue(new LocalStorageError('Quota exceeded', 'QUOTA_EXCEEDED'));
      
      await expect(service.saveDeck(mockDeck)).rejects.toThrow(DeckStorageError);
    });

    it('should handle server errors with graceful degradation', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockApi.createDeck.mockRejectedValue(new api.ApiError('Server error', 500));
      
      // With graceful degradation, server errors should fall back to local storage
      const result = await service.saveDeck(mockDeck);
      
      expect(result.storageType).toBe('local');
      expect(mockLocalStorageService.saveLocalDeck).toHaveBeenCalledWith(mockDeck);
    });
  });

  describe('updateDeck', () => {
    const updates = { name: 'Updated Deck' };

    it('should update local deck', async () => {
      const localId = 'local_123456_abc123';
      mockLocalStorageService.updateLocalDeck.mockResolvedValue({
        ...mockLocalDeck,
        id: localId,
        name: 'Updated Deck',
        storageType: 'local'
      } as any);
      
      const result = await service.updateDeck(localId, updates);
      
      expect(mockLocalStorageService.updateLocalDeck).toHaveBeenCalledWith(localId, updates);
      expect(result.name).toBe('Updated Deck');
      expect(result.storageType).toBe('local');
    });

    it('should update server deck', async () => {
      const serverId = 1;
      mockApi.updateDeck.mockResolvedValue({
        ...mockServerDeck,
        id: serverId,
        name: 'Updated Deck'
      } as any);
      
      const result = await service.updateDeck(serverId, updates);
      
      expect(mockApi.updateDeck).toHaveBeenCalledWith(serverId, updates);
      expect(result.name).toBe('Updated Deck');
      expect(result.storageType).toBe('server');
    });

    it('should handle local storage update errors', async () => {
      const localId = 'local_123456_abc123';
      mockLocalStorageService.updateLocalDeck.mockRejectedValue(new LocalStorageError('Deck not found', 'DECK_NOT_FOUND'));
      
      await expect(service.updateDeck(localId, updates)).rejects.toThrow(DeckStorageError);
    });

    it('should handle server update errors', async () => {
      const serverId = 1;
      mockApi.updateDeck.mockRejectedValue(new api.ApiError('Server error', 500));
      
      await expect(service.updateDeck(serverId, updates)).rejects.toThrow(DeckStorageError);
    });
  });

  describe('deleteDeck', () => {
    it('should delete local deck', async () => {
      const localId = 'local_123456_abc123';
      mockLocalStorageService.deleteLocalDeck.mockResolvedValue();
      
      await service.deleteDeck(localId);
      
      expect(mockLocalStorageService.deleteLocalDeck).toHaveBeenCalledWith(localId);
    });

    it('should delete server deck', async () => {
      const serverId = 1;
      mockApi.deleteDeck.mockResolvedValue(true);
      
      await service.deleteDeck(serverId);
      
      expect(mockApi.deleteDeck).toHaveBeenCalledWith(serverId);
    });

    it('should handle local storage delete errors', async () => {
      const localId = 'local_123456_abc123';
      mockLocalStorageService.deleteLocalDeck.mockRejectedValue(new LocalStorageError('Deck not found', 'DECK_NOT_FOUND'));
      
      await expect(service.deleteDeck(localId)).rejects.toThrow(DeckStorageError);
    });

    it('should handle server delete errors', async () => {
      const serverId = 1;
      mockApi.deleteDeck.mockRejectedValue(new api.ApiError('Server error', 500));
      
      await expect(service.deleteDeck(serverId)).rejects.toThrow(DeckStorageError);
    });
  });

  describe('getDeck', () => {
    it('should get local deck by ID', async () => {
      const localId = 'local_123456_abc123';
      mockLocalStorageService.getLocalDecks.mockResolvedValue([
        { ...mockLocalDeck, id: localId, storageType: 'local' } as any
      ]);
      
      const result = await service.getDeck(localId);
      
      expect(result).toBeTruthy();
      expect(result?.id).toBe(localId);
      expect(result?.storageType).toBe('local');
    });

    it('should get server deck by ID', async () => {
      const serverId = 1;
      mockApi.fetchDecks.mockResolvedValue([
        { ...mockServerDeck, id: serverId } as any
      ]);
      
      const result = await service.getDeck(serverId);
      
      expect(result).toBeTruthy();
      expect(result?.id).toBe(serverId);
      expect(result?.storageType).toBe('server');
    });

    it('should return null for non-existent deck', async () => {
      const localId = 'local_nonexistent';
      mockLocalStorageService.getLocalDecks.mockResolvedValue([]);
      
      const result = await service.getDeck(localId);
      
      expect(result).toBeNull();
    });

    it('should handle storage errors gracefully', async () => {
      const localId = 'local_123456_abc123';
      mockLocalStorageService.getLocalDecks.mockRejectedValue(new LocalStorageError('Storage error', 'STORAGE_ERROR'));
      
      const result = await service.getDeck(localId);
      
      expect(result).toBeNull();
    });
  });

  describe('clearLocalDecks', () => {
    it('should clear all local decks', async () => {
      mockLocalStorageService.clearAllLocalDecks.mockResolvedValue();
      
      await service.clearLocalDecks();
      
      expect(mockLocalStorageService.clearAllLocalDecks).toHaveBeenCalled();
    });

    it('should handle clear errors', async () => {
      mockLocalStorageService.clearAllLocalDecks.mockRejectedValue(new LocalStorageError('Clear failed', 'CLEAR_FAILED'));
      
      await expect(service.clearLocalDecks()).rejects.toThrow(DeckStorageError);
    });
  });

  describe('getStorageStats', () => {
    it('should return storage statistics', async () => {
      mockAuthProvider.mockReturnValue(true);
      mockLocalStorageService.getStorageStats.mockResolvedValue({
        deckCount: 2,
        maxDecks: 20,
        storageUsed: 1024,
        lastModified: '2024-01-01T00:00:00Z',
      });
      mockApi.fetchDecks.mockResolvedValue([mockServerDeck as any]);
      
      const result = await service.getStorageStats();
      
      expect(result.local.deckCount).toBe(2);
      expect(result.local.available).toBe(true);
      expect(result.server.deckCount).toBe(1);
      expect(result.server.available).toBe(true);
      expect(result.total).toBe(3);
    });

    it('should handle storage errors in stats', async () => {
      mockAuthProvider.mockReturnValue(false);
      mockLocalStorageService.getStorageStats.mockRejectedValue(new LocalStorageError('Stats failed', 'STATS_FAILED'));
      
      const result = await service.getStorageStats();
      
      expect(result.local.available).toBe(false);
      expect(result.server.available).toBe(false);
      expect(result.total).toBe(0);
    });
  });
});