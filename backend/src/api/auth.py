# backend/src/api/auth.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from ..services.auth_service import AuthService
from ..services.user_service import UserService
from ..services.migration_service import MigrationService
from ..exceptions.auth_exceptions import (
    AuthenticationError,
    TokenValidationError,
    GoogleOAuthError,
    UserNotFoundError
)

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication."""
    id_token: str = Field(..., description="Google ID token from OAuth flow")
    migration_data: Optional[Dict[str, Any]] = Field(None, description="Optional anonymous data to migrate")

class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
    onboarding: Optional[Dict[str, Any]] = None

class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="Valid refresh token")

class RefreshTokenResponse(BaseModel):
    """Response model for token refresh."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LogoutResponse(BaseModel):
    """Response model for logout."""
    success: bool
    message: str

# Dependency for getting current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to extract and validate current user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        auth_service = AuthService()
        user_info = auth_service.extract_user_from_token(credentials.credentials)
        
        # Verify user still exists in database
        user_service = UserService()
        user = user_service.get_user_by_id(user_info['user_id'])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return {
            'user_id': user.id,
            'google_id': user.google_id,
            'email': user.email,
            'name': user.name,
            'avatar': user.avatar
        }
        
    except TokenValidationError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except UserNotFoundError as e:
        logger.warning(f"User not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/google", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def google_oauth_callback(request: GoogleAuthRequest) -> AuthResponse:
    """
    Handle Google OAuth callback and authenticate user.
    
    This endpoint receives a Google ID token, verifies it with Google,
    creates or updates the user in the database, and returns JWT tokens.
    
    Args:
        request: Google authentication request containing ID token
        
    Returns:
        AuthResponse containing JWT tokens and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        auth_service = AuthService()
        user_service = UserService()
        migration_service = MigrationService()
        
        # Verify Google ID token and extract user info
        logger.info("Verifying Google ID token")
        google_user_info = auth_service.verify_google_token(request.id_token)
        
        # Create or update user in database
        logger.info(f"Processing user: {google_user_info['email']}")
        user = user_service.create_or_update_user(
            google_id=google_user_info['google_id'],
            email=google_user_info['email'],
            name=google_user_info['name']
        )
        
        # Handle onboarding and migration
        logger.info(f"Processing onboarding for user: {user.email}")
        onboarding_result = migration_service.handle_user_onboarding(user, request.migration_data)
        
        # Generate JWT tokens
        logger.info(f"Generating tokens for user: {user.email}")
        tokens = auth_service.generate_jwt_tokens(user)
        
        # Prepare response
        response = AuthResponse(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_type=tokens['token_type'],
            expires_in=tokens['expires_in'],
            user={
                'id': user.id,
                'google_id': user.google_id,
                'email': user.email,
                'name': user.name,
                'avatar': user.avatar,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            },
            onboarding=onboarding_result
        )
        
        logger.info(f"Successfully authenticated user: {user.email}")
        return response
        
    except GoogleOAuthError as e:
        logger.warning(f"Google OAuth verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {e}"
        )
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during Google OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_access_token(request: RefreshTokenRequest) -> RefreshTokenResponse:
    """
    Refresh access token using refresh token.
    
    This endpoint accepts a valid refresh token and returns a new access token.
    The refresh token itself is not renewed and remains valid until expiration.
    
    Args:
        request: Refresh token request
        
    Returns:
        RefreshTokenResponse containing new access token
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    try:
        auth_service = AuthService()
        
        logger.info("Processing token refresh request")
        new_tokens = auth_service.refresh_access_token(request.refresh_token)
        
        response = RefreshTokenResponse(
            access_token=new_tokens['access_token'],
            token_type=new_tokens['token_type'],
            expires_in=new_tokens['expires_in']
        )
        
        logger.info("Successfully refreshed access token")
        return response
        
    except TokenValidationError as e:
        logger.warning(f"Token refresh failed - invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {e}"
        )
    except UserNotFoundError as e:
        logger.warning(f"Token refresh failed - user not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )
    except AuthenticationError as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> LogoutResponse:
    """
    Logout user and invalidate session.
    
    This endpoint logs out the current user. Since we're using stateless JWT tokens,
    the actual token invalidation happens on the client side by removing the tokens.
    This endpoint serves as a confirmation and can be used for logging purposes.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        LogoutResponse confirming successful logout
    """
    try:
        logger.info(f"User logout: {current_user['email']}")
        
        # In a stateless JWT system, we don't need to invalidate tokens server-side
        # The client should remove the tokens from storage
        # This endpoint serves as confirmation and for audit logging
        
        response = LogoutResponse(
            success=True,
            message="Successfully logged out"
        )
        
        logger.info(f"Successfully logged out user: {current_user['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )

# Additional endpoint for getting current user info (useful for frontend)
@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    This endpoint returns the current user's information based on their JWT token.
    Useful for frontend applications to get user details after authentication.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        Dict containing current user information
    """
    try:
        logger.debug(f"Fetching user info for: {current_user['email']}")
        
        # Return user information (already validated by dependency)
        return {
            'id': current_user['user_id'],
            'google_id': current_user['google_id'],
            'email': current_user['email'],
            'name': current_user['name'],
            'avatar': current_user['avatar']
        }
        
    except Exception as e:
        logger.error(f"Unexpected error fetching user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching user information"
        )

@router.get("/onboarding", status_code=status.HTTP_200_OK)
async def get_onboarding_status(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get onboarding status for the current user.
    
    This endpoint returns the user's onboarding progress and next steps.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        Dict containing onboarding status and steps
    """
    try:
        logger.debug(f"Fetching onboarding status for: {current_user['email']}")
        
        # Get user from database
        user_service = UserService()
        user = user_service.get_user_by_id(current_user['user_id'])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get onboarding status
        migration_service = MigrationService()
        onboarding_status = migration_service.get_onboarding_status(user)
        
        return onboarding_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching onboarding status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching onboarding status"
        )