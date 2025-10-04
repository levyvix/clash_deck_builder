/**
 * Storage Health Indicator Component
 * 
 * Displays the current status of storage systems and provides
 * guidance when storage issues are detected.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { deckStorageService } from '../services/deckStorageService';

import { ErrorHandlingService } from '../services/errorHandlingService';
import '../styles/StorageHealthIndicator.css';

interface StorageHealth {
  local: {
    available: boolean;
    deckCount: number;
    maxDecks: number;
    usagePercentage: number;
    status: 'healthy' | 'warning' | 'error';
    message?: string;
  };
  server: {
    available: boolean;
    deckCount: number;
    status: 'healthy' | 'warning' | 'error';
    message?: string;
  };
  overall: 'healthy' | 'warning' | 'error';
}

interface StorageHealthIndicatorProps {
  onHealthChange?: (health: StorageHealth) => void;
  showDetails?: boolean;
}

const StorageHealthIndicator: React.FC<StorageHealthIndicatorProps> = ({
  onHealthChange,
  showDetails = false
}) => {
  const [health, setHealth] = useState<StorageHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  const checkStorageHealth = useCallback(async () => {
    setLoading(true);
    
    try {
      const stats = await deckStorageService.getStorageStats();
      
      // Analyze local storage health
      const localHealth = analyzeLocalStorageHealth(stats.local);
      
      // Analyze server storage health
      const serverHealth = analyzeServerStorageHealth(stats.server);
      
      // Determine overall health
      const overall = determineOverallHealth(localHealth, serverHealth);
      
      const healthData: StorageHealth = {
        local: localHealth,
        server: serverHealth,
        overall
      };
      
      setHealth(healthData);
      
      if (onHealthChange) {
        onHealthChange(healthData);
      }
    } catch (error) {
      console.error('Failed to check storage health:', error);
      
      const errorInfo = ErrorHandlingService.analyzeError(error);
      const criticalHealth: StorageHealth = {
        local: {
          available: false,
          deckCount: 0,
          maxDecks: 0,
          usagePercentage: 0,
          status: 'error',
          message: errorInfo.userMessage
        },
        server: {
          available: false,
          deckCount: 0,
          status: 'error',
          message: 'Unable to check server status'
        },
        overall: 'error'
      };
      
      setHealth(criticalHealth);
      
      if (onHealthChange) {
        onHealthChange(criticalHealth);
      }
    } finally {
      setLoading(false);
    }
  }, [onHealthChange]);

  useEffect(() => {
    checkStorageHealth();
    
    // Check health periodically
    const interval = setInterval(checkStorageHealth, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, [checkStorageHealth]);

  const analyzeLocalStorageHealth = (localStats: any) => {
    if (!localStats.available) {
      return {
        available: false,
        deckCount: 0,
        maxDecks: 0,
        usagePercentage: 0,
        status: 'error' as const,
        message: 'Local storage is not available'
      };
    }

    const usagePercentage = (localStats.deckCount / localStats.maxDecks) * 100;
    
    let status: 'healthy' | 'warning' | 'error' = 'healthy';
    let message: string | undefined;
    
    if (usagePercentage >= 90) {
      status = 'error';
      message = `Storage almost full (${localStats.deckCount}/${localStats.maxDecks} decks)`;
    } else if (usagePercentage >= 75) {
      status = 'warning';
      message = `Storage getting full (${localStats.deckCount}/${localStats.maxDecks} decks)`;
    }

    return {
      available: true,
      deckCount: localStats.deckCount,
      maxDecks: localStats.maxDecks,
      usagePercentage,
      status,
      message
    };
  };

  const analyzeServerStorageHealth = (serverStats: any) => {
    if (!serverStats.available) {
      return {
        available: false,
        deckCount: 0,
        status: 'warning' as const,
        message: 'Server storage not available'
      };
    }

    return {
      available: true,
      deckCount: serverStats.deckCount,
      status: 'healthy' as const
    };
  };

  const determineOverallHealth = (local: any, server: any): 'healthy' | 'warning' | 'error' => {
    if (local.status === 'error' && server.status === 'error') {
      return 'error';
    }
    
    if (local.status === 'error' || server.status === 'error' || 
        local.status === 'warning' || server.status === 'warning') {
      return 'warning';
    }
    
    return 'healthy';
  };

  const getHealthIcon = (status: 'healthy' | 'warning' | 'error') => {
    switch (status) {
      case 'healthy':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      default:
        return '❓';
    }
  };

  const getHealthColor = (status: 'healthy' | 'warning' | 'error') => {
    switch (status) {
      case 'healthy':
        return '#27ae60';
      case 'warning':
        return '#f39c12';
      case 'error':
        return '#e74c3c';
      default:
        return '#95a5a6';
    }
  };

  if (loading) {
    return (
      <div className="storage-health-indicator storage-health-indicator--loading">
        <span className="storage-health-indicator__icon">⏳</span>
        <span className="storage-health-indicator__text">Checking storage...</span>
      </div>
    );
  }

  if (!health) {
    return null;
  }

  return (
    <div className={`storage-health-indicator storage-health-indicator--${health.overall}`}>
      <div 
        className="storage-health-indicator__summary"
        onClick={() => setExpanded(!expanded)}
        style={{ cursor: showDetails ? 'pointer' : 'default' }}
      >
        <span className="storage-health-indicator__icon">
          {getHealthIcon(health.overall)}
        </span>
        <span className="storage-health-indicator__text">
          Storage: {health.overall}
        </span>
        {showDetails && (
          <span className="storage-health-indicator__toggle">
            {expanded ? '▼' : '▶'}
          </span>
        )}
      </div>

      {showDetails && expanded && (
        <div className="storage-health-indicator__details">
          {/* Local Storage Details */}
          <div className="storage-health-detail">
            <div className="storage-health-detail__header">
              <span className="storage-health-detail__icon">
                {getHealthIcon(health.local.status)}
              </span>
              <span className="storage-health-detail__title">Local Storage</span>
            </div>
            
            {health.local.available ? (
              <div className="storage-health-detail__content">
                <div className="storage-health-detail__stat">
                  Decks: {health.local.deckCount}/{health.local.maxDecks}
                </div>
                <div className="storage-health-detail__progress">
                  <div 
                    className="storage-health-detail__progress-bar"
                    style={{ 
                      width: `${health.local.usagePercentage}%`,
                      backgroundColor: getHealthColor(health.local.status)
                    }}
                  />
                </div>
                {health.local.message && (
                  <div className="storage-health-detail__message">
                    {health.local.message}
                  </div>
                )}
              </div>
            ) : (
              <div className="storage-health-detail__content">
                <div className="storage-health-detail__message storage-health-detail__message--error">
                  {health.local.message || 'Not available'}
                </div>
              </div>
            )}
          </div>

          {/* Server Storage Details */}
          <div className="storage-health-detail">
            <div className="storage-health-detail__header">
              <span className="storage-health-detail__icon">
                {getHealthIcon(health.server.status)}
              </span>
              <span className="storage-health-detail__title">Server Storage</span>
            </div>
            
            {health.server.available ? (
              <div className="storage-health-detail__content">
                <div className="storage-health-detail__stat">
                  Decks: {health.server.deckCount}
                </div>
                {health.server.message && (
                  <div className="storage-health-detail__message">
                    {health.server.message}
                  </div>
                )}
              </div>
            ) : (
              <div className="storage-health-detail__content">
                <div className="storage-health-detail__message storage-health-detail__message--warning">
                  {health.server.message || 'Not available'}
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="storage-health-detail__actions">
            <button 
              className="storage-health-detail__action"
              onClick={checkStorageHealth}
            >
              Refresh Status
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default StorageHealthIndicator;