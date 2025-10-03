# backend/tests/unit/test_clash_api_service.py

import pytest
from unittest.mock import MagicMock, patch
import httpx
from src.services.clash_api_service import ClashRoyaleAPIService, ClashAPIError


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
async def test_clash_api_get_cards_rate_limit():
    """Test API rate limit error handling"""
    service = ClashRoyaleAPIService(api_key="test_key")
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 429
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        with pytest.raises(ClashAPIError) as exc_info:
            await service.get_cards()
        
        assert "rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_clash_api_get_cards_server_error():
    """Test API server error handling"""
    service = ClashRoyaleAPIService(api_key="test_key")
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        with pytest.raises(ClashAPIError) as exc_info:
            await service.get_cards()
        
        assert "server error" in str(exc_info.value)
        assert exc_info.value.status_code == 500


def test_transform_card_data():
    """Test card data transformation"""
    service = ClashRoyaleAPIService(api_key="test_key")
    
    card_data = {
        "id": 26000000,
        "name": "Knight",
        "elixirCost": 3,
        "rarity": "common",
        "type": "troop",
        "arena": {"name": "Training Camp"},
        "iconUrls": {
            "medium": "https://api-assets.clashroyale.com/cards/300/knight.png"
        }
    }
    
    card = service._transform_card_data(card_data)
    
    assert card.id == 26000000
    assert card.name == "Knight"
    assert card.elixir_cost == 3
    assert card.rarity == "Common"
    assert card.type == "Troop"
    assert card.arena == "Training Camp"
    assert card.image_url == "https://api-assets.clashroyale.com/cards/300/knight.png"
    assert card.image_url_evo is None


def test_transform_card_data_with_evolution():
    """Test card data transformation with evolution image"""
    service = ClashRoyaleAPIService(api_key="test_key")
    
    card_data = {
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
    
    card = service._transform_card_data(card_data)
    
    assert card.name == "Fireball"
    assert card.image_url_evo == "https://api-assets.clashroyale.com/cards/300/fireball_evo.png"


def test_transform_card_data_missing_required_field():
    """Test card data transformation with missing required field"""
    service = ClashRoyaleAPIService(api_key="test_key")
    
    card_data = {
        "id": 26000000,
        "name": "Knight",
        # Missing elixirCost
        "rarity": "common",
        "type": "troop",
        "iconUrls": {
            "medium": "https://api-assets.clashroyale.com/cards/300/knight.png"
        }
    }
    
    with pytest.raises(ValueError) as exc_info:
        service._transform_card_data(card_data)
    
    assert "Missing elixir cost" in str(exc_info.value)