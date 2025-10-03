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
}

const CardDisplay: React.FC<CardDisplayProps> = ({
  card,
  isEvolution = false,
  onClick,
  showOptions = false,
  onAddToDeck,
  onRemoveFromDeck,
  inDeck = false,
}) => {
  const [imageError, setImageError] = useState(false);

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

  return (
    <div
      className={`card-display ${rarityClass} ${onClick ? 'card-display--clickable' : ''}`}
      onClick={handleClick}
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
            <span className="card-display__elixir-icon">⚡</span>
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
