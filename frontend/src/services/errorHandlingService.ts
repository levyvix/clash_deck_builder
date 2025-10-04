/**
 * Enhanced Error Handling Service for Anonymous Deck Storage
 * 
 * Provides comprehensive error handling with user-friendly messages,
 * retry mechanisms, and graceful degradation strategies.
 */

import { LocalStorageError, LocalStorageQuotaError, LocalStorageUnavailableError, LocalStorageDataCorruptionError } from './localStorageService';
import { DeckStorageError } from './deckStorageService';
import { ApiError } from './api';

// Error severity levels
export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

// Error categories for better handling
export type ErrorCategory = 'storage' | 'network' | 'validation' | 'quota' | 'permission' | 'corruption';

// Enhanced error information
export interface EnhancedError {
  message: string;
  userMessage: string;
  severity: ErrorSeverity;
  category: ErrorCategory;
  code: string;
  retryable: boolean;
  actionable: boolean;
  suggestedActions: string[];
  technicalDetails?: string;
}

// Retry configuration
export interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
}

// Default retry configuration
const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 10000, // 10 seconds
  backoffMultiplier: 2,
};

/**
 * Enhanced Error Handling Service
 */
export class ErrorHandlingService {
  
  /**
   * Analyze and enhance error information
   */
  static analyzeError(error: unknown): EnhancedError {
    // Handle LocalStorage specific errors
    if (error instanceof LocalStorageUnavailableError) {
      return {
        message: error.message,
        userMessage: 'Your browser\'s local storage is not available or disabled.',
        severity: 'high',
        category: 'storage',
        code: error.code,
        retryable: false,
        actionable: true,
        suggestedActions: [
          'Enable cookies and local storage in your browser settings',
          'Try using a different browser',
          'Disable private/incognito mode if active',
          'Clear browser data and try again'
        ],
        technicalDetails: 'localStorage API is not available or throws exceptions'
      };
    }

    if (error instanceof LocalStorageQuotaError) {
      return {
        message: error.message,
        userMessage: 'Your browser\'s storage is full. You need to free up space to save more decks.',
        severity: 'medium',
        category: 'quota',
        code: error.code,
        retryable: false,
        actionable: true,
        suggestedActions: [
          'Delete some old decks to free up space',
          'Clear browser data for this site',
          'Use a different browser with more available storage',
          'Consider signing in to save decks to the server instead'
        ],
        technicalDetails: 'localStorage quota exceeded (typically 5-10MB limit)'
      };
    }

    if (error instanceof LocalStorageDataCorruptionError) {
      return {
        message: error.message,
        userMessage: 'Your saved deck data was corrupted and has been reset.',
        severity: 'medium',
        category: 'corruption',
        code: error.code,
        retryable: false,
        actionable: false,
        suggestedActions: [
          'Your decks have been cleared to prevent further issues',
          'You can start saving new decks normally',
          'Consider signing in to prevent data loss in the future'
        ],
        technicalDetails: 'localStorage data structure was invalid or corrupted'
      };
    }

    if (error instanceof LocalStorageError) {
      return {
        message: error.message,
        userMessage: 'There was a problem with local storage.',
        severity: 'medium',
        category: 'storage',
        code: error.code,
        retryable: true,
        actionable: true,
        suggestedActions: [
          'Try the operation again',
          'Refresh the page and try again',
          'Check your browser settings for storage permissions'
        ],
        technicalDetails: error.message
      };
    }

    // Handle DeckStorage specific errors
    if (error instanceof DeckStorageError) {
      const baseError = this.analyzeDeckStorageError(error);
      return baseError;
    }

    // Handle API errors
    if (error instanceof ApiError) {
      return this.analyzeApiError(error);
    }

    // Handle generic errors
    if (error instanceof Error) {
      return {
        message: error.message,
        userMessage: 'An unexpected error occurred.',
        severity: 'medium',
        category: 'validation',
        code: 'UNKNOWN_ERROR',
        retryable: true,
        actionable: false,
        suggestedActions: [
          'Try the operation again',
          'Refresh the page if the problem persists'
        ],
        technicalDetails: error.message
      };
    }

    // Handle unknown errors
    return {
      message: 'Unknown error occurred',
      userMessage: 'Something went wrong. Please try again.',
      severity: 'medium',
      category: 'validation',
      code: 'UNKNOWN_ERROR',
      retryable: true,
      actionable: false,
      suggestedActions: [
        'Try the operation again',
        'Refresh the page if the problem persists'
      ]
    };
  }

