/**
 * Tests for DeckSlot evolution toggle functionality
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import DeckSlot from './DeckSlot';
import { Card, DeckSlot as DeckSlotType } from '../types';

describe('DeckSlot Evolution Toggle', () => {
  const mockEvolutionCapableCard: Card = {
    id: 26000000, // Knight - evolution capable
    name: 'Knight',
    elixir_cost: 3,
    rarity: 'Common',
    type: 'Troop',
    arena: 'Training Camp',
    image_url: 'https://example.com/knight.png',
    image_url_evo: 'https://example.com/knight_evo.png'
  };

  const mockNonEvolutionCard: Card = {
    id: 99999999, // Non-existent ID - not evolution capable
    name: 'Test Spell',
    elixir_cost: 2,
    rarity: 'Common',
    type: 'Spell',
    arena: 'Arena 1',
    image_url: 'https://example.com/spell.png'
  };

  const mockApiEvolutionCard: Card = {
    id: 99999998,
    name: 'API Evolution Card',
    elixir_cost: 4,
    rarity: 'Rare',
    type: 'Troop',
    arena: 'Arena 2',
    image_url: 'https://example.com/api.png',
    can_evolve: true // API provides evolution capability
  };

  const defaultProps = {
    slotIndex: 0,
    onCardClick: jest.fn(),
    onRemoveCard: jest.fn(),
    onToggleEvolution: jest.fn(),
    canAddEvolution: true,
    showOptions: true
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should show evolution toggle for evolution-capable cards', () => {
    const slot: DeckSlotType = {
      card: mockEvolutionCapableCard,
      isEvolution: false
    };

    render(<DeckSlot slot={slot} {...defaultProps} />);

    expect(screen.getByText('Mark as Evolution')).toBeInTheDocument();
  });

  it('should not show evolution toggle for non-evolution-capable cards', () => {
    const slot: DeckSlotType = {
      card: mockNonEvolutionCard,
      isEvolution: false
    };

    render(<DeckSlot slot={slot} {...defaultProps} />);

    expect(screen.queryByText('Mark as Evolution')).not.toBeInTheDocument();
    expect(screen.queryByText('Remove Evolution')).not.toBeInTheDocument();
    
    // But remove button should still be present
    expect(screen.getByText('Remove from Deck')).toBeInTheDocument();
  });

  it('should respect API can_evolve field', () => {
    const slot: DeckSlotType = {
      card: mockApiEvolutionCard,
      isEvolution: false
    };

    render(<DeckSlot slot={slot} {...defaultProps} />);

    // Should show evolution toggle because API says can_evolve: true
    expect(screen.getByText('Mark as Evolution')).toBeInTheDocument();
  });

  it('should show "Remove Evolution" text when card is already evolved', () => {
    const slot: DeckSlotType = {
      card: mockEvolutionCapableCard,
      isEvolution: true
    };

    render(<DeckSlot slot={slot} {...defaultProps} />);

    expect(screen.getByText('Remove Evolution')).toBeInTheDocument();
  });

  it('should not show evolution options when showOptions is false', () => {
    const slot: DeckSlotType = {
      card: mockEvolutionCapableCard,
      isEvolution: false
    };

    render(<DeckSlot slot={slot} {...defaultProps} showOptions={false} />);

    expect(screen.queryByText('Mark as Evolution')).not.toBeInTheDocument();
    expect(screen.queryByText('Remove from Deck')).not.toBeInTheDocument();
  });

  it('should handle API can_evolve field set to false', () => {
    const cardWithFalseFlag: Card = {
      ...mockEvolutionCapableCard,
      can_evolve: false // API explicitly says it cannot evolve
    };

    const slot: DeckSlotType = {
      card: cardWithFalseFlag,
      isEvolution: false
    };

    render(<DeckSlot slot={slot} {...defaultProps} />);

    // Should not show evolution toggle because API says can_evolve: false
    expect(screen.queryByText('Mark as Evolution')).not.toBeInTheDocument();
  });
});