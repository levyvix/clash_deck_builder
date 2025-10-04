import React, { useState, useEffect, useMemo } from 'react';
import { Card, DeckSlot as DeckSlotType, FilterState, SortConfig, Notification as NotificationType, AnimationState } from '../types';
import { fetchCards, ApiError } from '../services/api';
import { 
  calculateAverageElixir, 
  canAddEvolution, 
  isDeckComplete, 
  getEmptySlotIndex 
} from '../services/deckCalculations';
import { canCardEvolve } from '../services/evolutionService';
import { deckStorageService } from '../services/deckStorageService';
import { formatUserMessage } from '../services/errorHandlingService';
import { useAuth } from '../contexts/AuthContext';
import DeckSlot from './DeckSlot';
import CardGallery from './CardGallery';
import CardFilters from './CardFilters';
import SortControls from './SortControls';
import Notification from './Notification';
import RemoveDropZone from './RemoveDropZone';
import WelcomeMessage from './WelcomeMessage';
import '../styles/DeckBuilder.css';

interface DeckBuilderProps {
  initialDeck?: DeckSlotType[];
  onDeckSaved?: () => void;
}

const DeckBuilder: React.FC<DeckBuilderProps> = ({ initialDeck, onDeckSaved }) => {
  const { isAuthenticated } = useAuth();
  
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
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    field: 'name',
    direction: 'asc'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGalleryCard, setSelectedGalleryCard] = useState<Card | null>(null);
  const [selectedDeckSlot, setSelectedDeckSlot] = useState<number | null>(null);
  const [notifications, setNotifications] = useState<NotificationType[]>([]);
  const [savingDeck, setSavingDeck] = useState(false);
  const [deckName, setDeckName] = useState('');
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [cardsInDeck, setCardsInDeck] = useState<Set<number>>(new Set());
  const [animationStates, setAnimationStates] = useState<AnimationState>({});

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
      // Update cardsInDeck set based on initialDeck
      const cardIds = new Set<number>();
      initialDeck.forEach(slot => {
        if (slot.card) {
          cardIds.add(slot.card.id);
        }
      });
      setCardsInDeck(cardIds);
    }
  }, [initialDeck]);

  // Initialize cardsInDeck set from currentDeck on mount
  useEffect(() => {
    const cardIds = new Set<number>();
    currentDeck.forEach(slot => {
      if (slot.card) {
        cardIds.add(slot.card.id);
      }
    });
    setCardsInDeck(cardIds);
  }, [currentDeck]);

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

  // Sort cards function with proper handling for different data types
  const sortCards = useMemo(() => {
    return (cards: Card[], config: SortConfig): Card[] => {
      return [...cards].sort((a, b) => {
        let aValue: any = a[config.field];
        let bValue: any = b[config.field];
        
        // Special handling for rarity hierarchy
        if (config.field === 'rarity') {
          const rarityOrder = { 
            'Common': 1, 
            'Rare': 2, 
            'Epic': 3, 
            'Legendary': 4, 
            'Champion': 5 
          };
          aValue = rarityOrder[a.rarity as keyof typeof rarityOrder] || 0;
          bValue = rarityOrder[b.rarity as keyof typeof rarityOrder] || 0;
        }
        
        // Handle arena field (convert to number if it's a string like "Arena 1")
        if (config.field === 'arena') {
          // Extract number from arena string or use 0 if not available
          const getArenaNumber = (arena: string | undefined): number => {
            if (!arena) return 0;
            const match = arena.match(/\d+/);
            return match ? parseInt(match[0], 10) : 0;
          };
          aValue = getArenaNumber(a.arena);
          bValue = getArenaNumber(b.arena);
        }
        
        // Numeric comparison
        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return config.direction === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        // String comparison (for name field)
        const comparison = aValue.toString().localeCompare(bValue.toString());
        return config.direction === 'asc' ? comparison : -comparison;
      });
    };
  }, []);

  // Add notification helper
  const addNotification = (message: string, type: NotificationType['type']) => {
    const id = `${Date.now()}-${Math.random()}`;
    setNotifications(prev => [...prev, { id, message, type }]);
  };

  // Dismiss notification
  const dismissNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Update evolution states - auto-mark first two slots as evolution if capable
  const updateEvolutionStates = (newDeck: DeckSlotType[]) => {
    const updatedDeck = newDeck.map((slot, index) => {
      if (!slot?.card) return slot;
      
      // Auto-mark cards in positions 0 and 1 (first two slots) as evolution if they support it
      const shouldBeEvolution = index < 2 && canCardEvolve(slot.card);
      return {
        ...slot,
        isEvolution: shouldBeEvolution
      };
    });
    
    setCurrentDeck(updatedDeck);
    return updatedDeck;
  };



  // Add card with animation - prevents multiple animations on same card
  const addCardWithAnimation = (card: Card, slotIndex?: number) => {
    const cardId = card.id;
    
    // Skip if already animating to prevent glitches
    if (animationStates[cardId]?.isAnimating) {
      console.log(`Skipping animation for card ${cardId} - already animating`);
      return;
    }
    
    // Check if card is already in deck
    if (cardsInDeck.has(card.id)) {
      addNotification('Card already in deck', 'error');
      return;
    }

    // Determine slot index
    const targetSlotIndex = slotIndex !== undefined ? slotIndex : getEmptySlotIndex(currentDeck);
    
    if (targetSlotIndex === -1) {
      addNotification('Deck is full. Remove a card first.', 'error');
      return;
    }

    // Check if target slot is occupied (for specific slot placement)
    if (slotIndex !== undefined && currentDeck[slotIndex].card) {
      addNotification('Slot is already occupied', 'error');
      return;
    }

    // Set animation state FIRST to ensure proper initial state
    setAnimationStates(prev => ({
      ...prev,
      [cardId]: { isAnimating: true, animationType: 'entering' }
    }));
    
    // Add card to deck immediately - React will batch these updates
    const newDeck = [...currentDeck];
    newDeck[targetSlotIndex] = { card, isEvolution: false };
    
    // Update evolution states automatically
    updateEvolutionStates(newDeck);
    
    // Add card ID to cardsInDeck set
    const newCardsInDeck = new Set(cardsInDeck);
    newCardsInDeck.add(card.id);
    setCardsInDeck(newCardsInDeck);
    
    setSelectedGalleryCard(null);
    addNotification(`${card.name} added to deck`, 'success');
    
    // Clear animation state after animation completes
    setTimeout(() => {
      setAnimationStates(prev => {
        const newState = { ...prev };
        if (newState[cardId]) {
          newState[cardId] = { isAnimating: false, animationType: null };
        }
        return newState;
      });
    }, 200); // Match CSS animation duration exactly
  };

  // Add card to deck
  const addCardToDeck = (card: Card) => {
    addCardWithAnimation(card);
  };

  // Add card to specific slot (for drag and drop)
  const addCardToSlot = (cardId: number, slotIndex: number) => {
    // Find the card
    const card = cards.find(c => c.id === cardId);
    if (!card) {
      addNotification('Card not found', 'error');
      return;
    }

    // Check if card is already in deck
    if (cardsInDeck.has(card.id)) {
      addNotification('Card already in deck', 'error');
      return;
    }

    // Check if target slot is occupied
    if (currentDeck[slotIndex].card) {
      addNotification('Slot is already occupied', 'error');
      return;
    }

    // Set animation state
    setAnimationStates(prev => ({
      ...prev,
      [card.id]: { isAnimating: true, animationType: 'entering' }
    }));
    
    // Add card to deck
    const newDeck = [...currentDeck];
    newDeck[slotIndex] = { card, isEvolution: false };
    
    // Update evolution states automatically
    updateEvolutionStates(newDeck);
    
    // Add card ID to cardsInDeck set
    const newCardsInDeck = new Set(cardsInDeck);
    newCardsInDeck.add(card.id);
    setCardsInDeck(newCardsInDeck);
    
    addNotification(`${card.name} added to deck`, 'success');
    
    // Clear animation state after animation completes
    setTimeout(() => {
      setAnimationStates(prev => {
        const newState = { ...prev };
        if (newState[card.id]) {
          newState[card.id] = { isAnimating: false, animationType: null };
        }
        return newState;
      });
    }, 200);
  };

  // Remove card from deck
  const removeCardFromDeck = (slotIndex: number) => {
    const slot = currentDeck[slotIndex];
    if (!slot.card) return;

    const cardId = slot.card.id;
    const cardName = slot.card.name;

    // Clear any existing animation states for this card
    setAnimationStates(prev => {
      const newState = { ...prev };
      delete newState[cardId];
      return newState;
    });

    const newDeck = [...currentDeck];
    newDeck[slotIndex] = { card: null, isEvolution: false };
    
    // Update evolution states after removal
    updateEvolutionStates(newDeck);
    
    // Remove card ID from cardsInDeck set
    const newCardsInDeck = new Set(cardsInDeck);
    newCardsInDeck.delete(cardId);
    setCardsInDeck(newCardsInDeck);
    
    setSelectedDeckSlot(null);
    addNotification(`${cardName} removed from deck`, 'success');
  };



  // Swap cards between deck slots
  const swapCards = (sourceIndex: number, targetIndex: number) => {
    if (sourceIndex === targetIndex) return;

    // Clear animation states for both cards involved in the swap to prevent glitches
    const sourceCard = currentDeck[sourceIndex]?.card;
    const targetCard = currentDeck[targetIndex]?.card;
    
    setAnimationStates(prev => {
      const newState = { ...prev };
      if (sourceCard) delete newState[sourceCard.id];
      if (targetCard) delete newState[targetCard.id];
      return newState;
    });

    const newDeck = [...currentDeck];
    const temp = newDeck[sourceIndex];
    newDeck[sourceIndex] = newDeck[targetIndex];
    newDeck[targetIndex] = temp;
    
    // Update evolution states after swap
    updateEvolutionStates(newDeck);
    
    addNotification('Cards swapped', 'success');
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
      
      // Prepare deck data using unified format
      const deckData = {
        name: deckName.trim(),
        slots: currentDeck,
        average_elixir: averageElixir,
      };

      // Use unified storage service - it will determine storage type based on authentication
      const savedDeck = await deckStorageService.saveDeck(deckData);
      
      // Success handling
      const storageTypeText = savedDeck.storageType === 'local' ? 'locally' : 'to server';
      console.log(`✅ Deck saved ${storageTypeText}, response:`, savedDeck);
      addNotification(`Deck saved ${storageTypeText}`, 'success');
      
      // Close the save dialog
      setShowSaveDialog(false);
      setDeckName('');
      
      // Keep the current deck (don't clear it) so user can continue building or modify
      // This provides better UX as they can see what they just saved
      
      // Refresh saved decks list if callback provided
      if (onDeckSaved) {
        onDeckSaved();
      }
    } catch (err) {
      console.error('Failed to save deck:', err);
      
      // Use enhanced error handling for better user experience
      const userMessage = formatUserMessage(err, true);
      
      addNotification(userMessage, 'error');
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
        {/* Welcome Message for New Users */}
        <WelcomeMessage />
        
        {/* Deck Section */}
        <div className="deck-builder__deck-section deck-builder__deck-section--sticky">
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
          <div className={`deck-builder__slots ${deckComplete ? 'deck-area--complete' : ''}`}>
            {currentDeck.map((slot, index) => (
              <DeckSlot
                key={`slot-${index}-${slot.card?.id || 'empty'}`}
                slot={slot}
                slotIndex={index}
                onCardClick={handleDeckSlotClick}
                onRemoveCard={removeCardFromDeck}
                onToggleEvolution={toggleEvolution}
                onAddCardToSlot={addCardToSlot}
                onSwapCards={swapCards}
                canAddEvolution={canAddEvolution(currentDeck)}
                showOptions={selectedDeckSlot === index}
                animationState={slot.card ? animationStates[slot.card.id] : undefined}
                isDeckComplete={deckComplete}
              />
            ))}
          </div>

          {/* Remove Drop Zone */}
          <RemoveDropZone onRemoveCard={removeCardFromDeck} />

          {/* Save Deck Button */}
          <div className="deck-builder__actions">
            <button
              className={`deck-builder__save-button ${deckComplete ? 'save-button--ready' : ''}`}
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
                
                {/* Storage Type Indicator */}
                <div className="deck-builder__storage-info">
                  <span className={`storage-indicator storage-indicator--medium storage-indicator--${isAuthenticated ? 'server' : 'local'}`}>
                    {isAuthenticated ? 'Saving to Server' : 'Saving Locally'}
                  </span>
                  <p className="deck-builder__storage-description">
                    {isAuthenticated 
                      ? 'This deck will be saved to your account and synced across devices.'
                      : 'This deck will be saved in your browser. Sign in to save to your account.'
                    }
                  </p>
                </div>
                
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
          <SortControls
            sortConfig={sortConfig}
            onSort={setSortConfig}
          />
          <CardGallery
            cards={cards}
            filters={filters}
            sortConfig={sortConfig}
            sortCards={sortCards}
            onCardClick={handleGalleryCardClick}
            selectedCard={selectedGalleryCard}
            onAddToDeck={addCardToDeck}
            loading={false}
            cardsInDeck={cardsInDeck}
          />
        </div>
      </div>
    </div>
  );
};

export default DeckBuilder;
