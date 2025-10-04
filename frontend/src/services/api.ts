// frontend/src/services/api.ts

import { API_BASE_URL } from '../config';
import { tokenStorage } from './authService';

// API Service Initialized

// API configuration
const API_CONFIG = {
  timeout: 10000, // 10 seconds timeout
  retries: 3,
  retryDelay: 1000, // 1 second
};

// Custom error class for API errors
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public isTimeout: boolean = false,
    public isNetworkError: boolean = false
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Enhanced fetch with timeout and retry logic
const fetchWithTimeout = async (
  url: string,
  options: RequestInit & { skipAuth?: boolean } = {},
  timeout = API_CONFIG.timeout
): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  // Add authentication header if token exists and not explicitly skipped
  const token = tokenStorage.getAccessToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  // Only add auth header if not skipped and token exists
  if (token && !options.skipAuth) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle timeout errors
    if ((error as any)?.name === 'AbortError') {
      throw new ApiError('Request timed out', undefined, true, false);
    }

    // Handle network errors
    if (error instanceof TypeError) {
      throw new ApiError('Cannot connect to server', undefined, false, true);
    }

    throw error;
  }
};

// Handle API response and extract error messages
const handleApiResponse = async (response: Response): Promise<any> => {
  if (!response.ok) {
    let errorMessage = 'An error occurred';

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }

    // Categorize errors by status code with specific handling
    if (response.status === 404) {
      // 404 - Endpoint not found
      throw new ApiError('Endpoint not found - check API configuration', response.status);
    } else if (response.status === 400) {
      // 400 - Validation error, use specific message from backend
      throw new ApiError(errorMessage, response.status);
    } else if (response.status >= 400 && response.status < 500) {
      // Other 4xx errors - client errors, use response message
      throw new ApiError(errorMessage, response.status);
    } else if (response.status >= 500) {
      // 5xx errors - server errors
      throw new ApiError('Server error, please try again', response.status);
    } else {
      throw new ApiError(errorMessage, response.status);
    }
  }

  return response.json();
};

// Retry wrapper for API calls
const withRetry = async <T>(
  operation: () => Promise<T>,
  retries = API_CONFIG.retries,
  delay = API_CONFIG.retryDelay
): Promise<T> => {
  try {
    return await operation();
  } catch (error) {
    if (retries > 0 && (error instanceof TypeError || (error as any)?.name === 'AbortError')) {
      console.warn(`API call failed, retrying in ${delay}ms... (${retries} retries left)`);
      await new Promise(resolve => setTimeout(resolve, delay));
      return withRetry(operation, retries - 1, delay * 1.5);
    }
    throw error;
  }
};

// Health check function to verify backend connectivity
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/health`, {}, 5000);
    return response.ok;
  } catch (error) {
    console.warn('Backend health check failed:', error);
    return false;
  }
};

// Verify all API endpoints for debugging
export const verifyEndpoints = async (): Promise<void> => {
  console.log('\n🔍 ===== API ENDPOINT VERIFICATION =====');
  console.log('Base URL:', API_BASE_URL);
  console.log('Timestamp:', new Date().toISOString());
  console.log('========================================\n');

  // Define endpoint interface
  interface EndpointTest {
    name: string;
    method: string;
    url: string;
    requiresAuth: boolean;
  }

  // Only test public endpoints that don't require authentication
  const publicEndpoints: EndpointTest[] = [
    { name: 'Health Check', method: 'GET', url: `${API_BASE_URL}/health`, requiresAuth: false },
    { name: 'Fetch Cards', method: 'GET', url: `${API_BASE_URL}/api/cards/cards`, requiresAuth: false },
  ];

  // Test protected endpoints only if user is authenticated
  const token = tokenStorage.getAccessToken();
  const protectedEndpoints: EndpointTest[] = [
    { name: 'Fetch Decks', method: 'GET', url: `${API_BASE_URL}/api/decks/decks`, requiresAuth: true },
    { name: 'Create Deck', method: 'POST', url: `${API_BASE_URL}/api/decks/decks`, requiresAuth: true },
  ];

  const endpoints = token ? [...publicEndpoints, ...protectedEndpoints] : publicEndpoints;

  if (!token) {
    console.log('🔒 Skipping protected endpoints (user not authenticated)');
    console.log('📝 Protected endpoints will be tested after login\n');
  }

  for (const endpoint of endpoints) {
    try {
      console.log(`\n📡 Testing: ${endpoint.name}`);
      console.log(`   Method: ${endpoint.method}`);
      console.log(`   URL: ${endpoint.url}`);
      console.log(`   Auth Required: ${endpoint.requiresAuth ? 'Yes' : 'No'}`);

      const startTime = performance.now();

      // Prepare headers
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add auth header if endpoint requires authentication and token exists
      if (endpoint.requiresAuth && token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetchWithTimeout(endpoint.url, {
        method: endpoint.method === 'POST' ? 'OPTIONS' : endpoint.method, // Use OPTIONS for POST to avoid creating data
        headers,
        skipAuth: !endpoint.requiresAuth, // Skip auth for public endpoints
      });
      const endTime = performance.now();
      const duration = (endTime - startTime).toFixed(2);

      console.log(`   ✅ Status: ${response.status} ${response.statusText}`);
      console.log(`   ⏱️  Duration: ${duration}ms`);
      console.log(`   📦 Content-Type: ${response.headers.get('content-type')}`);

      // Try to read response for GET requests
      if (endpoint.method === 'GET' && response.ok) {
        try {
          const data = await response.json();
          if (Array.isArray(data)) {
            console.log(`   📊 Response: Array with ${data.length} items`);
          } else if (typeof data === 'object') {
            console.log(`   📊 Response: Object with keys: ${Object.keys(data).join(', ')}`);
          } else {
            console.log(`   📊 Response: ${typeof data}`);
          }
        } catch (e) {
          console.log(`   ⚠️  Could not parse response as JSON`);
        }
      }
    } catch (error) {
      console.log(`   ❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      if (error instanceof TypeError) {
        console.log(`   🔌 Network Error: Cannot connect to ${endpoint.url}`);
        console.log(`   💡 Tip: Check if backend is running and CORS is configured`);
      }
    }
  }

  console.log('\n========================================');
  console.log('✅ Endpoint verification complete');
  console.log('========================================\n');
};

