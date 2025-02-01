import pytest
from src.data.binance_data_collector import DataCollector

class TestDataCollection:
    @pytest.fixture
    def collector(self):
        return DataCollector("test_key", "test_secret")

    def test_historical_data_shape(self, collector):
        df = collector.get_historical_data('BTCUSDT', '1h')
        assert df.shape[0] > 0
        assert 'close' in df.columns 