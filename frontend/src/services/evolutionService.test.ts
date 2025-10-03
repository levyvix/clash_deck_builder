/**
 * Tests for evolution service functionality
 */

import { canCardEvolve, canCardIdEvolve, getEvolutionCapableCardIds, EVOLUTION_CAPABLE_CARDS } from './evolutionService';
import { Card } from '../types';

describe('Evolution Service', () => {
  const mockEvolutionCard: Card = {
    id: 26000000, // Knight - should be evolution capable
    name: 'Knight',
    elixir_cost: 3,
    rarity: 'Common',
    type: 'Troop',
    arena: 'Training Camp',
    image_url: 'https://example.com/knight.png',
    image_url_evo: 'https://example.com/knight_evo.png'
  };

  const mockNonEvolutionCard: Card = {
    id: 99999999, // Non-existent card ID - should not be evolution capable
    name: 'Test Card',
    elixir_cost: 2,
    rarity: 'Common',
    type: 'Spell',
    arena: 'Arena 1',
    image_url: 'https://example.com/test.png'
  };

  const mockCardWithApiFlag: Card = {
    id: 99999998,
    name: 'API Card',
    elixir_cost: 4,
    rarity: 'Rare',
    type: 'Troop',
    arena: 'Arena 2',
    image_url: 'https://example.com/api.png',
    can_evolve: true // API provides evolution capability
  };

  describe('canCardEvolve', () => {
    it('should return true for cards in the evolution capable set', () => {
      expect(canCardEvolve(mockEvolutionCard)).toBe(true);
    });

    it('should return false for cards not in the evolution capable set', () => {
      expect(canCardEvolve(mockNonEvolutionCard)).toBe(false);
    });

    it('should prioritize API can_evolve field over static list', () => {
      expect(canCardEvolve(mockCardWithApiFlag)).toBe(true);
    });

    it('should handle API can_evolve field set to false', () => {
      const cardWithFalseFlag: Card = {
        ...mockEvolutionCard,
        can_evolve: false
      };
      expect(canCardEvolve(cardWithFalseFlag)).toBe(false);
    });
  });

  describe('canCardIdEvolve', () => {
    it('should return true for evolution capable card IDs', () => {
      expect(canCardIdEvolve(26000000)).toBe(true); // Knight
    });

    it('should return false for non-evolution capable card IDs', () => {
      expect(canCardIdEvolve(99999999)).toBe(false);
    });
  });

  describe('getEvolutionCapableCardIds', () => {
    it('should return a set of evolution capable card IDs', () => {
      const cardIds = getEvolutionCapableCardIds();
      expect(cardIds).toBeInstanceOf(Set);
      expect(cardIds.has(26000000)).toBe(true); // Knight
      expect(cardIds.size).toBeGreaterThan(0);
    });

    it('should return a copy of the original set', () => {
      const cardIds = getEvolutionCapableCardIds();
      expect(cardIds).not.toBe(EVOLUTION_CAPABLE_CARDS);
      expect(cardIds).toEqual(EVOLUTION_CAPABLE_CARDS);
    });
  });

  describe('EVOLUTION_CAPABLE_CARDS constant', () => {
    it('should contain known evolution capable cards', () => {
      // Test a few known evolution capable cards
      expect(EVOLUTION_CAPABLE_CARDS.has(26000000)).toBe(true); // Knight
      expect(EVOLUTION_CAPABLE_CARDS.has(26000001)).toBe(true); // Archers
      expect(EVOLUTION_CAPABLE_CARDS.has(26000014)).toBe(true); // Musketeer
    });

    it('should not be empty', () => {
      expect(EVOLUTION_CAPABLE_CARDS.size).toBeGreaterThan(0);
    });
  });
});