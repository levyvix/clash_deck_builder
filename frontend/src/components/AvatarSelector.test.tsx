import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AvatarSelector from './AvatarSelector';
import { fetchCards } from '../services/api';

// Mock the API
jest.mock('../services/api');
const mockFetchCards = fetchCards as jest.MockedFunction<typeof fetchCards>;

const mockCards = [
  {
    id: 1,
    name: 'Knight',
    elixir_cost: 3,
    rarity: 'Common' as const,
    type: 'Troop' as const,
    image_url: 'https://example.com/knight.png'
  },
  {
    id: 2,
    name: 'Wizard',
    elixir_cost: 5,
    rarity: 'Rare' as const,
    type: 'Troop' as const,
    image_url: 'https://example.com/wizard.png'
  },
  {
    id: 3,
    name: 'P.E.K.K.A',
    elixir_cost: 7,
    rarity: 'Epic' as const,
    type: 'Troop' as const,
    image_url: 'https://example.com/pekka.png'
  },
  {
    id: 4,
    name: 'Sparky',
    elixir_cost: 6,
    rarity: 'Legendary' as const,
    type: 'Troop' as const,
    image_url: 'https://example.com/sparky.png'
  }
];

describe('AvatarSelector', () => {
  const defaultProps = {
    isOpen: true,
    currentAvatar: '1',
    onSelect: jest.fn(),
    onClose: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockFetchCards.mockResolvedValue(mockCards);
  });

  it('should not render when isOpen is false', () => {
    render(<AvatarSelector {...defaultProps} isOpen={false} />);
    expect(screen.queryByText('Choose Your Avatar')).not.toBeInTheDocument();
  });

  it('should render modal when isOpen is true', () => {
    render(<AvatarSelector {...defaultProps} />);
    expect(screen.getByText('Choose Your Avatar')).toBeInTheDocument();
  });

  it('should fetch cards when modal opens', async () => {
    render(<AvatarSelector {...defaultProps} />);
    
    await waitFor(() => {
      expect(mockFetchCards).toHaveBeenCalledTimes(1);
    });
  });

  it('should display loading state while fetching cards', () => {
    mockFetchCards.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<AvatarSelector {...defaultProps} />);
    expect(screen.getByText('Loading cards...')).toBeInTheDocument();
  });

  it('should display cards after successful fetch', async () => {
    render(<AvatarSelector {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
      expect(screen.getByText('Wizard')).toBeInTheDocument();
      expect(screen.getByText('P.E.K.K.A')).toBeInTheDocument();
      expect(screen.getByText('Sparky')).toBeInTheDocument();
    });
  });

  it('should display error message on fetch failure', async () => {
    mockFetchCards.mockRejectedValue(new Error('Network error'));
    
    render(<AvatarSelector {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load cards. Please try again.')).toBeInTheDocument();
    });
  });

  it('should filter cards by search term', async () => {
    render(<AvatarSelector {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search cards...');
    fireEvent.change(searchInput, { target: { value: 'wizard' } });

    expect(screen.getByText('Wizard')).toBeInTheDocument();
    expect(screen.queryByText('Knight')).not.toBeInTheDocument();
  });

  it('should filter cards by rarity', async () => {
    render(<AvatarSelector {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    const raritySelect = screen.getByDisplayValue('All Rarities');
    fireEvent.change(raritySelect, { target: { value: 'Legendary' } });

    expect(screen.getByText('Sparky')).toBeInTheDocument();
    expect(screen.queryByText('Knight')).not.toBeInTheDocument();
    expect(screen.queryByText('Wizard')).not.toBeInTheDocument();
  });

  it('should highlight currently selected avatar', async () => {
    render(<AvatarSelector {...defaultProps} currentAvatar="1" />);
    
    await waitFor(() => {
      const knightCard = screen.getByText('Knight').closest('.avatar-selector__card');
      expect(knightCard).toHaveClass('avatar-selector__card--selected');
    });
  });

  it('should call onSelect when card is clicked', async () => {
    const onSelect = jest.fn();
    render(<AvatarSelector {...defaultProps} onSelect={onSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Wizard')).toBeInTheDocument();
    });

    const wizardCard = screen.getByText('Wizard').closest('.avatar-selector__card');
    fireEvent.click(wizardCard!);

    expect(onSelect).toHaveBeenCalledWith('2');
  });

  it('should call onClose when close button is clicked', () => {
    const onClose = jest.fn();
    render(<AvatarSelector {...defaultProps} onClose={onClose} />);
    
    const closeButton = screen.getByLabelText('Close avatar selector');
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when backdrop is clicked', () => {
    const onClose = jest.fn();
    render(<AvatarSelector {...defaultProps} onClose={onClose} />);
    
    const backdrop = document.querySelector('.avatar-selector__backdrop');
    fireEvent.click(backdrop!);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('should not close when modal content is clicked', () => {
    const onClose = jest.fn();
    render(<AvatarSelector {...defaultProps} onClose={onClose} />);
    
    const modal = document.querySelector('.avatar-selector__modal');
    fireEvent.click(modal!);

    expect(onClose).not.toHaveBeenCalled();
  });

  it('should display no results message when no cards match filters', async () => {
    render(<AvatarSelector {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search cards...');
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } });

    expect(screen.getByText('No cards found matching your criteria.')).toBeInTheDocument();
  });

  it('should apply correct rarity classes to cards', async () => {
    render(<AvatarSelector {...defaultProps} />);
    
    await waitFor(() => {
      const knightCard = screen.getByText('Knight').closest('.avatar-selector__card');
      const wizardCard = screen.getByText('Wizard').closest('.avatar-selector__card');
      const pekkaCard = screen.getByText('P.E.K.K.A').closest('.avatar-selector__card');
      const sparkyCard = screen.getByText('Sparky').closest('.avatar-selector__card');

      expect(knightCard).toHaveClass('avatar-selector__card--common');
      expect(wizardCard).toHaveClass('avatar-selector__card--rare');
      expect(pekkaCard).toHaveClass('avatar-selector__card--epic');
      expect(sparkyCard).toHaveClass('avatar-selector__card--legendary');
    });
  });

  it('should retry loading cards when retry button is clicked', async () => {
    mockFetchCards.mockRejectedValueOnce(new Error('Network error'));
    
    render(<AvatarSelector {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load cards. Please try again.')).toBeInTheDocument();
    });

    mockFetchCards.mockResolvedValue(mockCards);
    
    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
    });

    expect(mockFetchCards).toHaveBeenCalledTimes(2);
  });
});