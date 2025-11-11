"""
Utility functions for Futu DataSource.

This module contains utility functions used by the Futu DataSource implementation,
including data conversion, validation, and helper functions.
"""

from typing import Any, Dict, Optional
import datetime
from .constants import ERROR_INVALID_SYMBOL


def validate_symbol(symbol: str) -> bool:
    """
    Validate if a symbol is in correct format for Futu API.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Basic validation - can be enhanced based on Futu's symbol format
    return len(symbol) >= 2 and symbol.isalnum()


def convert_futu_bar_to_rqalpha(bar_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Futu API bar data to RQAlpha format.
    
    Args:
        bar_data: Raw bar data from Futu API
        
    Returns:
        Dict: Bar data in RQAlpha format
    """
    # This is a placeholder implementation
    # Actual conversion would depend on Futu API response format
    return {
        "open": bar_data.get("open_price", 0.0),
        "high": bar_data.get("high_price", 0.0),
        "low": bar_data.get("low_price", 0.0),
        "close": bar_data.get("close_price", 0.0),
        "volume": bar_data.get("volume", 0),
        "datetime": bar_data.get("datetime", datetime.datetime.now())
    }


def handle_futu_error(error: Exception) -> str:
    """
    Handle Futu API errors and convert to appropriate error codes.
    
    Args:
        error: Exception from Futu API
        
    Returns:
        str: Error code
    """
    error_msg = str(error).lower()
    
    if "connection" in error_msg or "connect" in error_msg:
        return "CONNECTION_FAILED"
    elif "timeout" in error_msg:
        return "API_TIMEOUT"
    elif "invalid" in error_msg and "symbol" in error_msg:
        return ERROR_INVALID_SYMBOL
    else:
        return "UNKNOWN_ERROR"