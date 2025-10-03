// frontend/src/services/api.ts

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// API configuration
const API_CONFIG = {
  timeout: 10000, // 10 seconds timeout
  retries: 3,
  retryDelay: 1000, // 1 second
};

// Enhanced fetch with timeout and retry logic
const fetchWithTimeout = async (url: string, options: RequestInit = {}, timeout = API_CONFIG.timeout): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
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

export const fetchCards = async () => {
  return withRetry(async () => {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/cards`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching cards:", error);
      throw error;
    }
  });
};

export const fetchDecks = async () => {
  return withRetry(async () => {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/decks`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching decks:", error);
      throw error;
    }
  });
};

export const createDeck = async (deckData: any) => {
  return withRetry(async () => {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/decks`, {
        method: 'POST',
        body: JSON.stringify(deckData),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error creating deck:", error);
      throw error;
    }
  });
};

export const updateDeck = async (deckId: number, deckData: any) => {
  return withRetry(async () => {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/decks/${deckId}`, {
        method: 'PUT',
        body: JSON.stringify(deckData),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error updating deck:", error);
      throw error;
    }
  });
};

export const deleteDeck = async (deckId: number) => {
  return withRetry(async () => {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/decks/${deckId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return true;
    } catch (error) {
      console.error("Error deleting deck:", error);
      throw error;
    }
  });
};
