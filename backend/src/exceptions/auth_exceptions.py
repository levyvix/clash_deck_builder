# backend/src/exceptions/auth_exceptions.py

"""Authentication-related exceptions for the application."""


class AuthenticationError(Exception):
    """Base exception for authentication-related errors."""
    pass


class TokenValidationError(AuthenticationError):
    """Exception raised when JWT token validation fails."""
    pass


class GoogleOAuthError(AuthenticationError):
    """Exception raised when Google OAuth verification fails."""
    pass


class UserNotFoundError(AuthenticationError):
    """Exception raised when a user is not found in the database."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when provided credentials are invalid."""
    pass


class TokenExpiredError(TokenValidationError):
    """Exception raised when a token has expired."""
    pass


class InsufficientPermissionsError(AuthenticationError):
    """Exception raised when user lacks required permissions."""
    pass