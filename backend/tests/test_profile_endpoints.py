# backend/tests/test_profile_endpoints.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from src.main import app
from src.models.user import User
from src.exceptions.auth_exceptions import UserNotFoundError
from src.utils.database import DatabaseError
from src.api.auth import get_current_user

# Mock user data
MOCK_USER = User(
    id="test-user-id",
    google_id="google-123",
    email="test@example.com",
    name="Test User",
    avatar="knight",
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc)
)

MOCK_CURRENT_USER = {
    'user_id': 'test-user-id',
    'google_id': 'google-123',
    'email': 'test@example.com',
    'name': 'Test User',
    'avatar': 'knight'
}

# Override the dependency for testing
def override_get_current_user():
    return MOCK_CURRENT_USER

client = TestClient(app)

class TestProfileEndpoints:
    """Test cases for profile management endpoints."""
    
    def setup_method(self):
        """Setup method to override dependencies before each test."""
        app.dependency_overrides[get_current_user] = override_get_current_user
    
    def teardown_method(self):
        """Teardown method to clear dependency overrides after each test."""
        app.dependency_overrides.clear()
    
    @patch('src.api.profile.UserService')
    def test_get_profile_success(self, mock_user_service):
        """Test successful profile retrieval."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service_instance.get_user_by_id.return_value = MOCK_USER
        mock_user_service.return_value = mock_service_instance
        
        # Make request
        response = client.get("/api/profile")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == MOCK_USER.id
        assert data["email"] == MOCK_USER.email
        assert data["name"] == MOCK_USER.name
        assert data["avatar"] == MOCK_USER.avatar
        assert "created_at" in data
        assert "updated_at" in data
        
        # Verify service calls
        mock_service_instance.get_user_by_id.assert_called_once_with('test-user-id')
    
    @patch('src.api.profile.UserService')
    def test_get_profile_user_not_found(self, mock_user_service):
        """Test profile retrieval when user not found."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service_instance.get_user_by_id.return_value = None
        mock_user_service.return_value = mock_service_instance
        
        # Make request
        response = client.get("/api/profile")
        
        # Assertions
        assert response.status_code == 404
        assert "User profile not found" in response.json()["error"]["message"]
    
    @patch('src.api.profile.UserService')
    def test_get_profile_database_error(self, mock_user_service):
        """Test profile retrieval with database error."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service_instance.get_user_by_id.side_effect = DatabaseError("Database connection failed")
        mock_user_service.return_value = mock_service_instance
        
        # Make request
        response = client.get("/api/profile")
        
        # Assertions
        assert response.status_code == 500
        assert "Failed to retrieve profile" in response.json()["error"]["message"]
    
    @patch('src.api.profile.UserService')
    def test_update_profile_name_success(self, mock_user_service):
        """Test successful profile name update."""
        # Setup mocks
        updated_user = User(
            id=MOCK_USER.id,
            google_id=MOCK_USER.google_id,
            email=MOCK_USER.email,
            name="Updated Name",
            avatar=MOCK_USER.avatar,
            created_at=MOCK_USER.created_at,
            updated_at=datetime.now(timezone.utc)
        )
        mock_service_instance = Mock()
        mock_service_instance.update_user.return_value = updated_user
        mock_user_service.return_value = mock_service_instance
        
        # Make request
        response = client.put("/api/profile", json={"name": "Updated Name"})
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["id"] == MOCK_USER.id
        
        # Verify service calls
        mock_service_instance.update_user.assert_called_once()
        call_args = mock_service_instance.update_user.call_args
        assert call_args[0][0] == 'test-user-id'  # user_id
        assert call_args[0][1].name == "Updated Name"  # UserUpdate object
    
    @patch('src.api.profile.UserService')
    def test_update_profile_avatar_success(self, mock_user_service):
        """Test successful profile avatar update."""
        # Setup mocks
        updated_user = User(
            id=MOCK_USER.id,
            google_id=MOCK_USER.google_id,
            email=MOCK_USER.email,
            name=MOCK_USER.name,
            avatar="wizard",
            created_at=MOCK_USER.created_at,
            updated_at=datetime.now(timezone.utc)
        )
        mock_service_instance = Mock()
        mock_service_instance.update_user.return_value = updated_user
        mock_user_service.return_value = mock_service_instance
        
        # Make request
        response = client.put("/api/profile", json={"avatar": "wizard"})
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["avatar"] == "wizard"
        assert data["name"] == MOCK_USER.name  # Name unchanged
    
    @patch('src.api.profile.UserService')
    def test_update_profile_both_fields_success(self, mock_user_service):
        """Test successful profile update with both name and avatar."""
        # Setup mocks
        updated_user = User(
            id=MOCK_USER.id,
            google_id=MOCK_USER.google_id,
            email=MOCK_USER.email,
            name="New Name",
            avatar="archer",
            created_at=MOCK_USER.created_at,
            updated_at=datetime.now(timezone.utc)
        )
        mock_service_instance = Mock()
        mock_service_instance.update_user.return_value = updated_user
        mock_user_service.return_value = mock_service_instance
        
        # Make request
        response = client.put("/api/profile", json={"name": "New Name", "avatar": "archer"})
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["avatar"] == "archer"
    
    def test_update_profile_no_fields(self):
        """Test profile update with no fields provided."""
        # Make request
        response = client.put("/api/profile", json={})
        
        # Assertions
        assert response.status_code == 400
        assert "At least one field" in response.json()["error"]["message"]
    
    def test_update_profile_invalid_name_special_chars(self):
        """Test profile update with invalid name containing special characters."""
        # Make request
        response = client.put("/api/profile", json={"name": "Test@User!"})
        
        # Assertions
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert any("Name can only contain letters, numbers, and spaces" in str(error) for error in error_detail)
    
    def test_update_profile_invalid_name_too_long(self):
        """Test profile update with name that's too long."""
        # Make request with 51 character name
        long_name = "a" * 51
        response = client.put("/api/profile", json={"name": long_name})
        
        # Assertions
        assert response.status_code == 422  # Validation error
    
    def test_update_profile_empty_name(self):
        """Test profile update with empty name."""
        # Make request
        response = client.put("/api/profile", json={"name": "   "})
        
        # Assertions
        assert response.status_code == 422  # Validation error
    
    @patch('src.api.profile.UserService')
    def test_update_profile_user_not_found(self, mock_user_service):
        """Test profile update when user not found."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service_instance.update_user.side_effect = UserNotFoundError("User not found")
        mock_user_service.return_value = mock_service_instance
        
        # Make request
        response = client.put("/api/profile", json={"name": "New Name"})
        
        # Assertions
        assert response.status_code == 404
        assert "User profile not found" in response.json()["error"]["message"]
    
    @patch('src.api.profile.UserService')
    def test_update_profile_database_error(self, mock_user_service):
        """Test profile update with database error."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service_instance.update_user.side_effect = DatabaseError("Database error")
        mock_user_service.return_value = mock_service_instance
        
        # Make request
        response = client.put("/api/profile", json={"name": "New Name"})
        
        # Assertions
        assert response.status_code == 500
        assert "Failed to update profile" in response.json()["error"]["message"]


class TestProfileEndpointsAuthentication:
    """Test authentication requirements for profile endpoints."""
    
    def test_profile_endpoints_require_authentication(self):
        """Test that profile endpoints require authentication."""
        # Test GET without auth
        response = client.get("/api/profile")
        assert response.status_code == 403  # No Authorization header
        
        # Test PUT without auth
        response = client.put("/api/profile", json={"name": "Test"})
        assert response.status_code == 403  # No Authorization header