  /**
   * Analyze DeckStorageError specifically
   */
  private static analyzeDeckStorageError(error: DeckStorageError): EnhancedError {
    switch (error.code) {
      case 'LOCAL_STORAGE_UNAVAILABLE':
        return {
          message: error.message,
          userMessage: 'Cannot save decks locally because browser storage is disabled.',
          severity: 'high',
          category: 'storage',
          code: error.code,
          retryable: false,
          actionable: true,
          suggestedActions: [
            'Enable local storage in your browser settings',
            'Sign in to save decks to the server instead',
            'Try using a different browser'
          ]
        };

      case 'DECK_LIMIT_EXCEEDED':
        return {
          message: error.message,
          userMessage: 'You\'ve reached the maximum of 20 saved decks.',
          severity: 'medium',
          category: 'quota',
          code: error.code,
          retryable: false,
          actionable: true,
          suggestedActions: [
            'Delete some old decks to make room for new ones',
            'Sign in to save unlimited decks to the server'
          ]
        };

      case 'SERVER_SAVE_FAILED':
        return {
          message: error.message,
          userMessage: 'Could not save to server. Your deck will be saved locally instead.',
          severity: 'medium',
          category: 'network',
          code: error.code,
          retryable: true,
          actionable: true,
          suggestedActions: [
            'Check your internet connection',
            'Try saving again in a moment',
            'Your deck is saved locally for now'
          ]
        };

      case 'STORAGE_UNAVAILABLE':
        return {
          message: error.message,
          userMessage: 'Cannot access any storage. Your decks cannot be saved right now.',
          severity: 'critical',
          category: 'storage',
          code: error.code,
          retryable: true,
          actionable: true,
          suggestedActions: [
            'Check your internet connection',
            'Enable local storage in browser settings',
            'Try refreshing the page'
          ]
        };

      default:
        return {
          message: error.message,
          userMessage: 'There was a problem saving your deck.',
          severity: 'medium',
          category: 'storage',
          code: error.code,
          retryable: true,
          actionable: false,
          suggestedActions: [
            'Try the operation again',
            'Refresh the page if the problem persists'
          ]
        };
    }
  }

  /**
   * Analyze API errors specifically
   */
  private static analyzeApiError(error: ApiError): EnhancedError {
    if (error.isTimeout) {
      return {
        message: error.message,
        userMessage: 'The request took too long. Please check your connection.',
        severity: 'medium',
        category: 'network',
        code: 'TIMEOUT',
        retryable: true,
        actionable: true,
        suggestedActions: [
          'Check your internet connection',
          'Try again in a moment',
          'Use local storage if the problem persists'
        ]
      };
    }

    if (error.isNetworkError) {
      return {
        message: error.message,
        userMessage: 'Cannot connect to the server. Working in offline mode.',
        severity: 'medium',
        category: 'network',
        code: 'NETWORK_ERROR',
        retryable: true,
        actionable: true,
        suggestedActions: [
          'Check your internet connection',
          'Your decks will be saved locally for now',
          'Try again when connection is restored'
        ]
      };
    }

    if (error.statusCode && error.statusCode >= 500) {
      return {
        message: error.message,
        userMessage: 'The server is having problems. Please try again later.',
        severity: 'medium',
        category: 'network',
        code: 'SERVER_ERROR',
        retryable: true,
        actionable: true,
        suggestedActions: [
          'Try again in a few minutes',
          'Use local storage for now',
          'Contact support if the problem persists'
        ]
      };
    }

    return {
      message: error.message,
      userMessage: 'There was a problem with the server request.',
      severity: 'medium',
      category: 'network',
      code: 'API_ERROR',
      retryable: true,
      actionable: false,
      suggestedActions: [
        'Try the operation again',
        'Check your internet connection'
      ]
    };
  }

