"""
Binance Data Collector Module
"""
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd
from binance import Client, ThreadedWebsocketManager
from binance.exceptions import BinanceAPIException

from ..config import settings
from ..utils.helpers import safe_request
from ..utils.logger import get_logger
from .base_collector import BaseCollector

log = get_logger(__name__)

class BinanceCollector(BaseCollector):
    """Binance Data Collector for Cryptocurrency Trading"""
    
    # Valid time intervals
    VALID_INTERVALS = [
        Client.KLINE_INTERVAL_1MINUTE,
        Client.KLINE_INTERVAL_3MINUTE,
        Client.KLINE_INTERVAL_5MINUTE,
        Client.KLINE_INTERVAL_15MINUTE,
        Client.KLINE_INTERVAL_30MINUTE,
        Client.KLINE_INTERVAL_1HOUR,
        Client.KLINE_INTERVAL_2HOUR,
        Client.KLINE_INTERVAL_4HOUR,
        Client.KLINE_INTERVAL_6HOUR,
        Client.KLINE_INTERVAL_8HOUR,
        Client.KLINE_INTERVAL_12HOUR,
        Client.KLINE_INTERVAL_1DAY,
        Client.KLINE_INTERVAL_3DAY,
        Client.KLINE_INTERVAL_1WEEK,
        Client.KLINE_INTERVAL_1MONTH
    ]
    
    def __init__(self):
        """Initialize Binance client"""
        super().__init__()
        try:
            self.client = Client(
                settings.api.binance_api_key,
                settings.api.binance_api_secret
            )
            self.ws_manager = ThreadedWebsocketManager(
                api_key=settings.api.binance_api_key,
                api_secret=settings.api.binance_api_secret
            )
            log.info("Binance client initialized successfully")
        except Exception as e:
            self._handle_error(e, "Failed to initialize Binance client")
    
    def fetch_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[Union[int, datetime]] = None,
        end_time: Optional[Union[int, datetime]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Fetch historical kline data
        
        Args:
            symbol: Trading pair
            interval: Kline interval
            start_time: Start time
            end_time: End time
            limit: Data limit
            
        Returns:
            pd.DataFrame: Historical data
        """
        if not self._validate_symbol(symbol):
            raise ValueError(f"Invalid trading pair: {symbol}")
        if not self._validate_interval(interval, self.VALID_INTERVALS):
            raise ValueError(f"Invalid interval: {interval}")
        
        try:
            # Format timestamps
            start_ts = self._format_timestamp(start_time)
            end_ts = self._format_timestamp(end_time)
            
            # Get kline data
            klines = safe_request(
                self.client.get_historical_klines,
                symbol=symbol,
                interval=interval,
                start_str=start_ts,
                end_str=end_ts,
                limit=limit
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(
                klines,
                columns=[
                    'timestamp', 'open', 'high', 'low', 'close',
                    'volume', 'close_time', 'quote_volume',
                    'trades', 'taker_buy_base', 'taker_buy_quote',
                    'ignore'
                ]
            )
            
            # Convert data types
            numeric_columns = [
                'open', 'high', 'low', 'close', 'volume',
                'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote'
            ]
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            log.info(
                f"Successfully fetched {len(df)} records "
                f"for {symbol} {interval}"
            )
            return df
            
        except BinanceAPIException as e:
            self._handle_error(e, f"Failed to fetch historical data for {symbol}")
        except Exception as e:
            self._handle_error(e, "Failed to process historical data")
    
    def fetch_realtime_data(
        self,
        symbol: str,
        callback: callable
    ) -> None:
        """Fetch realtime kline data
        
        Args:
            symbol: Trading pair
            callback: Callback function for handling realtime data
        """
        if not self._validate_symbol(symbol):
            raise ValueError(f"Invalid trading pair: {symbol}")
        
        try:
            self.ws_manager.start()
            self.ws_manager.start_kline_socket(
                symbol=symbol,
                callback=callback
            )
            log.info(f"Started realtime data subscription for {symbol}")
            
        except Exception as e:
            self._handle_error(e, f"Failed to subscribe to realtime data for {symbol}")
    
    def fetch_ticker(self, symbol: str) -> Dict:
        """Fetch 24-hour ticker data
        
        Args:
            symbol: Trading pair
            
        Returns:
            Dict: Ticker data
        """
        if not self._validate_symbol(symbol):
            raise ValueError(f"Invalid trading pair: {symbol}")
        
        try:
            ticker = safe_request(
                self.client.get_ticker,
                symbol=symbol
            )
            log.info(f"Successfully fetched ticker data for {symbol}")
            return ticker
            
        except Exception as e:
            self._handle_error(e, f"Failed to fetch ticker data for {symbol}")
    
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
        if not self._validate_symbol(symbol):
            raise ValueError(f"Invalid trading pair: {symbol}")
        
        try:
            depth = safe_request(
                self.client.get_order_book,
                symbol=symbol,
                limit=limit
            )
            log.info(f"Successfully fetched order book data for {symbol}")
            return depth
            
        except Exception as e:
            self._handle_error(e, f"Failed to fetch order book data for {symbol}")
    
    def close(self):
        """Close WebSocket connection"""
        try:
            if hasattr(self, 'ws_manager'):
                self.ws_manager.stop()
                log.info("WebSocket connection closed")
        except Exception as e:
            log.error(f"Failed to close WebSocket connection: {str(e)}")

# Usage example
if __name__ == "__main__":
    collector = BinanceCollector()
    
    # Fetch 1-hour kline data for BTC/USDT
    df = collector.fetch_historical_data(
        symbol="BTCUSDT",
        interval=Client.KLINE_INTERVAL_1HOUR,
        limit=100
    )
    print(df.head())
    
    # Fetch realtime data
    def handle_message(msg):
        """Handle WebSocket message"""
        print(f"Received realtime data: {msg}")
    
    collector.fetch_realtime_data(
        symbol="BTCUSDT",
        callback=handle_message
    )
    
    # Fetch ticker data
    ticker = collector.fetch_ticker("BTCUSDT")
    print(f"24-hour ticker: {ticker}")
    
    # Fetch order book
    depth = collector.fetch_order_book("BTCUSDT", limit=5)
    print(f"Order book: {depth}")
    
    # Close connection
    collector.close() 