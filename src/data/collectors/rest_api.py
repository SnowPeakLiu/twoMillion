"""REST API collector module."""

from typing import Optional, Dict, Any, Union
from datetime import datetime
import pandas as pd
from binance.spot import Spot
from .base import BaseCollector

class RestApiCollector(BaseCollector):
    """Collector for Binance REST API data."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the collector.
        
        Args:
            data_dir: Directory to store downloaded data
        """
        super().__init__(data_dir)
        self.client = Spot()
    
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