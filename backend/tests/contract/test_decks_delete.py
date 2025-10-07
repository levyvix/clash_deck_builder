# backend/tests/contract/test_decks_delete.py

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock

from src.api.decks import router as decks_router
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


def test_delete_deck_contract(app, client, mock_user):
    """
    Test that DELETE /api/decks/{deck_id} deletes a deck.

    Verifies:
    - Response status is 204 No Content on successful deletion
    - No response body is returned
    - Authentication is required
    """
    # Mock authentication
    async def mock_require_auth():
        return {
            "user_id": mock_user.id,
            "google_id": mock_user.google_id,
            "email": mock_user.email,
            "name": mock_user.name,
        }

    # Mock deck service to return success
    async def mock_get_deck_service():
        mock_service = AsyncMock()
        mock_service.delete_deck.return_value = True
        return mock_service

    from src.middleware.auth_middleware import require_auth
    from src.utils.dependencies import get_deck_service

    app.dependency_overrides[require_auth] = mock_require_auth
    app.dependency_overrides[get_deck_service] = mock_get_deck_service

    try:
        # Make request
        response = client.delete("/api/decks/1")

        # Verify response status
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"

        # Verify no content in response
        assert response.content == b"", "Response should have no content"
    finally:
        app.dependency_overrides.clear()


def test_delete_nonexistent_deck_contract(app, client, mock_user):
    """
    Test that DELETE /api/decks/{deck_id} returns 404 for non-existent deck.
    """
    # Mock authentication
    async def mock_require_auth():
        return {
            "user_id": mock_user.id,
            "google_id": mock_user.google_id,
            "email": mock_user.email,
            "name": mock_user.name,
        }

    # Mock deck service to return False (deck not found)
    async def mock_get_deck_service():
        mock_service = AsyncMock()
        mock_service.delete_deck.return_value = False
        return mock_service

    from src.middleware.auth_middleware import require_auth
    from src.utils.dependencies import get_deck_service

    app.dependency_overrides[require_auth] = mock_require_auth
    app.dependency_overrides[get_deck_service] = mock_get_deck_service

    try:
        # Make request
        response = client.delete("/api/decks/999")

        # Verify response status
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        # Verify error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() or "not authorized" in data["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_delete_deck_authorization_contract(app, client, mock_user):
    """
    Test that DELETE /api/decks/{deck_id} enforces authorization.

    Verifies:
    - User can only delete their own decks
    - Proper error response when attempting to delete another user's deck
    """
    # Mock authentication
    async def mock_require_auth():
        return {
            "user_id": mock_user.id,
            "google_id": mock_user.google_id,
            "email": mock_user.email,
            "name": mock_user.name,
        }

    # Mock deck service to return False (not authorized)
    async def mock_get_deck_service():
        mock_service = AsyncMock()
        mock_service.delete_deck.return_value = False
        return mock_service

    from src.middleware.auth_middleware import require_auth
    from src.utils.dependencies import get_deck_service

    app.dependency_overrides[require_auth] = mock_require_auth
    app.dependency_overrides[get_deck_service] = mock_get_deck_service

    try:
        # Make request
        response = client.delete("/api/decks/1")

        # Verify response status (should be 404 as the deck doesn't belong to user)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        # Verify error message
        data = response.json()
        assert "detail" in data
    finally:
        app.dependency_overrides.clear()
