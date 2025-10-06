// frontend/src/services/__tests__/cardCacheService.test.ts

import {
  cacheCards,
  getCachedCards,
  invalidateCardCache,
  getCardCacheStats
} from '../cardCacheService';

describe('Card Cache Service', () => {
  // Clear localStorage before each test
  beforeEach(() => {
    localStorage.clear();
  });

  // Clear localStorage after all tests
  afterAll(() => {
    localStorage.clear();
  });

  describe('cacheCards', () => {
    it('should cache cards to localStorage', () => {
      const cards = [
        { id: 1, name: 'Knight', elixir_cost: 3 },
        { id: 2, name: 'Archer', elixir_cost: 3 }
      ];

      cacheCards(cards);

      const cached = localStorage.getItem('clash_cards_cache');
      expect(cached).not.toBeNull();

      const parsed = JSON.parse(cached!);
      expect(parsed.data).toEqual(cards);
      expect(parsed.version).toBe('1.0');
      expect(parsed.timestamp).toBeDefined();
    });

    it('should overwrite existing cache', () => {
      const cards1 = [{ id: 1, name: 'Knight', elixir_cost: 3 }];
      const cards2 = [{ id: 2, name: 'Archer', elixir_cost: 3 }];

      cacheCards(cards1);
      cacheCards(cards2);

      const cached = getCachedCards();
      expect(cached).toEqual(cards2);
    });
  });

  describe('getCachedCards', () => {
    it('should return null if no cache exists', () => {
      const cached = getCachedCards();
      expect(cached).toBeNull();
    });

    it('should return cached cards if valid', () => {
      const cards = [
        { id: 1, name: 'Knight', elixir_cost: 3 },
        { id: 2, name: 'Archer', elixir_cost: 3 }
      ];

      cacheCards(cards);
      const cached = getCachedCards();

      expect(cached).toEqual(cards);
    });

    it('should return null for expired cache', () => {
      const cards = [{ id: 1, name: 'Knight', elixir_cost: 3 }];

      // Manually create an expired cache entry
      const expiredCache = {
        version: '1.0',
        timestamp: Date.now() - (25 * 60 * 60 * 1000), // 25 hours ago
        data: cards
      };

      localStorage.setItem('clash_cards_cache', JSON.stringify(expiredCache));

      const cached = getCachedCards();
      expect(cached).toBeNull();
    });

    it('should return null for version mismatch', () => {
      const cards = [{ id: 1, name: 'Knight', elixir_cost: 3 }];

      // Manually create cache with different version
      const oldCache = {
        version: '0.9',
        timestamp: Date.now(),
        data: cards
      };

      localStorage.setItem('clash_cards_cache', JSON.stringify(oldCache));

      const cached = getCachedCards();
      expect(cached).toBeNull();
    });

    it('should return null for corrupted cache data', () => {
      localStorage.setItem('clash_cards_cache', 'invalid json data');

      const cached = getCachedCards();
      expect(cached).toBeNull();
    });
  });

  describe('invalidateCardCache', () => {
    it('should remove cache from localStorage', () => {
      const cards = [{ id: 1, name: 'Knight', elixir_cost: 3 }];
      cacheCards(cards);

      expect(localStorage.getItem('clash_cards_cache')).not.toBeNull();

      invalidateCardCache();

      expect(localStorage.getItem('clash_cards_cache')).toBeNull();
    });

    it('should not throw error if cache does not exist', () => {
      expect(() => invalidateCardCache()).not.toThrow();
    });
  });

  describe('getCardCacheStats', () => {
    it('should return exists: false when no cache exists', () => {
      const stats = getCardCacheStats();
      expect(stats.exists).toBe(false);
    });

    it('should return cache statistics when cache exists', () => {
      const cards = [
        { id: 1, name: 'Knight', elixir_cost: 3 },
        { id: 2, name: 'Archer', elixir_cost: 3 }
      ];

      cacheCards(cards);

      const stats = getCardCacheStats();
      expect(stats.exists).toBe(true);
      expect(stats.cardCount).toBe(2);
      expect(stats.version).toBe('1.0');
      expect(stats.age).toBeDefined();
      expect(stats.ageFormatted).toBeDefined();
      expect(stats.isExpired).toBe(false);
    });

    it('should correctly identify expired cache', () => {
      const cards = [{ id: 1, name: 'Knight', elixir_cost: 3 }];

      // Manually create an expired cache entry
      const expiredCache = {
        version: '1.0',
        timestamp: Date.now() - (25 * 60 * 60 * 1000), // 25 hours ago
        data: cards
      };

      localStorage.setItem('clash_cards_cache', JSON.stringify(expiredCache));

      const stats = getCardCacheStats();
      expect(stats.exists).toBe(true);
      expect(stats.isExpired).toBe(true);
    });

    it('should format age correctly for hours and minutes', () => {
      const cards = [{ id: 1, name: 'Knight', elixir_cost: 3 }];

      // Manually create cache that is 2 hours and 30 minutes old
      const twoHoursThirtyMinutes = (2 * 60 * 60 * 1000) + (30 * 60 * 1000);
      const oldCache = {
        version: '1.0',
        timestamp: Date.now() - twoHoursThirtyMinutes,
        data: cards
      };

      localStorage.setItem('clash_cards_cache', JSON.stringify(oldCache));

      const stats = getCardCacheStats();
      expect(stats.ageFormatted).toMatch(/2h 30m/);
    });

    it('should format age correctly for minutes only', () => {
      const cards = [{ id: 1, name: 'Knight', elixir_cost: 3 }];
      cacheCards(cards);

      const stats = getCardCacheStats();
      expect(stats.ageFormatted).toMatch(/^\d+m$/);
    });
  });

  describe('Cache Integration', () => {
    it('should handle complete cache lifecycle', () => {
      const cards = [
        { id: 1, name: 'Knight', elixir_cost: 3 },
        { id: 2, name: 'Archer', elixir_cost: 3 }
      ];

      // 1. No cache initially
      expect(getCachedCards()).toBeNull();

      // 2. Cache cards
      cacheCards(cards);

      // 3. Retrieve cached cards
      const cached = getCachedCards();
      expect(cached).toEqual(cards);

      // 4. Check stats
      const stats = getCardCacheStats();
      expect(stats.exists).toBe(true);
      expect(stats.cardCount).toBe(2);

      // 5. Invalidate cache
      invalidateCardCache();

      // 6. Cache should be gone
      expect(getCachedCards()).toBeNull();
      expect(getCardCacheStats().exists).toBe(false);
    });
  });
});
