import React, { useState } from 'react';
import '../styles/RemoveDropZone.css';

interface RemoveDropZoneProps {
  onRemoveCard: (sourceIndex: number) => void;
}

interface DragData {
  cardId: number;
  sourceType: 'gallery' | 'deck';
  sourceIndex?: number;
}

const RemoveDropZone: React.FC<RemoveDropZoneProps> = ({ onRemoveCard }) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault(); // Allow drop
    e.dataTransfer.dropEffect = 'move';
    
    // Only highlight if dragging from deck
    try {
      const dragData: DragData = JSON.parse(e.dataTransfer.getData('application/json'));
      if (dragData.sourceType === 'deck') {
        setIsDragOver(true);
      }
    } catch {
      // If we can't parse the data yet, still allow drag over
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    // Only trigger if leaving the zone itself, not child elements
    if (e.currentTarget === e.target || !e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);

    try {
      const dragData: DragData = JSON.parse(e.dataTransfer.getData('application/json'));
      
      // Only handle drops from deck slots
      if (dragData.sourceType === 'deck' && dragData.sourceIndex !== undefined) {
        onRemoveCard(dragData.sourceIndex);
      }
    } catch (error) {
      console.error('Failed to parse drag data:', error);
    }
  };

  return (
    <div 
      className={`remove-drop-zone ${isDragOver ? 'remove-drop-zone--drag-over' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="remove-drop-zone__icon">🗑️</div>
      <div className="remove-drop-zone__text">
        {isDragOver ? 'Drop to remove' : 'Drag here to remove'}
      </div>
    </div>
  );
};

export default RemoveDropZone;
