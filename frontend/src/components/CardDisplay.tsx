import React, { useState } from 'react';
import { Card } from '../types';
import '../styles/CardDisplay.css';

interface CardDisplayProps {
  card: Card;
  isEvolution?: boolean;
  onClick?: () => void;
  showOptions?: boolean;
  onAddToDeck?: () => void;
  onRemoveFromDeck?: () => void;
  inDeck?: boolean;
  disabled?: boolean;
  draggable?: boolean;
  sourceType?: 'gallery' | 'deck';
  sourceIndex?: number;
}

interface DragData {
  cardId: number;
  sourceType: 'gallery' | 'deck';
  sourceIndex?: number;
}

const CardDisplay: React.FC<CardDisplayProps> = ({
  card,
  isEvolution = false,
  onClick,
  showOptions = false,
  onAddToDeck,
  onRemoveFromDeck,
  inDeck = false,
  disabled = false,
  draggable = false,
  sourceType = 'gallery',
  sourceIndex,
}) => {
  const [imageError, setImageError] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Use evolution image if available and isEvolution is true
  const imageUrl = isEvolution && card.image_url_evo ? card.image_url_evo : card.image_url;

  // Get rarity class for styling
  const rarityClass = `card-display--${card.rarity.toLowerCase()}`;

  const handleImageError = () => {
    setImageError(true);
  };

  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    // Set drag data
    const dragData: DragData = {
      cardId: card.id,
      sourceType,
      sourceIndex,
    };
    e.dataTransfer.setData('application/json', JSON.stringify(dragData));
    e.dataTransfer.effectAllowed = 'move';

    // Create ghost element for drag preview
    const ghostElement = e.currentTarget.cloneNode(true) as HTMLElement;
    ghostElement.style.position = 'absolute';
    ghostElement.style.top = '-9999px';
    ghostElement.style.width = '120px';
    ghostElement.style.opacity = '0.8';
    ghostElement.style.transform = 'rotate(-5deg)';
    document.body.appendChild(ghostElement);

    // Set the ghost element as drag image
    e.dataTransfer.setDragImage(ghostElement, 60, 70);

    // Clean up ghost element after drag starts
    setTimeout(() => {
      document.body.removeChild(ghostElement);
    }, 0);

    // Add dragging class
    setIsDragging(true);
  };

  const handleDragEnd = () => {
    // Remove dragging class
    setIsDragging(false);
  };

  return (
    <div
      className={`card-display ${rarityClass} ${onClick ? 'card-display--clickable' : ''} ${inDeck || disabled ? 'card-display--in-deck' : ''} ${isDragging ? 'card-display--dragging' : ''}`}
      onClick={handleClick}
      draggable={draggable && !inDeck && !disabled}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="card-display__image-container">
        {imageError ? (
          <div className="card-display__placeholder">
            <span className="card-display__placeholder-text">{card.name}</span>
          </div>
        ) : (
          <img
            src={imageUrl}
            alt={card.name}
            className="card-display__image"
            onError={handleImageError}
          />
        )}
      </div>

      <div className="card-display__info">
        <h3 className="card-display__name">{card.name}</h3>
        <div className="card-display__stats">
          <span className="card-display__elixir">
            <span className="card-display__elixir-icon">💧</span>
            {card.elixir_cost}
          </span>
          <span className={`card-display__rarity card-display__rarity--${card.rarity.toLowerCase()}`}>
            {card.rarity}
          </span>
        </div>
      </div>

      {showOptions && (
        <div className="card-display__actions">
          {inDeck ? (
            <button
              className="card-display__button card-display__button--remove"
              onClick={(e) => {
                e.stopPropagation();
                onRemoveFromDeck?.();
              }}
            >
              Remove from Deck
            </button>
          ) : (
            <button
              className="card-display__button card-display__button--add"
              onClick={(e) => {
                e.stopPropagation();
                onAddToDeck?.();
              }}
            >
              Add to Deck
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default CardDisplay;
