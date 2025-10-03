// frontend/src/App.tsx

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import DeckBuilder from './components/DeckBuilder';
import SavedDecks from './components/SavedDecks';
import { fetchDecks, createDeck, updateDeck, deleteDeck } from './services/api';
import './App.css'; // Assuming some basic styling

function App() {
  const [savedDecks, setSavedDecks] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const getDecks = async () => {
      try {
        const decks = await fetchDecks();
        setSavedDecks(decks);
      } catch (error: any) {
        setError(error.message || "Failed to fetch decks.");
        console.error("Failed to fetch decks:", error);
      }
    };
    getDecks();
  }, []);

  const handleSelectDeck = (id: number) => {
    console.log('Select deck', id);
    // Logic to load selected deck into DeckBuilder
  };

  const handleRenameDeck = async (id: number, newName: string) => {
    try {
      const deckToUpdate = savedDecks.find(deck => deck.id === id);
      if (deckToUpdate) {
        const updatedDeck = { ...deckToUpdate, name: newName };
        await updateDeck(id, updatedDeck);
        setSavedDecks(savedDecks.map(deck => (deck.id === id ? updatedDeck : deck)));
      }
    } catch (error: any) {
      setError(error.message || "Failed to rename deck.");
      console.error("Failed to rename deck:", error);
    }
  };

  const handleDeleteDeck = async (id: number) => {
    try {
      await deleteDeck(id);
      setSavedDecks(savedDecks.filter(deck => deck.id !== id));
    } catch (error: any) {
      setError(error.message || "Failed to delete deck.");
      console.error("Failed to delete deck:", error);
    }
  };

  return (
    <Router>
      <div className="App">
        <nav>
          <ul>
            <li>
              <Link to="/">Deck Builder</Link>
            </li>
            <li>
              <Link to="/saved-decks">Saved Decks</Link>
            </li>
          </ul>
        </nav>

        {error && <div className="error-message">Error: {error}</div>}

        <Routes>
          <Route path="/" element={<DeckBuilder />} />
          <Route
            path="/saved-decks"
            element={
              <SavedDecks
                decks={savedDecks}
                onSelectDeck={handleSelectDeck}
                onRenameDeck={handleRenameDeck}
                onDeleteDeck={handleDeleteDeck}
              />
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;