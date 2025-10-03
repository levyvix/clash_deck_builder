# backend/src/exceptions/__init__.py

"""Custom exceptions for the Clash Royale Deck Builder application."""

from mysql.connector import Error as MySQLError


class DatabaseError(Exception):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class DeckNotFoundError(Exception):
    """Raised when a deck is not found."""
    
    def __init__(self, deck_id: int, user_id: str = None):
        self.deck_id = deck_id
        self.user_id = user_id
        if user_id:
            message = f"Deck with ID {deck_id} not found for user {user_id}"
        else:
            message = f"Deck with ID {deck_id} not found"
        super().__init__(message)


class DeckValidationError(Exception):
    """Raised when deck validation fails."""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class SerializationError(Exception):
    """Raised when JSON serialization/deserialization fails."""
    
    def __init__(self, message: str, data_type: str = None):
        self.message = message
        self.data_type = data_type
        super().__init__(self.message)


class DeckLimitExceededError(Exception):
    """Raised when user tries to create more than the maximum allowed decks."""
    
    def __init__(self, user_id: str, max_decks: int = 20):
        self.user_id = user_id
        self.max_decks = max_decks
        message = f"User {user_id} has reached the maximum limit of {max_decks} decks"
        super().__init__(message)


class ClashAPIError(Exception):
    """Raised when Clash Royale API calls fail."""
    
    def __init__(self, message: str, status_code: int = None, original_error: Exception = None):
        self.message = message
        self.status_code = status_code
        self.original_error = original_error
        super().__init__(self.message)


class ValidationError(Exception):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, value: any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)