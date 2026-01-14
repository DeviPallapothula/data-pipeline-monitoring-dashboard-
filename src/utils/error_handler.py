"""
Error Handler Module

This module provides centralized error handling utilities for the application.
It includes custom exception classes and error response formatters.
"""

from flask import jsonify
import logging
import traceback

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass


class ValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


def handle_error(error, status_code=500, message=None):
    """
    Handle errors and return appropriate JSON response.
    
    Args:
        error: The exception that occurred
        status_code: HTTP status code (default: 500)
        message: Custom error message (optional)
    
    Returns:
        JSON response with error details
    """
    error_message = message or str(error)
    error_type = type(error).__name__
    
    # Log the error with full traceback
    logger.error(
        f"Error occurred: {error_type} - {error_message}",
        exc_info=True
    )
    
    response = {
        'error': True,
        'message': error_message,
        'type': error_type,
        'status_code': status_code
    }
    
    # In development, include traceback
    import os
    if os.getenv('FLASK_ENV') == 'development':
        response['traceback'] = traceback.format_exc()
    
    return jsonify(response), status_code


def validate_request_data(data, required_fields):
    """
    Validate that required fields are present in request data.
    
    Args:
        data: Dictionary of request data
        required_fields: List of required field names
    
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )


def safe_database_operation(operation, error_message="Database operation failed"):
    """
    Safely execute a database operation with error handling.
    
    Args:
        operation: Function to execute
        error_message: Custom error message if operation fails
    
    Returns:
        Result of the operation
    
    Raises:
        DatabaseError: If operation fails
    """
    try:
        return operation()
    except Exception as e:
        logger.error(f"{error_message}: {str(e)}", exc_info=True)
        raise DatabaseError(f"{error_message}: {str(e)}") from e
