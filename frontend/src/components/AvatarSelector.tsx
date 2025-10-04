import React, { useState, useEffect, useMemo } from 'react';
import { Card } from '../types/index';
import { fetchCards } from '../services/api';
import '../styles/AvatarSelector.css';

interface AvatarSelectorProps {
  isOpen: boolean;
  currentAvatar: string | null;
  onSelect: (cardId: string) => void;
  onClose: () => void;
}

const AvatarSelector: React.FC<AvatarSelectorProps> = ({
  isOpen,
  currentAvatar,
  onSelect,
  onClose
}) => {
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRarity, setSelectedRarity] = useState<string>('');

  // Fetch cards when modal opens
  useEffect(() => {
    if (isOpen && cards.length === 0) {
      loadCards();
    }
  }, [isOpen, cards.length]);

  const loadCards = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedCards = await fetchCards();
      setCards(fetchedCards);
    } catch (err) {
      setError('Failed to load cards. Please try again.');
      console.error('Error loading cards for avatar selection:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort cards
  const filteredCards = useMemo(() => {
    let filtered = cards;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(card =>
        card.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by rarity
    if (selectedRarity) {
      filtered = filtered.filter(card => card.rarity === selectedRarity);
    }

    // Sort by rarity (Legendary first, then Champion, Epic, Rare, Common)
    const rarityOrder = { 'Legendary': 0, 'Champion': 1, 'Epic': 2, 'Rare': 3, 'Common': 4 };
    filtered.sort((a, b) => {
      const rarityDiff = rarityOrder[a.rarity] - rarityOrder[b.rarity];
      if (rarityDiff !== 0) return rarityDiff;
      return a.name.localeCompare(b.name);
    });

    return filtered;
  }, [cards, searchTerm, selectedRarity]);

  const handleCardSelect = (card: Card) => {
    onSelect(card.id.toString());
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const getRarityClass = (rarity: string) => {
    return `avatar-selector__card--${rarity.toLowerCase()}`;
  };

  if (!isOpen) return null;

  return (
    <div className="avatar-selector__backdrop" onClick={handleBackdropClick}>
      <div className="avatar-selector__modal">
        <div className="avatar-selector__header">
          <h3 className="avatar-selector__title">Choose Your Avatar</h3>
          <button 
            className="avatar-selector__close-button"
            onClick={onClose}
            aria-label="Close avatar selector"
          >
            ×
          </button>
        </div>

        <div className="avatar-selector__filters">
          <div className="avatar-selector__search">
            <input
              type="text"
              placeholder="Search cards..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="avatar-selector__search-input"
            />
          </div>
          
          <div className="avatar-selector__rarity-filter">
            <select
              value={selectedRarity}
              onChange={(e) => setSelectedRarity(e.target.value)}
              className="avatar-selector__rarity-select"
            >
              <option value="">All Rarities</option>
              <option value="Legendary">Legendary</option>
              <option value="Champion">Champion</option>
              <option value="Epic">Epic</option>
              <option value="Rare">Rare</option>
              <option value="Common">Common</option>
            </select>
          </div>
        </div>

        <div className="avatar-selector__content">
          {loading && (
            <div className="avatar-selector__loading">
              <p>Loading cards...</p>
            </div>
          )}

          {error && (
            <div className="avatar-selector__error">
              <p>{error}</p>
              <button 
                onClick={loadCards}
                className="avatar-selector__retry-button"
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && (
            <div className="avatar-selector__grid">
              {filteredCards.map((card) => (
                <div
                  key={card.id}
                  className={`avatar-selector__card ${getRarityClass(card.rarity)} ${
                    currentAvatar === card.id.toString() ? 'avatar-selector__card--selected' : ''
                  }`}
                  onClick={() => handleCardSelect(card)}
                >
                  <img
                    src={card.image_url}
                    alt={card.name}
                    className="avatar-selector__card-image"
                  />
                  <div className="avatar-selector__card-info">
                    <span className="avatar-selector__card-name">{card.name}</span>
                    <span className="avatar-selector__card-rarity">{card.rarity}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && !error && filteredCards.length === 0 && (
            <div className="avatar-selector__no-results">
              <p>No cards found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AvatarSelector;