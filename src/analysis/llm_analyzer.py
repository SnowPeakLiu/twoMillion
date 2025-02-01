"""
LLM Analysis Module for Cryptocurrency Trading
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Union

import openai
import pandas as pd

from ..config import settings
from ..utils.helpers import format_timestamp
from ..utils.logger import get_logger

log = get_logger(__name__)

class LLMAnalyzer:
    """LLM Market Analyzer for Cryptocurrency Trading"""
    
    # Supported models
    SUPPORTED_MODELS = [
        "gpt-4-turbo-preview",  # Latest GPT-4 model
        "gpt-4",                # Standard GPT-4
        "gpt-3.5-turbo",       # GPT-3.5
        "gpt-3.5-turbo-16k"    # Long context GPT-3.5
    ]
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """Initialize the analyzer
        
        Args:
            model_name: Name of the model to use, defaults to gpt-3.5-turbo
        """
        if model_name not in self.SUPPORTED_MODELS:
            log.warning(
                f"Unknown model {model_name}, "
                f"using default model gpt-3.5-turbo"
            )
            model_name = "gpt-3.5-turbo"
        
        self.model_name = model_name
        self.api_key = settings.api.openai_api_key
        openai.api_key = self.api_key
        
        log.info(f"Using model: {self.model_name}")
        
        self.system_prompt = """You are an experienced cryptocurrency trading analyst, skilled in analyzing market trends using technical and market data.

        Your task is to generate a detailed analysis report based on the provided market data. The analysis should include:
        1. Market trend assessment
        2. Key support and resistance levels
        3. Technical indicator analysis
        4. Trading recommendations
        5. Risk warnings

        Please ensure the analysis is objective, professional, and provides clear actionable recommendations.
        The output should be in JSON format with the following fields:
        {
            "trend_direction": str,  # Market trend direction
            "confidence_level": int,  # Confidence level (0-100)
            "technical_analysis": {
                "trend": str,  # Trend analysis
                "support_resistance": {
                    "support": float,  # Support level
                    "resistance": float  # Resistance level
                },
                "indicators": {
                    "ma": str,  # Moving average analysis
                    "macd": str,  # MACD analysis
                    "rsi": str  # RSI analysis
                }
            },
            "trading_advice": {
                "position": str,  # Position recommendation
                "entry_points": List[float],  # Entry points
                "stop_loss": float,  # Stop loss level
                "take_profit": float  # Take profit level
            },
            "risk_assessment": {
                "risk_level": str,  # Risk level
                "key_risks": List[str]  # Key risks
            }
        }
        """
    
    def analyze(
        self,
        market_data: pd.DataFrame,
        additional_context: Optional[Dict] = None
    ) -> Dict:
        """Analyze market data
        
        Args:
            market_data: Market data with technical indicators
            additional_context: Additional context information
            
        Returns:
            Dict: Analysis results
        """
        try:
            # Prepare analysis data
            analysis_data = self._prepare_data(market_data)
            
            # Add additional context if provided
            if additional_context:
                analysis_data.update(additional_context)
            
            # Call LLM for analysis
            response = self._call_llm(analysis_data)
            
            # Parse response
            analysis_result = self._parse_response(response)
            
            log.info("Market analysis completed")
            return analysis_result
            
        except Exception as e:
            log.error(f"Market analysis failed: {str(e)}")
            raise
    
    def _prepare_data(self, df: pd.DataFrame) -> Dict:
        """Prepare data for analysis
        
        Args:
            df: Market data
            
        Returns:
            Dict: Formatted data
        """
        try:
            # Get latest data
            latest = df.iloc[-1]
            
            # Calculate price change
            price_change = (
                latest['close'] - df.iloc[-2]['close']
            ) / df.iloc[-2]['close'] * 100
            
            # Prepare data dictionary
            data = {
                "current_price": latest['close'],
                "timestamp": format_timestamp(latest['timestamp']),
                "price_change_percent": round(price_change, 2),
                "volume": latest['volume'],
                "technical_indicators": {
                    "ma": {
                        "MA5": latest.get('MA5'),
                        "MA10": latest.get('MA10'),
                        "MA20": latest.get('MA20'),
                        "MA60": latest.get('MA60')
                    },
                    "momentum": {
                        "RSI": latest.get('RSI'),
                        "MACD": latest.get('MACD'),
                        "MACD_SIGNAL": latest.get('MACD_SIGNAL'),
                        "STOCH_K": latest.get('STOCH_K'),
                        "STOCH_D": latest.get('STOCH_D')
                    },
                    "volatility": {
                        "ATR": latest.get('ATR'),
                        "BB_UPPER": latest.get('BB_UPPER'),
                        "BB_LOWER": latest.get('BB_LOWER')
                    },
                    "volume": {
                        "OBV": latest.get('OBV'),
                        "VOLUME_MA20": latest.get('VOLUME_MA20')
                    }
                },
                "patterns": {
                    "DOJI": bool(latest.get('DOJI')),
                    "HAMMER": bool(latest.get('HAMMER')),
                    "SHOOTING_STAR": bool(latest.get('SHOOTING_STAR'))
                }
            }
            
            return data
            
        except Exception as e:
            log.error(f"Data preparation failed: {str(e)}")
            raise
    
    def _call_llm(self, data: Dict) -> str:
        """Call LLM for analysis
        
        Args:
            data: Analysis data
            
        Returns:
            str: LLM response
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze the following market data:\n{json.dumps(data, indent=2)}"
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            log.error(f"LLM call failed: {str(e)}")
            raise
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response
        
        Args:
            response: LLM response text
            
        Returns:
            Dict: Parsed analysis results
        """
        try:
            # Extract JSON part
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1]
            
            # Parse JSON
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = [
                'trend_direction',
                'confidence_level',
                'technical_analysis',
                'trading_advice',
                'risk_assessment'
            ]
            
            missing_fields = [
                field for field in required_fields
                if field not in result
            ]
            
            if missing_fields:
                raise ValueError(f"Response missing required fields: {missing_fields}")
            
            return result
            
        except json.JSONDecodeError as e:
            log.error(f"JSON parsing failed: {str(e)}")
            raise
        except Exception as e:
            log.error(f"Response parsing failed: {str(e)}")
            raise

# Usage example
if __name__ == "__main__":
    # Create sample data
    data = {
        'timestamp': pd.Timestamp.now(),
        'open': 100,
        'high': 105,
        'low': 98,
        'close': 102,
        'volume': 5000,
        'MA5': 101,
        'MA10': 100,
        'MA20': 99,
        'RSI': 55,
        'MACD': 0.5,
        'MACD_SIGNAL': 0.3,
        'ATR': 2.5
    }
    df = pd.DataFrame([data])
    
    # Create analyzer instance (using default model)
    analyzer = LLMAnalyzer()
    
    # Or specify a particular model
    # analyzer = LLMAnalyzer(model_name="gpt-4")
    
    # Perform analysis
    result = analyzer.analyze(df)
    
    # Print results
    print(json.dumps(result, indent=2)) 