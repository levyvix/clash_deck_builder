// Demo component to showcase storage type indicators
import React from 'react';
import '../styles/StorageIndicators.css';

const StorageIndicatorDemo: React.FC = () => {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f5f5f5' }}>
      <h2>Storage Type Indicators Demo</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>Size Variants</h3>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '10px' }}>
          <span className="storage-indicator storage-indicator--small storage-indicator--local">
            Small Local
          </span>
          <span className="storage-indicator storage-indicator--medium storage-indicator--local">
            Medium Local
          </span>
          <span className="storage-indicator storage-indicator--large storage-indicator--local">
            Large Local
          </span>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span className="storage-indicator storage-indicator--small storage-indicator--server">
            Small Server
          </span>
          <span className="storage-indicator storage-indicator--medium storage-indicator--server">
            Medium Server
          </span>
          <span className="storage-indicator storage-indicator--large storage-indicator--server">
            Large Server
          </span>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Badge Variants (for deck cards)</h3>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span className="storage-badge storage-badge--local">
            💾 Local
          </span>
          <span className="storage-badge storage-badge--server">
            ☁️ Server
          </span>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Storage Summary</h3>
        <div className="storage-summary">
          <span className="storage-indicator storage-indicator--medium storage-indicator--local">
            Local <span className="storage-summary__count">5</span>
          </span>
          <span className="storage-indicator storage-indicator--medium storage-indicator--server">
            Server <span className="storage-summary__count">3</span>
          </span>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>In Context (Simulated Deck Card)</h3>
        <div style={{ 
          position: 'relative',
          backgroundColor: 'white',
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          padding: '16px',
          width: '300px',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ 
            position: 'absolute',
            top: '8px',
            right: '8px'
          }}>
            <span className="storage-badge storage-badge--local">
              💾 Local
            </span>
          </div>
          <h4 style={{ marginTop: '20px', marginBottom: '10px' }}>My Awesome Deck</h4>
          <p style={{ color: '#666', fontSize: '14px' }}>This is how storage indicators look on deck cards</p>
        </div>
      </div>
    </div>
  );
};

export default StorageIndicatorDemo;