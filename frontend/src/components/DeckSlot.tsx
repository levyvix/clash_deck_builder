import React, { useState, useEffect } from 'react';
import { DeckSlot as DeckSlotType } from '../types';
import '../styles/DeckSlot.css';
import '../styles/animations.css';

interface DeckSlotProps {
  slot: DeckSlotType;
  slotIndex: number;
  onCardClick: (slotIndex: number) => void;
  onRemoveCard: (slotIndex: number) => void;
  onToggleEvolution: (slotIndex: number) => void;
  onAddCardToSlot?: (cardId: number, slotIndex: number) => void;
  onSwapCards?: (sourceIndex: number, targetIndex: number) => void;
  canAddEvolution: boolean;
  showOptions: boolean;
}

interface DragData {
  cardId: number;
  sourceType: 'gallery' | 'deck';
  sourceIndex?: number;
}

const DeckSlot: React.FC<DeckSlotProps> = ({
  slot,
  slotIndex,
  onCardClick,
  onRemoveCard,
  onToggleEvolution,
  onAddCardToSlot,
  onSwapCards,
  canAddEvolution,
  showOptions,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [animationState, setAnimationState] = useState<'entering' | 'leaving' | 'idle'>('idle');
  const [previousCardId, setPreviousCardId] = useState<number | null>(slot.card?.id || null);

  // Detect when a card is added or removed
  useEffect(() => {
    const currentCardId = slot.card?.id || null;
    
    // Card was added
    if (currentCardId && !previousCardId) {
      setAnimationState('entering');
      const timer = setTimeout(() => setAnimationState('idle'), 300);
      return () => clearTimeout(timer);
    }
    
    // Card was removed
    if (!currentCardId && previousCardId) {
      setAnimationState('leaving');
      const timer = setTimeout(() => {
        setAnimationState('idle');
        setPreviousCardId(null);
      }, 300);
      return () => clearTimeout(timer);
    }
    
    // Card was swapped (different card ID)
    if (currentCardId && previousCardId && currentCardId !== previousCardId) {
      setAnimationState('entering');
      const timer = setTimeout(() => setAnimationState('idle'), 300);
      setPreviousCardId(currentCardId);
      return () => clearTimeout(timer);
    }
    
    setPreviousCardId(currentCardId);
  }, [slot.card?.id, previousCardId]);

  const handleClick = () => {
    if (slot.card) {
      onCardClick(slotIndex);
    }
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRemoveCard(slotIndex);
  };

  const handleToggleEvolution = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleEvolution(slotIndex);
  };

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    if (!slot.card) return;

    const dragData: DragData = {
      cardId: slot.card.id,
      sourceType: 'deck',
      sourceIndex: slotIndex,
    };

    e.dataTransfer.setData('application/json', JSON.stringify(dragData));
    e.dataTransfer.effectAllowed = 'move';
    
    setIsDragging(true);
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault(); // Allow drop
    e.dataTransfer.dropEffect = 'move';
    
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    // Only trigger if leaving the slot itself, not child elements
    if (e.currentTarget === e.target || !e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);

    try {
      const dragData: DragData = JSON.parse(e.dataTransfer.getData('application/json'));
      
      if (dragData.sourceType === 'gallery') {
        // Handle drop from gallery - only if slot is empty
        if (!slot.card && onAddCardToSlot) {
          onAddCardToSlot(dragData.cardId, slotIndex);
        }
      } else if (dragData.sourceType === 'deck' && dragData.sourceIndex !== undefined) {
        // Handle drop from another deck slot - swap cards
        if (dragData.sourceIndex !== slotIndex && onSwapCards) {
          onSwapCards(dragData.sourceIndex, slotIndex);
        }
      }
    } catch (error) {
      console.error('Failed to parse drag data:', error);
    }
  };

  // Empty slot
  if (!slot.card) {
    return (
      <div 
        className={`deck-slot deck-slot--empty ${isDragOver ? 'deck-slot--drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="deck-slot__empty-icon">+</div>
        <div className="deck-slot__empty-text">{isDragOver ? 'Drop here' : 'Empty'}</div>
      </div>
    );
  }

  // Filled slot
  const imageUrl = slot.isEvolution && slot.card.image_url_evo 
    ? slot.card.image_url_evo 
    : slot.card.image_url;

  const animationClass = animationState === 'entering' 
    ? 'deck-slot__card--entering' 
    : animationState === 'leaving' 
    ? 'deck-slot__card--leaving' 
    : '';

  return (
    <div 
      className={`deck-slot deck-slot--filled ${isDragging ? 'deck-slot--dragging' : ''} ${isDragOver ? 'deck-slot--drag-over' : ''} ${animationClass}`}
      onClick={handleClick}
      draggable={true}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <img 
        src={imageUrl} 
        alt={slot.card.name}
        className="deck-slot__image"
      />
      
      {slot.isEvolution && (
        <div className="deck-slot__evolution-badge">
          <span className="deck-slot__evolution-icon">⭐</span>
        </div>
      )}

      <div className="deck-slot__info">
        <div className="deck-slot__elixir">{slot.card.elixir_cost}</div>
      </div>

      {showOptions && (
        <div className="deck-slot__options">
          <button 
            className="deck-slot__option-btn deck-slot__option-btn--remove"
            onClick={handleRemove}
          >
            Remove from Deck
          </button>
          <button 
            className="deck-slot__option-btn deck-slot__option-btn--evolution"
            onClick={handleToggleEvolution}
            disabled={!slot.isEvolution && !canAddEvolution}
            title={!slot.isEvolution && !canAddEvolution ? 'Evolution limit reached (max 2)' : ''}
          >
            {slot.isEvolution ? 'Remove Evolution' : 'Mark as Evolution'}
          </button>
        </div>
      )}
    </div>
  );
};

export default DeckSlot;
