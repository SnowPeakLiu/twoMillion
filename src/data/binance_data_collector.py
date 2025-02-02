"""
Binance data collector module for fetching market data.
No API key is required for basic market data collection.

This module provides a unified interface for collecting both real-time and historical
market data from Binance using REST API and WebSocket connections. It handles:
- Historical and real-time kline/candlestick data
- Market trades and order book data
- Exchange information and trading pair details
- Real-time market data streams
"""

from typing import Optional, Dict, Any, Union, Callable
from datetime import datetime
import pandas as pd
from .collectors import RestApiCollector, WebSocketCollector

class DataCollector:
    """Collects market data from Binance.
    
    This class provides a unified interface for collecting market data from Binance,
    combining both REST API and WebSocket functionality. It delegates the actual
    data collection to specialized collector classes.
    
    The collector supports two main types of data collection:
    1. REST API calls for historical and snapshot data
    2. WebSocket streams for real-time market data
    
    Example:
        >>> collector = DataCollector()
        >>> # Get historical kline data
        >>> df = collector.get_historical_klines('BTCUSDT', '1h', '2024-01-01')
        >>> # Start a real-time trade stream
        >>> collector.start_trade_stream('BTCUSDT', callback_function)
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the data collector.
        
        Args:
            data_dir: Directory to store downloaded data. If None, uses './data'
                     in the current working directory.
        """
        self._rest_api = RestApiCollector(data_dir)
        self._websocket = WebSocketCollector(data_dir)
    
    # REST API methods
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 500) -> pd.DataFrame:
        """Get kline/candlestick data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            limit: Number of records to get (max 1000)
            
        Returns:
            DataFrame with columns: [open_time, open, high, low, close, volume,
            close_time, quote_volume, trades, taker_buy_base, taker_buy_quote]
        """
        return self._rest_api.get_klines(symbol, interval, limit)
    
    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_date: Union[str, datetime],
        end_date: Optional[Union[str, datetime]] = None,
        save: bool = True
    ) -> pd.DataFrame:
        """Get historical kline data for a date range.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, etc.)
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime), defaults to current time
            save: Whether to save data to CSV file
            
        Returns:
            DataFrame with historical kline data in the same format as get_klines()
        """
        return self._rest_api.get_historical_klines(symbol, interval, start_date, end_date, save)
    
    def get_ticker_24h(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """Get 24-hour price change statistics.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT'). If None, gets all symbols.
            
        Returns:
            DataFrame with columns including price change, volume, and other statistics
            for the last 24 hours.
        """
        return self._rest_api.get_ticker_24h(symbol)
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            limit: Number of bids and asks (max 5000)
            
        Returns:
            Dictionary containing order book data with 'bids' and 'asks' lists
        """
        return self._rest_api.get_order_book(symbol, limit)
    
    def get_recent_trades(self, symbol: str, limit: int = 500) -> pd.DataFrame:
        """Get recent trades for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            limit: Number of trades to get (max 1000)
            
        Returns:
            DataFrame with columns: [id, price, qty, quoteQty, time, isBuyerMaker]
        """
        return self._rest_api.get_recent_trades(symbol, limit)
    
    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get exchange information.
        
        Args:
            symbol: Optional symbol to get specific trading rules
            
        Returns:
            Dictionary containing exchange information including trading rules,
            rate limits, and symbol-specific details if a symbol is provided
        """
        return self._rest_api.get_exchange_info(symbol)
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            
        Returns:
            Dictionary containing symbol information including base/quote assets,
            status, trading rules, filters, and permissions
            
        Raises:
            ValueError: If the symbol is not found
        """
        return self._rest_api.get_symbol_info(symbol)
    
    # WebSocket methods
    def start_kline_stream(self, symbol: str, interval: str, callback: Callable):
        """Start a kline/candlestick WebSocket stream.
        
        The callback function will receive real-time kline data in the format:
        {
            'e': 'kline',
            'E': event time,
            's': symbol,
            'k': {
                't': kline start time,
                'T': kline close time,
                's': symbol,
                'i': interval,
                'o': open price,
                'c': close price,
                'h': high price,
                'l': low price,
                'v': volume,
                'n': number of trades
            }
        }
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, etc.)
            callback: Function to handle incoming messages
        """
        return self._websocket.start_kline_stream(symbol, interval, callback)
    
    def start_trade_stream(self, symbol: str, callback: Callable):
        """Start a trade WebSocket stream.
        
        The callback function will receive real-time trade data in the format:
        {
            'e': 'trade',
            'E': event time,
            's': symbol,
            't': trade ID,
            'p': price,
            'q': quantity,
            'b': buyer order ID,
            'a': seller order ID,
            'T': trade time,
            'm': is buyer market maker
        }
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            callback: Function to handle incoming messages
        """
        return self._websocket.start_trade_stream(symbol, callback)
    
    def stop_streams(self):
        """Stop all active WebSocket streams.
        
        This method:
        1. Unsubscribes from all active streams
        2. Closes the WebSocket connection
        3. Cleans up resources
        """
        return self._websocket.stop_streams() 