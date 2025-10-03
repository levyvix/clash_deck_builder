// frontend/src/components/SavedDecks.tsx

import React from 'react';

interface SavedDecksProps {
  decks: any[]; // Array of saved decks
  onSelectDeck: (deckId: number) => void;
  onRenameDeck: (deckId: number, newName: string) => void;
  onDeleteDeck: (deckId: number) => void;
}

const SavedDecks: React.FC<SavedDecksProps> = ({ decks, onSelectDeck, onRenameDeck, onDeleteDeck }) => {
  return (
    <div className="saved-decks">
      <h2>Saved Decks</h2>
      <ul>
        {decks.map(deck => (
          <li key={deck.id}>
            <span>{deck.name}</span>
            <button onClick={() => onSelectDeck(deck.id)}>Load</button>
            <button onClick={() => onRenameDeck(deck.id, prompt("New name:") || deck.name)}>Rename</button>
            <button onClick={() => onDeleteDeck(deck.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SavedDecks;
