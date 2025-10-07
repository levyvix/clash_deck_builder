# backend/tests/contract/test_decks_create.py

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock

from src.api.decks import router as decks_router
from src.models.card import Card
from src.models.deck import Deck
from src.models.user import User


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    app = FastAPI()
    app.include_router(decks_router, prefix="/api")
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_cards():
    """Sample cards for deck creation"""
    return [
        Card(id=26000000, name="Knight", elixir_cost=3, rarity="Common", type="Troop",
             image_url="https://example.com/knight.png"),
        Card(id=26000001, name="Archers", elixir_cost=3, rarity="Common", type="Troop",
             image_url="https://example.com/archers.png"),
        Card(id=26000002, name="Goblins", elixir_cost=2, rarity="Common", type="Troop",
             image_url="https://example.com/goblins.png"),
        Card(id=26000003, name="Giant", elixir_cost=5, rarity="Rare", type="Troop",
             image_url="https://example.com/giant.png"),
        Card(id=26000004, name="P.E.K.K.A", elixir_cost=7, rarity="Epic", type="Troop",
             image_url="https://example.com/pekka.png"),
        Card(id=26000005, name="Minions", elixir_cost=3, rarity="Common", type="Troop",
             image_url="https://example.com/minions.png"),
        Card(id=28000000, name="Arrows", elixir_cost=3, rarity="Common", type="Spell",
             image_url="https://example.com/arrows.png"),
        Card(id=28000001, name="Fireball", elixir_cost=4, rarity="Rare", type="Spell",
             image_url="https://example.com/fireball.png"),
    ]


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    from datetime import datetime
    return User(
        id="test-user-123",
        google_id="google-id-123",
        email="test@example.com",
        name="Test User",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def test_create_deck_contract(app, client, sample_cards, mock_user):
    """
    Test that POST /api/decks creates a deck with the expected structure.

    Verifies:
    - Request accepts Deck object with cards and evolution_slots
    - Response returns created Deck with id assigned
    - Response status is 201 Created
    - Average elixir is calculated correctly
    """
    # Prepare deck data
    deck_data = {
        "name": "Test Deck",
        "cards": [card.model_dump() for card in sample_cards],
        "evolution_slots": [sample_cards[0].model_dump()],  # Knight as evolution
    }

    # Expected created deck
    created_deck = Deck(
        id=1,
        name="Test Deck",
        user_id=mock_user.id,
        cards=sample_cards,
        evolution_slots=[sample_cards[0]],
        average_elixir=4.0,
    )

    # Mock authentication dependency
    async def mock_require_auth():
        return {
            "user_id": mock_user.id,
            "google_id": mock_user.google_id,
            "email": mock_user.email,
            "name": mock_user.name,
        }

    # Mock deck service dependency
    async def mock_get_deck_service():
        mock_service = AsyncMock()
        mock_service.create_deck.return_value = created_deck
        return mock_service

    from src.middleware.auth_middleware import require_auth
    from src.utils.dependencies import get_deck_service

    app.dependency_overrides[require_auth] = mock_require_auth
    app.dependency_overrides[get_deck_service] = mock_get_deck_service

    try:
        # Make request
        response = client.post("/api/decks", json=deck_data)

        # Verify response status
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        # Verify response structure
        data = response.json()
        assert "id" in data, "Response should have 'id' field"
        assert "name" in data, "Response should have 'name' field"
        assert "user_id" in data, "Response should have 'user_id' field"
        assert "cards" in data, "Response should have 'cards' field"
        assert "evolution_slots" in data, "Response should have 'evolution_slots' field"
        assert "average_elixir" in data, "Response should have 'average_elixir' field"

        # Verify data types
        assert isinstance(data["id"], int), "id should be integer"
        assert isinstance(data["name"], str), "name should be string"
        assert isinstance(data["cards"], list), "cards should be list"
        assert isinstance(data["evolution_slots"], list), "evolution_slots should be list"
        assert isinstance(data["average_elixir"], (int, float)), "average_elixir should be number"

        # Verify data values
        assert data["id"] == 1
        assert data["name"] == "Test Deck"
        assert data["user_id"] == mock_user.id
        assert len(data["cards"]) == 8
        assert len(data["evolution_slots"]) == 1

        # Verify cards structure
        card = data["cards"][0]
        assert "id" in card
        assert "name" in card
        assert "elixir_cost" in card
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()
