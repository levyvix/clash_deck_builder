import React from 'react';
import { DeckSlot as DeckSlotType } from '../types';
import '../styles/DeckSlot.css';

interface DeckSlotProps {
  slot: DeckSlotType;
  slotIndex: number;
  onCardClick: (slotIndex: number) => void;
  onRemoveCard: (slotIndex: number) => void;
  onToggleEvolution: (slotIndex: number) => void;
  canAddEvolution: boolean;
  showOptions: boolean;
}

const DeckSlot: React.FC<DeckSlotProps> = ({
  slot,
  slotIndex,
  onCardClick,
  onRemoveCard,
  onToggleEvolution,
  canAddEvolution,
  showOptions,
}) => {
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

  // Empty slot
  if (!slot.card) {
    return (
      <div className="deck-slot deck-slot--empty">
        <div className="deck-slot__empty-icon">+</div>
        <div className="deck-slot__empty-text">Empty</div>
      </div>
    );
  }

  // Filled slot
  const imageUrl = slot.isEvolution && slot.card.image_url_evo 
    ? slot.card.image_url_evo 
    : slot.card.image_url;

  return (
    <div className="deck-slot deck-slot--filled" onClick={handleClick}>
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
