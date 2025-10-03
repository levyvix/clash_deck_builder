import React, { useState, useEffect, useMemo } from 'react';
import { Card, DeckSlot as DeckSlotType, FilterState, Notification as NotificationType } from '../types';
import { fetchCards, createDeck, ApiError } from '../services/api';
import { 
  calculateAverageElixir, 
  canAddEvolution, 
  isDeckComplete, 
  getEmptySlotIndex 
} from '../services/deckCalculations';
import DeckSlot from './DeckSlot';
import CardGallery from './CardGallery';
import CardFilters from './CardFilters';
import Notification from './Notification';
import '../styles/DeckBuilder.css';

interface DeckBuilderProps {
  initialDeck?: DeckSlotType[];
  onDeckSaved?: () => void;
}

const DeckBuilder: React.FC<DeckBuilderProps> = ({ initialDeck, onDeckSaved }) => {
  // Initialize deck with 8 empty slots
  const [currentDeck, setCurrentDeck] = useState<DeckSlotType[]>(
    initialDeck || Array(8).fill(null).map(() => ({ card: null, isEvolution: false }))
  );
  const [cards, setCards] = useState<Card[]>([]);
  const [filters, setFilters] = useState<FilterState>({
    name: '',
    elixirCost: null,
    rarity: null,
    type: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGalleryCard, setSelectedGalleryCard] = useState<Card | null>(null);
  const [selectedDeckSlot, setSelectedDeckSlot] = useState<number | null>(null);
  const [notifications, setNotifications] = useState<NotificationType[]>([]);
  const [savingDeck, setSavingDeck] = useState(false);
  const [deckName, setDeckName] = useState('');
  const [showSaveDialog, setShowSaveDialog] = useState(false);

  // Fetch cards on component mount
  useEffect(() => {
    const loadCards = async () => {
      try {
        setLoading(true);
        setError(null);
        const fetchedCards = await fetchCards();
        setCards(fetchedCards);
      } catch (err) {
        console.error('Failed to fetch cards:', err);
        
        let errorMessage = 'Failed to load cards. Please refresh the page.';
        
        if (err instanceof ApiError) {
          if (err.isTimeout) {
            errorMessage = 'Request timed out. Please check your connection and try again.';
          } else if (err.isNetworkError) {
            errorMessage = 'Cannot connect to server. Please check your connection.';
          } else if (err.statusCode && err.statusCode >= 500) {
            errorMessage = 'Server error, please try again later.';
          } else {
            errorMessage = err.message;
          }
        }
        
        setError(errorMessage);
        addNotification(errorMessage, 'error');
      } finally {
        setLoading(false);
      }
    };

    loadCards();
  }, []);

  // Update deck when initialDeck prop changes
  useEffect(() => {
    if (initialDeck) {
      setCurrentDeck(initialDeck);
    }
  }, [initialDeck]);

  // Calculate average elixir in real-time
  const averageElixir = useMemo(() => {
    return calculateAverageElixir(currentDeck);
  }, [currentDeck]);

  // Count filled slots
  const filledSlotCount = useMemo(() => {
    return currentDeck.filter(slot => slot.card !== null).length;
  }, [currentDeck]);

  // Check if deck is complete
  const deckComplete = useMemo(() => {
    return isDeckComplete(currentDeck);
  }, [currentDeck]);

  // Add notification helper
  const addNotification = (message: string, type: NotificationType['type']) => {
    const id = `${Date.now()}-${Math.random()}`;
    setNotifications(prev => [...prev, { id, message, type }]);
  };

  // Dismiss notification
  const dismissNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Add card to deck
  const addCardToDeck = (card: Card) => {
    const emptySlotIndex = getEmptySlotIndex(currentDeck);
    
    if (emptySlotIndex === -1) {
      addNotification('Deck is full. Remove a card first.', 'error');
      return;
    }

    const newDeck = [...currentDeck];
    newDeck[emptySlotIndex] = { card, isEvolution: false };
    setCurrentDeck(newDeck);
    setSelectedGalleryCard(null);
    addNotification(`${card.name} added to deck`, 'success');
  };

  // Remove card from deck
  const removeCardFromDeck = (slotIndex: number) => {
    const slot = currentDeck[slotIndex];
    if (!slot.card) return;

    const newDeck = [...currentDeck];
    newDeck[slotIndex] = { card: null, isEvolution: false };
    setCurrentDeck(newDeck);
    setSelectedDeckSlot(null);
    addNotification(`${slot.card.name} removed from deck`, 'success');
  };

  // Toggle evolution status
  const toggleEvolution = (slotIndex: number) => {
    const slot = currentDeck[slotIndex];
    if (!slot.card) return;

    // If trying to mark as evolution, check limit
    if (!slot.isEvolution && !canAddEvolution(currentDeck)) {
      addNotification('Evolution limit reached (max 2)', 'error');
      return;
    }

    const newDeck = [...currentDeck];
    newDeck[slotIndex] = { ...slot, isEvolution: !slot.isEvolution };
    setCurrentDeck(newDeck);
    
    const action = newDeck[slotIndex].isEvolution ? 'marked as evolution' : 'evolution removed';
    addNotification(`${slot.card.name} ${action}`, 'success');
  };

  // Save deck
  const saveDeck = async () => {
    if (!deckComplete) {
      addNotification('Deck must have 8 cards to save', 'error');
      return;
    }

    if (!deckName.trim()) {
      addNotification('Please enter a deck name', 'error');
      return;
    }

    try {
      setSavingDeck(true);
      
      // Prepare deck data for API
      const deckData = {
        name: deckName.trim(),
        cards: currentDeck.map(slot => slot.card!.id),
        evolution_slots: currentDeck
          .filter(slot => slot.isEvolution)
          .map(slot => slot.card!.id),
        average_elixir: averageElixir,
      };

      await createDeck(deckData);
      addNotification('Deck saved successfully!', 'success');
      setShowSaveDialog(false);
      setDeckName('');
      
      if (onDeckSaved) {
        onDeckSaved();
      }
    } catch (err) {
      console.error('Failed to save deck:', err);
      
      let errorMessage = 'Failed to save deck. Please try again.';
      
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
      }
      
      addNotification(errorMessage, 'error');
    } finally {
      setSavingDeck(false);
    }
  };

  // Handle card click in gallery
  const handleGalleryCardClick = (card: Card) => {
    setSelectedGalleryCard(selectedGalleryCard?.id === card.id ? null : card);
    setSelectedDeckSlot(null);
  };

  // Handle deck slot click
  const handleDeckSlotClick = (slotIndex: number) => {
    setSelectedDeckSlot(selectedDeckSlot === slotIndex ? null : slotIndex);
    setSelectedGalleryCard(null);
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({
      name: '',
      elixirCost: null,
      rarity: null,
      type: null,
    });
  };

  // Handle save button click
  const handleSaveClick = () => {
    if (!deckComplete) {
      addNotification('Deck must have 8 cards to save', 'error');
      return;
    }
    setShowSaveDialog(true);
  };

  // Loading state
  if (loading) {
    return (
      <div className="deck-builder">
        <div className="deck-builder__loading">
          <div className="deck-builder__spinner"></div>
          <p>Loading cards...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="deck-builder">
        <div className="deck-builder__error">
          <p className="deck-builder__error-message">{error}</p>
          <button 
            className="deck-builder__error-button"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="deck-builder">
      <Notification notifications={notifications} onDismiss={dismissNotification} />
      
      <div className="deck-builder__container">
        {/* Deck Section */}
        <div className="deck-builder__deck-section">
          <div className="deck-builder__deck-header">
            <h2 className="deck-builder__title">Build Your Deck</h2>
            <div className="deck-builder__stats">
              <div className="deck-builder__stat">
                <span className="deck-builder__stat-label">Cards:</span>
                <span className="deck-builder__stat-value">{filledSlotCount}/8</span>
              </div>
              <div className="deck-builder__stat">
                <span className="deck-builder__stat-label">Avg Elixir:</span>
                <span className="deck-builder__stat-value">{averageElixir.toFixed(1)}</span>
              </div>
            </div>
          </div>

          {/* Deck Slots Grid */}
          <div className="deck-builder__slots">
            {currentDeck.map((slot, index) => (
              <DeckSlot
                key={index}
                slot={slot}
                slotIndex={index}
                onCardClick={handleDeckSlotClick}
                onRemoveCard={removeCardFromDeck}
                onToggleEvolution={toggleEvolution}
                canAddEvolution={canAddEvolution(currentDeck)}
                showOptions={selectedDeckSlot === index}
              />
            ))}
          </div>

          {/* Save Deck Button */}
          <div className="deck-builder__actions">
            <button
              className="deck-builder__save-button"
              onClick={handleSaveClick}
              disabled={!deckComplete}
              title={!deckComplete ? 'Add 8 cards to save deck' : 'Save deck'}
            >
              Save Deck
            </button>
          </div>

          {/* Save Dialog */}
          {showSaveDialog && (
            <div className="deck-builder__dialog-overlay" onClick={() => setShowSaveDialog(false)}>
              <div className="deck-builder__dialog" onClick={(e) => e.stopPropagation()}>
                <h3 className="deck-builder__dialog-title">Save Deck</h3>
                <input
                  type="text"
                  className="deck-builder__dialog-input"
                  placeholder="Enter deck name..."
                  value={deckName}
                  onChange={(e) => setDeckName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && saveDeck()}
                  autoFocus
                />
                <div className="deck-builder__dialog-actions">
                  <button
                    className="deck-builder__dialog-button deck-builder__dialog-button--cancel"
                    onClick={() => {
                      setShowSaveDialog(false);
                      setDeckName('');
                    }}
                    disabled={savingDeck}
                  >
                    Cancel
                  </button>
                  <button
                    className="deck-builder__dialog-button deck-builder__dialog-button--save"
                    onClick={saveDeck}
                    disabled={savingDeck || !deckName.trim()}
                  >
                    {savingDeck ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Card Gallery Section */}
        <div className="deck-builder__gallery-section">
          <CardFilters
            filters={filters}
            onFilterChange={setFilters}
            onClearFilters={clearFilters}
          />
          <CardGallery
            cards={cards}
            filters={filters}
            onCardClick={handleGalleryCardClick}
            selectedCard={selectedGalleryCard}
            onAddToDeck={addCardToDeck}
            loading={false}
          />
        </div>
      </div>
    </div>
  );
};

export default DeckBuilder;
