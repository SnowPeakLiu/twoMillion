"""
Binance data collector module for fetching market data.
No API key is required for basic market data collection.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import pandas as pd
from binance.spot import Spot

class DataCollector:
    """Collects market data from Binance."""
    
    def __init__(self, base_url: str = "https://api.binance.com"):
        """Initialize the data collector.
        
        Args:
            base_url: Binance API base URL. Use https://testnet.binance.vision for testing.
        """
        self.client = Spot(base_url=base_url)
        self.logger = logging.getLogger(__name__)
    
    def get_klines(self, 
                   symbol: str, 
                   interval: str,
                   limit: int = 500,
                   start_time: Optional[int] = None,
                   end_time: Optional[int] = None) -> pd.DataFrame:
        """Get kline/candlestick data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            limit: Number of records to get (max 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            DataFrame with columns: [open_time, open, high, low, close, volume, close_time, 
            quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]
        """
        try:
            klines = self.client.klines(
                symbol=symbol.upper(),
                interval=interval,
                limit=limit,
                startTime=start_time,
                endTime=end_time
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
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
            
            # Convert timestamps to datetime
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching klines for {symbol}: {str(e)}")
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
                data = [self.client.ticker_24hr(symbol.upper())]
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
            return self.client.depth(symbol=symbol.upper(), limit=limit)
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
            trades = self.client.trades(symbol=symbol.upper(), limit=limit)
            df = pd.DataFrame(trades)
            
            # Convert numeric columns
            numeric_columns = ['price', 'qty', 'quoteQty']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
            
            # Convert timestamp
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching recent trades for {symbol}: {str(e)}")
            raise 