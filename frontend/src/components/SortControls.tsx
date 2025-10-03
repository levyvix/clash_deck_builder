import React from 'react';
import { SortConfig } from '../types';
import '../styles/SortControls.css';

interface SortControlsProps {
  sortConfig: SortConfig;
  onSort: (config: SortConfig) => void;
}

const SortControls: React.FC<SortControlsProps> = ({ sortConfig, onSort }) => {
  const handleSort = (field: SortConfig['field']) => {
    const newDirection = sortConfig.field === field && sortConfig.direction === 'asc' ? 'desc' : 'asc';
    onSort({ field, direction: newDirection });
  };

  const getSortIcon = (field: SortConfig['field']) => {
    if (sortConfig.field !== field) {
      return '↕'; // Default sort icon
    }
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  const sortFields = [
    { field: 'name' as const, label: 'Name' },
    { field: 'elixir_cost' as const, label: 'Elixir' },
    { field: 'rarity' as const, label: 'Rarity' },
    { field: 'arena' as const, label: 'Arena' }
  ];

  return (
    <div className="sort-controls">
      <span className="sort-controls__label">Sort by:</span>
      <div className="sort-controls__buttons">
        {sortFields.map(({ field, label }) => (
          <button
            key={field}
            className={`sort-button ${sortConfig.field === field ? 'sort-button--active' : ''}`}
            onClick={() => handleSort(field)}
            title={`Sort by ${label} ${sortConfig.field === field && sortConfig.direction === 'asc' ? 'descending' : 'ascending'}`}
          >
            <span className="sort-button__label">{label}</span>
            <span className="sort-button__icon">{getSortIcon(field)}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SortControls;