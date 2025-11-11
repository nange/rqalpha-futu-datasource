"""
RQAlpha Futu DataSource - A datasource plugin for RQAlpha that integrates with Futu API.

This package provides a datasource implementation for RQAlpha that connects to Futu's
market data API for real-time and historical market data.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main functionality to make it easily accessible
from .datasource import FutuDataSource

__all__ = ["FutuDataSource"]