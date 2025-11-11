"""
Constants for Futu DataSource.

This module contains constants used throughout the Futu DataSource implementation,
including error codes, configuration keys, and API constants.
"""

# Futu API related constants
FUTU_HOST = "127.0.0.1"
FUTU_PORT = 11111

# Market data types
MARKET_HK = "HK"  # Hong Kong market
MARKET_US = "US"  # US market
MARKET_SH = "SH"  # Shanghai market
MARKET_SZ = "SZ"  # Shenzhen market

# Data frequency constants
FREQUENCY_DAILY = "1d"
FREQUENCY_HOURLY = "1h"
FREQUENCY_MINUTE = "1m"
FREQUENCY_TICK = "tick"

# Error codes
ERROR_CONNECTION_FAILED = "CONNECTION_FAILED"
ERROR_API_TIMEOUT = "API_TIMEOUT"
ERROR_INVALID_SYMBOL = "INVALID_SYMBOL"

# Configuration keys
CONFIG_HOST = "host"
CONFIG_PORT = "port"
CONFIG_API_KEY = "api_key"
CONFIG_MARKET = "market"
