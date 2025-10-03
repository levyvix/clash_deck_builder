# backend/tests/test_user_service.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from src.services.user_service import UserService
from src.models.user import User, UserCreate, UserUpdate
from src.exceptions.auth_exceptions import UserNotFoundError
from src.utils.database import DatabaseError


@pytest.fixture
def user_service():
    """Create UserService instance for testing."""
    return UserService()


@pytest.fixture
def sample_user_create():
    """Create sample UserCreate data."""
    return UserCreate(
        google_id="test-google-id",
        email="test@example.com",
        name="Test User",
        avatar=None
    )


@pytest.fixture
def sample_user():
    """Create sample User data."""
    return User(
        id="test-user-id",
        google_id="test-google-id",
        email="test@example.com",
        name="Test User",
        avatar=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class TestUserService:
    """Test cases for UserService."""
    
    @patch('src.services.user_service.get_db_session')
    def test_get_user_by_id_found(self, mock_get_session, user_service, sample_user):
        """Test getting user by ID when user exists."""
        # Mock database session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock database result
        mock_session.fetchone.return_value = {
            'id': sample_user.id,
            'google_id': sample_user.google_id,
            'email': sample_user.email,
            'name': sample_user.name,
            'avatar': sample_user.avatar,
            'created_at': sample_user.created_at,
            'updated_at': sample_user.updated_at
        }
        
        result = user_service.get_user_by_id(sample_user.id)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.email == sample_user.email
        assert result.name == sample_user.name
    
    @patch('src.services.user_service.get_db_session')
    def test_get_user_by_id_not_found(self, mock_get_session, user_service):
        """Test getting user by ID when user doesn't exist."""
        # Mock database session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock no result
        mock_session.fetchone.return_value = None
        
        result = user_service.get_user_by_id("non-existent-id")
        
        assert result is None
    
    @patch('src.services.user_service.get_db_session')
    def test_get_user_by_google_id_found(self, mock_get_session, user_service, sample_user):
        """Test getting user by Google ID when user exists."""
        # Mock database session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock database result
        mock_session.fetchone.return_value = {
            'id': sample_user.id,
            'google_id': sample_user.google_id,
            'email': sample_user.email,
            'name': sample_user.name,
            'avatar': sample_user.avatar,
            'created_at': sample_user.created_at,
            'updated_at': sample_user.updated_at
        }
        
        result = user_service.get_user_by_google_id(sample_user.google_id)
        
        assert result is not None
        assert result.google_id == sample_user.google_id
        assert result.email == sample_user.email
    
    @patch('src.services.user_service.get_db_session')
    def test_get_user_by_email_found(self, mock_get_session, user_service, sample_user):
        """Test getting user by email when user exists."""
        # Mock database session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock database result
        mock_session.fetchone.return_value = {
            'id': sample_user.id,
            'google_id': sample_user.google_id,
            'email': sample_user.email,
            'name': sample_user.name,
            'avatar': sample_user.avatar,
            'created_at': sample_user.created_at,
            'updated_at': sample_user.updated_at
        }
        
        result = user_service.get_user_by_email(sample_user.email)
        
        assert result is not None
        assert result.email == sample_user.email
        assert result.google_id == sample_user.google_id
    
    @patch('src.services.user_service.UserService.get_user_by_id')
    @patch('src.services.user_service.get_db_session')
    def test_create_user_success(self, mock_get_session, mock_get_user, user_service, sample_user_create, sample_user):
        """Test successful user creation."""
        # Mock database session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock get_user_by_id to return the created user
        mock_get_user.return_value = sample_user
        
        result = user_service.create_user(sample_user_create)
        
        assert result is not None
        assert result.email == sample_user_create.email
        assert result.google_id == sample_user_create.google_id
        
        # Verify database insert was called
        mock_session.execute.assert_called_once()
    
    @patch('src.services.user_service.UserService.get_user_by_id')
    @patch('src.services.user_service.get_db_session')
    def test_update_user_success(self, mock_get_session, mock_get_user, user_service, sample_user):
        """Test successful user update."""
        # Mock database session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.rowcount = 1
        
        # Mock get_user_by_id calls
        updated_user = User(
            id=sample_user.id,
            google_id=sample_user.google_id,
            email=sample_user.email,
            name="Updated Name",
            avatar="new-avatar",
            created_at=sample_user.created_at,
            updated_at=datetime.now(timezone.utc)
        )
        mock_get_user.side_effect = [sample_user, updated_user]  # First call for existence check, second for result
        
        update_data = UserUpdate(name="Updated Name", avatar="new-avatar")
        result = user_service.update_user(sample_user.id, update_data)
        
        assert result is not None
        assert result.name == "Updated Name"
        assert result.avatar == "new-avatar"
        
        # Verify database update was called
        mock_session.execute.assert_called_once()
    
    @patch('src.services.user_service.UserService.get_user_by_id')
    def test_update_user_not_found(self, mock_get_user, user_service):
        """Test updating non-existent user."""
        mock_get_user.return_value = None
        
        update_data = UserUpdate(name="Updated Name")
        
        with pytest.raises(UserNotFoundError):
            user_service.update_user("non-existent-id", update_data)
    
    @patch('src.services.user_service.UserService.get_user_by_google_id')
    @patch('src.services.user_service.UserService.create_user')
    def test_get_or_create_user_existing(self, mock_create, mock_get_by_google_id, user_service, sample_user):
        """Test get_or_create_user when user already exists."""
        mock_get_by_google_id.return_value = sample_user
        
        google_user_info = {
            'google_id': sample_user.google_id,
            'email': sample_user.email,
            'name': sample_user.name
        }
        
        result = user_service.get_or_create_user(google_user_info)
        
        assert result == sample_user
        mock_create.assert_not_called()  # Should not create new user
    
    @patch('src.services.user_service.UserService.get_user_by_google_id')
    @patch('src.services.user_service.UserService.create_user')
    def test_get_or_create_user_new(self, mock_create, mock_get_by_google_id, user_service, sample_user):
        """Test get_or_create_user when user doesn't exist."""
        mock_get_by_google_id.return_value = None
        mock_create.return_value = sample_user
        
        google_user_info = {
            'google_id': sample_user.google_id,
            'email': sample_user.email,
            'name': sample_user.name
        }
        
        result = user_service.get_or_create_user(google_user_info)
        
        assert result == sample_user
        mock_create.assert_called_once()  # Should create new user


if __name__ == "__main__":
    pytest.main([__file__])