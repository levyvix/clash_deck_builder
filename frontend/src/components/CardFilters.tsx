// frontend/src/components/CardFilters.tsx

import React, { useState } from 'react';

interface CardFiltersProps {
  onFilterChange: (filters: any) => void;
}

const CardFilters: React.FC<CardFiltersProps> = ({ onFilterChange }) => {
  const [name, setName] = useState('');
  const [rarity, setRarity] = useState('');
  const [elixir, setElixir] = useState('');
  const [type, setType] = useState('');
  const [arena, setArena] = useState('');

  const handleFilter = () => {
    onFilterChange({
      name, rarity, elixir, type, arena
    });
  };

  return (
    <div className="card-filters">
      <input type="text" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
      <select value={rarity} onChange={e => setRarity(e.target.value)}>
        <option value="">All Rarities</option>
        {/* Populate with actual rarities */}
      </select>
      <select value={elixir} onChange={e => setElixir(e.target.value)}>
        <option value="">All Elixirs</option>
        {/* Populate with actual elixir costs */}
      </select>
      <select value={type} onChange={e => setType(e.target.value)}>
        <option value="">All Types</option>
        {/* Populate with actual card types */}
      </select>
      <input type="text" placeholder="Arena" value={arena} onChange={e => setArena(e.target.value)} />
      <button onClick={handleFilter}>Apply Filters</button>
    </div>
  );
};

export default CardFilters;
