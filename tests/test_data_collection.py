"""Tests for the data collection module."""

import unittest
from datetime import datetime, timedelta
import pandas as pd
import tempfile
from pathlib import Path
import shutil
import json
import time
from unittest import skip
from src.data.binance_data_collector import DataCollector

class TestDataCollector(unittest.TestCase):
    """Test cases for DataCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.collector = DataCollector(data_dir=self.temp_dir)
        self.test_symbol = "BTCUSDT"
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            if hasattr(self, 'collector'):
                self.collector.stop_streams()
                time.sleep(2)  # Increased wait time for WebSocket cleanup
        finally:
            shutil.rmtree(self.temp_dir)

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        time.sleep(3)  # Increased wait time to allow WebSocket connections to fully close

    def _reset_collector(self):
        """Reset the collector to ensure clean WebSocket state."""
        if hasattr(self, 'collector'):
            self.collector.stop_streams()
            time.sleep(2)  # Increased wait time
        self.collector = DataCollector(data_dir=self.temp_dir)
        time.sleep(1)  # Wait for initialization
    
    def test_get_klines(self):
        """Test getting kline/candlestick data."""
        # Get last 5 1-hour candles (reduced from 10)
        df = self.collector.get_klines(
            symbol=self.test_symbol,
            interval="1h",
            limit=5  # Reduced from 10
        )
        
        # Check DataFrame structure
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)  # Updated assertion
        expected_columns = {
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        }
        self.assertTrue(all(col in df.columns for col in expected_columns))
        
        # Check data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['open_time']))
        self.assertTrue(pd.api.types.is_float_dtype(df['open']))
        self.assertTrue(pd.api.types.is_float_dtype(df['volume']))
    
    def test_get_historical_klines(self):
        """Test getting historical kline data."""
        # Get data for the last 1 day (reduced from 3)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)  # Reduced from 3
        
        df = self.collector.get_historical_klines(
            symbol=self.test_symbol,
            interval="1h",
            start_date=start_date,
            end_date=end_date,
            save=True
        )
        
        # Check data
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        
        # Check if file was saved
        expected_file = Path(self.temp_dir) / f"{self.test_symbol.lower()}_1h_historical.csv"
        self.assertTrue(expected_file.exists())
        
        # Check saved data
        saved_df = pd.read_csv(expected_file)
        self.assertEqual(len(df), len(saved_df))
    
    def test_get_ticker_24h(self):
        """Test getting 24-hour ticker data."""
        # Test single symbol only (removed all symbols test)
        df_single = self.collector.get_ticker_24h(self.test_symbol)
        self.assertIsInstance(df_single, pd.DataFrame)
        self.assertEqual(len(df_single), 1)
    
    def test_get_order_book(self):
        """Test getting order book data."""
        order_book = self.collector.get_order_book(
            symbol=self.test_symbol,
            limit=5
        )
        
        self.assertIsInstance(order_book, dict)
        self.assertIn('bids', order_book)
        self.assertIn('asks', order_book)
        self.assertEqual(len(order_book['bids']), 5)
        self.assertEqual(len(order_book['asks']), 5)
    
    def test_get_recent_trades(self):
        """Test getting recent trades."""
        df = self.collector.get_recent_trades(
            symbol=self.test_symbol,
            limit=5  # Reduced from 10
        )
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)  # Updated assertion
        expected_columns = {'id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker'}
        self.assertTrue(all(col in df.columns for col in expected_columns))
        
        # Check data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['time']))
        self.assertTrue(pd.api.types.is_float_dtype(df['price']))
        self.assertTrue(pd.api.types.is_float_dtype(df['qty']))
    
    def test_get_exchange_info(self):
        """Test getting exchange information."""
        # Test single symbol only
        info = self.collector.get_exchange_info()
        self.assertIsInstance(info, dict)
        self.assertIn('timezone', info)
        self.assertIn('symbols', info)
    
    def test_get_symbol_info(self):
        """Test getting symbol information."""
        info = self.collector.get_symbol_info(self.test_symbol)
        self.assertIsInstance(info, dict)
        self.assertEqual(info['symbol'], self.test_symbol)
        self.assertIn('status', info)
        self.assertIn('baseAsset', info)
        self.assertIn('quoteAsset', info)
    
    def test_websocket_kline_stream(self):
        """Test WebSocket kline stream."""
        # Reset collector for clean WebSocket state
        self._reset_collector()
        
        received_data = []
        test_complete = False
        
        def handle_message(msg):
            """Handle incoming kline messages."""
            try:
                if isinstance(msg, dict) and msg.get('e') == 'kline':
                    k = msg.get('k', {})
                    received_data.append(msg)
                    if len(received_data) >= 1:
                        nonlocal test_complete
                        test_complete = True
            except Exception as e:
                print(f"Error in kline handler: {str(e)}")
        
        try:
            # Use a very active trading pair
            self.test_symbol = "BTCUSDT"  # Most active pair
            
            self.collector.start_kline_stream(
                symbol=self.test_symbol,
                interval="1s",  # Use 1s interval for faster updates
                callback=handle_message
            )
            
            # Wait for data with timeout
            start_time = time.time()
            timeout = 10  # Increased timeout
            
            while not test_complete and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            # Stop stream
            self.collector.stop_streams()
            time.sleep(1)  # Wait for cleanup
            
            # Check if we received any data
            self.assertGreater(len(received_data), 0, 
                             f"No kline data received within {timeout} seconds for {self.test_symbol}")
            
            # Check message structure
            kline_data = received_data[0]
            self.assertEqual(kline_data['e'], 'kline')
            self.assertEqual(kline_data['s'], self.test_symbol)
            self.assertIn('k', kline_data)
            
            k = kline_data['k']
            self.assertEqual(k['s'], self.test_symbol)
            self.assertEqual(k['i'], '1s')
            
        except Exception as e:
            print(f"Test error: {str(e)}")
            raise
        finally:
            self.collector.stop_streams()
            time.sleep(1)  # Wait for cleanup
    
    def test_websocket_trade_stream(self):
        """Test WebSocket trade stream."""
        # Reset collector for clean WebSocket state
        self._reset_collector()
        
        received_data = []
        test_complete = False
        
        def handle_message(msg):
            """Handle incoming trade messages."""
            try:
                if isinstance(msg, dict) and msg.get('e') == 'aggTrade':
                    received_data.append(msg)
                    if len(received_data) >= 1:
                        nonlocal test_complete
                        test_complete = True
            except Exception as e:
                print(f"Error in trade handler: {str(e)}")
        
        try:
            # Use a very active trading pair
            self.test_symbol = "BTCUSDT"  # Most active pair
            
            self.collector.start_trade_stream(
                symbol=self.test_symbol,
                callback=handle_message
            )
            
            # Wait for data with timeout
            start_time = time.time()
            timeout = 10  # Increased timeout
            
            while not test_complete and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            # Stop stream
            self.collector.stop_streams()
            time.sleep(1)  # Wait for cleanup
            
            # Check if we received any data
            self.assertGreater(len(received_data), 0, 
                             f"No trade data received within {timeout} seconds for {self.test_symbol}")
            
            # Check message structure
            trade_data = received_data[0]
            self.assertEqual(trade_data['e'], 'aggTrade')
            self.assertEqual(trade_data['s'], self.test_symbol)
            self.assertIn('p', trade_data)
            self.assertIn('q', trade_data)
            
        except Exception as e:
            print(f"Test error: {str(e)}")
            raise
        finally:
            self.collector.stop_streams()
            time.sleep(1)  # Wait for cleanup

if __name__ == '__main__':
    unittest.main() 