/**
 * Unified Deck Storage Service
 * 
 * Provides a single interface for deck operations regardless of storage type.
 * Abstracts local storage (anonymous users) and server storage (authenticated users).
 * Handles mixed storage scenarios where users have both local and server decks.
 */

import { 
  Deck, 
  DeckSlot, 
  StorageType, 
  UnifiedDeck, 
  LocalDeck, 
  DeckStorageResult,
  isLocalDeckId,
  DeckInput,
  DeckUpdate,
  StorageStats
} from '../types';
import { localStorageService, LocalStorageError } from './localStorageService';
import { fetchDecks, createDeck, updateDeck, deleteDeck, DeckPayload, ApiError } from './api';
import { withRetry, withGracefulDegradation, ErrorHandlingService } from './errorHandlingService';

// Custom error class for deck storage operations
export class DeckStorageError extends Error {
  constructor(
    message: string,
    public code: string,
    public storageType?: 'local' | 'server'
  ) {
    super(message);
    this.name = 'DeckStorageError';
  }
}

/**
 * Unified Deck Storage Service Class
 * 
 * Provides a single interface for deck operations that works with both
 * local storage (anonymous users) and server storage (authenticated users).
 */
export class DeckStorageService {
  private authStateProvider: () => boolean;

  constructor(authStateProvider: () => boolean) {
    this.authStateProvider = authStateProvider;
  }

  /**
   * Check if user is currently authenticated
   */
  private isAuthenticated(): boolean {
    return this.authStateProvider();
  }

  /**
   * Determine the current storage type based on authentication and available data
   */
  async getStorageType(): Promise<StorageType> {
    const isAuth = this.isAuthenticated();
    
    if (!isAuth) {
      // Anonymous user - only local storage
      return 'local';
    }

    // Authenticated user - check if they have local decks too
    try {
      const localDecks = await localStorageService.getLocalDecks();
      if (localDecks.length > 0) {
        return 'mixed'; // Has both local and server storage
      }
    } catch (error) {
      // Local storage not available or error - server only
      console.warn('Local storage check failed:', error);
    }

    return 'server';
  }

  /**
   * Check if a deck ID belongs to local storage
   */
  isLocalDeck(id: string | number): boolean {
    return isLocalDeckId(id);
  }

  /**
   * Transform local deck to unified format
   */
  private transformLocalDeck(localDeck: LocalDeck): UnifiedDeck {
    return {
      ...localDeck,
      storageType: 'local' as const,
    };
  }

  /**
   * Transform server deck to unified format
   */
  private transformServerDeck(serverDeck: Deck): UnifiedDeck {
    return {
      ...serverDeck,
      id: serverDeck.id || 0, // Ensure ID is present
      storageType: 'server' as const,
    };
  }

  /**
   * Convert unified deck slots to server format for API calls
   */
  private convertSlotsToServerFormat(slots: DeckSlot[]): { cards: any[], evolution_slots: any[] } {
    const cards: any[] = [];
    const evolution_slots: any[] = [];

    slots.forEach(slot => {
      if (slot.card) {
        cards.push(slot.card);
        if (slot.isEvolution) {
          evolution_slots.push(slot.card);
        }
      }
    });

    return { cards, evolution_slots };
  }

  /**
   * Get all decks from both local and server storage with retry logic
   */
  async getAllDecks(): Promise<DeckStorageResult> {
    const localDecks: UnifiedDeck[] = [];
    const serverDecks: UnifiedDeck[] = [];
    let localError: Error | null = null;
    let serverError: Error | null = null;

    // Always try to get local decks with retry (they might exist even for authenticated users)
    try {
      const rawLocalDecks = await withRetry(
        () => localStorageService.getLocalDecks(),
        { maxAttempts: 2, baseDelay: 300 }
      );
      localDecks.push(...rawLocalDecks.map(deck => this.transformLocalDeck(deck)));
      console.log(`📱 Retrieved ${localDecks.length} local decks`);
    } catch (error) {
      localError = error instanceof Error ? error : new Error('Unknown local storage error');
      console.warn('Failed to retrieve local decks:', localError.message);
    }

    // Try to get server decks if authenticated with retry
    if (this.isAuthenticated()) {
      try {
        const rawServerDecks = await withRetry(
          () => fetchDecks(),
          { maxAttempts: 3, baseDelay: 1000 }
        );
        serverDecks.push(...rawServerDecks.map((deck: Deck) => this.transformServerDeck(deck)));
        console.log(`☁️ Retrieved ${serverDecks.length} server decks`);
      } catch (error) {
        serverError = error instanceof Error ? error : new Error('Unknown server error');
        console.warn('Failed to retrieve server decks:', serverError.message);
      }
    }

    // Determine storage type
    const storageType = await this.getStorageType();
    const totalCount = localDecks.length + serverDecks.length;

    console.log(`🎯 Total decks: ${totalCount} (${localDecks.length} local, ${serverDecks.length} server)`);
    console.log(`📊 Storage type: ${storageType}`);

    // Enhanced error handling with graceful degradation
    if (localError && serverError && this.isAuthenticated()) {
      // Both failed for authenticated user - this is critical
      throw new DeckStorageError(
        'Cannot access any deck storage. Please check your connection and browser settings.',
        'STORAGE_UNAVAILABLE'
      );
    }

    if (localError && !this.isAuthenticated()) {
      // Local storage failed for anonymous user - check if it's a critical error
      const isCriticalError = (localError instanceof LocalStorageError && 
          (localError.code === 'STORAGE_UNAVAILABLE' || localError.code === 'QUOTA_EXCEEDED')) ||
          (localError.message && localError.message.includes('Storage unavailable'));
      
      if (isCriticalError) {
        // These are critical errors that prevent anonymous users from using the app
        throw new DeckStorageError(
          localError instanceof LocalStorageError ? localError.message : 'Local storage is not available. Please enable cookies and local storage in your browser.',
          localError instanceof LocalStorageError ? localError.code : 'LOCAL_STORAGE_UNAVAILABLE',
          'local'
        );
      } else {
        // For other errors (like data corruption), continue with empty data
        console.warn('Local storage error for anonymous user, continuing with empty data:', localError.message);
      }
    }

    // If only one storage type failed, continue with available data
    // This provides graceful degradation
    if (localError && this.isAuthenticated() && serverDecks.length > 0) {
      console.warn('Local storage unavailable, but server decks are available');
    }

    if (serverError && this.isAuthenticated() && localDecks.length > 0) {
      console.warn('Server unavailable, but local decks are available');
    }

    return {
      localDecks,
      serverDecks,
      totalCount,
      storageType,
    };
  }

