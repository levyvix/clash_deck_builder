# backend/tests/contract/test_decks_get.py

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock

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
    """Sample cards for deck"""
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


@pytest.fixture
def sample_deck(sample_cards, mock_user):
    """Sample deck for retrieval"""
    return Deck(
        id=1,
        name="Test Deck",
        user_id=mock_user.id,
        cards=sample_cards,
        evolution_slots=[sample_cards[0]],
        average_elixir=4.0,
    )


def test_get_all_decks_contract(app, client, mock_user, sample_deck):
    """
    Test that GET /api/decks returns all user decks.

    Verifies:
    - Response is a list of Deck objects
    - Each deck has correct structure
    - Response status is 200 OK
    """
    # Mock authentication
    async def mock_require_auth():
        return {
            "user_id": mock_user.id,
            "google_id": mock_user.google_id,
            "email": mock_user.email,
            "name": mock_user.name,
        }

    # Mock deck service
    async def mock_get_deck_service():
        mock_service = AsyncMock()
        mock_service.get_user_decks.return_value = [sample_deck]
        return mock_service

    from src.middleware.auth_middleware import require_auth
    from src.utils.dependencies import get_deck_service

    app.dependency_overrides[require_auth] = mock_require_auth
    app.dependency_overrides[get_deck_service] = mock_get_deck_service

    try:
        # Make request
        response = client.get("/api/decks")

        # Verify response status
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Verify response is a list
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) == 1, f"Expected 1 deck, got {len(data)}"

        # Verify deck structure
        deck = data[0]
        assert "id" in deck
        assert "name" in deck
        assert "user_id" in deck
        assert "cards" in deck
        assert "evolution_slots" in deck
        assert "average_elixir" in deck

        # Verify values
        assert deck["id"] == 1
        assert deck["name"] == "Test Deck"
        assert len(deck["cards"]) == 8
    finally:
        app.dependency_overrides.clear()


def test_get_single_deck_contract(app, client, mock_user, sample_deck):
    """
    Test that GET /api/decks/{deck_id} returns a specific deck.

    Verifies:
    - Response is a single Deck object
    - Deck has correct structure and data
    - Response status is 200 OK
    - 404 returned for non-existent deck
    """
    # Mock authentication
    async def mock_require_auth():
        return {
            "user_id": mock_user.id,
            "google_id": mock_user.google_id,
            "email": mock_user.email,
            "name": mock_user.name,
        }

    # Mock deck service
    async def mock_get_deck_service():
        mock_service = AsyncMock()
        mock_service.get_deck.return_value = sample_deck
        return mock_service

    from src.middleware.auth_middleware import require_auth
    from src.utils.dependencies import get_deck_service

    app.dependency_overrides[require_auth] = mock_require_auth
    app.dependency_overrides[get_deck_service] = mock_get_deck_service

    try:
        # Make request
        response = client.get("/api/decks/1")

        # Verify response status
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Verify response structure
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "user_id" in data
        assert "cards" in data
        assert "evolution_slots" in data
        assert "average_elixir" in data

        # Verify values
        assert data["id"] == 1
        assert data["name"] == "Test Deck"
        assert data["user_id"] == mock_user.id
        assert len(data["cards"]) == 8
        assert len(data["evolution_slots"]) == 1
    finally:
        app.dependency_overrides.clear()


def test_get_nonexistent_deck_contract(app, client, mock_user):
    """
    Test that GET /api/decks/{deck_id} returns 404 for non-existent deck.
    """
    # Mock authentication
    async def mock_require_auth():
        return {
            "user_id": mock_user.id,
            "google_id": mock_user.google_id,
            "email": mock_user.email,
            "name": mock_user.name,
        }

    # Mock deck service to return None (deck not found)
    async def mock_get_deck_service():
        mock_service = AsyncMock()
        mock_service.get_deck.return_value = None
        return mock_service

    from src.middleware.auth_middleware import require_auth
    from src.utils.dependencies import get_deck_service

    app.dependency_overrides[require_auth] = mock_require_auth
    app.dependency_overrides[get_deck_service] = mock_get_deck_service

    try:
        # Make request
        response = client.get("/api/decks/999")

        # Verify response status
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        # Verify error message
        data = response.json()
        assert "detail" in data
    finally:
        app.dependency_overrides.clear()
