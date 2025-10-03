"""
Integration tests for deck CRUD operations
"""
import pytest
import json
from src.services.deck_service import DeckService
from src.models.deck import Deck
from src.models.user import User
from src.models.card import Card
from src.exceptions import DeckNotFoundError, DeckLimitExceededError
from src.utils.database import get_db_session


class TestDeckOperations:
    """Test deck CRUD operations with real database"""
    
    @pytest.fixture
    def sample_cards(self):
        """Sample cards for testing"""
        return [
            Card(id=26000000, name="Knight", elixir_cost=3, rarity="Common", type="Troop"),
            Card(id=26000001, name="Archers", elixir_cost=3, rarity="Common", type="Troop"),
            Card(id=26000002, name="Goblins", elixir_cost=2, rarity="Common", type="Troop"),
            Card(id=26000003, name="Giant", elixir_cost=5, rarity="Rare", type="Troop"),
            Card(id=26000004, name="P.E.K.K.A", elixir_cost=7, rarity="Epic", type="Troop"),
            Card(id=26000005, name="Minions", elixir_cost=3, rarity="Common", type="Troop"),
            Card(id=28000000, name="Fireball", elixir_cost=4, rarity="Rare", type="Spell"),
            Card(id=28000001, name="Arrows", elixir_cost=3, rarity="Common", type="Spell")
        ]
    
    @pytest.fixture
    def test_user(self):
        """Test user for deck operations"""
        return User(id=1, username="test_user_1", email="test1@example.com")
    
    @pytest.fixture
    def deck_service(self, clean_database):
        """Deck service with database session"""
        with get_db_session() as session:
            yield DeckService(session)
    
    @pytest.mark.asyncio
    async def test_create_deck(self, deck_service, test_user, sample_cards):
        """Test creating a new deck"""
        deck = Deck(
            name="Test Integration Deck",
            cards=sample_cards,
            evolution_slots=[sample_cards[0]],  # Knight as evolution
            user_id=test_user.id
        )
        
        created_deck = await deck_service.create_deck(deck, test_user)
        
        assert created_deck.id is not None
        assert created_deck.name == "Test Integration Deck"
        assert created_deck.user_id == test_user.id
        assert len(created_deck.cards) == 8
        assert len(created_deck.evolution_slots) == 1
        assert created_deck.average_elixir is not None
        assert created_deck.average_elixir > 0
    
    @pytest.mark.asyncio
    async def test_get_deck(self, deck_service, test_user, sample_cards):
        """Test retrieving a deck by ID"""
        # Create a deck first
        deck = Deck(
            name="Test Get Deck",
            cards=sample_cards,
            evolution_slots=[],
            user_id=test_user.id
        )
        created_deck = await deck_service.create_deck(deck, test_user)
        
        # Retrieve the deck
        retrieved_deck = await deck_service.get_deck(created_deck.id, test_user)
        
        assert retrieved_deck is not None
        assert retrieved_deck.id == created_deck.id
        assert retrieved_deck.name == "Test Get Deck"
        assert retrieved_deck.user_id == test_user.id
        assert len(retrieved_deck.cards) == 8
        assert len(retrieved_deck.evolution_slots) == 0
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_deck(self, deck_service, test_user):
        """Test retrieving a non-existent deck"""
        retrieved_deck = await deck_service.get_deck(99999, test_user)
        assert retrieved_deck is None
    
    @pytest.mark.asyncio
    async def test_get_user_decks(self, deck_service, test_user, sample_cards):
        """Test retrieving all decks for a user"""
        # Create multiple decks
        deck1 = Deck(name="Deck 1", cards=sample_cards, user_id=test_user.id)
        deck2 = Deck(name="Deck 2", cards=sample_cards, user_id=test_user.id)
        
        await deck_service.create_deck(deck1, test_user)
        await deck_service.create_deck(deck2, test_user)
        
        # Get all user decks (including existing test data)
        user_decks = await deck_service.get_user_decks(test_user)
        
        # Should have at least the 2 we created plus existing test data
        assert len(user_decks) >= 2
        
        # Check that our created decks are in the list
        deck_names = [deck.name for deck in user_decks]
        assert "Deck 1" in deck_names
        assert "Deck 2" in deck_names
    
    @pytest.mark.asyncio
    async def test_update_deck(self, deck_service, test_user, sample_cards):
        """Test updating an existing deck"""
        # Create a deck first
        deck = Deck(
            name="Original Deck",
            cards=sample_cards,
            evolution_slots=[],
            user_id=test_user.id
        )
        created_deck = await deck_service.create_deck(deck, test_user)
        
        # Update the deck
        created_deck.name = "Updated Deck"
        created_deck.evolution_slots = [sample_cards[0], sample_cards[1]]
        
        updated_deck = await deck_service.update_deck(created_deck, test_user)
        
        assert updated_deck.name == "Updated Deck"
        assert len(updated_deck.evolution_slots) == 2
        
        # Verify the update persisted
        retrieved_deck = await deck_service.get_deck(created_deck.id, test_user)
        assert retrieved_deck.name == "Updated Deck"
        assert len(retrieved_deck.evolution_slots) == 2
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_deck(self, deck_service, test_user, sample_cards):
        """Test updating a non-existent deck"""
        deck = Deck(
            id=99999,
            name="Nonexistent Deck",
            cards=sample_cards,
            user_id=test_user.id
        )
        
        with pytest.raises(DeckNotFoundError):
            await deck_service.update_deck(deck, test_user)
    
    @pytest.mark.asyncio
    async def test_delete_deck(self, deck_service, test_user, sample_cards):
        """Test deleting a deck"""
        # Create a deck first
        deck = Deck(
            name="Deck to Delete",
            cards=sample_cards,
            user_id=test_user.id
        )
        created_deck = await deck_service.create_deck(deck, test_user)
        
        # Delete the deck
        deleted = await deck_service.delete_deck(created_deck.id, test_user)
        assert deleted is True
        
        # Verify the deck is gone
        retrieved_deck = await deck_service.get_deck(created_deck.id, test_user)
        assert retrieved_deck is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_deck(self, deck_service, test_user):
        """Test deleting a non-existent deck"""
        with pytest.raises(DeckNotFoundError):
            await deck_service.delete_deck(99999, test_user)
    
    @pytest.mark.asyncio
    async def test_get_deck_count(self, deck_service, test_user, sample_cards):
        """Test getting deck count for a user"""
        initial_count = await deck_service.get_deck_count(test_user)
        
        # Create a new deck
        deck = Deck(
            name="Count Test Deck",
            cards=sample_cards,
            user_id=test_user.id
        )
        await deck_service.create_deck(deck, test_user)
        
        # Check count increased
        new_count = await deck_service.get_deck_count(test_user)
        assert new_count == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_deck_limit_enforcement(self, deck_service, sample_cards):
        """Test that deck limit is enforced"""
        # Create a test user with no existing decks
        test_user = User(id=999, username="limit_test", email="limit@test.com")
        
        # Create maximum number of decks
        for i in range(deck_service.max_decks_per_user):
            deck = Deck(
                name=f"Deck {i+1}",
                cards=sample_cards,
                user_id=test_user.id
            )
            await deck_service.create_deck(deck, test_user)
        
        # Try to create one more deck - should fail
        extra_deck = Deck(
            name="Extra Deck",
            cards=sample_cards,
            user_id=test_user.id
        )
        
        with pytest.raises(DeckLimitExceededError):
            await deck_service.create_deck(extra_deck, test_user)
    
    @pytest.mark.asyncio
    async def test_deck_serialization_deserialization(self, deck_service, test_user, sample_cards):
        """Test that card data is properly serialized and deserialized"""
        # Create deck with evolution slots
        deck = Deck(
            name="Serialization Test",
            cards=sample_cards,
            evolution_slots=[sample_cards[0], sample_cards[3]],  # Knight and Giant
            user_id=test_user.id
        )
        
        created_deck = await deck_service.create_deck(deck, test_user)
        retrieved_deck = await deck_service.get_deck(created_deck.id, test_user)
        
        # Verify all card data is preserved
        assert len(retrieved_deck.cards) == len(sample_cards)
        assert len(retrieved_deck.evolution_slots) == 2
        
        # Check specific card properties
        knight = next(card for card in retrieved_deck.cards if card.name == "Knight")
        assert knight.elixir_cost == 3
        assert knight.rarity == "Common"
        assert knight.type == "Troop"
        
        # Check evolution slots
        evo_names = [card.name for card in retrieved_deck.evolution_slots]
        assert "Knight" in evo_names
        assert "Giant" in evo_names
    
    @pytest.mark.asyncio
    async def test_average_elixir_calculation(self, deck_service, test_user, sample_cards):
        """Test that average elixir is calculated correctly"""
        deck = Deck(
            name="Elixir Test",
            cards=sample_cards,
            user_id=test_user.id
        )
        
        created_deck = await deck_service.create_deck(deck, test_user)
        
        # Calculate expected average
        total_elixir = sum(card.elixir_cost for card in sample_cards)
        expected_average = total_elixir / len(sample_cards)
        
        assert created_deck.average_elixir == expected_average
        
        # Verify it persists
        retrieved_deck = await deck_service.get_deck(created_deck.id, test_user)
        assert retrieved_deck.average_elixir == expected_average
    
    @pytest.mark.asyncio
    async def test_deck_user_isolation(self, deck_service, sample_cards):
        """Test that users can only access their own decks"""
        user1 = User(id=1, username="user1", email="user1@test.com")
        user2 = User(id=2, username="user2", email="user2@test.com")
        
        # Create deck for user1
        deck = Deck(
            name="User1 Deck",
            cards=sample_cards,
            user_id=user1.id
        )
        created_deck = await deck_service.create_deck(deck, user1)
        
        # User2 should not be able to access user1's deck
        retrieved_deck = await deck_service.get_deck(created_deck.id, user2)
        assert retrieved_deck is None
        
        # User2 should not be able to update user1's deck
        deck_copy = Deck(
            id=created_deck.id,
            name="Hacked Deck",
            cards=sample_cards,
            user_id=user2.id
        )
        
        with pytest.raises(DeckNotFoundError):
            await deck_service.update_deck(deck_copy, user2)
        
        # User2 should not be able to delete user1's deck
        with pytest.raises(DeckNotFoundError):
            await deck_service.delete_deck(created_deck.id, user2)