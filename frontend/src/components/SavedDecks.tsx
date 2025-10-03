// frontend/src/components/SavedDecks.tsx

import React, { useState, useEffect } from 'react';
import { Deck } from '../types';
import { fetchDecks, updateDeck, deleteDeck, ApiError } from '../services/api';
import '../styles/SavedDecks.css';

interface SavedDecksProps {
  onSelectDeck: (deck: Deck) => void;
  onNotification?: (message: string, type: 'success' | 'error' | 'info') => void;
}

const SavedDecks: React.FC<SavedDecksProps> = ({ onSelectDeck, onNotification }) => {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingDeckId, setEditingDeckId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);

  useEffect(() => {
    loadDecks();
  }, []);

  const loadDecks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDecks();
      setDecks(data);
    } catch (err) {
      console.error('Failed to load decks:', err);
      
      let errorMessage = 'Failed to load decks';
      
      if (err instanceof ApiError) {
        if (err.isTimeout) {
          errorMessage = 'Request timed out. Please try again.';
        } else if (err.isNetworkError) {
          errorMessage = 'Cannot connect to server. Please check your connection.';
        } else if (err.statusCode && err.statusCode >= 500) {
          errorMessage = 'Server error, please try again later.';
        } else {
          errorMessage = err.message;
        }
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      if (onNotification) {
        onNotification(errorMessage, 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDeck = (deck: Deck) => {
    onSelectDeck(deck);
    if (onNotification) {
      onNotification(`Loaded deck: ${deck.name}`, 'success');
    }
  };

  const handleStartRename = (deck: Deck) => {
    setEditingDeckId(deck.id!);
    setEditingName(deck.name);
  };

  const handleCancelRename = () => {
    setEditingDeckId(null);
    setEditingName('');
  };

  const handleSaveRename = async (deckId: number) => {
    if (!editingName.trim()) {
      if (onNotification) {
        onNotification('Deck name cannot be empty', 'error');
      }
      return;
    }

    try {
      await updateDeck(deckId, { name: editingName.trim() });
      setDecks(decks.map(deck => 
        deck.id === deckId ? { ...deck, name: editingName.trim() } : deck
      ));
      setEditingDeckId(null);
      setEditingName('');
      if (onNotification) {
        onNotification('Deck renamed successfully', 'success');
      }
    } catch (err) {
      console.error('Failed to rename deck:', err);
      
      let errorMessage = 'Failed to rename deck';
      
      if (err instanceof ApiError) {
        if (err.isTimeout) {
          errorMessage = 'Request timed out. Please try again.';
        } else if (err.isNetworkError) {
          errorMessage = 'Cannot connect to server';
        } else if (err.statusCode && err.statusCode >= 500) {
          errorMessage = 'Server error, please try again';
        } else {
          errorMessage = err.message;
        }
      }
      
      if (onNotification) {
        onNotification(errorMessage, 'error');
      }
    }
  };

  const handleDeleteClick = (deckId: number) => {
    setDeleteConfirmId(deckId);
  };

  const handleCancelDelete = () => {
    setDeleteConfirmId(null);
  };

  const handleConfirmDelete = async (deckId: number) => {
    try {
      await deleteDeck(deckId);
      setDecks(decks.filter(deck => deck.id !== deckId));
      setDeleteConfirmId(null);
      if (onNotification) {
        onNotification('Deck deleted successfully', 'success');
      }
    } catch (err) {
      console.error('Failed to delete deck:', err);
      
      let errorMessage = 'Failed to delete deck';
      
      if (err instanceof ApiError) {
        if (err.isTimeout) {
          errorMessage = 'Request timed out. Please try again.';
        } else if (err.isNetworkError) {
          errorMessage = 'Cannot connect to server';
        } else if (err.statusCode && err.statusCode >= 500) {
          errorMessage = 'Server error, please try again';
        } else {
          errorMessage = err.message;
        }
      }
      
      if (onNotification) {
        onNotification(errorMessage, 'error');
      }
    }
  };

  if (loading) {
    return (
      <div className="saved-decks">
        <h2>Saved Decks</h2>
        <div className="saved-decks__loading">
          <div className="spinner"></div>
          <p>Loading decks...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="saved-decks">
        <h2>Saved Decks</h2>
        <div className="saved-decks__error">
          <p>{error}</p>
          <button onClick={loadDecks} className="btn btn--primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (decks.length === 0) {
    return (
      <div className="saved-decks">
        <h2>Saved Decks</h2>
        <div className="saved-decks__empty">
          <p>No saved decks yet</p>
          <p className="saved-decks__empty-hint">
            Build a deck and save it to see it here!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="saved-decks">
      <h2>Saved Decks</h2>
      <div className="saved-decks__grid">
        {decks.map(deck => (
          <div key={deck.id} className="deck-card">
            {/* Delete Confirmation Modal */}
            {deleteConfirmId === deck.id && (
              <div className="deck-card__confirm-overlay">
                <div className="deck-card__confirm-dialog">
                  <p>Delete this deck?</p>
                  <div className="deck-card__confirm-actions">
                    <button 
                      onClick={() => handleConfirmDelete(deck.id!)}
                      className="btn btn--danger"
                    >
                      Delete
                    </button>
                    <button 
                      onClick={handleCancelDelete}
                      className="btn btn--secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Deck Name */}
            <div className="deck-card__header">
              {editingDeckId === deck.id ? (
                <div className="deck-card__rename">
                  <input
                    type="text"
                    value={editingName}
                    onChange={(e) => setEditingName(e.target.value)}
                    className="deck-card__rename-input"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleSaveRename(deck.id!);
                      } else if (e.key === 'Escape') {
                        handleCancelRename();
                      }
                    }}
                  />
                  <div className="deck-card__rename-actions">
                    <button 
                      onClick={() => handleSaveRename(deck.id!)}
                      className="btn btn--small btn--success"
                      title="Save"
                    >
                      ✓
                    </button>
                    <button 
                      onClick={handleCancelRename}
                      className="btn btn--small btn--secondary"
                      title="Cancel"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ) : (
                <h3 className="deck-card__name">{deck.name}</h3>
              )}
            </div>

            {/* Card Thumbnails */}
            <div className="deck-card__cards">
              {deck.slots.map((slot, index) => (
                <div key={index} className="deck-card__card-thumbnail">
                  {slot.card ? (
                    <>
                      <img 
                        src={slot.isEvolution && slot.card.image_url_evo 
                          ? slot.card.image_url_evo 
                          : slot.card.image_url
                        }
                        alt={slot.card.name}
                        className="deck-card__card-image"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.src = 'https://via.placeholder.com/80x100?text=Card';
                        }}
                      />
                      {slot.isEvolution && (
                        <div className="deck-card__evolution-badge">⭐</div>
                      )}
                    </>
                  ) : (
                    <div className="deck-card__card-empty">?</div>
                  )}
                </div>
              ))}
            </div>

            {/* Deck Stats */}
            <div className="deck-card__stats">
              <span className="deck-card__stat">
                <strong>Avg Elixir:</strong> {deck.average_elixir.toFixed(1)}
              </span>
              <span className="deck-card__stat">
                <strong>Cards:</strong> {deck.slots.filter(s => s.card).length}/8
              </span>
            </div>

            {/* Actions */}
            <div className="deck-card__actions">
              <button 
                onClick={() => handleSelectDeck(deck)}
                className="btn btn--primary btn--full-width"
              >
                Load Deck
              </button>
              <div className="deck-card__secondary-actions">
                <button 
                  onClick={() => handleStartRename(deck)}
                  className="btn btn--secondary btn--small"
                  disabled={editingDeckId !== null}
                >
                  Rename
                </button>
                <button 
                  onClick={() => handleDeleteClick(deck.id!)}
                  className="btn btn--danger btn--small"
                  disabled={deleteConfirmId !== null}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SavedDecks;
