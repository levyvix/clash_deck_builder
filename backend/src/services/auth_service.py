# backend/src/services/auth_service.py

import logging
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError

from ..utils.config import get_settings
from ..models.user import User
from ..exceptions.auth_exceptions import (
    AuthenticationError,
    TokenValidationError,
    GoogleOAuthError,
    UserNotFoundError
)

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling Google OAuth authentication and JWT token management."""
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self.jwt_secret = self.settings.jwt_secret
        self.jwt_algorithm = self.settings.jwt_algorithm
        self.access_token_expire_minutes = self.settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = self.settings.jwt_refresh_token_expire_days
    
    def verify_google_token(self, id_token_str: str) -> Dict[str, Any]:
        """
        Verify Google ID token and extract user information.
        
        Args:
            id_token_str: Google ID token string
            
        Returns:
            Dict containing user information from Google
            
        Raises:
            GoogleOAuthError: If token verification fails
        """
        try:
            # Verify the token with Google
            id_info = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                self.settings.google_client_id
            )
            
            # Verify the issuer
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise GoogleOAuthError("Invalid token issuer")
            
            # Extract user information
            user_info = {
                'google_id': id_info['sub'],
                'email': id_info['email'],
                'name': id_info.get('name', ''),
                'picture': id_info.get('picture', ''),
                'email_verified': id_info.get('email_verified', False)
            }
            
            # Validate required fields
            if not user_info['google_id'] or not user_info['email']:
                raise GoogleOAuthError("Missing required user information from Google token")
            
            if not user_info['email_verified']:
                raise GoogleOAuthError("Email not verified with Google")
            
            logger.info(f"Successfully verified Google token for user: {user_info['email']}")
            return user_info
            
        except GoogleAuthError as e:
            logger.error(f"Google token verification failed: {e}")
            raise GoogleOAuthError(f"Invalid Google token: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Google token verification: {e}")
            raise GoogleOAuthError(f"Token verification failed: {e}")
    
    def generate_jwt_tokens(self, user: User) -> Dict[str, str]:
        """
        Generate access and refresh JWT tokens for a user.
        
        Args:
            user: User object
            
        Returns:
            Dict containing access_token and refresh_token
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Generate access token
            access_payload = {
                'user_id': user.id,
                'google_id': user.google_id,
                'email': user.email,
                'type': 'access',
                'iat': now,
                'exp': now + timedelta(minutes=self.access_token_expire_minutes)
            }
            
            access_token = jwt.encode(
                access_payload, 
                self.jwt_secret, 
                algorithm=self.jwt_algorithm
            )
            
            # Generate refresh token
            refresh_payload = {
                'user_id': user.id,
                'google_id': user.google_id,
                'type': 'refresh',
                'iat': now,
                'exp': now + timedelta(days=self.refresh_token_expire_days)
            }
            
            refresh_token = jwt.encode(
                refresh_payload, 
                self.jwt_secret, 
                algorithm=self.jwt_algorithm
            )
            
            logger.info(f"Generated JWT tokens for user: {user.email}")
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'expires_in': self.access_token_expire_minutes * 60
            }
            
        except Exception as e:
            logger.error(f"Failed to generate JWT tokens for user {user.id}: {e}")
            raise AuthenticationError(f"Token generation failed: {e}")
    
    def verify_jwt_token(self, token: str, token_type: str = 'access') -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            token_type: Type of token ('access' or 'refresh')
            
        Returns:
            Dict containing token payload
            
        Raises:
            TokenValidationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm]
            )
            
            # Verify token type
            if payload.get('type') != token_type:
                raise TokenValidationError(f"Invalid token type. Expected {token_type}")
            
            # Verify required fields
            required_fields = ['user_id', 'google_id', 'iat', 'exp']
            for field in required_fields:
                if field not in payload:
                    raise TokenValidationError(f"Missing required field: {field}")
            
            # Check expiration
            exp_timestamp = payload['exp']
            if isinstance(exp_timestamp, datetime):
                exp_time = exp_timestamp
            else:
                exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            
            if exp_time < datetime.now(timezone.utc):
                raise TokenValidationError("Token has expired")
            
            logger.debug(f"Successfully verified {token_type} token for user: {payload['user_id']}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise TokenValidationError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise TokenValidationError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            raise TokenValidationError(f"Token verification failed: {e}")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict containing new access_token
            
        Raises:
            TokenValidationError: If refresh token is invalid
            UserNotFoundError: If user no longer exists
        """
        try:
            # Verify refresh token
            payload = self.verify_jwt_token(refresh_token, 'refresh')
            
            # Get user from database to ensure they still exist
            from .user_service import UserService
            user_service = UserService()
            user = user_service.get_user_by_id(payload['user_id'])
            
            if not user:
                raise UserNotFoundError("User no longer exists")
            
            # Generate new access token
            now = datetime.now(timezone.utc)
            access_payload = {
                'user_id': user.id,
                'google_id': user.google_id,
                'email': user.email,
                'type': 'access',
                'iat': now,
                'exp': now + timedelta(minutes=self.access_token_expire_minutes)
            }
            
            access_token = jwt.encode(
                access_payload, 
                self.jwt_secret, 
                algorithm=self.jwt_algorithm
            )
            
            logger.info(f"Refreshed access token for user: {user.email}")
            
            return {
                'access_token': access_token,
                'token_type': 'bearer',
                'expires_in': self.access_token_expire_minutes * 60
            }
            
        except (TokenValidationError, UserNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise AuthenticationError(f"Token refresh failed: {e}")
    
    def extract_user_from_token(self, token: str) -> Dict[str, Any]:
        """
        Extract user information from access token.
        
        Args:
            token: JWT access token
            
        Returns:
            Dict containing user information
            
        Raises:
            TokenValidationError: If token is invalid
        """
        payload = self.verify_jwt_token(token, 'access')
        
        return {
            'user_id': payload['user_id'],
            'google_id': payload['google_id'],
            'email': payload.get('email')
        }