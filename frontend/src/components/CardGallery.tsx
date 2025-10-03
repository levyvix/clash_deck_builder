import React, { useMemo } from 'react';
import { Card, FilterState, SortConfig } from '../types';
import CardDisplay from './CardDisplay';
import '../styles/CardGallery.css';

interface CardGalleryProps {
  cards: Card[];
  filters: FilterState;
  sortConfig: SortConfig;
  sortCards: (cards: Card[], config: SortConfig) => Card[];
  onCardClick: (card: Card) => void;
  selectedCard: Card | null;
  onAddToDeck: (card: Card) => void;
  loading?: boolean;
  cardsInDeck?: Set<number>;
}

const CardGallery: React.FC<CardGalleryProps> = ({
  cards,
  filters,
  sortConfig,
  sortCards,
  onCardClick,
  selectedCard,
  onAddToDeck,
  loading = false,
  cardsInDeck = new Set(),
}) => {
  // Filter and sort cards based on active filters and sort configuration
  const filteredAndSortedCards = useMemo(() => {
    // First, filter the cards
    const filtered = cards.filter((card) => {
      // Name filter (case-insensitive)
      if (filters.name && !card.name.toLowerCase().includes(filters.name.toLowerCase())) {
        return false;
      }

      // Elixir cost filter
      if (filters.elixirCost !== null && card.elixir_cost !== filters.elixirCost) {
        return false;
      }

      // Rarity filter
      if (filters.rarity && filters.rarity !== 'All' && card.rarity !== filters.rarity) {
        return false;
      }

      // Type filter
      if (filters.type && filters.type !== 'All' && card.type !== filters.type) {
        return false;
      }

      return true;
    });

    // Then, sort the filtered cards
    return sortCards(filtered, sortConfig);
  }, [cards, filters, sortConfig, sortCards]);

  // Loading skeleton
  if (loading) {
    return (
      <div className="card-gallery">
        <div className="card-gallery__grid">
          {Array.from({ length: 12 }).map((_, index) => (
            <div key={index} className="card-gallery__skeleton">
              <div className="card-gallery__skeleton-image"></div>
              <div className="card-gallery__skeleton-text"></div>
              <div className="card-gallery__skeleton-text card-gallery__skeleton-text--short"></div>
              <div className="card-gallery__skeleton-stats">
                <div className="card-gallery__skeleton-stat"></div>
                <div className="card-gallery__skeleton-stat"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (filteredAndSortedCards.length === 0) {
    return (
      <div className="card-gallery">
        <div className="card-gallery__empty">
          <p className="card-gallery__empty-message">No cards found</p>
          <p className="card-gallery__empty-hint">Try adjusting your filters</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card-gallery">
      <div className="card-gallery__header">
        <p className="card-gallery__count">
          {filteredAndSortedCards.length} {filteredAndSortedCards.length === 1 ? 'card' : 'cards'} found
        </p>
      </div>
      <div className="card-gallery__grid">
        {filteredAndSortedCards.map((card) => (
          <CardDisplay
            key={card.id}
            card={card}
            onClick={() => onCardClick(card)}
            showOptions={selectedCard?.id === card.id}
            onAddToDeck={() => onAddToDeck(card)}
            inDeck={cardsInDeck.has(card.id)}
            draggable={true}
            sourceType="gallery"
          />
        ))}
      </div>
    </div>
  );
};

export default CardGallery;
