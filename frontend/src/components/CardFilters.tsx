import React, { useState, useEffect } from 'react';
import { FilterState } from '../types';
import '../styles/CardFilters.css';

interface CardFiltersProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  onClearFilters: () => void;
}

const CardFilters: React.FC<CardFiltersProps> = ({
  filters,
  onFilterChange,
  onClearFilters,
}) => {
  const [nameInput, setNameInput] = useState(filters.name);

  // Debounce name filter with 300ms delay
  useEffect(() => {
    const timer = setTimeout(() => {
      if (nameInput !== filters.name) {
        onFilterChange({ ...filters, name: nameInput });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [nameInput]);

  // Update local state when filters prop changes externally
  useEffect(() => {
    setNameInput(filters.name);
  }, [filters.name]);

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNameInput(e.target.value);
  };

  const handleElixirChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value === 'all' ? null : parseInt(e.target.value);
    onFilterChange({ ...filters, elixirCost: value });
  };

  const handleRarityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value === 'all' ? null : e.target.value;
    onFilterChange({ ...filters, rarity: value });
  };

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value === 'all' ? null : e.target.value;
    onFilterChange({ ...filters, type: value });
  };

  // Calculate active filter count
  const activeFilterCount = [
    filters.name !== '',
    filters.elixirCost !== null,
    filters.rarity !== null,
    filters.type !== null,
  ].filter(Boolean).length;

  const hasActiveFilters = activeFilterCount > 0;

  return (
    <div className="card-filters">
      <div className="card-filters__header">
        <h3 className="card-filters__title">Filter Cards</h3>
        {activeFilterCount > 0 && (
          <span className="card-filters__badge">{activeFilterCount}</span>
        )}
      </div>

      <div className="card-filters__controls">
        <div className="card-filters__control">
          <label htmlFor="name-filter" className="card-filters__label">
            Name
          </label>
          <input
            id="name-filter"
            type="text"
            className="card-filters__input"
            placeholder="Search by name..."
            value={nameInput}
            onChange={handleNameChange}
          />
        </div>

        <div className="card-filters__control">
          <label htmlFor="elixir-filter" className="card-filters__label">
            Elixir Cost
          </label>
          <select
            id="elixir-filter"
            className="card-filters__select"
            value={filters.elixirCost === null ? 'all' : filters.elixirCost}
            onChange={handleElixirChange}
          >
            <option value="all">All</option>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((cost) => (
              <option key={cost} value={cost}>
                {cost}
              </option>
            ))}
          </select>
        </div>

        <div className="card-filters__control">
          <label htmlFor="rarity-filter" className="card-filters__label">
            Rarity
          </label>
          <select
            id="rarity-filter"
            className="card-filters__select"
            value={filters.rarity || 'all'}
            onChange={handleRarityChange}
          >
            <option value="all">All</option>
            <option value="Common">Common</option>
            <option value="Rare">Rare</option>
            <option value="Epic">Epic</option>
            <option value="Legendary">Legendary</option>
            <option value="Champion">Champion</option>
          </select>
        </div>

        <div className="card-filters__control">
          <label htmlFor="type-filter" className="card-filters__label">
            Type
          </label>
          <select
            id="type-filter"
            className="card-filters__select"
            value={filters.type || 'all'}
            onChange={handleTypeChange}
          >
            <option value="all">All</option>
            <option value="Troop">Troop</option>
            <option value="Spell">Spell</option>
            <option value="Building">Building</option>
          </select>
        </div>
      </div>

      <button
        className="card-filters__clear-button"
        onClick={onClearFilters}
        disabled={!hasActiveFilters}
      >
        Clear Filters
      </button>
    </div>
  );
};

export default CardFilters;
