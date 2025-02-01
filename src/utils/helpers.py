"""
Utility Functions Module
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from .logger import get_logger

log = get_logger(__name__)

def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON file
    
    Args:
        file_path: JSON file path
        
    Returns:
        Dict: JSON data
        
    Raises:
        FileNotFoundError: File not found
        json.JSONDecodeError: JSON parsing error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        log.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        log.error(f"JSON parsing error: {str(e)}")
        raise

def save_json(
    data: Union[Dict[str, Any], List[Any]],
    file_path: Union[str, Path],
    indent: int = 2
) -> None:
    """Save data to JSON file
    
    Args:
        data: Data to save
        file_path: Save path
        indent: JSON indentation spaces
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    except Exception as e:
        log.error(f"Failed to save JSON file: {str(e)}")
        raise

def format_timestamp(
    timestamp: Union[int, float, str],
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """Format timestamp
    
    Args:
        timestamp: Unix timestamp (milliseconds)
        format_str: Time format string
        
    Returns:
        str: Formatted time string
    """
    try:
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        # Convert to seconds
        if timestamp > 1e12:
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp).strftime(format_str)
    except Exception as e:
        log.error(f"Failed to format timestamp: {str(e)}")
        raise

@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def safe_request(func: callable, *args, **kwargs) -> Any:
    """Safe request wrapper
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Any: Function return value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log.error(f"Request failed: {str(e)}")
        raise

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        pd.DataFrame: DataFrame with technical indicators
    """
    try:
        # Calculate moving averages
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        
        # Calculate volume weighted moving average
        df['VWMA'] = (df['close'] * df['volume']).rolling(
            window=20
        ).sum() / df['volume'].rolling(window=20).sum()
        
        # Calculate volatility
        df['volatility'] = df['close'].pct_change().rolling(
            window=20
        ).std()
        
        return df
    except Exception as e:
        log.error(f"Failed to calculate technical indicators: {str(e)}")
        raise

def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str]
) -> bool:
    """Validate DataFrame contains required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        bool: Validation result
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        log.error(f"Missing required columns: {missing_columns}")
        return False
    return True

# Example usage
if __name__ == "__main__":
    # Test timestamp formatting
    print(format_timestamp(1645084800000))  # 2022-02-17 12:00:00
    
    # Test DataFrame validation
    df = pd.DataFrame({
        'timestamp': [1645084800000],
        'open': [100],
        'high': [101],
        'low': [99],
        'close': [100.5],
        'volume': [1000]
    })
    
    required_cols = ['timestamp', 'close', 'volume']
    print(validate_dataframe(df, required_cols))  # True 