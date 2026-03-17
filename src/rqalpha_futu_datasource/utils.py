"""
Utility functions for Futu DataSource.

This module contains utility functions used by the Futu DataSource implementation,
including data conversion, validation, and helper functions.
"""

from typing import Tuple
import datetime
from rqalpha.const import EXCHANGE
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


def rq_to_futu_code(order_book_id: str) -> Tuple[str, str]:
    if not order_book_id or not isinstance(order_book_id, str):
        raise ValueError(ERROR_INVALID_SYMBOL)
    parts = order_book_id.split(".")
    if len(parts) != 2:
        raise ValueError(ERROR_INVALID_SYMBOL)
    code, exch = parts[0], parts[1].upper()
    if exch == EXCHANGE.XSHG:
        return "SH", code
    if exch == EXCHANGE.XSHE:
        return "SZ", code
    if exch == EXCHANGE.XHKG:
        return "HK", code
    if exch in (EXCHANGE.XNAS, EXCHANGE.XNYS):
        return "US", code
    raise ValueError(ERROR_INVALID_SYMBOL)


def dt_to_int(dt: datetime.datetime, daily: bool) -> int:
    return int(dt.strftime("%Y%m%d%H%M%S"))


def get_market_dir(order_book_id: str) -> str:
    """
    Get the market directory name based on order_book_id.
    """
    parts = order_book_id.split(".")
    if len(parts) != 2:
        raise ValueError(ERROR_INVALID_SYMBOL)
    exch = parts[1].upper()
    if exch in (EXCHANGE.XSHG, EXCHANGE.XSHE):
        return "CN"
    if exch == EXCHANGE.XHKG:
        return "HK"
    if exch in (EXCHANGE.XNAS, EXCHANGE.XNYS):
        return "US"
    raise ValueError(f"Unknown exchange in order_book_id: {order_book_id}")


def futu_path(data_root: str, order_book_id: str, frequency: str) -> str:
    from .constants import SUPPORTED_FREQUENCIES
    import os

    freq = frequency.lower()
    if freq not in SUPPORTED_FREQUENCIES:
        raise ValueError("unsupported frequency")
    file_freq = "1mo" if freq == "1mon" else freq
    market_dir = get_market_dir(order_book_id)
    return os.path.join(data_root, market_dir, order_book_id, f"{file_freq}.csv")
