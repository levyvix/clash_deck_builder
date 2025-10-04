/**
 * Integration tests for DeckStorageService
 * 
 * Tests the service with real authentication context and storage interactions.
 */

import { DeckStorageService, createDeckStorageService, initializeDeckStorageService } from './deckStorageService';
import { Deck, DeckSlot, Card } from '../types';

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
  name: 'Integration Test Deck',
  slots: Array(8).fill(mockDeckSlot),
  average_elixir: 3.0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

describe('DeckStorageService Integration', () => {
  describe('createDeckStorageService', () => {
    it('should create service with auth provider function', () => {
      const authProvider = () => false;
      const service = createDeckStorageService(authProvider);
      
      expect(service).toBeInstanceOf(DeckStorageService);
    });
  });

  describe('initializeDeckStorageService', () => {
    it('should initialize global service instance', () => {
      const authProvider = () => true;
      
      // This should not throw
      expect(() => {
        initializeDeckStorageService(authProvider);
      }).not.toThrow();
    });
  });

  describe('Service with different auth states', () => {
    it('should handle anonymous user workflow', async () => {
      let isAuthenticated = false;
      const service = createDeckStorageService(() => isAuthenticated);
      
      // Check storage type for anonymous user
      const storageType = await service.getStorageType();
      expect(storageType).toBe('local');
      
      // Check ID detection
      expect(service.isLocalDeck('local_123_abc')).toBe(true);
      expect(service.isLocalDeck(1)).toBe(false);
    });

    it('should handle authenticated user workflow', async () => {
      let isAuthenticated = true;
      const service = createDeckStorageService(() => isAuthenticated);
      
      // Check ID detection
      expect(service.isLocalDeck('local_123_abc')).toBe(true);
      expect(service.isLocalDeck(1)).toBe(false);
      expect(service.isLocalDeck('123')).toBe(false);
    });

    it('should handle authentication state changes', async () => {
      let isAuthenticated = false;
      const service = createDeckStorageService(() => isAuthenticated);
      
      // Start as anonymous
      let storageType = await service.getStorageType();
      expect(storageType).toBe('local');
      
      // Change to authenticated
      isAuthenticated = true;
      
      // Storage type should reflect new state
      // Note: This will be 'server' since we don't have local decks in this test
      storageType = await service.getStorageType();
      expect(['server', 'mixed']).toContain(storageType);
    });
  });

  describe('Error handling', () => {
    it('should handle service creation with invalid auth provider', () => {
      // This should still work, just return false
      const service = createDeckStorageService(() => {
        throw new Error('Auth provider error');
      });
      
      expect(service).toBeInstanceOf(DeckStorageService);
    });
  });

  describe('Type safety', () => {
    it('should handle mixed ID types correctly', () => {
      const service = createDeckStorageService(() => false);
      
      // String IDs (local)
      expect(service.isLocalDeck('local_123456_abc123')).toBe(true);
      expect(service.isLocalDeck('local_')).toBe(true);
      
      // Numeric IDs (server)
      expect(service.isLocalDeck(1)).toBe(false);
      expect(service.isLocalDeck(0)).toBe(false);
      
      // Other string IDs (server)
      expect(service.isLocalDeck('123')).toBe(false);
      expect(service.isLocalDeck('deck_123')).toBe(false);
      expect(service.isLocalDeck('')).toBe(false);
    });
  });

  describe('Service configuration', () => {
    it('should work with different auth provider implementations', async () => {
      // Simple boolean provider
      const simpleService = createDeckStorageService(() => true);
      expect(await simpleService.getStorageType()).toMatch(/server|mixed/);
      
      // Complex provider with logic
      const complexService = createDeckStorageService(() => {
        const token = 'mock_token';
        return Boolean(token && token.length > 0);
      });
      expect(await complexService.getStorageType()).toMatch(/server|mixed/);
      
      // Provider that returns false
      const anonymousService = createDeckStorageService(() => false);
      expect(await anonymousService.getStorageType()).toBe('local');
    });
  });
});