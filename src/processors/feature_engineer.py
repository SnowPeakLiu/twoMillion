"""
Feature Engineering Module for Cryptocurrency Trading Analysis
"""
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import talib
from loguru import logger

from ..utils.logger import get_logger

log = get_logger(__name__)

class FeatureEngineer:
    """Feature Engineering Class for Market Data Processing"""
    
    def __init__(self):
        self.required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    def process(
        self,
        df: pd.DataFrame,
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Process data and add technical indicators
        
        Args:
            df: Raw market data
            features: List of features to add, if None adds all features
            
        Returns:
            pd.DataFrame: Processed data with technical indicators
        """
        try:
            # Validate data
            self._validate_data(df)
            
            # If no features specified, add all features
            if features is None:
                features = [
                    'trend_features',
                    'momentum_features',
                    'volatility_features',
                    'volume_features',
                    'pattern_features'
                ]
            
            # Add features
            for feature in features:
                feature_method = getattr(self, f'add_{feature}')
                df = feature_method(df)
            
            # Remove rows with NaN values
            df = df.dropna()
            
            log.info(f"Feature engineering completed, data shape: {df.shape}")
            return df
            
        except Exception as e:
            log.error(f"Feature engineering failed: {str(e)}")
            raise
    
    def _validate_data(self, df: pd.DataFrame) -> None:
        """Validate input data
        
        Args:
            df: Input DataFrame
            
        Raises:
            ValueError: If required columns are missing
        """
        missing_columns = [
            col for col in self.required_columns
            if col not in df.columns
        ]
        
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )
    
    def add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend-related features
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with trend features added
        """
        try:
            # Moving averages
            df['MA5'] = talib.MA(df['close'], timeperiod=5)
            df['MA10'] = talib.MA(df['close'], timeperiod=10)
            df['MA20'] = talib.MA(df['close'], timeperiod=20)
            df['MA60'] = talib.MA(df['close'], timeperiod=60)
            
            # Exponential moving averages
            df['EMA12'] = talib.EMA(df['close'], timeperiod=12)
            df['EMA26'] = talib.EMA(df['close'], timeperiod=26)
            
            # ADX - Average Directional Index
            df['ADX'] = talib.ADX(
                df['high'],
                df['low'],
                df['close'],
                timeperiod=14
            )
            
            return df
            
        except Exception as e:
            log.error(f"Failed to add trend features: {str(e)}")
            raise
    
    def add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-related features
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with momentum features added
        """
        try:
            # RSI
            df['RSI'] = talib.RSI(df['close'], timeperiod=14)
            
            # MACD
            macd, signal, _ = talib.MACD(
                df['close'],
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            df['MACD'] = macd
            df['MACD_SIGNAL'] = signal
            
            # Stochastic
            df['STOCH_K'], df['STOCH_D'] = talib.STOCH(
                df['high'],
                df['low'],
                df['close'],
                fastk_period=14,
                slowk_period=3,
                slowd_period=3
            )
            
            return df
            
        except Exception as e:
            log.error(f"Failed to add momentum features: {str(e)}")
            raise
    
    def add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-related features
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with volatility features added
        """
        try:
            # ATR - Average True Range
            df['ATR'] = talib.ATR(
                df['high'],
                df['low'],
                df['close'],
                timeperiod=14
            )
            
            # Bollinger Bands
            df['BB_UPPER'], df['BB_MIDDLE'], df['BB_LOWER'] = talib.BBANDS(
                df['close'],
                timeperiod=20,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
            
            return df
            
        except Exception as e:
            log.error(f"Failed to add volatility features: {str(e)}")
            raise
    
    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-related features
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with volume features added
        """
        try:
            # OBV - On Balance Volume
            df['OBV'] = talib.OBV(df['close'], df['volume'])
            
            # Volume moving average
            df['VOLUME_MA20'] = talib.MA(df['volume'], timeperiod=20)
            
            # Money Flow Index
            df['MFI'] = talib.MFI(
                df['high'],
                df['low'],
                df['close'],
                df['volume'],
                timeperiod=14
            )
            
            return df
            
        except Exception as e:
            log.error(f"Failed to add volume features: {str(e)}")
            raise
    
    def add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add candlestick pattern features
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with pattern features added
        """
        try:
            # Single candlestick patterns
            df['DOJI'] = talib.CDLDOJI(
                df['open'],
                df['high'],
                df['low'],
                df['close']
            )
            df['HAMMER'] = talib.CDLHAMMER(
                df['open'],
                df['high'],
                df['low'],
                df['close']
            )
            df['SHOOTING_STAR'] = talib.CDLSHOOTINGSTAR(
                df['open'],
                df['high'],
                df['low'],
                df['close']
            )
            
            return df
            
        except Exception as e:
            log.error(f"Failed to add pattern features: {str(e)}")
            raise

# Usage example
if __name__ == "__main__":
    # Create sample data
    data = {
        'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='H'),
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 101,
        'volume': np.random.randint(1000, 10000, 100)
    }
    df = pd.DataFrame(data)
    
    # Create feature engineering instance
    engineer = FeatureEngineer()
    
    # Process data
    processed_df = engineer.process(df)
    
    # Display results
    print(processed_df.head())
    print("\nFeature list:")
    print(processed_df.columns.tolist()) 