/**
 * Unit tests for enhanced SavedDecks component with mixed storage support
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import SavedDecks from './SavedDecks';

// Mock the deck storage service
jest.mock('../services/deckStorageService', () => ({
  initializeDeckStorageService: jest.fn(),
  deckStorageService: {
    getAllDecks: jest.fn(),
    updateDeck: jest.fn(),
    deleteDeck: jest.fn(),
  },
  DeckStorageError: class MockDeckStorageError extends Error {
    public code: string;
    constructor(message: string, mockCode: string) {
      super(message);
      this.name = 'DeckStorageError';
      this.code = mockCode;
    }
  },
}));

const mockGetAllDecks = require('../services/deckStorageService').deckStorageService.getAllDecks;

// Mock useAuth hook
jest.mock('../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

const mockUseAuth = require('../contexts/AuthContext').useAuth;

// Mock deck data
const mockLocalDeck = {
  id: 'local_123456789_abc',
  name: 'Local Test Deck',
  slots: Array(8).fill({ card: null, isEvolution: false }),
  average_elixir: 3.5,
  storageType: 'local' as const,
  created_at: '2024-01-01T00:00:00Z',
};

const mockServerDeck = {
  id: 1,
  name: 'Server Test Deck',
  slots: Array(8).fill({ card: null, isEvolution: false }),
  average_elixir: 4.0,
  storageType: 'server' as const,
  created_at: '2024-01-01T00:00:00Z',
};

describe('SavedDecks Enhanced Component', () => {
  const mockOnSelectDeck = jest.fn();
  const mockOnNotification = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Default mock for useAuth
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      user: null,
      isLoading: false,
    });
  });

  it('should render loading state initially', () => {
    mockGetAllDecks.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(
      <SavedDecks
        onSelectDeck={mockOnSelectDeck}
        onNotification={mockOnNotification}
      />
    );

    expect(screen.getByText('Loading decks...')).toBeInTheDocument();
  });

  it('should display mixed storage summary when both local and server decks exist', async () => {
    // Mock authenticated user with mixed storage
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', name: 'Test User' },
      isLoading: false,
    });

    // Mock mixed storage scenario
    mockGetAllDecks.mockResolvedValue({
      localDecks: [mockLocalDeck],
      serverDecks: [mockServerDeck],
      totalCount: 2,
      storageType: 'mixed',
    });

    render(
      <SavedDecks
        onSelectDeck={mockOnSelectDeck}
        onNotification={mockOnNotification}
      />
    );

    // Wait for loading to complete and content to appear
    await waitFor(() => {
      expect(screen.getByText('Local Test Deck')).toBeInTheDocument();
    });

    // Check for storage summary
    expect(screen.getByText('💾 1 Local')).toBeInTheDocument();
    expect(screen.getByText('☁️ 1 Server')).toBeInTheDocument();
  });

  it('should display storage type indicators on deck cards', async () => {
    mockGetAllDecks.mockResolvedValue({
      localDecks: [mockLocalDeck],
      serverDecks: [mockServerDeck],
      totalCount: 2,
      storageType: 'mixed',
    });

    render(
      <SavedDecks
        onSelectDeck={mockOnSelectDeck}
        onNotification={mockOnNotification}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Local Test Deck')).toBeInTheDocument();
      expect(screen.getByText('Server Test Deck')).toBeInTheDocument();
    });

    // Check for storage badges on deck cards
    const localBadges = screen.getAllByText('💾 Local');
    const serverBadges = screen.getAllByText('☁️ Server');
    
    expect(localBadges.length).toBeGreaterThan(0);
    expect(serverBadges.length).toBeGreaterThan(0);
  });

  it('should display appropriate empty state for mixed storage', async () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', name: 'Test User' },
      isLoading: false,
    });

    mockGetAllDecks.mockResolvedValue({
      localDecks: [],
      serverDecks: [],
      totalCount: 0,
      storageType: 'mixed',
    });

    render(
      <SavedDecks
        onSelectDeck={mockOnSelectDeck}
        onNotification={mockOnNotification}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('No saved decks yet')).toBeInTheDocument();
    });

    // Check for mixed storage info in empty state
    expect(screen.getByText(/Local decks are saved in your browser/)).toBeInTheDocument();
    expect(screen.getByText(/Server decks are saved to your account/)).toBeInTheDocument();
  });

  it('should display only local decks for anonymous users', async () => {
    mockGetAllDecks.mockResolvedValue({
      localDecks: [mockLocalDeck],
      serverDecks: [],
      totalCount: 1,
      storageType: 'local',
    });

    render(
      <SavedDecks
        onSelectDeck={mockOnSelectDeck}
        onNotification={mockOnNotification}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Local Test Deck')).toBeInTheDocument();
    });

    // Should not show storage summary for single storage type
    expect(screen.queryByText('💾 1 Local')).not.toBeInTheDocument();
    expect(screen.queryByText('☁️ 0 Server')).not.toBeInTheDocument();

    // But should show storage badge on the deck card
    expect(screen.getByText('💾 Local')).toBeInTheDocument();
  });
});