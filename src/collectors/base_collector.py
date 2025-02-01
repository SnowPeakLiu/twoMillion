"""
Base Data Collector Module for Cryptocurrency Trading
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

from ..utils.logger import get_logger

log = get_logger(__name__)

class BaseCollector(ABC):
    """Base Data Collector Class"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        
    @abstractmethod
    def fetch_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[Union[int, datetime]] = None,
        end_time: Optional[Union[int, datetime]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Fetch historical market data
        
        Args:
            symbol: Trading pair
            interval: Kline interval
            start_time: Start time
            end_time: End time
            limit: Data limit
            
        Returns:
            pd.DataFrame: Historical market data
        """
        pass
    
    @abstractmethod
    def fetch_realtime_data(
        self,
        symbol: str,
        callback: callable
    ) -> None:
        """Fetch realtime market data
        
        Args:
            symbol: Trading pair
            callback: Callback function for handling realtime data
        """
        pass
    
    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Dict:
        """Fetch 24-hour ticker data
        
        Args:
            symbol: Trading pair
            
        Returns:
            Dict: Ticker data
        """
        pass
    
    @abstractmethod
    def fetch_order_book(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> Dict:
        """Fetch order book data
        
        Args:
            symbol: Trading pair
            limit: Depth limit
            
        Returns:
            Dict: Order book data
        """
        pass
    
    def _validate_symbol(self, symbol: str) -> bool:
        """Validate trading pair format
        
        Args:
            symbol: Trading pair to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(symbol, str):
            return False
        if len(symbol) < 2:
            return False
        return True
    
    def _validate_interval(
        self,
        interval: str,
        valid_intervals: List[str]
    ) -> bool:
        """Validate time interval
        
        Args:
            interval: Time interval to validate
            valid_intervals: List of valid intervals
            
        Returns:
            bool: True if valid, False otherwise
        """
        return interval in valid_intervals
    
    def _format_timestamp(
        self,
        timestamp: Optional[Union[int, datetime]]
    ) -> Optional[str]:
        """Format timestamp for API requests
        
        Args:
            timestamp: Timestamp to format
            
        Returns:
            Optional[str]: Formatted timestamp string or None
        """
        if timestamp is None:
            return None
        if isinstance(timestamp, datetime):
            return str(int(timestamp.timestamp() * 1000))
        return str(timestamp)
    
    def _handle_error(self, error: Exception, message: str) -> None:
        """Handle and log errors
        
        Args:
            error: Exception object
            message: Error message
        """
        log.error(f"{message}: {str(error)}")
        raise type(error)(f"{message}: {str(error)}")
    
    def close(self):
        """Close any open connections"""
        pass 