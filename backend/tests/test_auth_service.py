# backend/tests/test_auth_service.py

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import jwt

from src.services.auth_service import AuthService
from src.models.user import User
from src.exceptions.auth_exceptions import (
    GoogleOAuthError,
    TokenValidationError,
    AuthenticationError
)
from src.utils.config import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.google_client_id = "test-client-id"
    settings.jwt_secret = "test-secret-key-that-is-long-enough-for-validation"
    settings.jwt_algorithm = "HS256"
    settings.jwt_access_token_expire_minutes = 15
    settings.jwt_refresh_token_expire_days = 30
    return settings


@pytest.fixture
def auth_service(mock_settings):
    """Create AuthService instance with mock settings."""
    return AuthService(mock_settings)


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id="test-user-id",
        google_id="test-google-id",
        email="test@example.com",
        name="Test User",
        avatar=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class TestAuthService:
    """Test cases for AuthService."""
    
    def test_generate_jwt_tokens(self, auth_service, sample_user):
        """Test JWT token generation."""
        tokens = auth_service.generate_jwt_tokens(sample_user)
        
        assert 'access_token' in tokens
        assert 'refresh_token' in tokens
        assert 'token_type' in tokens
        assert 'expires_in' in tokens
        assert tokens['token_type'] == 'bearer'
        assert tokens['expires_in'] == 15 * 60  # 15 minutes in seconds
    
    def test_verify_jwt_token_valid_access_token(self, auth_service, sample_user):
        """Test verification of valid access token."""
        tokens = auth_service.generate_jwt_tokens(sample_user)
        access_token = tokens['access_token']
        
        payload = auth_service.verify_jwt_token(access_token, 'access')
        
        assert payload['user_id'] == sample_user.id
        assert payload['google_id'] == sample_user.google_id
        assert payload['email'] == sample_user.email
        assert payload['type'] == 'access'
    
    def test_verify_jwt_token_valid_refresh_token(self, auth_service, sample_user):
        """Test verification of valid refresh token."""
        tokens = auth_service.generate_jwt_tokens(sample_user)
        refresh_token = tokens['refresh_token']
        
        payload = auth_service.verify_jwt_token(refresh_token, 'refresh')
        
        assert payload['user_id'] == sample_user.id
        assert payload['google_id'] == sample_user.google_id
        assert payload['type'] == 'refresh'
    
    def test_verify_jwt_token_wrong_type(self, auth_service, sample_user):
        """Test verification fails when token type doesn't match."""
        tokens = auth_service.generate_jwt_tokens(sample_user)
        access_token = tokens['access_token']
        
        with pytest.raises(TokenValidationError, match="Invalid token type"):
            auth_service.verify_jwt_token(access_token, 'refresh')
    
    def test_verify_jwt_token_invalid_token(self, auth_service):
        """Test verification fails with invalid token."""
        with pytest.raises(TokenValidationError, match="Invalid token"):
            auth_service.verify_jwt_token("invalid-token", 'access')
    
    def test_extract_user_from_token(self, auth_service, sample_user):
        """Test extracting user information from token."""
        tokens = auth_service.generate_jwt_tokens(sample_user)
        access_token = tokens['access_token']
        
        user_info = auth_service.extract_user_from_token(access_token)
        
        assert user_info['user_id'] == sample_user.id
        assert user_info['google_id'] == sample_user.google_id
        assert user_info['email'] == sample_user.email
    
    @patch('src.services.auth_service.id_token.verify_oauth2_token')
    def test_verify_google_token_success(self, mock_verify, auth_service):
        """Test successful Google token verification."""
        mock_verify.return_value = {
            'iss': 'accounts.google.com',
            'sub': 'google-user-id',
            'email': 'user@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/photo.jpg',
            'email_verified': True
        }
        
        result = auth_service.verify_google_token("valid-token")
        
        assert result['google_id'] == 'google-user-id'
        assert result['email'] == 'user@example.com'
        assert result['name'] == 'Test User'
        assert result['email_verified'] is True
    
    @patch('src.services.auth_service.id_token.verify_oauth2_token')
    def test_verify_google_token_invalid_issuer(self, mock_verify, auth_service):
        """Test Google token verification fails with invalid issuer."""
        mock_verify.return_value = {
            'iss': 'invalid-issuer.com',
            'sub': 'google-user-id',
            'email': 'user@example.com',
            'email_verified': True
        }
        
        with pytest.raises(GoogleOAuthError, match="Invalid token issuer"):
            auth_service.verify_google_token("invalid-token")
    
    @patch('src.services.auth_service.id_token.verify_oauth2_token')
    def test_verify_google_token_unverified_email(self, mock_verify, auth_service):
        """Test Google token verification fails with unverified email."""
        mock_verify.return_value = {
            'iss': 'accounts.google.com',
            'sub': 'google-user-id',
            'email': 'user@example.com',
            'email_verified': False
        }
        
        with pytest.raises(GoogleOAuthError, match="Email not verified"):
            auth_service.verify_google_token("invalid-token")


if __name__ == "__main__":
    pytest.main([__file__])