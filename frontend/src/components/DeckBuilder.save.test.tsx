import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DeckBuilder from './DeckBuilder';
import { fetchCards } from '../services/api';
import { AuthProvider } from '../contexts/AuthContext';
import { OnboardingProvider } from '../contexts/OnboardingContext';
import { deckStorageService } from '../services/deckStorageService';

// Mock the API
jest.mock('../services/api');
const mockFetchCards = fetchCards as jest.MockedFunction<typeof fetchCards>;

// Mock the auth service
jest.mock('../services/authService', () => ({
  validateToken: jest.fn().mockResolvedValue(null),
}));

// Mock the deck storage service
jest.mock('../services/deckStorageService', () => ({
  deckStorageService: {
    saveDeck: jest.fn(),
  },
  initializeDeckStorageService: jest.fn(),
  DeckStorageError: class MockDeckStorageError extends Error {
    public code: string;
    public storageType?: 'local' | 'server';
    
    constructor(message: string, code: string, storageType?: 'local' | 'server') {
      super(message);
      this.name = 'DeckStorageError';
      this.code = code;
      this.storageType = storageType;
    }
  },
}));

const mockDeckStorageService = deckStorageService as jest.Mocked<typeof deckStorageService>;

// Mock cards data
const mockCards = [
  {
    id: 26000000,
    name: 'Knight',
    elixir_cost: 3,
    rarity: 'Common' as const,
    type: 'Troop' as const,
    arena: 'Arena 1',
    image_url: 'knight.png',
    image_url_evo: 'knight_evo.png',
    can_evolve: true
  },
  {
    id: 26000001,
    name: 'Archers',
    elixir_cost: 3,
    rarity: 'Common' as const,
    type: 'Troop' as const,
    arena: 'Arena 1',
    image_url: 'archers.png',
    image_url_evo: 'archers_evo.png',
    can_evolve: true
  },
  {
    id: 26000100,
    name: 'Fireball',
    elixir_cost: 4,
    rarity: 'Rare' as const,
    type: 'Spell' as const,
    arena: 'Arena 1',
    image_url: 'fireball.png',
    can_evolve: false
  },
  {
    id: 26000101,
    name: 'Zap',
    elixir_cost: 2,
    rarity: 'Common' as const,
    type: 'Spell' as const,
    arena: 'Arena 1',
    image_url: 'zap.png',
    can_evolve: false
  },
  {
    id: 26000102,
    name: 'Giant',
    elixir_cost: 5,
    rarity: 'Rare' as const,
    type: 'Troop' as const,
    arena: 'Arena 1',
    image_url: 'giant.png',
    can_evolve: false
  },
  {
    id: 26000103,
    name: 'Wizard',
    elixir_cost: 5,
    rarity: 'Rare' as const,
    type: 'Troop' as const,
    arena: 'Arena 1',
    image_url: 'wizard.png',
    can_evolve: false
  },
  {
    id: 26000104,
    name: 'Dragon',
    elixir_cost: 4,
    rarity: 'Epic' as const,
    type: 'Troop' as const,
    arena: 'Arena 1',
    image_url: 'dragon.png',
    can_evolve: false
  },
  {
    id: 26000105,
    name: 'Arrows',
    elixir_cost: 3,
    rarity: 'Common' as const,
    type: 'Spell' as const,
    arena: 'Arena 1',
    image_url: 'arrows.png',
    can_evolve: false
  }
];

// Test wrapper component with providers
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AuthProvider>
    <OnboardingProvider>
      {children}
    </OnboardingProvider>
  </AuthProvider>
);

describe('DeckBuilder - Local Storage Integration', () => {
  beforeEach(() => {
    mockFetchCards.mockResolvedValue(mockCards);
    mockDeckStorageService.saveDeck.mockResolvedValue({
      id: 'local_123456789_abc',
      name: 'Test Deck',
      slots: [],
      average_elixir: 4.0,
      storageType: 'local',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should use unified storage service to save deck', async () => {
    const mockOnDeckSaved = jest.fn();
    
    render(
      <DeckBuilder onDeckSaved={mockOnDeckSaved} />, 
      { wrapper: TestWrapper }
    );

    // Wait for cards to load
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    // Add 8 cards to complete the deck
    const cardsToAdd = mockCards;
    for (let i = 0; i < 8; i++) {
      const card = cardsToAdd[i];
      const cardElement = screen.getByText(card.name);
      fireEvent.click(cardElement);
      
      const addButton = screen.getByText('Add to Deck');
      fireEvent.click(addButton);
    }

    // Wait for deck to be complete
    await waitFor(() => {
      expect(screen.getByText('8/8')).toBeInTheDocument();
    });

    // Click save deck button
    const saveButton = screen.getByText('Save Deck');
    expect(saveButton).not.toBeDisabled();
    fireEvent.click(saveButton);

    // Enter deck name in dialog
    const nameInput = screen.getByPlaceholderText('Enter deck name...');
    fireEvent.change(nameInput, { target: { value: 'Test Deck' } });

    // Click save in dialog
    const saveDialogButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveDialogButton);

    // Verify that the unified storage service was called
    await waitFor(() => {
      expect(mockDeckStorageService.saveDeck).toHaveBeenCalledWith({
        name: 'Test Deck',
        slots: expect.any(Array),
        average_elixir: expect.any(Number),
      });
    });

    // Verify success notification
    await waitFor(() => {
      expect(screen.getByText('Deck saved locally')).toBeInTheDocument();
    });

    // Verify callback was called
    expect(mockOnDeckSaved).toHaveBeenCalled();
  });

  test('should handle storage errors gracefully', async () => {
    // Import the mocked DeckStorageError
    const { DeckStorageError } = require('../services/deckStorageService');
    
    // Mock storage service to throw a DeckStorageError
    mockDeckStorageService.saveDeck.mockRejectedValue(
      new DeckStorageError('Storage quota exceeded', 'LOCAL_STORAGE_QUOTA_EXCEEDED', 'local')
    );

    render(<DeckBuilder />, { wrapper: TestWrapper });

    // Wait for cards to load
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    // Add 8 cards to complete the deck
    const cardsToAdd = mockCards;
    for (let i = 0; i < 8; i++) {
      const card = cardsToAdd[i];
      const cardElement = screen.getByText(card.name);
      fireEvent.click(cardElement);
      
      const addButton = screen.getByText('Add to Deck');
      fireEvent.click(addButton);
    }

    // Wait for deck to be complete
    await waitFor(() => {
      expect(screen.getByText('8/8')).toBeInTheDocument();
    });

    // Click save deck button
    const saveButton = screen.getByText('Save Deck');
    fireEvent.click(saveButton);

    // Enter deck name in dialog
    const nameInput = screen.getByPlaceholderText('Enter deck name...');
    fireEvent.change(nameInput, { target: { value: 'Test Deck' } });

    // Click save in dialog
    const saveDialogButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveDialogButton);

    // Verify error notification is shown
    await waitFor(() => {
      expect(screen.getByText(/There was a problem saving your deck/)).toBeInTheDocument();
    });
  });
});