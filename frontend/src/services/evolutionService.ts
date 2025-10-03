/**
 * Evolution service for managing card evolution capabilities
 */

import { Card } from '../types';

/**
 * Set of card IDs that are capable of evolution.
 * Based on Clash Royale game data - these are the cards that have evolution variants.
 * 
 * Note: This is a static list based on known evolution-capable cards.
 * In a production environment, this data would ideally come from the API.
 */
export const EVOLUTION_CAPABLE_CARDS = new Set<number>([
  // Common Cards
  26000000, // Knight
  26000001, // Archers
  26000002, // Goblins
  26000003, // Giant
  26000004, // P.E.K.K.A
  26000005, // Minions
  26000006, // Balloon
  26000007, // Witch
  26000008, // Barbarians
  26000009, // Golem
  26000010, // Skeletons
  26000011, // Valkyrie
  26000012, // Skeleton Army
  26000013, // Bomber
  26000014, // Musketeer
  26000015, // Baby Dragon
  26000016, // Prince
  26000017, // Wizard
  26000018, // Mini P.E.K.K.A
  26000019, // Spear Goblins
  26000020, // Giant Skeleton
  26000021, // Hog Rider
  26000022, // Minion Horde
  26000023, // Ice Wizard
  26000024, // Royal Giant
  26000025, // Guards
  26000026, // Princess
  26000027, // Dark Prince
  26000028, // Three Musketeers
  26000029, // Lava Hound
  26000030, // Ice Spirit
  26000031, // Fire Spirit
  26000032, // Miner
  26000033, // Sparky
  26000034, // Bowler
  26000035, // Lumberjack
  26000036, // Battle Ram
  26000037, // Inferno Dragon
  26000038, // Ice Golem
  26000039, // Mega Minion
  26000040, // Dart Goblin
  26000041, // Goblin Hut
  26000042, // Electro Wizard
  26000043, // Elite Barbarians
  26000044, // Hunter
  26000045, // Executioner
  26000046, // Bandit
  26000047, // Royal Recruits
  26000048, // Night Witch
  26000049, // Bats
  26000050, // Royal Ghost
  26000051, // Ram Rider
  26000052, // Zappies
  26000053, // Rascals
  26000054, // Cannon Cart
  26000055, // Mega Knight
  26000056, // Skeleton Barrel
  26000057, // Flying Machine
  26000058, // Wall Breakers
  26000059, // Royal Hogs
  26000060, // Goblin Giant
  26000061, // Fisherman
  26000062, // Magic Archer
  26000063, // Electro Dragon
  26000064, // Firecracker
  26000065, // Mighty Miner
  26000066, // Elixir Golem
  26000067, // Battle Healer
  26000068, // Skeleton King
  26000069, // Archer Queen
  26000070, // Golden Knight
  26000071, // Monk
  26000072, // Skeleton Dragons
  26000073, // Mother Witch
  26000074, // Electro Spirit
  26000075, // Electro Giant
  26000076, // Champion
  26000077, // Little Prince
  26000078, // Phoenix
  26000079, // Dagger Duchess
]);

/**
 * Check if a card is capable of evolution.
 * 
 * @param card - The card to check for evolution capability
 * @returns true if the card can evolve, false otherwise
 */
export const canCardEvolve = (card: Card): boolean => {
  // First check if the card has the can_evolve field from API
  if (card.can_evolve !== undefined) {
    return card.can_evolve;
  }
  
  // Fallback to static list if API doesn't provide evolution capability data
  return EVOLUTION_CAPABLE_CARDS.has(card.id);
};

/**
 * Check if a card ID is capable of evolution.
 * 
 * @param cardId - The card ID to check
 * @returns true if the card can evolve, false otherwise
 */
export const canCardIdEvolve = (cardId: number): boolean => {
  return EVOLUTION_CAPABLE_CARDS.has(cardId);
};

/**
 * Get all evolution-capable card IDs.
 * 
 * @returns Set of card IDs that can evolve
 */
export const getEvolutionCapableCardIds = (): Set<number> => {
  return new Set(EVOLUTION_CAPABLE_CARDS);
};