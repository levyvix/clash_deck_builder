/**
 * Utility functions for deck calculations and validation
 */

import { DeckSlot } from '../types';

/**
 * Calculate the average elixir cost of cards in the deck
 * @param slots - Array of 8 deck slots
 * @returns Average elixir cost rounded to 1 decimal place, or 0.0 if deck is empty
 */
export const calculateAverageElixir = (slots: DeckSlot[]): number => {
  const filledSlots = slots.filter(slot => slot.card !== null);
  
  if (filledSlots.length === 0) {
    return 0.0;
  }
  
  const totalElixir = filledSlots.reduce((sum, slot) => {
    return sum + (slot.card?.elixir_cost || 0);
  }, 0);
  
  const average = totalElixir / filledSlots.length;
  
  // Round to 1 decimal place
  return Math.round(average * 10) / 10;
};

/**
 * Check if another evolution slot can be added to the deck
 * @param slots - Array of 8 deck slots
 * @returns true if fewer than 2 evolution slots are used, false otherwise
 */
export const canAddEvolution = (slots: DeckSlot[]): boolean => {
  const evolutionCount = slots.filter(slot => slot.isEvolution).length;
  return evolutionCount < 2;
};

/**
 * Check if the deck is complete (all 8 slots filled)
 * @param slots - Array of 8 deck slots
 * @returns true if all 8 slots have cards, false otherwise
 */
export const isDeckComplete = (slots: DeckSlot[]): boolean => {
  return slots.length === 8 && slots.every(slot => slot.card !== null);
};

/**
 * Find the index of the first empty slot in the deck
 * @param slots - Array of 8 deck slots
 * @returns Index of first empty slot, or -1 if deck is full
 */
export const getEmptySlotIndex = (slots: DeckSlot[]): number => {
  return slots.findIndex(slot => slot.card === null);
};
