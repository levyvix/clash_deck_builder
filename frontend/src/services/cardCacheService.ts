// frontend/src/services/cardCacheService.ts

/**
 * Card Cache Service
 *
 * Provides localStorage-based caching for card data to reduce API calls.
 * Cards rarely change, so we cache them with a 24-hour TTL.
 */

const CACHE_KEY = 'clash_cards_cache';
const CACHE_VERSION = '1.0';
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

interface CachedCards {
  version: string;
  timestamp: number;
  data: any[];
}

/**
 * Save cards to localStorage cache with timestamp
 */
export const cacheCards = (cards: any[]): void => {
  try {
    const cacheData: CachedCards = {
      version: CACHE_VERSION,
      timestamp: Date.now(),
      data: cards
    };

    localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
    console.log(`✅ Cached ${cards.length} cards to localStorage`);
  } catch (error) {
    console.warn('⚠️ Failed to cache cards to localStorage:', error);
    // If localStorage is full, clear old cache and retry
    if (error instanceof DOMException && error.name === 'QuotaExceededError') {
      invalidateCardCache();
      try {
        const cacheData: CachedCards = {
          version: CACHE_VERSION,
          timestamp: Date.now(),
          data: cards
        };
        localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
      } catch (retryError) {
        console.error('❌ Failed to cache cards even after clearing cache:', retryError);
      }
    }
  }
};

/**
 * Retrieve cards from localStorage cache if valid
 *
 * @returns Cached cards if valid, null otherwise
 */
export const getCachedCards = (): any[] | null => {
  try {
    const cached = localStorage.getItem(CACHE_KEY);

    if (!cached) {
      console.log('📭 No cached cards found');
      return null;
    }

    const cacheData: CachedCards = JSON.parse(cached);

    // Check version compatibility
    if (cacheData.version !== CACHE_VERSION) {
      console.log('🔄 Cache version mismatch, invalidating cache');
      invalidateCardCache();
      return null;
    }

    // Check if cache has expired
    const age = Date.now() - cacheData.timestamp;
    if (age > CACHE_TTL) {
      const hours = Math.floor(age / (60 * 60 * 1000));
      console.log(`⏰ Cache expired (${hours} hours old), fetching fresh data`);
      invalidateCardCache();
      return null;
    }

    // Cache is valid
    const ageMinutes = Math.floor(age / (60 * 1000));
    console.log(`✅ Using cached cards (${ageMinutes} minutes old, ${cacheData.data.length} cards)`);
    return cacheData.data;

  } catch (error) {
    console.warn('⚠️ Error reading card cache:', error);
    invalidateCardCache();
    return null;
  }
};

/**
 * Invalidate card cache
 */
export const invalidateCardCache = (): void => {
  try {
    localStorage.removeItem(CACHE_KEY);
    console.log('🗑️ Card cache invalidated');
  } catch (error) {
    console.warn('⚠️ Failed to invalidate card cache:', error);
  }
};

/**
 * Get cache statistics
 */
export const getCardCacheStats = (): {
  exists: boolean;
  age?: number;
  ageFormatted?: string;
  cardCount?: number;
  version?: string;
  isExpired?: boolean;
} => {
  try {
    const cached = localStorage.getItem(CACHE_KEY);

    if (!cached) {
      return { exists: false };
    }

    const cacheData: CachedCards = JSON.parse(cached);
    const age = Date.now() - cacheData.timestamp;
    const isExpired = age > CACHE_TTL;

    // Format age as human-readable string
    const hours = Math.floor(age / (60 * 60 * 1000));
    const minutes = Math.floor((age % (60 * 60 * 1000)) / (60 * 1000));
    const ageFormatted = hours > 0
      ? `${hours}h ${minutes}m`
      : `${minutes}m`;

    return {
      exists: true,
      age,
      ageFormatted,
      cardCount: cacheData.data.length,
      version: cacheData.version,
      isExpired
    };

  } catch (error) {
    return { exists: false };
  }
};
