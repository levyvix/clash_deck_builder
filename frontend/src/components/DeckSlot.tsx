import React, { useState } from 'react';
import { DeckSlot as DeckSlotType, AnimationState } from '../types';
import { canCardEvolve } from '../services/evolutionService';
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
  animationState?: AnimationState[number];
  isDeckComplete?: boolean; // Add prop to track deck completion
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
  animationState,
  isDeckComplete = false,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Function to get dynamic CSS classes for deck slots
  const getDeckSlotClasses = () => {
    const classes = ['deck-slot'];
    
    if (!slot.card) {
      classes.push('deck-slot--empty');
    } else {
      classes.push('deck-slot--filled');
    }
    
    if (isDragOver) {
      classes.push('deck-slot--drag-over');
    }
    
    if (isDragging) {
      classes.push('deck-slot--dragging');
    }
    
    return classes.join(' ');
  };

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
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'move';
    }
    
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
        className={getDeckSlotClasses()}
        data-testid={`deck-slot-${slotIndex}`}
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

  // Get animation classes for the card image
  const getCardAnimationClasses = () => {
    const classes = ['deck-slot__image'];
    
    // Only add animation classes when actively animating
    if (animationState?.isAnimating) {
      if (animationState.animationType === 'entering') {
        classes.push('deck-slot__card--entering');
      } else if (animationState.animationType === 'leaving') {
        classes.push('deck-slot__card--leaving');
      }
    }
    
    return classes.join(' ');
  };

  return (
    <div 
      className={getDeckSlotClasses()}
      data-testid={`deck-slot-${slotIndex}`}
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
        className={getCardAnimationClasses()}
      />
      


      <div className="deck-slot__info">
        <div className="deck-slot__elixir">{slot.card.elixir_cost}</div>
      </div>

      {/* Evolution Badge */}
      {slot.isEvolution && (
        <div className="deck-slot__evolution-badge">
          EVO
        </div>
      )}

      {showOptions && (
        <div className="deck-slot__options">
          <button
            className="deck-slot__option-btn deck-slot__option-btn--remove"
            onClick={handleRemove}
          >
            Remove from Deck
          </button>
          {canCardEvolve(slot.card) && (
            <button
              className="deck-slot__option-btn deck-slot__option-btn--evolution"
              onClick={handleToggleEvolution}
              disabled={!slot.isEvolution && !canAddEvolution}
              title={!slot.isEvolution && !canAddEvolution ? 'Evolution limit reached (max 2)' : ''}
            >
              {slot.isEvolution ? 'Remove Evolution' : 'Mark as Evolution'}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default DeckSlot;
