/**
 * Local Storage Service for Anonymous Deck Storage
 * 
 * Provides CRUD operations for deck management using browser localStorage.
 * Handles error scenarios like localStorage unavailability and quota exceeded.
 */

import { Deck, DeckSlot, LocalDeck, DeckInput, DeckUpdate } from '../types';

// Constants for localStorage management
const STORAGE_KEY = 'clash_deck_builder_local_decks';
const MAX_LOCAL_DECKS = 20;
const STORAGE_VERSION = '1.0';

// Local storage data structure
interface LocalStorageData {
  version: string;
  decks: LocalDeck[];
  metadata: {
    created: string;
    lastModified: string;
    deckCount: number;
  };
}

// Custom error classes for local storage operations
export class LocalStorageError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = 'LocalStorageError';
  }
}

export class LocalStorageQuotaError extends LocalStorageError {
  constructor() {
    super('Local storage quota exceeded. Please delete some decks to free up space.', 'QUOTA_EXCEEDED');
  }
}

export class LocalStorageUnavailableError extends LocalStorageError {
  constructor() {
    super('Local storage is not available in this browser or is disabled.', 'STORAGE_UNAVAILABLE');
  }
}

export class LocalStorageDataCorruptionError extends LocalStorageError {
  constructor() {
    super('Local storage data is corrupted and has been reset.', 'DATA_CORRUPTED');
  }
}

/**
 * Local Storage Service Class
 * 
 * Handles all localStorage operations for deck management with comprehensive
 * error handling and data validation.
 */
export class LocalStorageService {
  
