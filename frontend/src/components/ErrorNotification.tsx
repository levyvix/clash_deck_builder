/**
 * Enhanced Error Notification Component
 * 
 * Displays detailed error information with suggested actions
 * and retry mechanisms for recoverable errors.
 */

import React, { useState } from 'react';
import { EnhancedError, ErrorHandlingService } from '../services/errorHandlingService';
import '../styles/ErrorNotification.css';

interface ErrorNotificationProps {
  error: unknown;
  onRetry?: () => void;
  onDismiss: () => void;
  showTechnicalDetails?: boolean;
}

const ErrorNotification: React.FC<ErrorNotificationProps> = ({
  error,
  onRetry,
  onDismiss,
  showTechnicalDetails = false
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [retrying, setRetrying] = useState(false);
  
  const errorInfo = ErrorHandlingService.analyzeError(error);

  const handleRetry = async () => {
    if (!onRetry || !errorInfo.retryable) return;
    
    setRetrying(true);
    try {
      await onRetry();
      onDismiss(); // Close notification on successful retry
    } catch (retryError) {
      console.error('Retry failed:', retryError);
      // Keep notification open to show the new error
    } finally {
      setRetrying(false);
    }
  };

  const getSeverityIcon = () => {
    switch (errorInfo.severity) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'medium':
        return '⚡';
      case 'low':
        return 'ℹ️';
      default:
        return '❗';
    }
  };

  const getSeverityClass = () => {
    return `error-notification--${errorInfo.severity}`;
  };

  return (
    <div className={`error-notification ${getSeverityClass()}`}>
      <div className="error-notification__header">
        <div className="error-notification__icon">
          {getSeverityIcon()}
        </div>
        <div className="error-notification__title">
          <h4>Storage Error</h4>
          <p className="error-notification__message">{errorInfo.userMessage}</p>
        </div>
        <button 
          className="error-notification__close"
          onClick={onDismiss}
          aria-label="Close notification"
        >
          ✕
        </button>
      </div>

      {errorInfo.suggestedActions.length > 0 && (
        <div className="error-notification__actions">
          <h5>What you can do:</h5>
          <ul className="error-notification__action-list">
            {errorInfo.suggestedActions.map((action, index) => (
              <li key={index} className="error-notification__action-item">
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="error-notification__buttons">
        {errorInfo.retryable && onRetry && (
          <button
            className="error-notification__button error-notification__button--retry"
            onClick={handleRetry}
            disabled={retrying}
          >
            {retrying ? (
              <>
                <span className="spinner spinner--small"></span>
                Retrying...
              </>
            ) : (
              'Try Again'
            )}
          </button>
        )}
        
        {(showTechnicalDetails || errorInfo.technicalDetails) && (
          <button
            className="error-notification__button error-notification__button--details"
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? 'Hide Details' : 'Show Details'}
          </button>
        )}
      </div>

      {showDetails && errorInfo.technicalDetails && (
        <div className="error-notification__technical">
          <h5>Technical Details:</h5>
          <code className="error-notification__code">
            {errorInfo.technicalDetails}
          </code>
          <p className="error-notification__error-code">
            Error Code: {errorInfo.code}
          </p>
        </div>
      )}
    </div>
  );
};

export default ErrorNotification;