  /**
   * Save a deck to the appropriate storage based on authentication status
   * Includes retry logic and graceful degradation
   */
  async saveDeck(deck: DeckInput, forceLocal: boolean = false): Promise<UnifiedDeck> {
    const isAuth = this.isAuthenticated();
    
    // Determine target storage
    const useLocalStorage = !isAuth || forceLocal;

    if (useLocalStorage) {
      // For local storage, use retry mechanism
      return await withRetry(
        async () => {
          console.log(`💾 Saving deck "${deck.name}" to local storage`);
          const savedDeck = await localStorageService.saveLocalDeck(deck);
          return this.transformLocalDeck(savedDeck);
        },
        { maxAttempts: 2, baseDelay: 500 } // Quick retry for local operations
      ).catch(error => {
        if (error instanceof LocalStorageError) {
          throw new DeckStorageError(
            error.message,
            error.code,
            'local'
          );
        }
        throw new DeckStorageError(
          `Failed to save deck to local storage: ${error instanceof Error ? error.message : 'Unknown error'}`,
          'LOCAL_SAVE_FAILED',
          'local'
        );
      });
    } else {
      // For authenticated users, try server first with fallback to local
      return await withGracefulDegradation(
        // Primary: Save to server with retry
        async () => {
          return await withRetry(async () => {
            console.log(`☁️ Saving deck "${deck.name}" to server`);
            
            // Convert slots to server format
            const { cards, evolution_slots } = this.convertSlotsToServerFormat(deck.slots);
            
            const payload: DeckPayload = {
              name: deck.name,
              cards,
              evolution_slots,
              average_elixir: deck.average_elixir,
            };

            const savedDeck: Deck = await createDeck(payload);
            return this.transformServerDeck(savedDeck);
          });
        },
        // Fallback: Save to local storage
        async () => {
          console.log(`💾 Falling back to local storage for deck "${deck.name}"`);
          const savedDeck = await localStorageService.saveLocalDeck(deck);
          return this.transformLocalDeck(savedDeck);
        },
        {
          primaryDescription: 'server save',
          fallbackDescription: 'local storage save',
          onFallback: (error) => {
            console.warn('Server save failed, using local storage fallback:', error.message);
          }
        }
      ).catch(error => {
        // If both server and local storage fail, provide appropriate error
        const errorInfo = ErrorHandlingService.analyzeError(error);
        throw new DeckStorageError(
          errorInfo.message,
          errorInfo.code,
          'server'
        );
      });
    }
  }

  /**
   * Update an existing deck
   */
  async updateDeck(id: string | number, updates: DeckUpdate): Promise<UnifiedDeck> {
    const isLocal = this.isLocalDeck(id);

    if (isLocal) {
      try {
        console.log(`✏️ Updating local deck ${id}`);
        const updatedDeck = await localStorageService.updateLocalDeck(id as string, updates);
        return this.transformLocalDeck(updatedDeck);
      } catch (error) {
        if (error instanceof LocalStorageError) {
          throw new DeckStorageError(
            error.message,
            error.code,
            'local'
          );
        }
        throw new DeckStorageError(
          `Failed to update local deck: ${error instanceof Error ? error.message : 'Unknown error'}`,
          'LOCAL_UPDATE_FAILED',
          'local'
        );
      }
    } else {
      try {
        console.log(`☁️ Updating server deck ${id}`);
        
        // Convert slots to server format if slots are being updated
        let payload: any = { ...updates };
        if (updates.slots) {
          const { cards, evolution_slots } = this.convertSlotsToServerFormat(updates.slots);
          payload = {
            ...payload,
            cards,
            evolution_slots,
          };
          delete payload.slots; // Remove slots from payload as server expects cards/evolution_slots
        }

        const updatedDeck = await updateDeck(id as number, payload);
        return this.transformServerDeck(updatedDeck);
      } catch (error) {
        if (error instanceof ApiError) {
          throw new DeckStorageError(
            error.message,
            'SERVER_UPDATE_FAILED',
            'server'
          );
        }
        throw new DeckStorageError(
          `Failed to update server deck: ${error instanceof Error ? error.message : 'Unknown error'}`,
          'SERVER_UPDATE_FAILED',
          'server'
        );
      }
    }
  }

