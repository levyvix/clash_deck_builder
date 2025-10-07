# backend/tests/contract/test_clash_api.py

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock

from src.api.cards import router as cards_router
from src.models.card import Card


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    app = FastAPI()
    app.include_router(cards_router, prefix="/api")
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_cards():
    """Sample cards matching Clash Royale API format"""
    return [
        Card(
            id=26000000,
            name="Knight",
            elixir_cost=3,
            rarity="Common",
            type="Troop",
            arena="Training Camp",
            image_url="https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png",
            image_url_evo=None,
        ),
        Card(
            id=26000001,
            name="Archers",
            elixir_cost=3,
            rarity="Common",
            type="Troop",
            arena="Training Camp",
            image_url="https://api-assets.clashroyale.com/cards/300/W4Hp7g7f5E7RBfCD7DhsPVY7jqjKMDoOwQ3hDvRxRG0.png",
            image_url_evo=None,
        ),
    ]


def test_fetch_cards_contract(app, client, sample_cards):
    """
    Test that GET /api/cards returns a list of Card objects
    with the expected structure and fields.

    This verifies the API contract for card retrieval.
    """
    # Mock the card service dependency
    async def mock_get_card_service():
        mock_service = AsyncMock()
        mock_service.get_all_cards.return_value = sample_cards
        return mock_service

    # Override the dependency
    from src.utils.dependencies import get_card_service
    app.dependency_overrides[get_card_service] = mock_get_card_service

    try:
        # Make request
        response = client.get("/api/cards")

        # Verify response status
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Verify response is a list
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) == 2, f"Expected 2 cards, got {len(data)}"

        # Verify first card structure
        card = data[0]
        assert "id" in card, "Card should have 'id' field"
        assert "name" in card, "Card should have 'name' field"
        assert "elixir_cost" in card, "Card should have 'elixir_cost' field"
        assert "rarity" in card, "Card should have 'rarity' field"
        assert "type" in card, "Card should have 'type' field"
        assert "arena" in card, "Card should have 'arena' field"
        assert "image_url" in card, "Card should have 'image_url' field"
        assert "image_url_evo" in card, "Card should have 'image_url_evo' field"

        # Verify data types
        assert isinstance(card["id"], int), "id should be integer"
        assert isinstance(card["name"], str), "name should be string"
        assert isinstance(card["elixir_cost"], int), "elixir_cost should be integer"
        assert isinstance(card["rarity"], str), "rarity should be string"
        assert isinstance(card["type"], str), "type should be string"

        # Verify data values
        assert card["id"] == 26000000
        assert card["name"] == "Knight"
        assert card["elixir_cost"] == 3
        assert card["rarity"] == "Common"
        assert card["type"] == "Troop"

        # Verify cache headers are set
        assert "Cache-Control" in response.headers
        assert "ETag" in response.headers
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()
