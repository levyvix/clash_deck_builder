// frontend/src/components/SavedDecks.tsx

import React, { useState, useEffect, useCallback } from 'react';
import { Deck, UnifiedDeck, DeckStorageResult } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { 
  deckStorageService, 
  initializeDeckStorageService, 
  DeckStorageError
} from '../services/deckStorageService';
import { formatUserMessage } from '../services/errorHandlingService';
import ErrorNotification from './ErrorNotification';
import StorageHealthIndicator from './StorageHealthIndicator';
import '../styles/SavedDecks.css';

interface SavedDecksProps {
  onSelectDeck: (deck: Deck) => void;
  onNotification?: (message: string, type: 'success' | 'error' | 'info') => void;
  refreshTrigger?: number; // Increment this to trigger a refresh
}

const SavedDecks: React.FC<SavedDecksProps> = ({ onSelectDeck, onNotification, refreshTrigger }) => {
  const { isAuthenticated } = useAuth();
  const [deckData, setDeckData] = useState<DeckStorageResult>({
    localDecks: [],
    serverDecks: [],
    totalCount: 0,
    storageType: 'local'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown | null>(null);
  const [editingDeckId, setEditingDeckId] = useState<string | number | null>(null);
  const [editingName, setEditingName] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | number | null>(null);

  const loadDecks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await deckStorageService.getAllDecks();
      setDeckData(data);
      console.log(`📊 Loaded ${data.totalCount} decks (${data.localDecks.length} local, ${data.serverDecks.length} server)`);
    } catch (err) {
      console.error('Failed to load decks:', err);
      
      setError(err);
      
      // Use enhanced error handling for user notification
      const userMessage = formatUserMessage(err, false);
      if (onNotification) {
        onNotification(userMessage, 'error');
      }
    } finally {
      setLoading(false);
    }
  }, [onNotification]);

  // Initialize deck storage service when auth state changes
  useEffect(() => {
    initializeDeckStorageService(() => isAuthenticated);
    loadDecks();
  }, [isAuthenticated, loadDecks]);
  
  // Refresh decks when refreshTrigger changes
  useEffect(() => {
    if (refreshTrigger !== undefined && refreshTrigger > 0) {
      console.log('🔄 Refreshing saved decks list due to trigger change');
      loadDecks();
    }
  }, [refreshTrigger, loadDecks]);

  const handleSelectDeck = (deck: UnifiedDeck) => {
    // Convert UnifiedDeck back to Deck format for compatibility
    const deckForCallback: Deck = {
      id: deck.id, // Keep the original ID (string or number) for proper tracking
      name: deck.name,
      slots: deck.slots,
      average_elixir: deck.average_elixir,
      created_at: deck.created_at,
      updated_at: deck.updated_at,
    };
    
    onSelectDeck(deckForCallback);
    if (onNotification) {
      const storageLabel = deck.storageType === 'local' ? '(Local)' : '(Server)';
      onNotification(`Loaded deck: ${deck.name} ${storageLabel}`, 'success');
    }
  };

  const handleStartRename = (deck: UnifiedDeck) => {
    setEditingDeckId(deck.id);
    setEditingName(deck.name);
  };

  const handleCancelRename = () => {
    setEditingDeckId(null);
    setEditingName('');
  };

  const handleSaveRename = async (deckId: string | number) => {
    if (!editingName.trim()) {
      if (onNotification) {
        onNotification('Deck name cannot be empty', 'error');
      }
      return;
    }

    try {
      console.log(`🔄 Renaming deck ${deckId} to "${editingName.trim()}"`);

      await deckStorageService.updateDeck(deckId, { name: editingName.trim() });
      
      // Update local state
      setDeckData(prevData => ({
        ...prevData,
        localDecks: prevData.localDecks.map(deck => 
          deck.id === deckId ? { ...deck, name: editingName.trim() } : deck
        ),
        serverDecks: prevData.serverDecks.map(deck => 
          deck.id === deckId ? { ...deck, name: editingName.trim() } : deck
        ),
      }));
      
      setEditingDeckId(null);
      setEditingName('');
      if (onNotification) {
        onNotification('Deck renamed successfully', 'success');
      }
    } catch (err) {
      console.error('Failed to rename deck:', err);
      
      let errorMessage = 'Failed to rename deck';
      
      if (err instanceof DeckStorageError) {
        errorMessage = err.message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      if (onNotification) {
        onNotification(errorMessage, 'error');
      }
    }
  };

  const handleDeleteClick = (deckId: string | number) => {
    setDeleteConfirmId(deckId);
  };

  const handleCancelDelete = () => {
    setDeleteConfirmId(null);
  };

  const handleConfirmDelete = async (deckId: string | number) => {
    try {
      console.log(`🗑️ Deleting deck ${deckId}`);
      
      await deckStorageService.deleteDeck(deckId);
      
      // Update local state
      setDeckData(prevData => ({
        ...prevData,
        localDecks: prevData.localDecks.filter(deck => deck.id !== deckId),
        serverDecks: prevData.serverDecks.filter(deck => deck.id !== deckId),
        totalCount: prevData.totalCount - 1,
      }));
      
      setDeleteConfirmId(null);
      if (onNotification) {
        onNotification('Deck deleted successfully', 'success');
      }
    } catch (err) {
      console.error('Failed to delete deck:', err);
      
      let errorMessage = 'Failed to delete deck';
      
      if (err instanceof DeckStorageError) {
        errorMessage = err.message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
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
          <ErrorNotification
            error={error}
            onRetry={loadDecks}
            onDismiss={() => setError(null)}
            showTechnicalDetails={true}
          />
        </div>
      </div>
    );
  }

  if (deckData.totalCount === 0) {
    return (
      <div className="saved-decks">
        <h2>Saved Decks</h2>
        <div className="saved-decks__empty">
          <p>No saved decks yet</p>
          <p className="saved-decks__empty-hint">
            Build a deck and save it to see it here!
          </p>
          {deckData.storageType === 'mixed' && (
            <p className="saved-decks__storage-info">
              💾 Local decks are saved in your browser • ☁️ Server decks are saved to your account
            </p>
          )}
        </div>
      </div>
    );
  }

  // Combine all decks for display
  const allDecks = [...deckData.localDecks, ...deckData.serverDecks];

  return (
    <div className="saved-decks">
      <div className="saved-decks__header">
        <h2>Saved Decks</h2>
        
        {/* Storage Health Indicator */}
        <StorageHealthIndicator 
          showDetails={true}
          onHealthChange={(health) => {
            // Optionally handle health changes for additional notifications
            if (health.overall === 'error') {
              console.warn('Storage health is critical:', health);
            }
          }}
        />
        
        {deckData.storageType === 'mixed' && (
          <div className="saved-decks__storage-summary storage-summary">
            <span className="storage-indicator storage-indicator--medium storage-indicator--local">
              Local <span className="storage-summary__count">{deckData.localDecks.length}</span>
            </span>
            <span className="storage-indicator storage-indicator--medium storage-indicator--server">
              Server <span className="storage-summary__count">{deckData.serverDecks.length}</span>
            </span>
          </div>
        )}
      </div>
      <div className="saved-decks__grid">
        {allDecks.map(deck => (
          <div key={deck.id} className="deck-card">
            {/* Delete Confirmation Modal */}
            {deleteConfirmId === deck.id && (
              <div className="deck-card__confirm-overlay">
                <div className="deck-card__confirm-dialog">
                  <p>Delete this deck?</p>
                  <div className="deck-card__confirm-actions">
                    <button 
                      onClick={() => handleConfirmDelete(deck.id)}
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

            {/* Storage Type Indicator */}
            <div className="deck-card__storage-indicator">
              <span className={`storage-badge storage-badge--${deck.storageType}`}>
                {deck.storageType === 'local' ? '💾 Local' : '☁️ Server'}
              </span>
            </div>

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
                        handleSaveRename(deck.id);
                      } else if (e.key === 'Escape') {
                        handleCancelRename();
                      }
                    }}
                  />
                  <div className="deck-card__rename-actions">
                    <button 
                      onClick={() => handleSaveRename(deck.id)}
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
                  onClick={() => handleDeleteClick(deck.id)}
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
