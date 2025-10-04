/**
 * Tests for Enhanced Error Handling Service
 */

import { ErrorHandlingService, withRetry, withGracefulDegradation, formatUserMessage } from './errorHandlingService';
import { LocalStorageError, LocalStorageQuotaError, LocalStorageUnavailableError, LocalStorageDataCorruptionError } from './localStorageService';
import { DeckStorageError } from './deckStorageService';
import { ApiError } from './api';

describe('ErrorHandlingService', () => {
  describe('analyzeError', () => {
    it('should analyze LocalStorageUnavailableError correctly', () => {
      const error = new LocalStorageUnavailableError();
      const result = ErrorHandlingService.analyzeError(error);
      
      expect(result.severity).toBe('high');
      expect(result.category).toBe('storage');
      expect(result.retryable).toBe(false);
      expect(result.actionable).toBe(true);
      expect(result.suggestedActions).toContain('Enable cookies and local storage in your browser settings');
    });

    it('should analyze LocalStorageQuotaError correctly', () => {
      const error = new LocalStorageQuotaError();
      const result = ErrorHandlingService.analyzeError(error);
      
      expect(result.severity).toBe('medium');
      expect(result.category).toBe('quota');
      expect(result.retryable).toBe(false);
      expect(result.actionable).toBe(true);
      expect(result.suggestedActions).toContain('Delete some old decks to free up space');
    });

    it('should analyze LocalStorageDataCorruptionError correctly', () => {
      const error = new LocalStorageDataCorruptionError();
      const result = ErrorHandlingService.analyzeError(error);
      
      expect(result.severity).toBe('medium');
      expect(result.category).toBe('corruption');
      expect(result.retryable).toBe(false);
      expect(result.actionable).toBe(false);
    });

    it('should analyze DeckStorageError correctly', () => {
      const error = new DeckStorageError('Test error', 'DECK_LIMIT_EXCEEDED', 'local');
      const result = ErrorHandlingService.analyzeError(error);
      
      expect(result.severity).toBe('medium');
      expect(result.category).toBe('quota');
      expect(result.retryable).toBe(false);
      expect(result.actionable).toBe(true);
    });

    it('should analyze ApiError timeout correctly', () => {
      const error = new ApiError('Timeout', 408, true, false);
      const result = ErrorHandlingService.analyzeError(error);
      
      expect(result.severity).toBe('medium');
      expect(result.category).toBe('network');
      expect(result.retryable).toBe(true);
      expect(result.actionable).toBe(true);
    });

    it('should analyze ApiError network error correctly', () => {
      const error = new ApiError('Network error', 0, false, true);
      const result = ErrorHandlingService.analyzeError(error);
      
      expect(result.severity).toBe('medium');
      expect(result.category).toBe('network');
      expect(result.retryable).toBe(true);
      expect(result.actionable).toBe(true);
    });

    it('should handle unknown errors gracefully', () => {
      const error = new Error('Unknown error');
      const result = ErrorHandlingService.analyzeError(error);
      
      expect(result.severity).toBe('medium');
      expect(result.category).toBe('validation');
      expect(result.retryable).toBe(true);
      expect(result.actionable).toBe(false);
    });
  });

  describe('withRetry', () => {
    it('should succeed on first attempt', async () => {
      const operation = jest.fn().mockResolvedValue('success');
      
      const result = await withRetry(operation);
      
      expect(result).toBe('success');
      expect(operation).toHaveBeenCalledTimes(1);
    });

    it('should retry on retryable errors', async () => {
      jest.useRealTimers(); // Use real timers for this test
      
      const operation = jest.fn()
        .mockRejectedValueOnce(new Error('Temporary error'))
        .mockResolvedValue('success');
      
      const result = await withRetry(operation, { maxAttempts: 2, baseDelay: 1 }); // Very short delay
      
      expect(result).toBe('success');
      expect(operation).toHaveBeenCalledTimes(2);
      
      jest.useFakeTimers(); // Restore fake timers
    });

    it('should not retry on non-retryable errors', async () => {
      const operation = jest.fn().mockRejectedValue(new LocalStorageUnavailableError());
      
      await expect(withRetry(operation)).rejects.toThrow(LocalStorageUnavailableError);
      expect(operation).toHaveBeenCalledTimes(1);
    });

    it('should respect max attempts', async () => {
      jest.useRealTimers(); // Use real timers for this test
      
      const operation = jest.fn().mockRejectedValue(new Error('Always fails'));
      
      await expect(withRetry(operation, { maxAttempts: 3, baseDelay: 1 })).rejects.toThrow('Always fails');
      expect(operation).toHaveBeenCalledTimes(3);
      
      jest.useFakeTimers(); // Restore fake timers
    });
  });

  describe('withGracefulDegradation', () => {
    it('should use primary operation when it succeeds', async () => {
      const primary = jest.fn().mockResolvedValue('primary success');
      const fallback = jest.fn().mockResolvedValue('fallback success');
      
      const result = await withGracefulDegradation(
        primary,
        fallback,
        { primaryDescription: 'primary', fallbackDescription: 'fallback' }
      );
      
      expect(result).toBe('primary success');
      expect(primary).toHaveBeenCalledTimes(1);
      expect(fallback).not.toHaveBeenCalled();
    });

    it('should use fallback when primary fails', async () => {
      const primary = jest.fn().mockRejectedValue(new Error('Primary failed'));
      const fallback = jest.fn().mockResolvedValue('fallback success');
      const onFallback = jest.fn();
      
      const result = await withGracefulDegradation(
        primary,
        fallback,
        { 
          primaryDescription: 'primary', 
          fallbackDescription: 'fallback',
          onFallback
        }
      );
      
      expect(result).toBe('fallback success');
      expect(primary).toHaveBeenCalledTimes(1);
      expect(fallback).toHaveBeenCalledTimes(1);
      expect(onFallback).toHaveBeenCalled();
    });

    it('should throw when both primary and fallback fail', async () => {
      const primary = jest.fn().mockRejectedValue(new Error('Primary failed'));
      const fallback = jest.fn().mockRejectedValue(new Error('Fallback failed'));
      
      await expect(withGracefulDegradation(
        primary,
        fallback,
        { primaryDescription: 'primary', fallbackDescription: 'fallback' }
      )).rejects.toThrow('Fallback failed');
      
      expect(primary).toHaveBeenCalledTimes(1);
      expect(fallback).toHaveBeenCalledTimes(1);
    });
  });

  describe('formatUserMessage', () => {
    it('should format user message without actions', () => {
      const error = new LocalStorageUnavailableError();
      const message = formatUserMessage(error, false);
      
      expect(message).toContain('Your browser\'s local storage is not available');
      expect(message).not.toContain('Suggested actions:');
    });

    it('should format user message with actions', () => {
      const error = new LocalStorageUnavailableError();
      const message = formatUserMessage(error, true);
      
      expect(message).toContain('Your browser\'s local storage is not available');
      expect(message).toContain('Suggested actions:');
      expect(message).toContain('• Enable cookies and local storage');
    });

    it('should not include actions for non-actionable errors', () => {
      const error = new LocalStorageDataCorruptionError();
      const message = formatUserMessage(error, true);
      
      expect(message).toContain('Your saved deck data was corrupted');
      expect(message).not.toContain('Suggested actions:');
    });
  });

  describe('utility functions', () => {
    it('should identify recoverable errors', () => {
      const retryableError = new Error('Temporary error');
      const nonRetryableError = new LocalStorageUnavailableError();
      
      expect(ErrorHandlingService.isRecoverable(retryableError)).toBe(true);
      expect(ErrorHandlingService.isRecoverable(nonRetryableError)).toBe(true); // actionable
    });

    it('should get error severity correctly', () => {
      const criticalError = new LocalStorageUnavailableError();
      const mediumError = new LocalStorageQuotaError();
      
      expect(ErrorHandlingService.getErrorSeverity(criticalError)).toBe('high');
      expect(ErrorHandlingService.getErrorSeverity(mediumError)).toBe('medium');
    });
  });
});

// Mock timers for retry tests
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});