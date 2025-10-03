// frontend/src/components/CardDisplay.tsx

import React from 'react';

interface CardDisplayProps {
  card: {
    id: number;
    name: string;
    elixir_cost: number;
    rarity: string;
    type: string;
    arena?: string;
    image_url: string;
    image_url_evo?: string;
  };
  isEvo?: boolean;
}

const CardDisplay: React.FC<CardDisplayProps> = ({ card, isEvo = false }) => {
  const imageUrl = isEvo && card.image_url_evo ? card.image_url_evo : card.image_url;

  return (
    <div className="card-display">
      <img src={imageUrl} alt={card.name} />
      <h3>{card.name}</h3>
      <p>Elixir: {card.elixir_cost}</p>
      <p>Rarity: {card.rarity}</p>
      {/* Add more card details and styling based on rarity/type */}
    </div>
  );
};

export default CardDisplay;
