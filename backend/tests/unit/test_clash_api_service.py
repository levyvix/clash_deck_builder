# backend/tests/unit/test_clash_api_service.py

import pytest
from unittest.mock import MagicMock, patch
import httpx
import json
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


@pytest.fixture
def clash_api_service():
    """Create a ClashRoyaleAPIService instance for testing"""
    return ClashRoyaleAPIService(api_key="test_key")


class TestClashRoyaleAPIService:
    """Test suite for ClashRoyaleAPIService"""

    def test_init(self):
        """Test service initialization"""
        service = ClashRoyaleAPIService(api_key="test_key", base_url="https://custom.api.com")
        assert service.api_key == "test_key"
        assert service.base_url == "https://custom.api.com"
        assert service.headers == {"Authorization": "Bearer test_key"}
        assert service.timeout == 30.0

    def test_init_default_base_url(self):
        """Test service initialization with default base URL"""
        service = ClashRoyaleAPIService(api_key="test_key")
        assert service.base_url == "https://api.clashroyale.com/v1"

    @pytest.mark.asyncio
    async def test_get_cards_success(self, clash_api_service, sample_api_response):
        """Test successful API call and data transformation"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            cards = await clash_api_service.get_cards()
            
            # Verify API call was made correctly
            mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
                "https://api.clashroyale.com/v1/cards",
                headers={"Authorization": "Bearer test_key"}
            )
            
            # Verify response transformation
            assert len(cards) == 2
            assert cards[0].name == "Knight"
            assert cards[0].elixir_cost == 3
            assert cards[0].rarity == "Common"
            assert cards[0].type == "Troop"
            assert cards[0].arena == "Training Camp"
            assert cards[1].name == "Fireball"
            assert cards[1].image_url_evo is not None

    @pytest.mark.asyncio
    async def test_get_cards_auth_error(self, clash_api_service):
        """Test API authentication error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 401
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "Invalid API key" in str(exc_info.value)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_cards_forbidden_error(self, clash_api_service):
        """Test API forbidden error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 403
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "API access forbidden" in str(exc_info.value)
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_cards_rate_limit(self, clash_api_service):
        """Test API rate limit error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 429
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "rate limit exceeded" in str(exc_info.value)
            assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_get_cards_server_error(self, clash_api_service):
        """Test API server error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "server error" in str(exc_info.value)
            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_cards_client_error(self, clash_api_service):
        """Test API client error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 400
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "API request failed with status 400" in str(exc_info.value)
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_cards_timeout_error(self, clash_api_service):
        """Test API timeout error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.TimeoutException("Request timed out")
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "API request timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_cards_network_error(self, clash_api_service):
        """Test network error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.NetworkError("Connection failed")
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_cards_json_parse_error(self, clash_api_service):
        """Test JSON parsing error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "Failed to parse API response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_cards_missing_items_field(self, clash_api_service):
        """Test handling of API response missing 'items' field"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}  # Missing 'items' field
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "Invalid API response format: missing 'items' field" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_cards_partial_transformation_failure(self, clash_api_service):
        """Test handling when some cards fail transformation but others succeed"""
        api_response = {
            "items": [
                {
                    "id": 26000000,
                    "name": "Knight",
                    "elixirCost": 3,
                    "rarity": "common",
                    "type": "troop",
                    "iconUrls": {"medium": "https://example.com/knight.png"}
                },
                {
                    "id": 26000001,
                    "name": "Invalid Card",
                    # Missing required fields
                    "iconUrls": {"medium": "https://example.com/invalid.png"}
                }
            ]
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            cards = await clash_api_service.get_cards()
            
            # Should return only the valid card
            assert len(cards) == 1
            assert cards[0].name == "Knight"

    @pytest.mark.asyncio
    async def test_get_cards_unexpected_error(self, clash_api_service):
        """Test handling of unexpected errors"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Unexpected error")
            
            with pytest.raises(ClashAPIError) as exc_info:
                await clash_api_service.get_cards()
            
            assert "Unexpected error" in str(exc_info.value)


class TestCardDataTransformation:
    """Test suite for card data transformation methods"""

    @pytest.fixture
    def clash_api_service(self):
        return ClashRoyaleAPIService(api_key="test_key")

    def test_transform_card_data_complete(self, clash_api_service):
        """Test card data transformation with all fields"""
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
        
        card = clash_api_service._transform_card_data(card_data)
        
        assert card.id == 26000000
        assert card.name == "Knight"
        assert card.elixir_cost == 3
        assert card.rarity == "Common"
        assert card.type == "Troop"
        assert card.arena == "Training Camp"
        assert card.image_url == "https://api-assets.clashroyale.com/cards/300/knight.png"
        assert card.image_url_evo is None

    def test_transform_card_data_with_evolution(self, clash_api_service):
        """Test card data transformation with evolution image"""
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
        
        card = clash_api_service._transform_card_data(card_data)
        
        assert card.name == "Fireball"
        assert card.image_url_evo == "https://api-assets.clashroyale.com/cards/300/fireball_evo.png"

    def test_transform_card_data_no_arena(self, clash_api_service):
        """Test card data transformation without arena"""
        card_data = {
            "id": 26000000,
            "name": "Knight",
            "elixirCost": 3,
            "rarity": "common",
            "type": "troop",
            "iconUrls": {"medium": "https://example.com/knight.png"}
        }
        
        card = clash_api_service._transform_card_data(card_data)
        
        assert card.arena is None

    def test_transform_card_data_image_url_priority(self, clash_api_service):
        """Test image URL selection priority (medium > large > small)"""
        card_data = {
            "id": 26000000,
            "name": "Knight",
            "elixirCost": 3,
            "rarity": "common",
            "type": "troop",
            "iconUrls": {
                "small": "https://example.com/knight_small.png",
                "large": "https://example.com/knight_large.png",
                "medium": "https://example.com/knight_medium.png"
            }
        }
        
        card = clash_api_service._transform_card_data(card_data)
        assert card.image_url == "https://example.com/knight_medium.png"

    def test_transform_card_data_missing_id(self, clash_api_service):
        """Test card data transformation with missing ID"""
        card_data = {
            "name": "Knight",
            "elixirCost": 3,
            "rarity": "common",
            "type": "troop",
            "iconUrls": {"medium": "https://example.com/knight.png"}
        }
        
        with pytest.raises(ValueError) as exc_info:
            clash_api_service._transform_card_data(card_data)
        
        assert "Missing card ID" in str(exc_info.value)

    def test_transform_card_data_missing_name(self, clash_api_service):
        """Test card data transformation with missing name"""
        card_data = {
            "id": 26000000,
            "elixirCost": 3,
            "rarity": "common",
            "type": "troop",
            "iconUrls": {"medium": "https://example.com/knight.png"}
        }
        
        with pytest.raises(ValueError) as exc_info:
            clash_api_service._transform_card_data(card_data)
        
        assert "Missing or empty card name" in str(exc_info.value)

    def test_transform_card_data_empty_name(self, clash_api_service):
        """Test card data transformation with empty name"""
        card_data = {
            "id": 26000000,
            "name": "",
            "elixirCost": 3,
            "rarity": "common",
            "type": "troop",
            "iconUrls": {"medium": "https://example.com/knight.png"}
        }
        
        with pytest.raises(ValueError) as exc_info:
            clash_api_service._transform_card_data(card_data)
        
        assert "Missing or empty card name" in str(exc_info.value)

    def test_transform_card_data_missing_elixir_cost(self, clash_api_service):
        """Test card data transformation with missing elixir cost"""
        card_data = {
            "id": 26000000,
            "name": "Knight",
            "rarity": "common",
            "type": "troop",
            "iconUrls": {"medium": "https://example.com/knight.png"}
        }
        
        with pytest.raises(ValueError) as exc_info:
            clash_api_service._transform_card_data(card_data)
        
        assert "Missing elixir cost" in str(exc_info.value)

    def test_transform_card_data_invalid_rarity(self, clash_api_service):
        """Test card data transformation with invalid rarity"""
        card_data = {
            "id": 26000000,
            "name": "Knight",
            "elixirCost": 3,
            "rarity": "invalid",
            "type": "troop",
            "iconUrls": {"medium": "https://example.com/knight.png"}
        }
        
        with pytest.raises(ValueError) as exc_info:
            clash_api_service._transform_card_data(card_data)
        
        assert "Invalid or missing rarity: invalid" in str(exc_info.value)

    def test_transform_card_data_invalid_type(self, clash_api_service):
        """Test card data transformation with invalid type"""
        card_data = {
            "id": 26000000,
            "name": "Knight",
            "elixirCost": 3,
            "rarity": "common",
            "type": "invalid",
            "iconUrls": {"medium": "https://example.com/knight.png"}
        }
        
        with pytest.raises(ValueError) as exc_info:
            clash_api_service._transform_card_data(card_data)
        
        assert "Invalid or missing type: invalid" in str(exc_info.value)

    def test_transform_card_data_missing_image_url(self, clash_api_service):
        """Test card data transformation with missing image URL"""
        card_data = {
            "id": 26000000,
            "name": "Knight",
            "elixirCost": 3,
            "rarity": "common",
            "type": "troop",
            "iconUrls": {}
        }
        
        with pytest.raises(ValueError) as exc_info:
            clash_api_service._transform_card_data(card_data)
        
        assert "Missing card image URL" in str(exc_info.value)

    def test_transform_card_data_rarity_mapping(self, clash_api_service):
        """Test rarity mapping from API format to internal format"""
        rarities = [
            ("common", "Common"),
            ("rare", "Rare"),
            ("epic", "Epic"),
            ("legendary", "Legendary"),
            ("champion", "Champion")
        ]
        
        for api_rarity, expected_rarity in rarities:
            card_data = {
                "id": 26000000,
                "name": "Test Card",
                "elixirCost": 3,
                "rarity": api_rarity,
                "type": "troop",
                "iconUrls": {"medium": "https://example.com/test.png"}
            }
            
            card = clash_api_service._transform_card_data(card_data)
            assert card.rarity == expected_rarity

    def test_transform_card_data_type_mapping(self, clash_api_service):
        """Test type mapping from API format to internal format"""
        types = [
            ("troop", "Troop"),
            ("spell", "Spell"),
            ("building", "Building")
        ]
        
        for api_type, expected_type in types:
            card_data = {
                "id": 26000000,
                "name": "Test Card",
                "elixirCost": 3,
                "rarity": "common",
                "type": api_type,
                "iconUrls": {"medium": "https://example.com/test.png"}
            }
            
            card = clash_api_service._transform_card_data(card_data)
            assert card.type == expected_type