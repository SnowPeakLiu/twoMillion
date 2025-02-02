"""WebSocket collector module."""

import json
import time
import threading
import websocket
from typing import Optional, Callable, Set
from .base import BaseCollector

class WebSocketCollector(BaseCollector):
    """Collector for Binance WebSocket data."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the collector.
        
        Args:
            data_dir: Directory to store downloaded data
        """
        super().__init__(data_dir)
        self._ws = None
        self._ws_thread = None
        self._user_callback = None
        self._stream_ids: Set[str] = set()
        
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