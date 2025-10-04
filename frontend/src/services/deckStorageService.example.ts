/**
 * Example usage of DeckStorageService
 * 
 * This file demonstrates how to use the unified deck storage service
 * in different scenarios and authentication states.
 */

import { createDeckStorageService, deckStorageService, initializeDeckStorageService } from './deckStorageService';
import { useAuth } from '../contexts/AuthContext';
import { Deck, DeckSlot, Card } from '../types';

// Example 1: Initialize the service with authentication context
export const initializeServiceWithAuth = () => {
  // In a real app, you would get this from your auth context
  const authProvider = () => {
    // This could be a call to your auth context or token check
    const token = localStorage.getItem('access_token');
    return Boolean(token);
  };
  
  initializeDeckStorageService(authProvider);
  console.log('✅ DeckStorageService initialized with auth provider');
};

// Example 2: Using the service in a React component
export const useUnifiedDeckStorage = () => {
  const { isAuthenticated } = useAuth();
  
  // Create service instance with current auth state
  const service = createDeckStorageService(() => isAuthenticated);
  
  return service;
};

// Example 3: Basic deck operations
export const deckOperationsExample = async () => {
  // Assume service is already initialized
  const service = deckStorageService;
  
  try {
    // Get all decks (both local and server)
    console.log('📚 Fetching all decks...');
    const result = await service.getAllDecks();
    
    console.log(`Found ${result.totalCount} total decks:`);
    console.log(`- Local decks: ${result.localDecks.length}`);
    console.log(`- Server decks: ${result.serverDecks.length}`);
    console.log(`- Storage type: ${result.storageType}`);
    
    // Create a sample deck
    const sampleDeck: Omit<Deck, 'id'> = {
      name: 'Example Deck',
      slots: Array(8).fill({
        card: {
          id: 1,
          name: 'Knight',
          elixir_cost: 3,
          rarity: 'Common' as const,
          type: 'Troop' as const,
          image_url: 'knight.png',
        },
        isEvolution: false,
      }),
      average_elixir: 3.0,
    };
    
    // Save deck (will go to appropriate storage based on auth state)
    console.log('💾 Saving deck...');
    const savedDeck = await service.saveDeck(sampleDeck);
    console.log(`✅ Deck saved with ID: ${savedDeck.id} (${savedDeck.storageType})`);
    
    // Update the deck
    console.log('✏️ Updating deck...');
    const updatedDeck = await service.updateDeck(savedDeck.id, {
      name: 'Updated Example Deck'
    });
    console.log(`✅ Deck updated: ${updatedDeck.name}`);
    
    // Get specific deck
    console.log('🔍 Fetching specific deck...');
    const fetchedDeck = await service.getDeck(savedDeck.id);
    console.log(`✅ Fetched deck: ${fetchedDeck?.name}`);
    
    // Delete the deck
    console.log('🗑️ Deleting deck...');
    await service.deleteDeck(savedDeck.id);
    console.log('✅ Deck deleted');
    
  } catch (error) {
    console.error('❌ Deck operation failed:', error);
  }
};

// Example 4: Handling different storage scenarios
export const storageScenarioExamples = async () => {
  const service = deckStorageService;
  
  try {
    // Check current storage type
    const storageType = await service.getStorageType();
    console.log(`📊 Current storage type: ${storageType}`);
    
    switch (storageType) {
      case 'local':
        console.log('👤 Anonymous user - using local storage only');
        break;
      case 'server':
        console.log('🔐 Authenticated user - using server storage only');
        break;
      case 'mixed':
        console.log('🔄 Mixed storage - user has both local and server decks');
        break;
    }
    
    // Get storage statistics
    const stats = await service.getStorageStats();
    console.log('📈 Storage Statistics:');
    console.log(`- Total decks: ${stats.total}`);
    console.log(`- Local: ${stats.local.deckCount}/${stats.local.maxDecks} (${stats.local.available ? 'available' : 'unavailable'})`);
    console.log(`- Server: ${stats.server.deckCount} (${stats.server.available ? 'available' : 'unavailable'})`);
    
  } catch (error) {
    console.error('❌ Storage scenario check failed:', error);
  }
};

// Example 5: Force local storage (even for authenticated users)
export const forceLocalStorageExample = async () => {
  const service = deckStorageService;
  
  const sampleDeck: Omit<Deck, 'id'> = {
    name: 'Local Only Deck',
    slots: Array(8).fill({
      card: null,
      isEvolution: false,
    }),
    average_elixir: 0,
  };
  
  try {
    // Force save to local storage even if user is authenticated
    console.log('💾 Forcing save to local storage...');
    const savedDeck = await service.saveDeck(sampleDeck, true);
    console.log(`✅ Deck saved locally: ${savedDeck.id}`);
    
    // Verify it's a local deck
    const isLocal = service.isLocalDeck(savedDeck.id);
    console.log(`🔍 Is local deck: ${isLocal}`);
    
  } catch (error) {
    console.error('❌ Force local storage failed:', error);
  }
};

// Example 6: Error handling patterns
export const errorHandlingExample = async () => {
  const service = deckStorageService;
  
  try {
    // Try to get a non-existent deck
    const nonExistentDeck = await service.getDeck('local_nonexistent_123');
    console.log('🔍 Non-existent deck result:', nonExistentDeck); // Should be null
    
    // Try to update a non-existent deck
    await service.updateDeck('local_nonexistent_123', { name: 'Updated' });
    
  } catch (error) {
    console.log('✅ Expected error caught:', error instanceof Error ? error.message : String(error));
  }
  
  try {
    // Try to delete a non-existent deck
    await service.deleteDeck('local_nonexistent_123');
    
  } catch (error) {
    console.log('✅ Expected error caught:', error instanceof Error ? error.message : String(error));
  }
};

// Example 7: Migration scenario (user signs in after using local storage)
export const migrationScenarioExample = async () => {
  console.log('🔄 Migration Scenario Example:');
  console.log('1. User starts anonymous, saves decks locally');
  console.log('2. User signs in');
  console.log('3. System shows both local and server decks');
  
  // This would be handled automatically by the service
  // The getAllDecks() method will return both local and server decks
  // with proper storageType indicators for the UI to distinguish them
  
  const service = deckStorageService;
  const result = await service.getAllDecks();
  
  if (result.storageType === 'mixed') {
    console.log('✅ Migration scenario detected:');
    console.log(`- ${result.localDecks.length} local decks from anonymous usage`);
    console.log(`- ${result.serverDecks.length} server decks from authenticated usage`);
    console.log('- UI can display both with appropriate indicators');
  }
};

// Export all examples for easy testing
export const runAllExamples = async () => {
  console.log('🚀 Running DeckStorageService Examples...\n');
  
  try {
    initializeServiceWithAuth();
    await deckOperationsExample();
    await storageScenarioExamples();
    await forceLocalStorageExample();
    await errorHandlingExample();
    await migrationScenarioExample();
    
    console.log('\n✅ All examples completed successfully!');
  } catch (error) {
    console.error('\n❌ Example execution failed:', error);
  }
};