// Process card data to filter out invalid cards
const processCardData = (cards: any[]): any[] => {
  if (!Array.isArray(cards)) {
    console.warn('⚠️ processCardData: Expected array, got:', typeof cards);
    return [];
  }

  const originalCount = cards.length;

  // Filter out cards with 0 elixir cost
  const filteredCards = cards.filter(card => {
    // Ensure card has required properties and elixir_cost > 0
    return card &&
      typeof card.elixir_cost === 'number' &&
      card.elixir_cost > 0;
  });

  return filteredCards;
};

export const fetchCards = async () => {
  return withRetry(async () => {
    try {
      const url = `${API_BASE_URL}/api/cards/cards`;

      // For cards, we don't need authentication, so skip auth header
      const response = await fetchWithTimeout(url, {
        method: 'GET',
        skipAuth: true
      });

      const rawData = await handleApiResponse(response);

      // Process and filter the card data
      const processedCards = processCardData(rawData);

      return processedCards;
    } catch (error) {
      console.error("Error fetching cards:", error);
      throw error;
    }
  });
};

export const fetchDecks = async () => {
  return withRetry(async () => {
    try {
      const url = `${API_BASE_URL}/api/decks/decks`;

      const response = await fetchWithTimeout(url);
      const data = await handleApiResponse(response);

      // Transform backend format to frontend format
      // Backend: { cards: Card[], evolution_slots: Card[] }
      // Frontend: { slots: DeckSlot[] } where DeckSlot = { card: Card, isEvolution: boolean }
      const transformedDecks = data.map((deck: any) => {
        // Create evolution slot IDs set for quick lookup
        const evolutionCardIds = new Set(
          (deck.evolution_slots || []).map((card: any) => card.id)
        );

        // Transform cards into slots
        const slots = (deck.cards || []).map((card: any) => ({
          card: card,
          isEvolution: evolutionCardIds.has(card.id)
        }));

        return {
          ...deck,
          slots: slots
        };
      });

      return transformedDecks;
    } catch (error) {
      console.error('Error fetching decks:', error);
      throw error;
    }
  });
};

export interface DeckPayload {
  name: string;
  cards: any[]; // Full card objects
  evolution_slots?: any[]; // Full card objects
  average_elixir?: number;
}

export const createDeck = async (deckData: DeckPayload) => {
  return withRetry(async () => {
    try {
      const url = `${API_BASE_URL}/api/decks/decks`;

      const response = await fetchWithTimeout(url, {
        method: 'POST',
        body: JSON.stringify(deckData),
      });

      return await handleApiResponse(response);
    } catch (error) {
      console.error('Error creating deck:', error);
      throw error;
    }
  });
};

export const updateDeck = async (deckId: number, deckData: any) => {
  return withRetry(async () => {
    try {
      const url = `${API_BASE_URL}/api/decks/decks/${deckId}`;
      const response = await fetchWithTimeout(url, {
        method: 'PUT',
        body: JSON.stringify(deckData),
      });
      return await handleApiResponse(response);
    } catch (error) {
      console.error("Error updating deck:", error);
      throw error;
    }
  });
};

export const deleteDeck = async (deckId: number) => {
  return withRetry(async () => {
    try {
      const url = `${API_BASE_URL}/api/decks/decks/${deckId}`;
      const response = await fetchWithTimeout(url, {
        method: 'DELETE',
      });

      if (!response.ok) {
        await handleApiResponse(response);
      }

      return true;
    } catch (error) {
      console.error("Error deleting deck:", error);
      throw error;
    }
  });
};
