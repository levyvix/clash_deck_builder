# backend/src/exceptions/handlers.py

"""FastAPI exception handlers for the Clash Royale Deck Builder application."""

import logging
from typing import Dict, Any

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from mysql.connector import Error as MySQLError

from . import (
    DatabaseError,
    DeckNotFoundError,
    DeckValidationError,
    SerializationError,
    DeckLimitExceededError,
    ClashAPIError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int, error_type: str, message: str, details: Dict[str, Any] = None
) -> JSONResponse:
    """Create a standardized error response."""
    content = {"error": {"type": error_type, "message": message}}

    if details:
        content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=content)


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Handle database-related errors."""
    logger.error(f"Database error: {exc.message}", exc_info=exc.original_error)

    return create_error_response(
        status_code=500,
        error_type="database_error",
        message="A database error occurred. Please try again later.",
        details={"original_message": exc.message} if exc.original_error else None,
    )


async def mysql_error_handler(request: Request, exc: MySQLError) -> JSONResponse:
    """Handle MySQL connector errors."""
    logger.error(f"MySQL error: {exc}", exc_info=exc)

    return create_error_response(
        status_code=500,
        error_type="database_error",
        message="A database connection error occurred. Please try again later.",
    )


async def deck_not_found_handler(request: Request, exc: DeckNotFoundError) -> JSONResponse:
    """Handle deck not found errors."""
    logger.warning(f"Deck not found: {exc}")

    return create_error_response(
        status_code=404,
        error_type="deck_not_found",
        message=str(exc),
        details={"deck_id": exc.deck_id, "user_id": exc.user_id},
    )


async def deck_validation_error_handler(request: Request, exc: DeckValidationError) -> JSONResponse:
    """Handle deck validation errors."""
    logger.warning(f"Deck validation error: {exc.message}")

    details = {}
    if exc.field:
        details["field"] = exc.field

    return create_error_response(
        status_code=400, error_type="validation_error", message=exc.message, details=details if details else None
    )


async def serialization_error_handler(request: Request, exc: SerializationError) -> JSONResponse:
    """Handle JSON serialization/deserialization errors."""
    logger.error(f"Serialization error: {exc.message}")

    details = {}
    if exc.data_type:
        details["data_type"] = exc.data_type

    return create_error_response(
        status_code=500,
        error_type="serialization_error",
        message="Failed to process data. Please check your input format.",
        details=details if details else None,
    )


async def deck_limit_exceeded_handler(request: Request, exc: DeckLimitExceededError) -> JSONResponse:
    """Handle deck limit exceeded errors."""
    logger.warning(f"Deck limit exceeded: {exc}")

    return create_error_response(
        status_code=400,
        error_type="deck_limit_exceeded",
        message=str(exc),
        details={"user_id": exc.user_id, "max_decks": exc.max_decks},
    )


async def clash_api_error_handler(request: Request, exc: ClashAPIError) -> JSONResponse:
    """Handle Clash Royale API errors."""
    logger.error(f"Clash API error: {exc.message}", exc_info=exc.original_error)

    # Map API errors to appropriate HTTP status codes
    if exc.status_code:
        if exc.status_code == 404:
            status_code = 404
            message = "Requested resource not found in Clash Royale API"
        elif exc.status_code == 429:
            status_code = 503
            message = "Clash Royale API rate limit exceeded. Please try again later."
        elif exc.status_code >= 500:
            status_code = 503
            message = "Clash Royale API is currently unavailable. Please try again later."
        else:
            status_code = 502
            message = "Error communicating with Clash Royale API"
    else:
        status_code = 503
        message = "Clash Royale API is currently unavailable. Please try again later."

    return create_error_response(
        status_code=status_code,
        error_type="external_api_error",
        message=message,
        details={"api_status_code": exc.status_code, "api_message": exc.message},
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle custom validation errors."""
    logger.warning(f"Validation error: {exc.message}")

    details = {}
    if exc.field:
        details["field"] = exc.field
    if exc.value is not None:
        details["value"] = exc.value

    return create_error_response(
        status_code=400, error_type="validation_error", message=exc.message, details=details if details else None
    )


async def pydantic_validation_error_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(f"Pydantic validation error: {exc}")

    # Extract validation error details
    errors = []
    for error in exc.errors():
        errors.append(
            {"field": ".".join(str(loc) for loc in error["loc"]), "message": error["msg"], "type": error["type"]}
        )

    return create_error_response(
        status_code=400,
        error_type="validation_error",
        message="Input validation failed",
        details={"validation_errors": errors},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")

    return create_error_response(status_code=exc.status_code, error_type="http_error", message=exc.detail)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=exc)

    return create_error_response(
        status_code=500, error_type="internal_error", message="An unexpected error occurred. Please try again later."
    )


# Exception handler mapping for FastAPI
EXCEPTION_HANDLERS = {
    DatabaseError: database_error_handler,
    MySQLError: mysql_error_handler,
    DeckNotFoundError: deck_not_found_handler,
    DeckValidationError: deck_validation_error_handler,
    SerializationError: serialization_error_handler,
    DeckLimitExceededError: deck_limit_exceeded_handler,
    ClashAPIError: clash_api_error_handler,
    ValidationError: validation_error_handler,
    PydanticValidationError: pydantic_validation_error_handler,
    HTTPException: http_exception_handler,
    Exception: generic_exception_handler,
}