  /**
   * Execute operation with retry logic
   */
  static async withRetry<T>(
    operation: () => Promise<T>,
    config: Partial<RetryConfig> = {}
  ): Promise<T> {
    const retryConfig = { ...DEFAULT_RETRY_CONFIG, ...config };
    let lastError: unknown;

    for (let attempt = 1; attempt <= retryConfig.maxAttempts; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        
        // Analyze error to determine if it's retryable
        const errorInfo = ErrorHandlingService.analyzeError(error);
        
        if (!errorInfo.retryable || attempt === retryConfig.maxAttempts) {
          throw error;
        }

        // Calculate delay with exponential backoff
        const delay = Math.min(
          retryConfig.baseDelay * Math.pow(retryConfig.backoffMultiplier, attempt - 1),
          retryConfig.maxDelay
        );

        console.warn(`Operation failed (attempt ${attempt}/${retryConfig.maxAttempts}), retrying in ${delay}ms:`, errorInfo.message);
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError;
  }

  /**
   * Execute operation with graceful degradation
   */
  static async withGracefulDegradation<T>(
    primaryOperation: () => Promise<T>,
    fallbackOperation: () => Promise<T>,
    options: {
      primaryDescription: string;
      fallbackDescription: string;
      onFallback?: (error: EnhancedError) => void;
    }
  ): Promise<T> {
    try {
      return await primaryOperation();
    } catch (error) {
      const errorInfo = ErrorHandlingService.analyzeError(error);
      
      console.warn(`${options.primaryDescription} failed, falling back to ${options.fallbackDescription}:`, errorInfo.message);
      
      if (options.onFallback) {
        options.onFallback(errorInfo);
      }

      try {
        return await fallbackOperation();
      } catch (fallbackError) {
        const fallbackErrorInfo = ErrorHandlingService.analyzeError(fallbackError);
        console.error(`Both ${options.primaryDescription} and ${options.fallbackDescription} failed:`, {
          primary: errorInfo,
          fallback: fallbackErrorInfo
        });
        
        // Throw the more severe error
        if (fallbackErrorInfo.severity === 'critical' || errorInfo.severity !== 'critical') {
          throw fallbackError;
        }
        throw error;
      }
    }
  }

  /**
   * Format error message for user display
   */
  static formatUserMessage(error: unknown, includeActions: boolean = true): string {
    const errorInfo = ErrorHandlingService.analyzeError(error);
    
    let message = errorInfo.userMessage;
    
    if (includeActions && errorInfo.actionable && errorInfo.suggestedActions.length > 0) {
      message += '\n\nSuggested actions:\n' + errorInfo.suggestedActions.map(action => `• ${action}`).join('\n');
    }
    
    return message;
  }

  /**
   * Check if error is recoverable
   */
  static isRecoverable(error: unknown): boolean {
    const errorInfo = ErrorHandlingService.analyzeError(error);
    return errorInfo.retryable || errorInfo.actionable;
  }

  /**
   * Get error severity level
   */
  static getErrorSeverity(error: unknown): ErrorSeverity {
    const errorInfo = ErrorHandlingService.analyzeError(error);
    return errorInfo.severity;
  }
}

// Export convenience functions
export const analyzeError = ErrorHandlingService.analyzeError;
export const withRetry = ErrorHandlingService.withRetry;
export const withGracefulDegradation = ErrorHandlingService.withGracefulDegradation;
export const formatUserMessage = ErrorHandlingService.formatUserMessage;
export const isRecoverable = ErrorHandlingService.isRecoverable;
export const getErrorSeverity = ErrorHandlingService.getErrorSeverity;