  /**
   * Check if localStorage is available in the current environment
   */
  isLocalStorageAvailable(): boolean {
    try {
      if (typeof Storage === 'undefined') {
        return false;
      }
      
      // Test localStorage functionality
      const testKey = '__localStorage_test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Generate a unique ID for local decks
   */
  getNextLocalId(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    return `local_${timestamp}_${random}`;
  }

  /**
   * Validate deck data structure
   */
  private validateDeckData(deck: any): deck is Omit<Deck, 'id'> {
    return (
      deck &&
      typeof deck.name === 'string' &&
      deck.name.trim().length > 0 &&
      Array.isArray(deck.slots) &&
      deck.slots.length === 8 &&
      typeof deck.average_elixir === 'number' &&
      deck.slots.every((slot: any) => 
        slot &&
        typeof slot.isEvolution === 'boolean' &&
        (slot.card === null || (
          slot.card &&
          typeof slot.card.id === 'number' &&
          typeof slot.card.name === 'string' &&
          typeof slot.card.elixir_cost === 'number'
        ))
      )
    );
  }

  /**
   * Get the current localStorage data structure
   */
  private getStorageData(): LocalStorageData {
    if (!this.isLocalStorageAvailable()) {
      throw new LocalStorageUnavailableError();
    }

    try {
      const rawData = localStorage.getItem(STORAGE_KEY);
      
      if (!rawData) {
        // Initialize empty storage structure
        const initialData: LocalStorageData = {
          version: STORAGE_VERSION,
          decks: [],
          metadata: {
            created: new Date().toISOString(),
            lastModified: new Date().toISOString(),
            deckCount: 0,
          },
        };
        this.setStorageData(initialData);
        return initialData;
      }

      const parsedData = JSON.parse(rawData);
      
      // Validate data structure
      if (!parsedData.version || !Array.isArray(parsedData.decks) || !parsedData.metadata) {
        throw new Error('Invalid data structure');
      }

      return parsedData;
    } catch (error) {
      console.error('LocalStorage data corruption detected:', error);
      
      // Clear corrupted data and initialize fresh
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (clearError) {
        // Ignore clear errors
      }
      
      throw new LocalStorageDataCorruptionError();
    }
  }

  /**
   * Save data to localStorage with error handling
   */
  private setStorageData(data: LocalStorageData): void {
    if (!this.isLocalStorageAvailable()) {
      throw new LocalStorageUnavailableError();
    }

    try {
      const serializedData = JSON.stringify(data);
      localStorage.setItem(STORAGE_KEY, serializedData);
    } catch (error) {
      if (error instanceof DOMException && (
        error.code === 22 || // QUOTA_EXCEEDED_ERR
        error.code === 1014 || // NS_ERROR_DOM_QUOTA_REACHED (Firefox)
        error.name === 'QuotaExceededError' ||
        error.name === 'NS_ERROR_DOM_QUOTA_REACHED'
      )) {
        throw new LocalStorageQuotaError();
      }
      throw new LocalStorageError(`Failed to save data: ${error instanceof Error ? error.message : 'Unknown error'}`, 'SAVE_FAILED');
    }
  }

  /**
   * Save a new deck to localStorage
   */
  async saveLocalDeck(deck: DeckInput): Promise<LocalDeck> {
    // Validate input data
    if (!this.validateDeckData(deck)) {
      throw new LocalStorageError('Invalid deck data provided', 'INVALID_DATA');
    }

    const storageData = this.getStorageData();
    
    // Check deck count limit
    if (storageData.decks.length >= MAX_LOCAL_DECKS) {
      throw new LocalStorageError(
        `Maximum of ${MAX_LOCAL_DECKS} decks allowed. Please delete some decks to save new ones.`,
        'DECK_LIMIT_EXCEEDED'
      );
    }

    // Create new local deck
    const now = new Date().toISOString();
    const localDeck: LocalDeck = {
      ...deck,
      id: this.getNextLocalId(),
      storageType: 'local',
      created_at: now,
      updated_at: now,
    };

    // Add to storage
    storageData.decks.push(localDeck);
    storageData.metadata.lastModified = now;
    storageData.metadata.deckCount = storageData.decks.length;

    this.setStorageData(storageData);
    
    console.log(`✅ Saved local deck: ${localDeck.name} (ID: ${localDeck.id})`);
    return localDeck;
  }

  /**
   * Get all local decks from localStorage
   */
  async getLocalDecks(): Promise<LocalDeck[]> {
    try {
      const storageData = this.getStorageData();
      
      // Sort by creation date (newest first)
      const sortedDecks = storageData.decks.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      
      console.log(`📚 Retrieved ${sortedDecks.length} local decks`);
      return sortedDecks;
    } catch (error) {
      if (error instanceof LocalStorageError) {
        throw error;
      }
      throw new LocalStorageError(`Failed to retrieve decks: ${error instanceof Error ? error.message : 'Unknown error'}`, 'RETRIEVAL_FAILED');
    }
  }

  /**
   * Update an existing local deck
   */
  async updateLocalDeck(id: string, updates: DeckUpdate): Promise<LocalDeck> {
    const storageData = this.getStorageData();
    
    const deckIndex = storageData.decks.findIndex(deck => deck.id === id);
    if (deckIndex === -1) {
      throw new LocalStorageError(`Deck with ID ${id} not found`, 'DECK_NOT_FOUND');
    }

    // Validate updates if provided
    const updatedDeck = { ...storageData.decks[deckIndex], ...updates };
    if (!this.validateDeckData(updatedDeck)) {
      throw new LocalStorageError('Invalid deck data in updates', 'INVALID_DATA');
    }

    // Apply updates
    storageData.decks[deckIndex] = {
      ...updatedDeck,
      id,
      storageType: 'local',
      updated_at: new Date().toISOString(),
    } as LocalDeck;

    storageData.metadata.lastModified = new Date().toISOString();
    
    this.setStorageData(storageData);
    
    console.log(`✅ Updated local deck: ${storageData.decks[deckIndex].name} (ID: ${id})`);
    return storageData.decks[deckIndex];
  }

  /**
   * Delete a local deck by ID
   */
  async deleteLocalDeck(id: string): Promise<void> {
    const storageData = this.getStorageData();
    
    const deckIndex = storageData.decks.findIndex(deck => deck.id === id);
    if (deckIndex === -1) {
      throw new LocalStorageError(`Deck with ID ${id} not found`, 'DECK_NOT_FOUND');
    }

    const deckName = storageData.decks[deckIndex].name;
    
    // Remove deck from array
    storageData.decks.splice(deckIndex, 1);
    storageData.metadata.lastModified = new Date().toISOString();
    storageData.metadata.deckCount = storageData.decks.length;
    
    this.setStorageData(storageData);
    
    console.log(`🗑️ Deleted local deck: ${deckName} (ID: ${id})`);
  }

  /**
   * Clear all local decks (utility method for cleanup)
   */
  async clearAllLocalDecks(): Promise<void> {
    if (!this.isLocalStorageAvailable()) {
      throw new LocalStorageUnavailableError();
    }

    try {
      localStorage.removeItem(STORAGE_KEY);
      console.log('🧹 Cleared all local decks');
    } catch (error) {
      throw new LocalStorageError(`Failed to clear local decks: ${error instanceof Error ? error.message : 'Unknown error'}`, 'CLEAR_FAILED');
    }
  }

  /**
   * Get storage statistics
   */
  async getStorageStats(): Promise<{
    deckCount: number;
    maxDecks: number;
    storageUsed: number;
    lastModified: string;
  }> {
    try {
      const storageData = this.getStorageData();
      const serializedData = JSON.stringify(storageData);
      
      return {
        deckCount: storageData.decks.length,
        maxDecks: MAX_LOCAL_DECKS,
        storageUsed: new Blob([serializedData]).size,
        lastModified: storageData.metadata.lastModified,
      };
    } catch (error) {
      if (error instanceof LocalStorageError) {
        throw error;
      }
      throw new LocalStorageError(`Failed to get storage stats: ${error instanceof Error ? error.message : 'Unknown error'}`, 'STATS_FAILED');
    }
  }
}

// Export a singleton instance
export const localStorageService = new LocalStorageService();