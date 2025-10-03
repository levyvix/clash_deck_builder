// frontend/src/components/DeckBuilder.tsx

import React, { useState } from 'react';
import CardDisplay from './CardDisplay';

interface DeckBuilderProps {
  // Props for available cards, saved decks, etc.
}

const DeckBuilder: React.FC<DeckBuilderProps> = () => {
  const [currentDeck, setCurrentDeck] = useState<any[]>([]);
  const [evoSlots, setEvoSlots] = useState<any[]>([]);
  const [averageElixir, setAverageElixir] = useState(0);

  // Placeholder functions for adding/removing cards, assigning evo slots
  const addCardToDeck = (card: any) => {
    if (currentDeck.length < 8) {
      setCurrentDeck([...currentDeck, card]);
      // Recalculate average elixir
    }
  };

  const assignEvoSlot = (card: any) => {
    if (evoSlots.length < 2 && !evoSlots.includes(card)) {
      setEvoSlots([...evoSlots, card]);
    }
  };

  return (
    <div className="deck-builder">
      <h2>Current Deck (Avg Elixir: {averageElixir})</h2>
      <div className="deck-cards">
        {currentDeck.map((card, index) => (
          <CardDisplay key={index} card={card} isEvo={evoSlots.includes(card)} />
        ))}
      </div>
      {/* UI for available cards, filters, save/delete buttons */}
    </div>
  );
};

export default DeckBuilder;
