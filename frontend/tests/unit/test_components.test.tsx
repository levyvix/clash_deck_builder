// frontend/tests/unit/test_components.test.tsx

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import CardDisplay from '../../src/components/CardDisplay';
import CardFilters from '../../src/components/CardFilters';
import SavedDecks from '../../src/components/SavedDecks';

describe('CardDisplay', () => {
  const mockCard = {
    id: 1,
    name: "Archer",
    elixir_cost: 3,
    rarity: "Common",
    type: "Troop",
    image_url: "http://example.com/archer.png",
  };

  test('renders card name and elixir cost', () => {
    render(<CardDisplay card={mockCard} />);
    expect(screen.getByText(/Archer/i)).toBeInTheDocument();
    expect(screen.getByText(/Elixir: 3/i)).toBeInTheDocument();
  });
});

describe('CardFilters', () => {
  test('renders filter inputs and button', () => {
    const onFilterChange = jest.fn();
    render(<CardFilters onFilterChange={onFilterChange} />);
    expect(screen.getByPlaceholderText(/Name/i)).toBeInTheDocument();
    expect(screen.getByText(/Apply Filters/i)).toBeInTheDocument();
  });
});

describe('SavedDecks', () => {
  const mockDecks = [
    { id: 1, name: "Deck 1", cards: [], evolution_slots: [], average_elixir: 3.0 },
    { id: 2, name: "Deck 2", cards: [], evolution_slots: [], average_elixir: 3.5 },
  ];
  const mockFn = jest.fn();

  test('renders list of saved decks', () => {
    render(
      <SavedDecks
        decks={mockDecks}
        onSelectDeck={mockFn}
        onRenameDeck={mockFn}
        onDeleteDeck={mockFn}
      />
    );
    expect(screen.getByText(/Deck 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Deck 2/i)).toBeInTheDocument();
  });
});
