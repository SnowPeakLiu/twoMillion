"""
Binance data collector module for fetching market data.
No API key is required for basic market data collection.
"""

from typing import Optional, List, Dict, Any, Union, Callable
from datetime import datetime, timedelta
import logging
import os
import json
from pathlib import Path
import pandas as pd
from binance.spot import Spot
import websocket
import threading
import time

class DataCollector:
    """Collects market data from Binance."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the data collector.
        
        Args:
            data_dir: Directory to store downloaded data
        """
        self.client = Spot()
        self.logger = logging.getLogger(__name__)
        self._ws = None
        self._user_callback = None
        self._stream_ids = set()  # Track active stream IDs
        self.data_dir = data_dir if data_dir else os.path.join(os.getcwd(), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 500) -> pd.DataFrame:
        """Get kline/candlestick data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            limit: Number of records to get (max 1000)
            
        Returns:
            DataFrame with columns: [open_time, open, high, low, close, volume, close_time, 
            quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]
        """
        try:
            klines = self.client.klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 
                             'quote_volume', 'trades', 'taker_buy_base', 
                             'taker_buy_quote']
            df[numeric_columns] = df[numeric_columns].astype(float)
            
            # Convert timestamps to datetime
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching klines for {symbol}: {str(e)}")
            raise
    
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
            interval: Kline interval
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime), defaults to now
            save: Whether to save data to file
            
        Returns:
            DataFrame with historical kline data
        """
        try:
            # Convert dates to datetime if they're strings
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            elif end_date is None:
                end_date = datetime.now()
                
            # Convert to milliseconds timestamp
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)
            
            # Get historical klines
            klines = self.client.klines(
                symbol=symbol,
                interval=interval,
                startTime=start_ms,
                endTime=end_ms
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            numeric_columns = ['open', 'high', 'low', 'close', 'volume',
                             'quote_volume', 'trades', 'taker_buy_base',
                             'taker_buy_quote']
            df[numeric_columns] = df[numeric_columns].astype(float)
            
            # Save to file if requested
            if save and not df.empty:
                self._save_to_csv(df, f"{symbol.lower()}_{interval}_historical.csv")
                
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting historical klines: {str(e)}")
            raise
    
    def get_ticker_24h(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """Get 24-hour price change statistics.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT'). If None, gets all symbols.
            
        Returns:
            DataFrame with 24h statistics for one or all symbols
        """
        try:
            if symbol:
                data = [self.client.ticker_24hr(symbol=symbol)]
            else:
                data = self.client.ticker_24hr()
                
            df = pd.DataFrame(data)
            
            # Convert numeric columns
            numeric_columns = [
                'priceChange', 'priceChangePercent', 'weightedAvgPrice',
                'prevClosePrice', 'lastPrice', 'lastQty', 'bidPrice', 'bidQty',
                'askPrice', 'askQty', 'openPrice', 'highPrice', 'lowPrice',
                'volume', 'quoteVolume'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col])
                    
            # Convert timestamps
            if 'openTime' in df.columns:
                df['openTime'] = pd.to_datetime(df['openTime'], unit='ms')
            if 'closeTime' in df.columns:
                df['closeTime'] = pd.to_datetime(df['closeTime'], unit='ms')
                
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching 24h ticker data: {str(e)}")
            raise
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            limit: Number of bids and asks (max 5000)
            
        Returns:
            Dictionary containing order book data
        """
        try:
            return self.client.depth(symbol=symbol, limit=limit)
        except Exception as e:
            self.logger.error(f"Error fetching order book for {symbol}: {str(e)}")
            raise
    
    def get_recent_trades(self, symbol: str, limit: int = 500) -> pd.DataFrame:
        """Get recent trades for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            limit: Number of trades to get (max 1000)
            
        Returns:
            DataFrame containing recent trades
        """
        try:
            trades = self.client.trades(symbol=symbol, limit=limit)
            df = pd.DataFrame(trades)
            
            # Convert numeric columns
            numeric_columns = ['price', 'qty', 'quoteQty']
            df[numeric_columns] = df[numeric_columns].astype(float)
            
            # Convert timestamp
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching recent trades for {symbol}: {str(e)}")
            raise
    
    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get exchange information.
        
        Args:
            symbol: Optional symbol to get specific trading rules
            
        Returns:
            Dictionary containing exchange information
        """
        try:
            if symbol:
                return self.client.exchange_info(symbol=symbol)
            return self.client.exchange_info()
        except Exception as e:
            self.logger.error(f"Error fetching exchange info: {str(e)}")
            raise
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            
        Returns:
            Dictionary containing symbol information
        """
        try:
            info = self.client.exchange_info()
            for symbol_info in info['symbols']:
                if symbol_info['symbol'] == symbol:
                    return symbol_info
            raise ValueError(f"Symbol {symbol} not found")
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {str(e)}")
            raise
    
    def _init_websocket(self):
        """Initialize WebSocket client if not already initialized."""
        if self._ws is None:
            # Initialize WebSocket client
            self._ws = websocket.WebSocketApp(
                "wss://stream.binance.com:9443/stream",
                on_message=self._handle_ws_message,
                on_error=self._handle_ws_error,
                on_close=self._handle_ws_close,
                on_open=self._handle_ws_open
            )
            
            # Start WebSocket connection in a separate thread
            self._ws_thread = threading.Thread(target=self._ws.run_forever)
            self._ws_thread.daemon = True
            self._ws_thread.start()
            
            # Wait for connection to establish
            time.sleep(2)
            
    def _handle_ws_message(self, ws, message):
        """Handle incoming WebSocket messages."""
        try:
            # Parse message
            data = json.loads(message)
            
            # Skip subscription responses
            if 'result' in data:
                return
                
            # Extract stream data
            stream_data = data.get('data')
            if stream_data and self._user_callback:
                self._user_callback(stream_data)
                
        except Exception as e:
            self.logger.error(f"Error in WebSocket message handler: {str(e)}")
            
    def _handle_ws_error(self, ws, error):
        """Handle WebSocket errors."""
        self.logger.error(f"WebSocket error: {str(error)}")
        
    def _handle_ws_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close."""
        self.logger.info("WebSocket connection closed")
        
    def _handle_ws_open(self, ws):
        """Handle WebSocket connection open."""
        self.logger.info("WebSocket connection established")
            
    def start_kline_stream(self, symbol: str, interval: str, callback: Callable):
        """Start a kline/candlestick WebSocket stream.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            interval: Kline interval
            callback: Function to handle incoming messages
        """
        try:
            # Stop any existing streams
            self.stop_streams()
            
            self._user_callback = callback
            self._init_websocket()
            
            # Create stream name and subscribe
            symbol = symbol.lower()
            stream_name = f"{symbol}@kline_{interval}"
            self._stream_ids.add(stream_name)
            
            # Subscribe using the SUBSCRIBE method
            subscribe_request = {
                "method": "SUBSCRIBE",
                "params": [stream_name],
                "id": 1
            }
            self._ws.send(json.dumps(subscribe_request))
            
            # Wait for subscription to complete
            time.sleep(2)
            
            self.logger.info(f"Started kline stream for {symbol}")
        except Exception as e:
            self.logger.error(f"Error starting kline stream: {str(e)}")
            raise
            
    def start_trade_stream(self, symbol: str, callback: Callable):
        """Start a trade WebSocket stream.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            callback: Function to handle incoming messages
        """
        try:
            # Stop any existing streams
            self.stop_streams()
            
            self._user_callback = callback
            self._init_websocket()
            
            # Create stream name and subscribe
            symbol = symbol.lower()
            stream_name = f"{symbol}@aggTrade"
            self._stream_ids.add(stream_name)
            
            # Subscribe using the SUBSCRIBE method
            subscribe_request = {
                "method": "SUBSCRIBE",
                "params": [stream_name],
                "id": 2
            }
            self._ws.send(json.dumps(subscribe_request))
            
            # Wait for subscription to complete
            time.sleep(2)
            
            self.logger.info(f"Started trade stream for {symbol}")
        except Exception as e:
            self.logger.error(f"Error starting trade stream: {str(e)}")
            raise
            
    def stop_streams(self):
        """Stop all WebSocket streams."""
        try:
            if self._ws:
                # Unsubscribe from all active streams
                for stream_name in self._stream_ids:
                    unsubscribe_request = {
                        "method": "UNSUBSCRIBE",
                        "params": [stream_name],
                        "id": 3
                    }
                    self._ws.send(json.dumps(unsubscribe_request))
                    time.sleep(0.5)  # Give time between unsubscribes
                
                # Close WebSocket connection
                self._ws.close()
                self._ws = None
                self._ws_thread = None
                self._stream_ids.clear()
                self._user_callback = None
                
                self.logger.info("Stopped all WebSocket streams")
                time.sleep(1)  # Wait for cleanup
        except Exception as e:
            self.logger.error(f"Error stopping streams: {str(e)}")
            raise
    
    def _save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Name of the file
        """
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False)
        self.logger.info(f"Data saved to {filepath}")
    
    def _save_to_json(self, data: Dict[str, Any], filename: str):
        """Save dictionary to JSON file.
        
        Args:
            data: Dictionary to save
            filename: Name of the file
        """
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Data saved to {filepath}") 