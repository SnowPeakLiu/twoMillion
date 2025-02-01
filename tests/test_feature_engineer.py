"""
Feature engineering module tests
"""
import numpy as np
import pandas as pd
import pytest

from src.processors.feature_engineer import FeatureEngineer

@pytest.fixture
def sample_data():
    """Create test data"""
    data = {
        'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='H'),
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 101,
        'volume': np.random.randint(1000, 10000, 100)
    }
    return pd.DataFrame(data)

@pytest.fixture
def engineer():
    """Create feature engineering instance"""
    return FeatureEngineer()

def test_validate_data(engineer, sample_data):
    """Test data validation"""
    # Normal data should pass validation
    engineer._validate_data(sample_data)
    
    # Missing required columns should raise an exception
    invalid_data = sample_data.drop('close', axis=1)
    with pytest.raises(ValueError):
        engineer._validate_data(invalid_data)
    
    # Data type error should raise an exception
    invalid_data = sample_data.copy()
    invalid_data['close'] = invalid_data['close'].astype(str)
    with pytest.raises(ValueError):
        engineer._validate_data(invalid_data)

def test_trend_features(engineer, sample_data):
    """Test trend features"""
    df = engineer.add_trend_features(sample_data)
    
    # Check if all trend features are added
    expected_columns = [
        'MA5', 'MA10', 'MA20', 'MA60',
        'EMA12', 'EMA26',
        'BB_UPPER', 'BB_MIDDLE', 'BB_LOWER'
    ]
    
    for col in expected_columns:
        assert col in df.columns
    
    # Check if moving averages are calculated correctly
    assert df['MA5'].iloc[5:].notna().all()
    assert df['MA20'].iloc[20:].notna().all()
    
    # Check if Bollinger Bands are calculated correctly
    assert (df['BB_UPPER'] >= df['BB_MIDDLE']).all()
    assert (df['BB_MIDDLE'] >= df['BB_LOWER']).all()

def test_momentum_features(engineer, sample_data):
    """Test momentum features"""
    df = engineer.add_momentum_features(sample_data)
    
    # Check if all momentum features are added
    expected_columns = [
        'RSI', 'MACD', 'MACD_SIGNAL', 'MACD_HIST',
        'STOCH_K', 'STOCH_D'
    ]
    
    for col in expected_columns:
        assert col in df.columns
    
    # Check RSI range
    assert df['RSI'].dropna().between(0, 100).all()
    
    # Check STOCH range
    assert df['STOCH_K'].dropna().between(0, 100).all()
    assert df['STOCH_D'].dropna().between(0, 100).all()

def test_volatility_features(engineer, sample_data):
    """Test volatility features"""
    df = engineer.add_volatility_features(sample_data)
    
    # Check if all volatility features are added
    expected_columns = ['ATR', 'DAILY_VOLATILITY', 'STD20']
    
    for col in expected_columns:
        assert col in df.columns
    
    # Check if volatility is positive
    assert (df['ATR'].dropna() >= 0).all()
    assert (df['DAILY_VOLATILITY'].dropna() >= 0).all()
    assert (df['STD20'].dropna() >= 0).all()

def test_volume_features(engineer, sample_data):
    """Test volume features"""
    df = engineer.add_volume_features(sample_data)
    
    # Check if all volume features are added
    expected_columns = [
        'VOLUME_MA5', 'VOLUME_MA20',
        'VOLUME_CHANGE', 'OBV'
    ]
    
    for col in expected_columns:
        assert col in df.columns
    
    # Check if volume moving averages are calculated correctly
    assert df['VOLUME_MA5'].iloc[5:].notna().all()
    assert df['VOLUME_MA20'].iloc[20:].notna().all()

def test_pattern_features(engineer, sample_data):
    """Test pattern features"""
    df = engineer.add_pattern_features(sample_data)
    
    # Check if all pattern features are added
    expected_columns = ['DOJI', 'HAMMER', 'SHOOTING_STAR']
    
    for col in expected_columns:
        assert col in df.columns
    
    # Check if pattern recognition results are integers
    for col in expected_columns:
        assert df[col].dtype in [np.int32, np.int64]

def test_process_all_features(engineer, sample_data):
    """Test complete feature processing"""
    df = engineer.process(sample_data)
    
    # Check if data is successfully processed
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    
    # Check if there are no NaN values
    assert not df.isnull().any().any()
    
    # Check if all feature types are included
    feature_types = [
        'MA', 'EMA', 'BB_',  # Trend features
        'RSI', 'MACD', 'STOCH',  # Momentum features
        'ATR', 'VOLATILITY',  # Volatility features
        'VOLUME', 'OBV',  # Volume features
        'DOJI', 'HAMMER'  # Pattern features
    ]
    
    for feature_type in feature_types:
        assert any(
            col.startswith(feature_type) for col in df.columns
        ), f"Missing {feature_type} features"

def test_error_handling(engineer):
    """Test error handling"""
    # Empty DataFrame should raise an exception
    with pytest.raises(ValueError):
        engineer.process(pd.DataFrame())
    
    # Data type error should raise an exception
    invalid_data = pd.DataFrame({
        'timestamp': ['2024-01-01'],
        'open': ['invalid'],
        'high': ['invalid'],
        'low': ['invalid'],
        'close': ['invalid'],
        'volume': ['invalid']
    })
    
    with pytest.raises(ValueError):
        engineer.process(invalid_data) 