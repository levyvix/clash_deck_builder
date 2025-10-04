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
  id?: number;
  name: string;
  slots: DeckSlot[];  // Always 8 slots
  average_elixir: number;
  created_at?: string;
  updated_at?: string;
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
