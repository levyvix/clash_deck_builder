/**
 * Shared TypeScript type definitions for the Clash Royale Deck Builder
 */

export interface Card {
  id: number;
  name: string;
  elixir_cost: number;
  rarity: 'Common' | 'Rare' | 'Epic' | 'Legendary' | 'Champion';
  type: 'Troop' | 'Spell' | 'Building';
  arena?: string;
  image_url: string;
  image_url_evo?: string;
  can_evolve?: boolean; // Optional field for evolution capability
}

export interface DeckSlot {
  card: Card | null;
  isEvolution: boolean;
}

export interface Deck {
  id?: number | string; // Support both numeric (server) and string (local) IDs
  name: string;
  slots: DeckSlot[];  // Always 8 slots
  average_elixir: number;
  created_at?: string;
  updated_at?: string;
  storageType?: 'local' | 'server'; // Field to distinguish deck sources
}

export interface FilterState {
  name: string;
  elixirCost: number | null;
  rarity: string | null;
  type: string | null;
}

export interface SortConfig {
  field: 'name' | 'elixir_cost' | 'rarity' | 'arena';
  direction: 'asc' | 'desc';
}

export type NotificationType = 'success' | 'error' | 'info';

export interface Notification {
  id: string;
  message: string;
  type: NotificationType;
}

export interface AnimationState {
  [cardId: number]: {
    isAnimating: boolean;
    animationType: 'entering' | 'leaving' | null;
  };
}

// Authentication types
export interface User {
  id: string;
  googleId: string;
  email: string;
  name: string;
  avatar: string; // Card ID for avatar
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface GoogleUserInfo {
  sub: string; // Google ID
  email: string;
  name: string;
  picture?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
  onboarding?: any;
}

// Storage type definitions for mixed storage support
export type StorageType = 'local' | 'server' | 'mixed';

// Enhanced deck interface for unified storage operations
export interface UnifiedDeck extends Omit<Deck, 'id'> {
  id: number | string; // Support both numeric (server) and string (local) IDs
  storageType: 'local' | 'server';
}

// Local deck interface for localStorage operations
export interface LocalDeck extends Omit<Deck, 'id'> {
  id: string; // Format: 'local_${timestamp}_${random}'
  storageType: 'local';
  created_at: string;
  updated_at: string;
}

// Server deck interface for API operations
export interface ServerDeck extends Omit<Deck, 'id'> {
  id: number;
  storageType: 'server';
}

// Result interface for getAllDecks operations
export interface DeckStorageResult {
  localDecks: UnifiedDeck[];
  serverDecks: UnifiedDeck[];
  totalCount: number;
  storageType: StorageType;
}

// Type guards for storage type identification
export const isLocalDeck = (deck: Deck | UnifiedDeck): deck is LocalDeck => {
  return typeof deck.id === 'string' && deck.id.startsWith('local_');
};

export const isServerDeck = (deck: Deck | UnifiedDeck): deck is ServerDeck => {
  return typeof deck.id === 'number' || (typeof deck.id === 'string' && !deck.id.startsWith('local_'));
};

export const isLocalDeckId = (id: string | number): id is string => {
  return typeof id === 'string' && id.startsWith('local_');
};

export const isServerDeckId = (id: string | number): id is number => {
  return typeof id === 'number' || (typeof id === 'string' && !id.startsWith('local_'));
};

// Type predicate for checking if deck has storage type
export const hasStorageType = (deck: any): deck is Deck & { storageType: 'local' | 'server' } => {
  return deck && typeof deck === 'object' && 
         ('storageType' in deck) && 
         (deck.storageType === 'local' || deck.storageType === 'server');
};

// Utility type for deck operations that require ID
export type DeckWithId = Deck & { id: number | string };

// Type for deck creation (without ID)
export type DeckInput = Omit<Deck, 'id' | 'storageType' | 'created_at' | 'updated_at'>;

// Type for deck updates (partial without ID and storageType)
export type DeckUpdate = Partial<Omit<Deck, 'id' | 'storageType'>>;

// Storage statistics interface
export interface StorageStats {
  local: {
    deckCount: number;
    maxDecks: number;
    storageUsed: number;
    available: boolean;
  };
  server: {
    deckCount: number;
    available: boolean;
  };
  total: number;
  storageType: StorageType;
}
