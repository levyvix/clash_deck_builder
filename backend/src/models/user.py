# backend/src/models/user.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import uuid
import re


class User(BaseModel):
    """User model for Google OAuth authenticated users."""
    
    id: str
    google_id: str
    email: str
    name: str
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Model for creating a new user."""
    
    google_id: str = Field(..., min_length=1, description="Google user ID")
    email: str = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User display name")
    avatar: Optional[str] = Field(None, max_length=50, description="Avatar card ID")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate display name contains only alphanumeric characters and spaces."""
        if not re.match(r'^[a-zA-Z0-9\s]+$', v.strip()):
            raise ValueError('Name can only contain letters, numbers, and spaces')
        return v.strip()
    
    def generate_id(self) -> str:
        """Generate a unique UUID for the user."""
        return str(uuid.uuid4())


class UserUpdate(BaseModel):
    """Model for updating user information."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User display name")
    avatar: Optional[str] = Field(None, max_length=50, description="Avatar card ID")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate display name contains only alphanumeric characters and spaces."""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9\s]+$', v.strip()):
                raise ValueError('Name can only contain letters, numbers, and spaces')
            return v.strip()
        return v


class UserResponse(BaseModel):
    """Model for user API responses."""
    
    id: str
    email: str
    name: str
    avatar: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True