  /**
   * Delete a deck by ID
   */
  async deleteDeck(id: string | number): Promise<void> {
    const isLocal = this.isLocalDeck(id);

    if (isLocal) {
      try {
        console.log(`🗑️ Deleting local deck ${id}`);
        await localStorageService.deleteLocalDeck(id as string);
      } catch (error) {
        if (error instanceof LocalStorageError) {
          throw new DeckStorageError(
            error.message,
            error.code,
            'local'
          );
        }
        throw new DeckStorageError(
          `Failed to delete local deck: ${error instanceof Error ? error.message : 'Unknown error'}`,
          'LOCAL_DELETE_FAILED',
          'local'
        );
      }
    } else {
      try {
        console.log(`☁️ Deleting server deck ${id}`);
        await deleteDeck(id as number);
      } catch (error) {
        if (error instanceof ApiError) {
          throw new DeckStorageError(
            error.message,
            'SERVER_DELETE_FAILED',
            'server'
          );
        }
        throw new DeckStorageError(
          `Failed to delete server deck: ${error instanceof Error ? error.message : 'Unknown error'}`,
          'SERVER_DELETE_FAILED',
          'server'
        );
      }
    }
  }

  /**
   * Get a single deck by ID from appropriate storage
   */
  async getDeck(id: string | number): Promise<UnifiedDeck | null> {
    const isLocal = this.isLocalDeck(id);

    if (isLocal) {
      try {
        const localDecks = await localStorageService.getLocalDecks();
        const deck = localDecks.find((d: LocalDeck) => d.id === id);
        return deck ? this.transformLocalDeck(deck) : null;
      } catch (error) {
        console.warn(`Failed to get local deck ${id}:`, error);
        return null;
      }
    } else {
      try {
        // For server decks, we need to fetch all and find the specific one
        // This could be optimized with a dedicated API endpoint
        const serverDecks = await fetchDecks();
        const deck = serverDecks.find((d: Deck) => d.id === id);
        return deck ? this.transformServerDeck(deck) : null;
      } catch (error) {
        console.warn(`Failed to get server deck ${id}:`, error);
        return null;
      }
    }
  }

  /**
   * Clear all local decks (utility method)
   */
  async clearLocalDecks(): Promise<void> {
    try {
      await localStorageService.clearAllLocalDecks();
      console.log('🧹 Cleared all local decks');
    } catch (error) {
      throw new DeckStorageError(
        `Failed to clear local decks: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'LOCAL_CLEAR_FAILED',
        'local'
      );
    }
  }

  /**
   * Get storage statistics
   */
  async getStorageStats(): Promise<StorageStats> {
    const storageType = await this.getStorageType();
    let localStats = {
      deckCount: 0,
      maxDecks: 0,
      storageUsed: 0,
      available: false,
    };
    let serverStats = {
      deckCount: 0,
      available: false,
    };

    // Get local storage stats
    try {
      const stats = await localStorageService.getStorageStats();
      localStats = {
        deckCount: stats.deckCount,
        maxDecks: stats.maxDecks,
        storageUsed: stats.storageUsed,
        available: true,
      };
    } catch (error) {
      console.warn('Failed to get local storage stats:', error);
    }

    // Get server storage stats if authenticated
    if (this.isAuthenticated()) {
      try {
        const serverDecks = await fetchDecks();
        serverStats = {
          deckCount: serverDecks.length,
          available: true,
        };
      } catch (error) {
        console.warn('Failed to get server storage stats:', error);
      }
    }

    return {
      local: localStats,
      server: serverStats,
      total: localStats.deckCount + serverStats.deckCount,
      storageType,
    };
  }
}

// Factory function to create DeckStorageService with auth state provider
export const createDeckStorageService = (authStateProvider: () => boolean): DeckStorageService => {
  return new DeckStorageService(authStateProvider);
};

// Export singleton instance that can be configured
export let deckStorageService: DeckStorageService;

// Initialize function to set up the service with auth provider
export const initializeDeckStorageService = (authStateProvider: () => boolean): void => {
  deckStorageService = new DeckStorageService(authStateProvider);
  console.log('🔧 DeckStorageService initialized');
};