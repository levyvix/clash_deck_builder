# backend/tests/test_deck_service.py

import pytest
import json
from unittest.mock import MagicMock, patch
from mysql.connector import Error as MySQLError

from src.services.deck_service import DeckService
from src.models.deck import Deck
from src.models.user import User
from src.models.card import Card
from src.exceptions import (
    DatabaseError,
    DeckNotFoundError,
    SerializationError,
    DeckLimitExceededError
)


@pytest.fixture
def sample_cards():
    """Create sample cards for testing"""
    return [
        Card(id=1, name="Knight", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/knight.png"),
        Card(id=2, name="Archers", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/archers.png"),
        Card(id=3, name="Fireball", elixir_cost=4, rarity="Rare", type="Spell", image_url="http://example.com/fireball.png"),
        Card(id=4, name="Giant", elixir_cost=5, rarity="Rare", type="Troop", image_url="http://example.com/giant.png"),
        Card(id=5, name="Wizard", elixir_cost=5, rarity="Rare", type="Troop", image_url="http://example.com/wizard.png"),
        Card(id=6, name="Minions", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/minions.png"),
        Card(id=7, name="Zap", elixir_cost=2, rarity="Common", type="Spell", image_url="http://example.com/zap.png"),
        Card(id=8, name="Musketeer", elixir_cost=4, rarity="Rare", type="Troop", image_url="http://example.com/musketeer.png")
    ]


@pytest.fixture
def sample_deck(sample_cards):
    """Create a sample deck for testing"""
    return Deck(
        id=1,
        name="Test Deck",
        user_id=1,
        cards=sample_cards,
        evolution_slots=[sample_cards[0]],  # Knight evolution
        average_elixir=3.5
    )


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(id=1)


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    return MagicMock()


@pytest.fixture
def deck_service(mock_db_session):
    """Create a DeckService instance with mocked database session"""
    return DeckService(db_session=mock_db_session)


class TestDeckService:
    """Test suite for DeckService"""

    def test_init(self, mock_db_session):
        """Test service initialization"""
        service = DeckService(db_session=mock_db_session)
        assert service.db_session == mock_db_session
        assert service.max_decks_per_user == 20

    def test_serialize_cards(self, deck_service, sample_cards):
        """Test card serialization to JSON"""
        result = deck_service._serialize_cards(sample_cards[:2])
        
        # Parse the JSON to verify structure
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "Knight"
        assert parsed[0]["elixir_cost"] == 3
        assert parsed[1]["name"] == "Archers"

    def test_serialize_cards_empty_list(self, deck_service):
        """Test serialization of empty card list"""
        result = deck_service._serialize_cards([])
        assert result == "[]"

    def test_serialize_cards_error(self, deck_service):
        """Test serialization error handling"""
        # Create an object that can't be serialized
        invalid_card = MagicMock()
        invalid_card.model_dump.side_effect = TypeError("Cannot serialize")
        
        with pytest.raises(SerializationError) as exc_info:
            deck_service._serialize_cards([invalid_card])
        
        assert "Failed to serialize cards" in str(exc_info.value)
        assert exc_info.value.data_type == "cards"

    def test_deserialize_cards(self, deck_service, sample_cards):
        """Test card deserialization from JSON"""
        # First serialize some cards
        cards_json = deck_service._serialize_cards(sample_cards[:2])
        
        # Then deserialize them
        result = deck_service._deserialize_cards(cards_json)
        
        assert len(result) == 2
        assert result[0].name == "Knight"
        assert result[0].elixir_cost == 3
        assert result[1].name == "Archers"

    def test_deserialize_cards_empty_string(self, deck_service):
        """Test deserialization of empty string"""
        result = deck_service._deserialize_cards("")
        assert result == []

    def test_deserialize_cards_invalid_json(self, deck_service):
        """Test deserialization error handling with invalid JSON"""
        with pytest.raises(SerializationError) as exc_info:
            deck_service._deserialize_cards("invalid json")
        
        assert "Failed to deserialize cards" in str(exc_info.value)
        assert exc_info.value.data_type == "cards"

    def test_deserialize_cards_invalid_card_data(self, deck_service):
        """Test deserialization error handling with invalid card data"""
        invalid_json = json.dumps([{"invalid": "data"}])
        
        with pytest.raises(SerializationError) as exc_info:
            deck_service._deserialize_cards(invalid_json)
        
        assert "Failed to deserialize cards" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_check_deck_limit_under_limit(self, deck_service, sample_user):
        """Test deck limit check when user is under limit"""
        deck_service.db_session.fetchone.return_value = {'deck_count': 5}
        
        # Should not raise an exception
        await deck_service._check_deck_limit(sample_user.id)
        
        deck_service.db_session.execute.assert_called_once_with(
            "SELECT COUNT(*) as deck_count FROM decks WHERE user_id = %s",
            (sample_user.id,)
        )

    @pytest.mark.asyncio
    async def test_check_deck_limit_at_limit(self, deck_service, sample_user):
        """Test deck limit check when user is at limit"""
        deck_service.db_session.fetchone.return_value = {'deck_count': 20}
        
        with pytest.raises(DeckLimitExceededError) as exc_info:
            await deck_service._check_deck_limit(sample_user.id)
        
        assert exc_info.value.user_id == sample_user.id
        assert exc_info.value.max_decks == 20

    @pytest.mark.asyncio
    async def test_check_deck_limit_database_error(self, deck_service, sample_user):
        """Test deck limit check with database error"""
        deck_service.db_session.execute.side_effect = MySQLError("Database error")
        
        with pytest.raises(DatabaseError) as exc_info:
            await deck_service._check_deck_limit(sample_user.id)
        
        assert "Failed to check deck limit" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_deck_success(self, deck_service, sample_deck, sample_user):
        """Test successful deck creation"""
        # Mock deck limit check
        deck_service.db_session.fetchone.return_value = {'deck_count': 5}
        deck_service.db_session.lastrowid = 123
        
        result = await deck_service.create_deck(sample_deck, sample_user)
        
        # Verify database calls
        assert deck_service.db_session.execute.call_count == 2  # limit check + insert
        
        # Verify result
        assert result.id == 123
        assert result.user_id == sample_user.id
        assert result.name == sample_deck.name

    @pytest.mark.asyncio
    async def test_create_deck_limit_exceeded(self, deck_service, sample_deck, sample_user):
        """Test deck creation when limit is exceeded"""
        deck_service.db_session.fetchone.return_value = {'deck_count': 20}
        
        with pytest.raises(DeckLimitExceededError):
            await deck_service.create_deck(sample_deck, sample_user)

    @pytest.mark.asyncio
    async def test_create_deck_database_error(self, deck_service, sample_deck, sample_user):
        """Test deck creation with database error"""
        deck_service.db_session.fetchone.return_value = {'deck_count': 5}
        deck_service.db_session.execute.side_effect = [None, MySQLError("Insert failed")]
        
        with pytest.raises(DatabaseError) as exc_info:
            await deck_service.create_deck(sample_deck, sample_user)
        
        assert "Failed to create deck" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_deck_serialization_error(self, deck_service, sample_user, sample_cards):
        """Test deck creation with serialization error"""
        deck_service.db_session.fetchone.return_value = {'deck_count': 5}
        
        # Create a valid deck first
        valid_deck = Deck(
            name="Valid Deck",
            cards=sample_cards,
            evolution_slots=[],
            average_elixir=3.0
        )
        
        # Mock the _serialize_cards method to raise an error
        with patch.object(deck_service, '_serialize_cards', side_effect=SerializationError("Cannot serialize", "cards")):
            with pytest.raises(SerializationError):
                await deck_service.create_deck(valid_deck, sample_user)

    @pytest.mark.asyncio
    async def test_get_deck_success(self, deck_service, sample_user, sample_cards):
        """Test successful deck retrieval"""
        # Mock database response
        deck_row = {
            "id": 1,
            "name": "Test Deck",
            "user_id": 1,
            "cards": json.dumps([card.model_dump() for card in sample_cards]),
            "evolution_slots": json.dumps([sample_cards[0].model_dump()]),
            "average_elixir": 3.5
        }
        deck_service.db_session.fetchone.return_value = deck_row
        
        result = await deck_service.get_deck(1, sample_user)
        
        assert result is not None
        assert result.id == 1
        assert result.name == "Test Deck"
        assert len(result.cards) == 8
        assert len(result.evolution_slots) == 1
        assert result.average_elixir == 3.5

    @pytest.mark.asyncio
    async def test_get_deck_not_found(self, deck_service, sample_user):
        """Test deck retrieval when deck doesn't exist"""
        deck_service.db_session.fetchone.return_value = None
        
        result = await deck_service.get_deck(999, sample_user)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_deck_database_error(self, deck_service, sample_user):
        """Test deck retrieval with database error"""
        deck_service.db_session.execute.side_effect = MySQLError("Query failed")
        
        with pytest.raises(DatabaseError) as exc_info:
            await deck_service.get_deck(1, sample_user)
        
        assert "Failed to retrieve deck" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_deck_deserialization_error(self, deck_service, sample_user):
        """Test deck retrieval with deserialization error"""
        deck_row = {
            "id": 1,
            "name": "Test Deck",
            "user_id": 1,
            "cards": "invalid json",
            "evolution_slots": "[]",
            "average_elixir": 3.5
        }
        deck_service.db_session.fetchone.return_value = deck_row
        
        with pytest.raises(SerializationError):
            await deck_service.get_deck(1, sample_user)

    @pytest.mark.asyncio
    async def test_get_user_decks_success(self, deck_service, sample_user, sample_cards):
        """Test successful retrieval of all user decks"""
        # Mock database response with multiple decks
        deck_rows = [
            {
                "id": 1,
                "name": "Deck 1",
                "user_id": 1,
                "cards": json.dumps([card.model_dump() for card in sample_cards]),
                "evolution_slots": "[]",
                "average_elixir": 3.5
            },
            {
                "id": 2,
                "name": "Deck 2",
                "user_id": 1,
                "cards": json.dumps([card.model_dump() for card in sample_cards]),
                "evolution_slots": json.dumps([sample_cards[0].model_dump()]),
                "average_elixir": 4.0
            }
        ]
        deck_service.db_session.fetchall.return_value = deck_rows
        
        result = await deck_service.get_user_decks(sample_user)
        
        assert len(result) == 2
        assert result[0].name == "Deck 1"
        assert result[1].name == "Deck 2"
        assert len(result[1].evolution_slots) == 1

    @pytest.mark.asyncio
    async def test_get_user_decks_empty(self, deck_service, sample_user):
        """Test retrieval of user decks when user has no decks"""
        deck_service.db_session.fetchall.return_value = []
        
        result = await deck_service.get_user_decks(sample_user)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_decks_with_invalid_deck(self, deck_service, sample_user, sample_cards):
        """Test user deck retrieval with one invalid deck (should skip it)"""
        deck_rows = [
            {
                "id": 1,
                "name": "Valid Deck",
                "user_id": 1,
                "cards": json.dumps([card.model_dump() for card in sample_cards]),
                "evolution_slots": "[]",
                "average_elixir": 3.5
            },
            {
                "id": 2,
                "name": "Invalid Deck",
                "user_id": 1,
                "cards": "invalid json",
                "evolution_slots": "[]",
                "average_elixir": 4.0
            }
        ]
        deck_service.db_session.fetchall.return_value = deck_rows
        
        result = await deck_service.get_user_decks(sample_user)
        
        # Should return only the valid deck
        assert len(result) == 1
        assert result[0].name == "Valid Deck"

    @pytest.mark.asyncio
    async def test_update_deck_success(self, deck_service, sample_deck, sample_user, sample_cards):
        """Test successful deck update"""
        # Mock existing deck check
        existing_deck_row = {
            "id": 1,
            "name": "Old Name",
            "user_id": 1,
            "cards": json.dumps([card.model_dump() for card in sample_cards]),
            "evolution_slots": "[]",
            "average_elixir": 3.0
        }
        deck_service.db_session.fetchone.return_value = existing_deck_row
        deck_service.db_session.rowcount = 1
        
        result = await deck_service.update_deck(sample_deck, sample_user)
        
        assert result == sample_deck
        assert deck_service.db_session.execute.call_count == 2  # get + update

    @pytest.mark.asyncio
    async def test_update_deck_not_found(self, deck_service, sample_deck, sample_user):
        """Test deck update when deck doesn't exist"""
        deck_service.db_session.fetchone.return_value = None
        
        with pytest.raises(DeckNotFoundError) as exc_info:
            await deck_service.update_deck(sample_deck, sample_user)
        
        assert exc_info.value.deck_id == sample_deck.id
        assert exc_info.value.user_id == sample_user.id

    @pytest.mark.asyncio
    async def test_update_deck_no_rows_affected(self, deck_service, sample_deck, sample_user, sample_cards):
        """Test deck update when no rows are affected"""
        # Mock existing deck check
        existing_deck_row = {
            "id": 1,
            "name": "Old Name",
            "user_id": 1,
            "cards": json.dumps([card.model_dump() for card in sample_cards]),
            "evolution_slots": "[]",
            "average_elixir": 3.0
        }
        deck_service.db_session.fetchone.return_value = existing_deck_row
        deck_service.db_session.rowcount = 0  # No rows affected
        
        with pytest.raises(DeckNotFoundError):
            await deck_service.update_deck(sample_deck, sample_user)

    @pytest.mark.asyncio
    async def test_delete_deck_success(self, deck_service, sample_user, sample_cards):
        """Test successful deck deletion"""
        # Mock existing deck check
        existing_deck_row = {
            "id": 1,
            "name": "Test Deck",
            "user_id": 1,
            "cards": json.dumps([card.model_dump() for card in sample_cards]),
            "evolution_slots": "[]",
            "average_elixir": 3.5
        }
        deck_service.db_session.fetchone.return_value = existing_deck_row
        deck_service.db_session.rowcount = 1
        
        result = await deck_service.delete_deck(1, sample_user)
        
        assert result is True
        assert deck_service.db_session.execute.call_count == 2  # get + delete

    @pytest.mark.asyncio
    async def test_delete_deck_not_found(self, deck_service, sample_user):
        """Test deck deletion when deck doesn't exist"""
        deck_service.db_session.fetchone.return_value = None
        
        with pytest.raises(DeckNotFoundError) as exc_info:
            await deck_service.delete_deck(999, sample_user)
        
        assert exc_info.value.deck_id == 999
        assert exc_info.value.user_id == sample_user.id

    @pytest.mark.asyncio
    async def test_delete_deck_no_rows_affected(self, deck_service, sample_user, sample_cards):
        """Test deck deletion when no rows are affected"""
        # Mock existing deck check
        existing_deck_row = {
            "id": 1,
            "name": "Test Deck",
            "user_id": 1,
            "cards": json.dumps([card.model_dump() for card in sample_cards]),
            "evolution_slots": "[]",
            "average_elixir": 3.5
        }
        deck_service.db_session.fetchone.return_value = existing_deck_row
        deck_service.db_session.rowcount = 0  # No rows affected
        
        result = await deck_service.delete_deck(1, sample_user)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_deck_count_success(self, deck_service, sample_user):
        """Test successful deck count retrieval"""
        deck_service.db_session.fetchone.return_value = {'deck_count': 5}
        
        result = await deck_service.get_deck_count(sample_user)
        
        assert result == 5
        deck_service.db_session.execute.assert_called_once_with(
            "SELECT COUNT(*) as deck_count FROM decks WHERE user_id = %s",
            (sample_user.id,)
        )

    @pytest.mark.asyncio
    async def test_get_deck_count_no_result(self, deck_service, sample_user):
        """Test deck count retrieval when no result is returned"""
        deck_service.db_session.fetchone.return_value = None
        
        result = await deck_service.get_deck_count(sample_user)
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_get_deck_count_database_error(self, deck_service, sample_user):
        """Test deck count retrieval with database error"""
        deck_service.db_session.execute.side_effect = MySQLError("Query failed")
        
        with pytest.raises(DatabaseError) as exc_info:
            await deck_service.get_deck_count(sample_user)
        
        assert "Failed to get deck count" in str(exc_info.value)