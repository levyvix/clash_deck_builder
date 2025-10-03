# backend/tests/test_api_integration.py

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.api.cards import router as cards_router
from src.api.decks import router as decks_router
from src.models.card import Card
from src.models.deck import Deck
from src.models.user import User
from src.services.clash_api_service import ClashAPIError
from src.exceptions import (
    DatabaseError,
    DeckNotFoundError,
    SerializationError,
    DeckLimitExceededError,
    DeckValidationError,
)


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    app = FastAPI()
    app.include_router(cards_router)
    app.include_router(decks_router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_cards():
    """Create sample cards for testing"""
    return [
        Card(
            id=1,
            name="Knight",
            elixir_cost=3,
            rarity="Common",
            type="Troop",
            image_url="http://example.com/knight.png",
        ),
        Card(
            id=2,
            name="Archers",
            elixir_cost=3,
            rarity="Common",
            type="Troop",
            image_url="http://example.com/archers.png",
        ),
        Card(
            id=3,
            name="Fireball",
            elixir_cost=4,
            rarity="Rare",
            type="Spell",
            image_url="http://example.com/fireball.png",
        ),
        Card(
            id=4,
            name="Giant",
            elixir_cost=5,
            rarity="Rare",
            type="Troop",
            image_url="http://example.com/giant.png",
        ),
        Card(
            id=5,
            name="Wizard",
            elixir_cost=5,
            rarity="Rare",
            type="Troop",
            image_url="http://example.com/wizard.png",
        ),
        Card(
            id=6,
            name="Minions",
            elixir_cost=3,
            rarity="Common",
            type="Troop",
            image_url="http://example.com/minions.png",
        ),
        Card(
            id=7,
            name="Zap",
            elixir_cost=2,
            rarity="Common",
            type="Spell",
            image_url="http://example.com/zap.png",
        ),
        Card(
            id=8,
            name="Musketeer",
            elixir_cost=4,
            rarity="Rare",
            type="Troop",
            image_url="http://example.com/musketeer.png",
        ),
    ]


@pytest.fixture
def sample_deck(sample_cards):
    """Create a sample deck for testing"""
    return Deck(
        id=1,
        name="Test Deck",
        user_id=1,
        cards=sample_cards,
        evolution_slots=[sample_cards[0]],
        average_elixir=3.5,
    )


class TestCardsAPI:
    """Integration tests for Cards API endpoints"""

    def test_get_all_cards_success(self, app, client, sample_cards):
        """Test successful retrieval of all cards"""
        # Mock the service
        mock_service = AsyncMock()
        mock_service.get_cards.return_value = sample_cards

        # Override the dependency
        from src.utils.dependencies import get_clash_api_service

        app.dependency_overrides[get_clash_api_service] = lambda: mock_service

        response = client.get("/cards")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8
        assert data[0]["name"] == "Knight"
        assert data[0]["elixir_cost"] == 3
        assert data[0]["rarity"] == "Common"

        # Clean up
        app.dependency_overrides.clear()

    def test_get_all_cards_api_auth_error(self, app, client):
        """Test cards API with authentication error"""
        mock_service = AsyncMock()
        mock_service.get_cards.side_effect = ClashAPIError(
            "Invalid API key", status_code=401
        )

        from src.utils.dependencies import get_clash_api_service

        app.dependency_overrides[get_clash_api_service] = lambda: mock_service

        response = client.get("/cards")

        assert response.status_code == 401
        assert "Invalid Clash Royale API key" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_all_cards_api_forbidden_error(self, app, client):
        """Test cards API with forbidden error"""
        mock_service = AsyncMock()
        mock_service.get_cards.side_effect = ClashAPIError(
            "Access forbidden", status_code=403
        )

        from src.utils.dependencies import get_clash_api_service

        app.dependency_overrides[get_clash_api_service] = lambda: mock_service

        response = client.get("/cards")

        assert response.status_code == 403
        assert "Access forbidden to Clash Royale API" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_all_cards_api_rate_limit_error(self, app, client):
        """Test cards API with rate limit error"""
        mock_service = AsyncMock()
        mock_service.get_cards.side_effect = ClashAPIError(
            "Rate limit exceeded", status_code=429
        )

        from src.utils.dependencies import get_clash_api_service

        app.dependency_overrides[get_clash_api_service] = lambda: mock_service

        response = client.get("/cards")

        assert response.status_code == 429
        assert "rate limit exceeded" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_all_cards_api_server_error(self, app, client):
        """Test cards API with server error"""
        mock_service = AsyncMock()
        mock_service.get_cards.side_effect = ClashAPIError(
            "Server error", status_code=500
        )

        from src.utils.dependencies import get_clash_api_service

        app.dependency_overrides[get_clash_api_service] = lambda: mock_service

        response = client.get("/cards")

        assert response.status_code == 503
        assert "currently unavailable" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_all_cards_api_network_error(self, app, client):
        """Test cards API with network error"""
        mock_service = AsyncMock()
        mock_service.get_cards.side_effect = ClashAPIError("Network error")

        from src.utils.dependencies import get_clash_api_service

        app.dependency_overrides[get_clash_api_service] = lambda: mock_service

        response = client.get("/cards")

        assert response.status_code == 503
        assert "Unable to connect" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_all_cards_unexpected_error(self, app, client):
        """Test cards API with unexpected error"""
        mock_service = AsyncMock()
        mock_service.get_cards.side_effect = Exception("Unexpected error")

        from src.utils.dependencies import get_clash_api_service

        app.dependency_overrides[get_clash_api_service] = lambda: mock_service

        response = client.get("/cards")

        assert response.status_code == 500
        assert "unexpected error occurred" in response.json()["detail"]

        app.dependency_overrides.clear()


class TestDecksAPI:
    """Integration tests for Decks API endpoints"""

    def _setup_deck_dependencies(self, app, mock_user=None, mock_deck_service=None):
        """Helper method to set up deck API dependencies"""
        from src.api.decks import get_current_user
        from src.utils.dependencies import get_deck_service

        if mock_user:
            app.dependency_overrides[get_current_user] = lambda: mock_user
        if mock_deck_service:
            app.dependency_overrides[get_deck_service] = lambda: mock_deck_service

    def test_create_deck_success(self, app, client, sample_deck):
        """Test successful deck creation"""
        # Mock dependencies
        mock_user = User(id=1)
        mock_service = AsyncMock()
        created_deck = sample_deck.model_copy()
        created_deck.id = 123
        mock_service.create_deck.return_value = created_deck

        self._setup_deck_dependencies(app, mock_user, mock_service)

        # Prepare request data
        deck_data = sample_deck.model_dump()
        deck_data.pop("id")  # Remove ID for creation

        response = client.post("/decks", json=deck_data)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 123
        assert data["name"] == "Test Deck"
        assert len(data["cards"]) == 8

        app.dependency_overrides.clear()

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_create_deck_limit_exceeded(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test deck creation when limit is exceeded"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.create_deck.side_effect = DeckLimitExceededError(
            user_id=1, max_decks=20
        )
        mock_get_service.return_value = mock_service

        deck_data = sample_deck.model_dump()
        deck_data.pop("id")

        response = client.post("/decks", json=deck_data)

        assert response.status_code == 409
        assert "Maximum deck limit of 20 reached" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_create_deck_validation_error(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test deck creation with validation error"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.create_deck.side_effect = DeckValidationError("Invalid deck data")
        mock_get_service.return_value = mock_service

        deck_data = sample_deck.model_dump()
        deck_data.pop("id")

        response = client.post("/decks", json=deck_data)

        assert response.status_code == 400
        assert "Invalid deck data" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_create_deck_database_error(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test deck creation with database error"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.create_deck.side_effect = DatabaseError(
            "Database connection failed"
        )
        mock_get_service.return_value = mock_service

        deck_data = sample_deck.model_dump()
        deck_data.pop("id")

        response = client.post("/decks", json=deck_data)

        assert response.status_code == 500
        assert "database error" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_get_all_user_decks_success(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test successful retrieval of all user decks"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        decks = [sample_deck, sample_deck.model_copy()]
        decks[1].id = 2
        decks[1].name = "Second Deck"
        mock_service.get_user_decks.return_value = decks
        mock_get_service.return_value = mock_service

        response = client.get("/decks")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Test Deck"
        assert data[1]["name"] == "Second Deck"

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_get_all_user_decks_empty(self, mock_get_service, mock_get_user, client):
        """Test retrieval of user decks when user has no decks"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.get_user_decks.return_value = []
        mock_get_service.return_value = mock_service

        response = client.get("/decks")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_get_all_user_decks_database_error(
        self, mock_get_service, mock_get_user, client
    ):
        """Test retrieval of user decks with database error"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.get_user_decks.side_effect = DatabaseError(
            "Database connection failed"
        )
        mock_get_service.return_value = mock_service

        response = client.get("/decks")

        assert response.status_code == 500
        assert "database error" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_get_single_deck_success(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test successful retrieval of a single deck"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.get_deck.return_value = sample_deck
        mock_get_service.return_value = mock_service

        response = client.get("/decks/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Deck"
        assert len(data["cards"]) == 8

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_get_single_deck_not_found(self, mock_get_service, mock_get_user, client):
        """Test retrieval of non-existent deck"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.get_deck.return_value = None
        mock_get_service.return_value = mock_service

        response = client.get("/decks/999")

        assert response.status_code == 404
        assert "Deck with ID 999 not found" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_get_single_deck_not_found_exception(
        self, mock_get_service, mock_get_user, client
    ):
        """Test retrieval of deck with DeckNotFoundError exception"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.get_deck.side_effect = DeckNotFoundError(deck_id=999, user_id=1)
        mock_get_service.return_value = mock_service

        response = client.get("/decks/999")

        assert response.status_code == 404
        assert "Deck with ID 999 not found" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_get_single_deck_serialization_error(
        self, mock_get_service, mock_get_user, client
    ):
        """Test retrieval of deck with serialization error"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.get_deck.side_effect = SerializationError("Corrupted data")
        mock_get_service.return_value = mock_service

        response = client.get("/decks/1")

        assert response.status_code == 500
        assert "corrupted" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_update_deck_success(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test successful deck update"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        updated_deck = sample_deck.model_copy()
        updated_deck.name = "Updated Deck"
        mock_service.update_deck.return_value = updated_deck
        mock_get_service.return_value = mock_service

        deck_data = sample_deck.model_dump()
        deck_data["name"] = "Updated Deck"

        response = client.put("/decks/1", json=deck_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Deck"

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_update_deck_not_found(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test update of non-existent deck"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.update_deck.side_effect = DeckNotFoundError(deck_id=999, user_id=1)
        mock_get_service.return_value = mock_service

        deck_data = sample_deck.model_dump()

        response = client.put("/decks/999", json=deck_data)

        assert response.status_code == 404
        assert "Deck with ID 999 not found" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_update_deck_validation_error(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test deck update with validation error"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.update_deck.side_effect = DeckValidationError("Invalid deck data")
        mock_get_service.return_value = mock_service

        deck_data = sample_deck.model_dump()

        response = client.put("/decks/1", json=deck_data)

        assert response.status_code == 400
        assert "Invalid deck data" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_update_deck_database_error(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test deck update with database error"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.update_deck.side_effect = DatabaseError(
            "Database connection failed"
        )
        mock_get_service.return_value = mock_service

        deck_data = sample_deck.model_dump()

        response = client.put("/decks/1", json=deck_data)

        assert response.status_code == 500
        assert "database error" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_delete_deck_success(self, mock_get_service, mock_get_user, client):
        """Test successful deck deletion"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.delete_deck.return_value = True
        mock_get_service.return_value = mock_service

        response = client.delete("/decks/1")

        assert response.status_code == 204
        assert response.content == b""

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_delete_deck_not_found(self, mock_get_service, mock_get_user, client):
        """Test deletion of non-existent deck"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.delete_deck.side_effect = DeckNotFoundError(deck_id=999, user_id=1)
        mock_get_service.return_value = mock_service

        response = client.delete("/decks/999")

        assert response.status_code == 404
        assert "Deck with ID 999 not found" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_delete_deck_not_successful(self, mock_get_service, mock_get_user, client):
        """Test deck deletion when service returns False"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.delete_deck.return_value = False
        mock_get_service.return_value = mock_service

        response = client.delete("/decks/1")

        assert response.status_code == 404
        assert "Deck with ID 1 not found" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_delete_deck_database_error(self, mock_get_service, mock_get_user, client):
        """Test deck deletion with database error"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.delete_deck.side_effect = DatabaseError(
            "Database connection failed"
        )
        mock_get_service.return_value = mock_service

        response = client.delete("/decks/1")

        assert response.status_code == 500
        assert "database error" in response.json()["detail"]


class TestDependencyInjection:
    """Test dependency injection functionality"""

    @patch("src.api.decks.get_current_user")
    def test_get_current_user_dependency(self, mock_get_user, client):
        """Test that get_current_user dependency is properly injected"""
        mock_user = User(id=42)
        mock_get_user.return_value = mock_user

        # Mock the deck service to verify user is passed correctly
        with patch("src.api.decks.get_deck_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_user_decks.return_value = []
            mock_get_service.return_value = mock_service

            response = client.get("/decks")

            # Verify the service was called with the correct user
            mock_service.get_user_decks.assert_called_once_with(mock_user)

    @patch("src.api.cards.get_clash_api_service")
    def test_clash_api_service_dependency(self, mock_get_service, client):
        """Test that clash API service dependency is properly injected"""
        mock_service = AsyncMock()
        mock_service.get_cards.return_value = []
        mock_get_service.return_value = mock_service

        response = client.get("/cards")

        # Verify the service method was called
        mock_service.get_cards.assert_called_once()

    @patch("src.api.decks.get_deck_service")
    @patch("src.api.decks.get_current_user")
    def test_deck_service_dependency(self, mock_get_user, mock_get_service, client):
        """Test that deck service dependency is properly injected"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.get_user_decks.return_value = []
        mock_get_service.return_value = mock_service

        response = client.get("/decks")

        # Verify the service was obtained and used
        mock_get_service.assert_called_once()
        mock_service.get_user_decks.assert_called_once()


class TestErrorHandlingScenarios:
    """Test various error handling scenarios"""

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_unexpected_error_handling(self, mock_get_service, mock_get_user, client):
        """Test handling of unexpected errors"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.get_user_decks.side_effect = Exception("Unexpected error")
        mock_get_service.return_value = mock_service

        response = client.get("/decks")

        assert response.status_code == 500
        assert "unexpected error occurred" in response.json()["detail"]

    @patch("src.api.decks.get_current_user")
    @patch("src.api.decks.get_deck_service")
    def test_serialization_error_handling(
        self, mock_get_service, mock_get_user, client, sample_deck
    ):
        """Test handling of serialization errors"""
        mock_user = User(id=1)
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.create_deck.side_effect = SerializationError(
            "Failed to serialize cards"
        )
        mock_get_service.return_value = mock_service

        deck_data = sample_deck.model_dump()
        deck_data.pop("id")

        response = client.post("/decks", json=deck_data)

        assert response.status_code == 400
        assert "Invalid deck data" in response.json()["detail"]

    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON in request body"""
        response = client.post(
            "/decks", data="invalid json", headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422  # FastAPI validation error

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields in request"""
        incomplete_deck = {"name": "Incomplete Deck"}  # Missing cards field

        response = client.post("/decks", json=incomplete_deck)

        assert response.status_code == 422  # FastAPI validation error

    def test_invalid_deck_id_parameter(self, client):
        """Test handling of invalid deck ID parameter"""
        response = client.get("/decks/invalid_id")

        assert response.status_code == 422  # FastAPI validation error
