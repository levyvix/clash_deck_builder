// frontend/src/services/api.ts

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const fetchCards = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/cards`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching cards:", error);
    throw error;
  }
};

export const fetchDecks = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/decks`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching decks:", error);
    throw error;
  }
};

export const createDeck = async (deckData: any) => {
  try {
    const response = await fetch(`${API_BASE_URL}/decks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
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
};

export const updateDeck = async (deckId: number, deckData: any) => {
  try {
    const response = await fetch(`${API_BASE_URL}/decks/${deckId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
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
};

export const deleteDeck = async (deckId: number) => {
  try {
    const response = await fetch(`${API_BASE_URL}/decks/${deckId}`, {
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
};
