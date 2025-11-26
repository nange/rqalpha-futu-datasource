"""
Utility functions for Futu DataSource.

This module contains utility functions used by the Futu DataSource implementation,
including data conversion, validation, and helper functions.
"""

from typing import Any, Dict, Tuple
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
        "datetime": bar_data.get("datetime", datetime.datetime.now()),
    }


def rq_to_futu_code(order_book_id: str) -> Tuple[str, str]:
    if not order_book_id or not isinstance(order_book_id, str):
        raise ValueError(ERROR_INVALID_SYMBOL)
    parts = order_book_id.split(".")
    if len(parts) != 2:
        raise ValueError(ERROR_INVALID_SYMBOL)
    code, exch = parts[0], parts[1].upper()
    if exch == "XSHG":
        return "SH", code
    if exch == "XSHE":
        return "SZ", code
    if exch == "XHKG":
        return "HK", code
    if exch in ("XNAS", "XNYS"):
        return "US", code
    raise ValueError(ERROR_INVALID_SYMBOL)


def dt_to_int(dt: datetime.datetime, daily: bool) -> int:
    return int(dt.strftime("%Y%m%d%H%M%S"))


def futu_path(data_root: str, market: str, symbol: str, frequency: str) -> str:
    from .constants import SUPPORTED_FREQUENCIES

    freq = frequency.lower()
    if freq not in SUPPORTED_FREQUENCIES:
        raise ValueError("unsupported frequency")
    file_freq = "1mo" if freq == "1mon" else freq
    return f"{data_root}/{market}/{symbol}/{file_freq}.csv"
