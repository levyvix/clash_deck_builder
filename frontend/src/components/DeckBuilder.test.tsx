import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DeckBuilder from './DeckBuilder';
import { fetchCards } from '../services/api';
import { canCardEvolve } from '../services/evolutionService';

// Mock the API
jest.mock('../services/api');
const mockFetchCards = fetchCards as jest.MockedFunction<typeof fetchCards>;

// Mock the evolution service
jest.mock('../services/evolutionService');
const mockCanCardEvolve = canCardEvolve as jest.MockedFunction<typeof canCardEvolve>;

// Mock cards data
const mockCards = [
  {
    id: 26000000, // Knight - evolution capable
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
    id: 26000001, // Archers - evolution capable
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
    id: 26000100, // Fireball - not evolution capable
    name: 'Fireball',
    elixir_cost: 4,
    rarity: 'Rare' as const,
    type: 'Spell' as const,
    arena: 'Arena 1',
    image_url: 'fireball.png',
    can_evolve: false
  },
  {
    id: 26000101, // Zap - not evolution capable
    name: 'Zap',
    elixir_cost: 2,
    rarity: 'Common' as const,
    type: 'Spell' as const,
    arena: 'Arena 1',
    image_url: 'zap.png',
    can_evolve: false
  }
];

describe('DeckBuilder - Automatic Evolution for First Two Slots', () => {
  beforeEach(() => {
    mockFetchCards.mockResolvedValue(mockCards);
    
    // Mock evolution capability
    mockCanCardEvolve.mockImplementation((card) => {
      return card.can_evolve === true;
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should automatically mark evolution-capable cards in first two slots as evolution', async () => {
    render(<DeckBuilder />);

    // Wait for cards to load
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    // Add Knight to first slot (index 0)
    const knightCard = screen.getByText('Knight');
    fireEvent.click(knightCard);
    
    const addToDeckButton = screen.getByText('Add to Deck');
    fireEvent.click(addToDeckButton);

    // Add Archers to second slot (index 1)
    const archersCard = screen.getByText('Archers');
    fireEvent.click(archersCard);
    
    const addToDeckButton2 = screen.getByText('Add to Deck');
    fireEvent.click(addToDeckButton2);

    // Wait for animations to complete
    await waitFor(() => {
      // Check that both cards are in the deck and marked as evolution
      const deckSlots = screen.getAllByTestId(/deck-slot-/);
      
      // First slot should have Knight with evolution badge
      const firstSlot = deckSlots[0];
      expect(firstSlot).toHaveClass('deck-slot--filled');
      expect(firstSlot.querySelector('.deck-slot__evolution-badge')).toBeInTheDocument();
      
      // Second slot should have Archers with evolution badge
      const secondSlot = deckSlots[1];
      expect(secondSlot).toHaveClass('deck-slot--filled');
      expect(secondSlot.querySelector('.deck-slot__evolution-badge')).toBeInTheDocument();
    });
  });

  test('should not mark non-evolution-capable cards as evolution even in first two slots', async () => {
    render(<DeckBuilder />);

    // Wait for cards to load
    await waitFor(() => {
      expect(screen.getByText('Fireball')).toBeInTheDocument();
    });

    // Add Fireball to first slot (index 0)
    const fireballCard = screen.getByText('Fireball');
    fireEvent.click(fireballCard);
    
    const addToDeckButton = screen.getByText('Add to Deck');
    fireEvent.click(addToDeckButton);

    // Add Zap to second slot (index 1)
    const zapCard = screen.getByText('Zap');
    fireEvent.click(zapCard);
    
    const addToDeckButton2 = screen.getByText('Add to Deck');
    fireEvent.click(addToDeckButton2);

    // Wait for animations to complete
    await waitFor(() => {
      // Check that cards are in the deck but NOT marked as evolution
      const deckSlots = screen.getAllByTestId(/deck-slot-/);
      
      // First slot should have Fireball without evolution badge
      const firstSlot = deckSlots[0];
      expect(firstSlot).toHaveClass('deck-slot--filled');
      expect(firstSlot.querySelector('.deck-slot__evolution-badge')).not.toBeInTheDocument();
      
      // Second slot should have Zap without evolution badge
      const secondSlot = deckSlots[1];
      expect(secondSlot).toHaveClass('deck-slot--filled');
      expect(secondSlot.querySelector('.deck-slot__evolution-badge')).not.toBeInTheDocument();
    });
  });

  test('should update evolution states when cards are swapped between slots', async () => {
    render(<DeckBuilder />);

    // Wait for cards to load
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    // Add Knight to first slot
    const knightCard = screen.getByText('Knight');
    fireEvent.click(knightCard);
    fireEvent.click(screen.getByText('Add to Deck'));

    // Add Fireball to third slot (index 2)
    const fireballCard = screen.getByText('Fireball');
    fireEvent.click(fireballCard);
    fireEvent.click(screen.getByText('Add to Deck'));

    await waitFor(() => {
      const deckSlots = screen.getAllByTestId(/deck-slot-/);
      
      // Knight in first slot should be evolution
      expect(deckSlots[0].querySelector('.deck-slot__evolution-badge')).toBeInTheDocument();
      
      // Fireball in third slot should not be evolution
      expect(deckSlots[2].querySelector('.deck-slot__evolution-badge')).not.toBeInTheDocument();
    });

    // Simulate drag and drop to swap Knight (slot 0) with Fireball (slot 2)
    const knightSlot = screen.getAllByTestId(/deck-slot-/)[0];
    const fireballSlot = screen.getAllByTestId(/deck-slot-/)[2];

    // Create mock dataTransfer object
    const mockDataTransfer = {
      setData: jest.fn(),
      getData: jest.fn().mockReturnValue(JSON.stringify({
        cardId: 26000000,
        sourceType: 'deck',
        sourceIndex: 0
      })),
      effectAllowed: 'move',
      dropEffect: 'move'
    };

    // Simulate drag start on Knight
    fireEvent.dragStart(knightSlot, {
      dataTransfer: mockDataTransfer
    });

    // Simulate drop on Fireball slot
    fireEvent.dragOver(fireballSlot, {
      dataTransfer: mockDataTransfer
    });
    fireEvent.drop(fireballSlot, {
      dataTransfer: mockDataTransfer
    });

    await waitFor(() => {
      const deckSlots = screen.getAllByTestId(/deck-slot-/);
      
      // Fireball now in first slot should not be evolution (can't evolve)
      expect(deckSlots[0].querySelector('.deck-slot__evolution-badge')).not.toBeInTheDocument();
      
      // Knight now in third slot should not be evolution (not in first two slots)
      expect(deckSlots[2].querySelector('.deck-slot__evolution-badge')).not.toBeInTheDocument();
    });
  });

  test('should recalculate evolution states when cards are removed', async () => {
    render(<DeckBuilder />);

    // Wait for cards to load
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    // Add Knight to first slot
    const knightCard = screen.getByText('Knight');
    fireEvent.click(knightCard);
    fireEvent.click(screen.getByText('Add to Deck'));

    // Add Archers to second slot
    const archersCard = screen.getByText('Archers');
    fireEvent.click(archersCard);
    fireEvent.click(screen.getByText('Add to Deck'));

    // Add Fireball to third slot
    const fireballCard = screen.getByText('Fireball');
    fireEvent.click(fireballCard);
    fireEvent.click(screen.getByText('Add to Deck'));

    await waitFor(() => {
      const deckSlots = screen.getAllByTestId(/deck-slot-/);
      
      // First two slots should have evolution badges
      expect(deckSlots[0].querySelector('.deck-slot__evolution-badge')).toBeInTheDocument();
      expect(deckSlots[1].querySelector('.deck-slot__evolution-badge')).toBeInTheDocument();
      
      // Third slot should not have evolution badge
      expect(deckSlots[2].querySelector('.deck-slot__evolution-badge')).not.toBeInTheDocument();
    });

    // Remove Knight from first slot
    const firstSlot = screen.getAllByTestId(/deck-slot-/)[0];
    fireEvent.click(firstSlot);
    
    const removeButton = screen.getByText('Remove from Deck');
    fireEvent.click(removeButton);

    await waitFor(() => {
      const deckSlots = screen.getAllByTestId(/deck-slot-/);
      
      // First slot should now be empty
      expect(deckSlots[0]).toHaveClass('deck-slot--empty');
      
      // Archers should still be in second slot with evolution badge
      expect(deckSlots[1].querySelector('.deck-slot__evolution-badge')).toBeInTheDocument();
      
      // Fireball should still be in third slot without evolution badge
      expect(deckSlots[2].querySelector('.deck-slot__evolution-badge')).not.toBeInTheDocument();
    });
  });
});