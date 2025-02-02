"""Tests for the data collection module."""

import unittest
from datetime import datetime, timedelta
import pandas as pd
from src.data.binance_data_collector import DataCollector

class TestDataCollector(unittest.TestCase):
    """Test cases for DataCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = DataCollector()
        self.test_symbol = "BTCUSDT"
    
    def test_get_klines(self):
        """Test getting kline/candlestick data."""
        # Get last 10 1-hour candles
        df = self.collector.get_klines(
            symbol=self.test_symbol,
            interval="1h",
            limit=10
        )
        
        # Check DataFrame structure
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 10)
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
    
    def test_get_ticker_24h(self):
        """Test getting 24-hour ticker data."""
        # Test single symbol
        df_single = self.collector.get_ticker_24h(self.test_symbol)
        self.assertIsInstance(df_single, pd.DataFrame)
        self.assertEqual(len(df_single), 1)
        
        # Test all symbols
        df_all = self.collector.get_ticker_24h()
        self.assertIsInstance(df_all, pd.DataFrame)
        self.assertGreater(len(df_all), 1)
    
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
            limit=10
        )
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 10)
        expected_columns = {'id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker'}
        self.assertTrue(all(col in df.columns for col in expected_columns))
        
        # Check data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['time']))
        self.assertTrue(pd.api.types.is_float_dtype(df['price']))
        self.assertTrue(pd.api.types.is_float_dtype(df['qty']))

if __name__ == '__main__':
    unittest.main() 