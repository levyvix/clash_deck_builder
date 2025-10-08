# backend/tests/unit/test_services.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from src.services.clash_api_service import ClashRoyaleAPIService, ClashAPIError
from src.services.deck_service import DeckService
from src.models.deck import Deck
from src.models.user import User
from src.models.card import Card

@pytest.fixture
def mock_clash_api_service():
    service = ClashRoyaleAPIService(api_key="test_key")
    service.get_cards = AsyncMock(return_value=[])
    return service

@pytest.fixture
def mock_deck_service():
    mock_db_session = MagicMock()
    service = DeckService(db_session=mock_db_session)
    service._get_db_connection = MagicMock()
    return service

@pytest.fixture
def sample_api_response():
    return {
        "items": [
            {
                "id": 26000000,
                "name": "Knight",
                "elixirCost": 3,
                "rarity": "common",
                "type": "troop",
                "arena": {"name": "Training Camp"},
                "iconUrls": {
                    "medium": "https://api-assets.clashroyale.com/cards/300/knight.png"
                }
            },
            {
                "id": 26000001,
                "name": "Fireball",
                "elixirCost": 4,
                "rarity": "rare",
                "type": "spell",
                "arena": {"name": "Spell Valley"},
                "iconUrls": {
                    "medium": "https://api-assets.clashroyale.com/cards/300/fireball.png",
                    "evolutionMedium": "https://api-assets.clashroyale.com/cards/300/fireball_evo.png"
                }
            }
        ]
    }

@pytest.mark.asyncio
async def test_clash_api_get_cards_success(sample_api_response):
    """Test successful API call and data transformation"""
    service = ClashRoyaleAPIService(api_key="test_key")
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        cards = await service.get_cards()
        
        assert len(cards) == 2
        assert cards[0].name == "Knight"
        assert cards[0].elixir_cost == 3
        assert cards[0].rarity == "Common"
        assert cards[0].type == "Troop"
        assert cards[1].name == "Fireball"
        assert cards[1].image_url_evo is not None

@pytest.mark.asyncio
async def test_clash_api_get_cards_auth_error():
    """Test API authentication error handling"""
    service = ClashRoyaleAPIService(api_key="invalid_key")
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 401
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        with pytest.raises(ClashAPIError) as exc_info:
            await service.get_cards()
        
        assert "Invalid API key" in str(exc_info.value)
        assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_clash_api_get_cards_network_error():
    """Test network error handling"""
    service = ClashRoyaleAPIService(api_key="test_key")
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.NetworkError("Connection failed")
        
        with pytest.raises(ClashAPIError) as exc_info:
            await service.get_cards()
        
        assert "Network error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_clash_api_get_cards(mock_clash_api_service):
    cards = await mock_clash_api_service.get_cards()
    mock_clash_api_service.get_cards.assert_called_once()
    assert isinstance(cards, list)

@pytest.mark.asyncio
async def test_deck_service_create_deck(mock_deck_service):
    # Mock the database session methods
    mock_deck_service.db_session.fetchone.return_value = {'deck_count': 5}  # User has 5 decks (under limit)
    mock_deck_service.db_session.lastrowid = 1

    from datetime import datetime
    user = User(
        id="test-user-id",
        google_id="google-123",
        email="test@example.com",
        name="Test User",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Create 8 cards as required by deck validation
    cards = []
    for i in range(8):
        card = Card(
            id=i+1, 
            name=f"Card{i+1}", 
            elixir_cost=3, 
            rarity="Common", 
            type="Troop", 
            image_url=f"http://example.com/card{i+1}.png"
        )
        cards.append(card)
    
    deck_data = Deck(name="New Deck", cards=cards, evolution_slots=[], average_elixir=3.0)

    created_deck = await mock_deck_service.create_deck(deck_data, user)
    mock_deck_service.db_session.execute.assert_called()
    assert created_deck.id == 1
    assert created_deck.name == "New Deck"
