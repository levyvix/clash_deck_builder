# backend/src/api/auth.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from ..services.auth_service import AuthService
from ..services.user_service import UserService
from ..services.migration_service import MigrationService
from ..exceptions.auth_exceptions import AuthenticationError, TokenValidationError, GoogleOAuthError, UserNotFoundError

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
    """Extract and validate current user from JWT token."""
    auth_service = AuthService()
    user_service = UserService()

    try:
        user_info = auth_service.extract_user_from_token(credentials.credentials)
        user = user_service.get_user_by_id(user_info["user_id"])

        if not user:
            logger.warning(f"User {user_info['user_id']} no longer exists")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": user.id,
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "avatar": user.avatar,
        }

    except (TokenValidationError, UserNotFoundError) as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e), headers={"WWW-Authenticate": "Bearer"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/google", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def google_oauth_callback(request: GoogleAuthRequest) -> AuthResponse:
    """Handle Google OAuth callback and authenticate user."""
    auth_service = AuthService()
    user_service = UserService()
    migration_service = MigrationService()

    try:
        logger.info("Verifying Google ID token")
        google_user_info = auth_service.verify_google_token(request.id_token)

        logger.info(f"Processing user: {google_user_info['email']}")
        user = user_service.create_or_update_user(
            google_id=google_user_info["google_id"], email=google_user_info["email"], name=google_user_info["name"]
        )

        onboarding_result = migration_service.handle_user_onboarding(user, request.migration_data)
        tokens = auth_service.generate_jwt_tokens(user)

        logger.info(f"Successfully authenticated user: {user.email}")
        return AuthResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user={
                "id": user.id,
                "google_id": user.google_id,
                "email": user.email,
                "name": user.name,
                "avatar": user.avatar,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            },
            onboarding=onboarding_result,
        )

    except (GoogleOAuthError, AuthenticationError) as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during Google OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during authentication"
        )


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_access_token(request: RefreshTokenRequest) -> RefreshTokenResponse:
    """Refresh access token using refresh token."""
    auth_service = AuthService()

    try:
        logger.info("Processing token refresh request")
        new_tokens = auth_service.refresh_access_token(request.refresh_token)

        logger.info("Successfully refreshed access token")
        return RefreshTokenResponse(
            access_token=new_tokens["access_token"],
            token_type=new_tokens["token_type"],
            expires_in=new_tokens["expires_in"],
        )

    except (TokenValidationError, UserNotFoundError, AuthenticationError) as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during token refresh"
        )


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> LogoutResponse:
    """Logout user. Tokens are invalidated client-side in a stateless JWT system."""
    logger.info(f"User logout: {current_user['email']}")
    return LogoutResponse(success=True, message="Successfully logged out")


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current authenticated user information."""
    logger.debug(f"Fetching user info for: {current_user['email']}")
    return {
        "id": current_user["user_id"],
        "google_id": current_user["google_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "avatar": current_user["avatar"],
    }


@router.get("/onboarding", status_code=status.HTTP_200_OK)
async def get_onboarding_status(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get onboarding status for the current user."""
    user_service = UserService()
    migration_service = MigrationService()

    logger.debug(f"Fetching onboarding status for: {current_user['email']}")
    user = user_service.get_user_by_id(current_user["user_id"])

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return migration_service.get_onboarding_status(user)
