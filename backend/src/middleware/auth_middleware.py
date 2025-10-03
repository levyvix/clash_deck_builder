# backend/src/middleware/auth_middleware.py

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging

from ..services.auth_service import AuthService
from ..services.user_service import UserService
from ..exceptions.auth_exceptions import (
    TokenValidationError,
    UserNotFoundError
)

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer()

class AuthMiddleware:
    """Middleware class for JWT authentication."""
    
    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService()
    
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """
        Extract and validate current user from JWT token.
        
        This method can be used as a FastAPI dependency to protect routes
        that require authentication.
        
        Args:
            credentials: HTTP Bearer token credentials
            
        Returns:
            Dict containing user information
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        try:
            # Extract user info from token
            user_info = self.auth_service.extract_user_from_token(credentials.credentials)
            
            # Verify user still exists in database
            user = self.user_service.get_user_by_id(user_info['user_id'])
            
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
            logger.error(f"Unexpected error in authentication middleware: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    async def get_optional_user(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
    ) -> Optional[Dict[str, Any]]:
        """
        Extract user from JWT token if present, but don't require authentication.
        
        This method can be used for routes that work for both authenticated
        and anonymous users, but provide different functionality based on auth status.
        
        Args:
            credentials: Optional HTTP Bearer token credentials
            
        Returns:
            Dict containing user information if authenticated, None otherwise
        """
        if not credentials:
            return None
        
        try:
            return await self.get_current_user(credentials)
        except HTTPException:
            # If token is invalid, treat as anonymous user
            return None

# Global middleware instance
auth_middleware = AuthMiddleware()

# Convenience functions for use as dependencies
async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency function that requires authentication.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: Dict = Depends(require_auth)):
            return {"user_id": user["user_id"]}
    """
    return await auth_middleware.get_current_user(credentials)

async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """
    Dependency function for optional authentication.
    
    Usage:
        @router.get("/maybe-protected")
        async def maybe_protected_route(user: Optional[Dict] = Depends(optional_auth)):
            if user:
                return {"message": f"Hello {user['name']}"}
            else:
                return {"message": "Hello anonymous user"}
    """
    return await auth_middleware.get_optional_user(credentials)