from data.binance_data_collector import DataCollector
from features.feature_engineer import FeatureEngineer
from llm.llm_interface import LLMAnalyst
from interface.cli import TerminalUI
from config.settings import Config

def main():
    # 初始化配置
    config = Config()
    
    # 初始化各模块
    collector = DataCollector(config.binance_api_key, config.binance_api_secret)
    engineer = FeatureEngineer()
    analyst = LLMAnalyst(config.openai_api_key)
    ui = TerminalUI()

    # 主程序逻辑
    raw_data = collector.get_historical_data('BTCUSDT', '1h')
    processed_data = engineer.add_technical_indicators(raw_data)
    analysis = analyst.generate_analysis(processed_data.iloc[-1])
    ui.display_analysis(analysis)

if __name__ == "__main__":
    main() 