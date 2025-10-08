# backend/tests/unit/test_card_service.py

import pytest
from unittest.mock import MagicMock, patch
from mysql.connector import Error as MySQLError

from src.services.card_service import CardService
from src.models.card import Card
from src.exceptions import DatabaseError


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing."""
    return MagicMock()


@pytest.fixture
def card_service(mock_db_session):
    """Create a CardService instance with mock database session."""
    return CardService(db_session=mock_db_session)


@pytest.fixture
def sample_card_rows():
    """Sample database rows representing cards."""
    return [
        {
            "id": 26000000,
            "name": "Knight",
            "elixir_cost": 3,
            "rarity": "Common",
            "type": "Troop",
            "arena": "Training Camp",
            "image_url": "https://api-assets.clashroyale.com/cards/300/knight.png",
            "image_url_evo": None
        },
        {
            "id": 28000000,
            "name": "Fireball",
            "elixir_cost": 4,
            "rarity": "Rare",
            "type": "Spell",
            "arena": "Spell Valley",
            "image_url": "https://api-assets.clashroyale.com/cards/300/fireball.png",
            "image_url_evo": "https://api-assets.clashroyale.com/cards/300/fireball_evo.png"
        },
        {
            "id": 27000000,
            "name": "Cannon",
            "elixir_cost": 3,
            "rarity": "Common",
            "type": "Building",
            "arena": "Goblin Stadium",
            "image_url": "https://api-assets.clashroyale.com/cards/300/cannon.png",
            "image_url_evo": None
        }
    ]


@pytest.mark.asyncio
async def test_get_all_cards_success(card_service, mock_db_session, sample_card_rows):
    """Test get_all_cards() with mock database returning multiple cards."""
    # Arrange
    mock_db_session.fetchall.return_value = sample_card_rows
    
    # Act
    cards = await card_service.get_all_cards()
    
    # Assert
    assert len(cards) == 3
    assert all(isinstance(card, Card) for card in cards)
    
    # Verify first card
    assert cards[0].id == 26000000
    assert cards[0].name == "Knight"
    assert cards[0].elixir_cost == 3
    assert cards[0].rarity == "Common"
    assert cards[0].type == "Troop"
    assert cards[0].arena == "Training Camp"
    assert cards[0].image_url_evo is None
    
    # Verify second card (with evolution)
    assert cards[1].id == 28000000
    assert cards[1].name == "Fireball"
    assert cards[1].image_url_evo == "https://api-assets.clashroyale.com/cards/300/fireball_evo.png"
    
    # Verify database was called correctly
    mock_db_session.execute.assert_called_once()
    assert "SELECT" in mock_db_session.execute.call_args[0][0]
    assert "FROM cards" in mock_db_session.execute.call_args[0][0]
    mock_db_session.fetchall.assert_called_once()


@pytest.mark.asyncio
@patch('src.services.card_service.cards_cache')
async def test_get_all_cards_empty_database(mock_cache, card_service, mock_db_session):
    """Test get_all_cards() with empty database."""
    # Arrange
    mock_cache.get.return_value = None  # Cache miss
    mock_db_session.fetchall.return_value = []

    # Act
    cards = await card_service.get_all_cards()

    # Assert
    assert cards == []
    assert isinstance(cards, list)
    mock_db_session.execute.assert_called_once()
    mock_db_session.fetchall.assert_called_once()
    mock_cache.set.assert_called_once_with("all_cards", [])


@pytest.mark.asyncio
@patch('src.services.card_service.cards_cache')
async def test_get_all_cards_database_error(mock_cache, card_service, mock_db_session):
    """Test database error handling in get_all_cards()."""
    # Arrange
    mock_cache.get.return_value = None  # Cache miss
    mock_db_session.execute.side_effect = MySQLError("Connection lost")

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        await card_service.get_all_cards()

    assert "Failed to retrieve cards from database" in str(exc_info.value)
    assert exc_info.value.original_error is not None


@pytest.mark.asyncio
@patch('src.services.card_service.cards_cache')
async def test_get_all_cards_skips_invalid_cards(mock_cache, card_service, mock_db_session):
    """Test that get_all_cards() skips cards with validation errors."""
    # Arrange
    mock_cache.get.return_value = None  # Cache miss
    invalid_rows = [
        {
            "id": 26000000,
            "name": "Knight",
            "elixir_cost": 3,
            "rarity": "Common",
            "type": "Troop",
            "arena": "Training Camp",
            "image_url": "https://api-assets.clashroyale.com/cards/300/knight.png",
            "image_url_evo": None
        },
        {
            "id": 28000000,
            "name": "Invalid Card",
            "elixir_cost": 4,
            "rarity": "InvalidRarity",  # Invalid rarity
            "type": "Spell",
            "arena": "Spell Valley",
            "image_url": "https://api-assets.clashroyale.com/cards/300/invalid.png",
            "image_url_evo": None
        }
    ]
    mock_db_session.fetchall.return_value = invalid_rows

    # Act
    cards = await card_service.get_all_cards()

    # Assert - should only return the valid card
    assert len(cards) == 1
    assert cards[0].name == "Knight"


def test_transform_db_row_to_card_complete_data(card_service):
    """Test _transform_db_row_to_card() with complete data."""
    # Arrange
    row = {
        "id": 26000000,
        "name": "Knight",
        "elixir_cost": 3,
        "rarity": "Common",
        "type": "Troop",
        "arena": "Training Camp",
        "image_url": "https://api-assets.clashroyale.com/cards/300/knight.png",
        "image_url_evo": "https://api-assets.clashroyale.com/cards/300/knight_evo.png"
    }
    
    # Act
    card = card_service._transform_db_row_to_card(row)
    
    # Assert
    assert isinstance(card, Card)
    assert card.id == 26000000
    assert card.name == "Knight"
    assert card.elixir_cost == 3
    assert card.rarity == "Common"
    assert card.type == "Troop"
    assert card.arena == "Training Camp"
    assert card.image_url == "https://api-assets.clashroyale.com/cards/300/knight.png"
    assert card.image_url_evo == "https://api-assets.clashroyale.com/cards/300/knight_evo.png"


def test_transform_db_row_to_card_null_optional_fields(card_service):
    """Test _transform_db_row_to_card() with NULL optional fields."""
    # Arrange
    row = {
        "id": 26000000,
        "name": "Knight",
        "elixir_cost": 3,
        "rarity": "Common",
        "type": "Troop",
        "arena": None,  # NULL arena
        "image_url": "https://api-assets.clashroyale.com/cards/300/knight.png",
        "image_url_evo": None  # NULL evolution image
    }
    
    # Act
    card = card_service._transform_db_row_to_card(row)
    
    # Assert
    assert isinstance(card, Card)
    assert card.id == 26000000
    assert card.name == "Knight"
    assert card.arena is None
    assert card.image_url_evo is None


def test_transform_db_row_to_card_missing_required_field(card_service):
    """Test _transform_db_row_to_card() with missing required field."""
    # Arrange
    row = {
        "id": 26000000,
        "name": "Knight",
        # Missing elixir_cost
        "rarity": "Common",
        "type": "Troop",
        "arena": "Training Camp",
        "image_url": "https://api-assets.clashroyale.com/cards/300/knight.png",
        "image_url_evo": None
    }
    
    # Act & Assert
    with pytest.raises(TypeError) as exc_info:
        card_service._transform_db_row_to_card(row)
    
    assert "Missing required field" in str(exc_info.value)


def test_transform_db_row_to_card_invalid_rarity(card_service):
    """Test _transform_db_row_to_card() with invalid rarity value."""
    # Arrange
    row = {
        "id": 26000000,
        "name": "Knight",
        "elixir_cost": 3,
        "rarity": "InvalidRarity",  # Invalid rarity
        "type": "Troop",
        "arena": "Training Camp",
        "image_url": "https://api-assets.clashroyale.com/cards/300/knight.png",
        "image_url_evo": None
    }
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        card_service._transform_db_row_to_card(row)
    
    assert "Card validation failed" in str(exc_info.value)


def test_transform_db_row_to_card_invalid_type(card_service):
    """Test _transform_db_row_to_card() with invalid type value."""
    # Arrange
    row = {
        "id": 26000000,
        "name": "Knight",
        "elixir_cost": 3,
        "rarity": "Common",
        "type": "InvalidType",  # Invalid type
        "arena": "Training Camp",
        "image_url": "https://api-assets.clashroyale.com/cards/300/knight.png",
        "image_url_evo": None
    }
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        card_service._transform_db_row_to_card(row)
    
    assert "Card validation failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_card_by_id_success(card_service, mock_db_session):
    """Test get_card_by_id() with valid card ID."""
    # Arrange
    card_row = {
        "id": 26000000,
        "name": "Knight",
        "elixir_cost": 3,
        "rarity": "Common",
        "type": "Troop",
        "arena": "Training Camp",
        "image_url": "https://api-assets.clashroyale.com/cards/300/knight.png",
        "image_url_evo": None
    }
    mock_db_session.fetchone.return_value = card_row
    
    # Act
    card = await card_service.get_card_by_id(26000000)
    
    # Assert
    assert card is not None
    assert isinstance(card, Card)
    assert card.id == 26000000
    assert card.name == "Knight"
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_card_by_id_not_found(card_service, mock_db_session):
    """Test get_card_by_id() when card is not found."""
    # Arrange
    mock_db_session.fetchone.return_value = None
    
    # Act
    card = await card_service.get_card_by_id(99999999)
    
    # Assert
    assert card is None
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
@patch('src.services.card_service.cards_cache')
async def test_get_card_by_id_database_error(mock_cache, card_service, mock_db_session):
    """Test database error handling in get_card_by_id()."""
    # Arrange
    mock_cache.get.return_value = None  # Cache miss
    mock_db_session.execute.side_effect = MySQLError("Connection lost")

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        await card_service.get_card_by_id(26000000)

    assert "Failed to retrieve card" in str(exc_info.value)
    assert exc_info.value.original_error is not None
