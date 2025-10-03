// Test file for API error handling
import { ApiError, createDeck } from './api';

describe('API Error Handling', () => {
  // Mock fetch globally
  const originalFetch = global.fetch;
  
  beforeEach(() => {
    // Reset fetch mock before each test
    global.fetch = jest.fn();
  });
  
  afterAll(() => {
    // Restore original fetch
    global.fetch = originalFetch;
  });

  describe('createDeck error scenarios', () => {
    const mockDeckData = {
      name: 'Test Deck',
      cards: [],
      evolution_slots: [],
      average_elixir: 3.5,
    };

    test('should handle 404 error with specific message', async () => {
      // Mock 404 response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ detail: 'Endpoint not found' }),
      });

      try {
        await createDeck(mockDeckData);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).statusCode).toBe(404);
        expect((error as ApiError).message).toBe('Endpoint not found - check API configuration');
      }
    });

    test('should handle 400 validation error with specific message', async () => {
      // Mock 400 response with validation error
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ detail: 'Deck must have exactly 8 cards' }),
      });

      try {
        await createDeck(mockDeckData);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).statusCode).toBe(400);
        expect((error as ApiError).message).toBe('Deck must have exactly 8 cards');
      }
    });

    test('should handle network error with "Cannot connect to server" message', async () => {
      // Mock network error (TypeError)
      (global.fetch as jest.Mock).mockRejectedValueOnce(new TypeError('Failed to fetch'));

      try {
        await createDeck(mockDeckData);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).isNetworkError).toBe(true);
        expect((error as ApiError).message).toBe('Cannot connect to server');
      }
    });

    test('should handle timeout error', async () => {
      // Mock timeout by simulating AbortError
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        Object.assign(new Error('The operation was aborted'), { name: 'AbortError' })
      );

      try {
        await createDeck(mockDeckData);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).isTimeout).toBe(true);
        expect((error as ApiError).message).toBe('Request timed out');
      }
    });

    test('should handle 500 server error', async () => {
      // Mock 500 response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ detail: 'Database connection failed' }),
      });

      try {
        await createDeck(mockDeckData);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).statusCode).toBe(500);
        expect((error as ApiError).message).toBe('Server error, please try again');
      }
    });

    test('should handle successful 201 response', async () => {
      // Mock successful response
      const mockResponse = { id: 1, name: 'Test Deck', cards: [] };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponse,
      });

      const result = await createDeck(mockDeckData);
      expect(result).toEqual(mockResponse);
    });
  });
});
