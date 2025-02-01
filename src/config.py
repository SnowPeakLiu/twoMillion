"""
Configuration management module
"""
import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# Load environment variables
load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
ANALYSIS_DIR = DATA_DIR / "analysis"

# Create necessary directories
for dir_path in [DATA_DIR, CACHE_DIR, ANALYSIS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

class TradingSettings(BaseSettings):
    """Trading related configuration"""
    max_position_size: float = Field(
        default=0.1,
        description="Maximum position size as a fraction of total capital"
    )
    stop_loss_percentage: float = Field(
        default=0.02,
        description="Stop loss as a fraction of position"
    )
    take_profit_percentage: float = Field(
        default=0.06,
        description="Take profit as a fraction of position"
    )
    max_trades_per_day: int = Field(
        default=5,
        description="Maximum number of trades per day"
    )
    max_drawdown_percentage: float = Field(
        default=0.15,
        description="Maximum allowed drawdown"
    )

class APISettings(BaseSettings):
    """API configuration"""
    binance_api_key: str = Field(
        default=...,
        env='BINANCE_API_KEY'
    )
    binance_api_secret: str = Field(
        default=...,
        env='BINANCE_API_SECRET'
    )
    openai_api_key: str = Field(
        default=...,
        env='OPENAI_API_KEY'
    )

class AppSettings(BaseSettings):
    """Application configuration"""
    log_level: str = Field(
        default="INFO",
        env='LOG_LEVEL'
    )
    debug_mode: bool = Field(
        default=False,
        env='DEBUG_MODE'
    )
    data_cache_dir: Path = Field(
        default=CACHE_DIR
    )
    analysis_output_dir: Path = Field(
        default=ANALYSIS_DIR
    )

class Settings:
    """Global configuration class"""
    def __init__(self):
        self.trading = TradingSettings()
        self.api = APISettings()
        self.app = AppSettings()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format"""
        return {
            "trading": self.trading.dict(),
            "api": {
                k: v for k, v in self.api.dict().items()
                if not k.endswith('_secret')
            },
            "app": self.app.dict()
        }

# Global configuration instance
settings = Settings() 