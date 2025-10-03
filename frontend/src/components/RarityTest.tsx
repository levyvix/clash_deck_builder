import React from 'react';
import { Card } from '../types';
import CardDisplay from './CardDisplay';
import '../styles/CardDisplay.css';

/**
 * RarityTest Component
 * 
 * This component is used for visual testing of rarity colors.
 * It displays sample cards for each rarity to verify colors are correct.
 * 
 * To use: Import and render in App.tsx temporarily for testing.
 */

const RarityTest: React.FC = () => {
  const testCards: Card[] = [
    {
      id: 1,
      name: 'Common Card',
      elixir_cost: 3,
      rarity: 'Common',
      type: 'Troop',
      image_url: 'https://api-assets.clashroyale.com/cards/300/yHGpoEnmUWPGV_JQdNonSYEPc7D2zt0aSU41RgbHUkI.png',
    },
    {
      id: 2,
      name: 'Rare Card',
      elixir_cost: 4,
      rarity: 'Rare',
      type: 'Spell',
      image_url: 'https://api-assets.clashroyale.com/cards/300/Qg8Ufp_xaWi1e6Dn8RiZlbZu-JJUvYqPUTlNHQY6YQE.png',
    },
    {
      id: 3,
      name: 'Epic Card',
      elixir_cost: 5,
      rarity: 'Epic',
      type: 'Building',
      image_url: 'https://api-assets.clashroyale.com/cards/300/F5gNfJ4Qr3fYp0VqFqJvhQzFqJqJZqJqJqJqJqJqJqJ.png',
    },
    {
      id: 4,
      name: 'Legendary Card',
      elixir_cost: 6,
      rarity: 'Legendary',
      type: 'Troop',
      image_url: 'https://api-assets.clashroyale.com/cards/300/MlArURKhn_zWAZY-Xj1qIRKLVKquarG25BXDjUQajNs.png',
    },
    {
      id: 5,
      name: 'Champion Card',
      elixir_cost: 7,
      rarity: 'Champion',
      type: 'Troop',
      image_url: 'https://api-assets.clashroyale.com/cards/300/arNfvwQJ_F5m8xZKFRHXQXJ5T6pJqJqJqJqJqJqJqJq.png',
    },
  ];

  return (
    <div style={{ padding: '40px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <h1 style={{ marginBottom: '32px', textAlign: 'center' }}>Rarity Color Test</h1>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '24px',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {testCards.map((card) => (
          <div key={card.id} style={{ textAlign: 'center' }}>
            <CardDisplay card={card} />
            <div style={{ marginTop: '16px' }}>
              <h3 style={{ margin: '8px 0', fontSize: '16px' }}>{card.rarity}</h3>
              <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                Border & Badge Color Test
              </p>
            </div>
          </div>
        ))}
      </div>

      <div style={{ 
        marginTop: '48px', 
        padding: '24px', 
        backgroundColor: 'white',
        borderRadius: '8px',
        maxWidth: '800px',
        margin: '48px auto 0'
      }}>
        <h2 style={{ marginBottom: '16px' }}>Expected Colors:</h2>
        <ul style={{ lineHeight: '1.8' }}>
          <li><strong>Common:</strong> Gray border (#808080), gray badge</li>
          <li><strong>Rare:</strong> Orange border (#ff8c00), orange badge</li>
          <li><strong>Epic:</strong> Purple border (#9370db), purple badge</li>
          <li><strong>Legendary:</strong> Gold border (#ffd700), gradient badge (gold to orange)</li>
          <li><strong>Champion:</strong> Gold border (#ffd700), gold badge with dark text</li>
        </ul>
      </div>

      <div style={{ 
        marginTop: '24px', 
        padding: '24px', 
        backgroundColor: '#fff3cd',
        borderRadius: '8px',
        maxWidth: '800px',
        margin: '24px auto 0',
        border: '1px solid #ffc107'
      }}>
        <h3 style={{ marginTop: 0 }}>Testing Instructions:</h3>
        <ol style={{ lineHeight: '1.8', marginBottom: 0 }}>
          <li>Verify each card has the correct border color</li>
          <li>Verify each rarity badge has the correct background color</li>
          <li>Check that Legendary has a gradient effect</li>
          <li>Verify text is readable on all badge backgrounds</li>
          <li>Test on different screen sizes (desktop, tablet, mobile)</li>
          <li>Test with browser zoom at 100%, 150%, and 200%</li>
        </ol>
      </div>
    </div>
  );
};

export default RarityTest;
