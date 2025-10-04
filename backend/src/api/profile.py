# backend/src/api/profile.py

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
import logging
import re

from ..services.user_service import UserService
from ..models.user import UserUpdate
from ..exceptions.auth_exceptions import UserNotFoundError
from ..utils.database import DatabaseError
from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class ProfileUpdateRequest(BaseModel):
    """Request model for profile updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Display name")
    avatar: Optional[str] = Field(None, max_length=50, description="Avatar card ID")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate display name contains only alphanumeric characters and spaces."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Name cannot be empty')
            if not re.match(r'^[a-zA-Z0-9\s]+$', v):
                raise ValueError('Name can only contain letters, numbers, and spaces')
            if len(v) > 50:
                raise ValueError('Name cannot exceed 50 characters')
        return v

class ProfileResponse(BaseModel):
    """Response model for profile endpoints."""
    id: str
    googleId: str
    email: str
    name: str
    avatar: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

@router.get("", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)) -> ProfileResponse:
    """
    Get current user profile information.
    
    This endpoint returns the authenticated user's profile information.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        ProfileResponse containing user profile information
        
    Raises:
        HTTPException: If user not found or database error
    """
    try:
        user_service = UserService()
        
        logger.debug(f"Fetching profile for user: {current_user['email']}")
        
        # Get fresh user data from database
        user = user_service.get_user_by_id(current_user['user_id'])
        
        if not user:
            logger.error(f"User not found in database: {current_user['user_id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Return user data in the format expected by frontend
        user_data = {
            "id": user.id,
            "googleId": user.google_id,
            "email": user.email,
            "name": user.name,
            "avatar": user.avatar,
            "createdAt": user.created_at.isoformat() if user.created_at else None,
            "updatedAt": user.updated_at.isoformat() if user.updated_at else None
        }
        
        logger.info(f"Successfully retrieved profile for user: {user.email}")
        return user_data
        
    except HTTPException:
        raise
    except UserNotFoundError as e:
        logger.warning(f"User not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    except DatabaseError as e:
        logger.error(f"Database error retrieving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ProfileResponse:
    """
    Update user profile information.
    
    This endpoint allows users to update their display name and avatar.
    Name validation ensures only alphanumeric characters and spaces are allowed.
    
    Args:
        profile_data: Profile update request containing name and/or avatar
        current_user: Current authenticated user from JWT token
        
    Returns:
        ProfileResponse containing updated user profile information
        
    Raises:
        HTTPException: If validation fails, user not found, or database error
    """
    try:
        user_service = UserService()
        
        logger.info(f"Updating profile for user: {current_user['email']}")
        
        # Validate that at least one field is provided for update
        if profile_data.name is None and profile_data.avatar is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field (name or avatar) must be provided for update"
            )
        
        # Create UserUpdate object
        user_update = UserUpdate(
            name=profile_data.name,
            avatar=profile_data.avatar
        )
        
        # Update user in database
        updated_user = user_service.update_user(current_user['user_id'], user_update)
        
        # Return user data in the format expected by frontend
        user_data = {
            "id": updated_user.id,
            "googleId": updated_user.google_id,
            "email": updated_user.email,
            "name": updated_user.name,
            "avatar": updated_user.avatar,
            "createdAt": updated_user.created_at.isoformat() if updated_user.created_at else None,
            "updatedAt": updated_user.updated_at.isoformat() if updated_user.updated_at else None
        }
        
        logger.info(f"Successfully updated profile for user: {updated_user.email}")
        return user_data
        
    except HTTPException:
        raise
    except UserNotFoundError as e:
        logger.warning(f"User not found for profile update: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    except DatabaseError as e:
        logger.error(f"Database error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    except ValueError as e:
        logger.warning(f"Validation error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )