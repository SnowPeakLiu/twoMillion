"""
Command Line Interface Module
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..analysis.llm_analyzer import LLMAnalyzer
from ..collectors.binance_collector import BinanceCollector
from ..config import settings
from ..processors.feature_engineer import FeatureEngineer
from ..utils.logger import get_logger, setup_logger

log = get_logger(__name__)
console = Console()

class TradingAnalysisCLI:
    """Command Line Interface for Trading Analysis System"""
    
    def __init__(self):
        """Initialize CLI"""
        self.collector = BinanceCollector()
        self.engineer = FeatureEngineer()
        self.analyzer = LLMAnalyzer()
        
        # Setup logging
        log_file = Path("logs/app.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        setup_logger(log_file)
    
    def run(self, args: argparse.Namespace) -> None:
        """Run CLI
        
        Args:
            args: Command line arguments
        """
        try:
            # Fetch market data
            market_data = self._fetch_data(
                symbol=args.symbol,
                interval=args.interval,
                lookback=args.lookback
            )
            
            # Feature engineering
            processed_data = self.engineer.process(market_data)
            
            # Market analysis
            analysis = self.analyzer.analyze(processed_data)
            
            # Display results
            self._display_results(
                market_data=processed_data,
                analysis=analysis
            )
            
            # Save results
            if args.output:
                self._save_results(
                    analysis,
                    Path(args.output)
                )
            
        except Exception as e:
            log.error(f"Run failed: {str(e)}")
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    def _fetch_data(
        self,
        symbol: str,
        interval: str,
        lookback: str
    ) -> pd.DataFrame:
        """Fetch market data
        
        Args:
            symbol: Trading pair
            interval: Kline interval
            lookback: Lookback period
            
        Returns:
            pd.DataFrame: Market data
        """
        try:
            # Calculate start time
            start_time = datetime.now() - self._parse_lookback(lookback)
            
            # Fetch data
            with console.status("[bold green]Fetching market data..."):
                df = self.collector.fetch_historical_data(
                    symbol=symbol,
                    interval=interval,
                    start_time=start_time
                )
            
            console.print(
                f"[green]Successfully fetched {len(df)} records for {symbol}[/green]"
            )
            return df
            
        except Exception as e:
            log.error(f"Data fetch failed: {str(e)}")
            raise
    
    def _display_results(
        self,
        market_data: pd.DataFrame,
        analysis: Dict
    ) -> None:
        """Display analysis results
        
        Args:
            market_data: Market data
            analysis: Analysis results
        """
        # Create market overview table
        overview_table = Table(
            title="Market Overview",
            show_header=True,
            header_style="bold magenta"
        )
        
        overview_table.add_column("Indicator", style="cyan")
        overview_table.add_column("Value", justify="right")
        
        latest = market_data.iloc[-1]
        overview_table.add_row("Current Price", f"{latest['close']:.2f}")
        overview_table.add_row(
            "24h Change",
            self._format_change(
                latest['close'] - market_data.iloc[-24]['close']
                if len(market_data) >= 24 else 0
            )
        )
        overview_table.add_row("Volume", f"{latest['volume']:,.0f}")
        
        # Create technical analysis table
        ta_table = Table(
            title="Technical Indicators",
            show_header=True,
            header_style="bold magenta"
        )
        
        ta_table.add_column("Indicator", style="cyan")
        ta_table.add_column("Value", justify="right")
        
        ta_table.add_row("RSI", f"{latest.get('RSI', 'N/A'):.2f}")
        ta_table.add_row("MACD", f"{latest.get('MACD', 'N/A'):.4f}")
        ta_table.add_row("ATR", f"{latest.get('ATR', 'N/A'):.4f}")
        
        # Create analysis result panel
        analysis_text = Text()
        analysis_text.append("\nTrend Direction: ", style="cyan")
        analysis_text.append(
            analysis['trend_direction'],
            style="green" if "bullish" in analysis['trend_direction'].lower() else "red"
        )
        
        analysis_text.append("\nConfidence Level: ", style="cyan")
        analysis_text.append(
            f"{analysis['confidence_level']}%",
            style="bright_green" if analysis['confidence_level'] > 70
            else "yellow"
        )
        
        analysis_text.append("\n\nTechnical Analysis:\n", style="cyan")
        ta = analysis['technical_analysis']
        analysis_text.append(f"• Trend: {ta['trend']}\n")
        analysis_text.append(
            f"• Support: {ta['support_resistance']['support']}\n"
        )
        analysis_text.append(
            f"• Resistance: {ta['support_resistance']['resistance']}\n"
        )
        
        analysis_text.append("\nTrading Advice:\n", style="cyan")
        trade = analysis['trading_advice']
        analysis_text.append(f"• Position: {trade['position']}\n")
        analysis_text.append(
            f"• Entry Points: {', '.join(map(str, trade['entry_points']))}\n"
        )
        analysis_text.append(f"• Stop Loss: {trade['stop_loss']}\n")
        analysis_text.append(f"• Take Profit: {trade['take_profit']}\n")
        
        analysis_text.append("\nRisk Assessment:\n", style="cyan")
        risk = analysis['risk_assessment']
        analysis_text.append(f"• Risk Level: {risk['risk_level']}\n")
        analysis_text.append(
            "• Key Risks:\n  - " + "\n  - ".join(risk['key_risks'])
        )
        
        # Display results
        console.print("\n")
        console.print(overview_table)
        console.print("\n")
        console.print(ta_table)
        console.print("\n")
        console.print(Panel(
            analysis_text,
            title="Analysis Results",
            border_style="green"
        ))
    
    def _save_results(
        self,
        results: Dict,
        output_path: Path
    ) -> None:
        """Save analysis results
        
        Args:
            results: Analysis results
            output_path: Output file path
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    results,
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            console.print(
                f"\n[green]Analysis results saved to: {output_path}[/green]"
            )
        except Exception as e:
            log.error(f"Failed to save results: {str(e)}")
            console.print(f"[red]Failed to save results: {str(e)}[/red]")
    
    @staticmethod
    def _parse_lookback(lookback: str) -> timedelta:
        """Parse lookback period
        
        Args:
            lookback: Lookback period string (e.g., '7d', '24h', '30m')
            
        Returns:
            timedelta: Time interval
            
        Raises:
            ValueError: Invalid time format
        """
        units = {
            'm': 'minutes',
            'h': 'hours',
            'd': 'days',
            'w': 'weeks'
        }
        
        try:
            value = int(lookback[:-1])
            unit = lookback[-1].lower()
            
            if unit not in units:
                raise ValueError
            
            return timedelta(**{units[unit]: value})
            
        except (IndexError, ValueError):
            raise ValueError(
                f"Invalid time format: {lookback}. "
                "Please use format like '7d', '24h', '30m'"
            )
    
    @staticmethod
    def _format_change(change: float) -> str:
        """Format price change
        
        Args:
            change: Price change value
            
        Returns:
            str: Formatted string
        """
        color = "green" if change >= 0 else "red"
        sign = "+" if change >= 0 else ""
        return f"[{color}]{sign}{change:.2f}[/{color}]"

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Cryptocurrency Trading Analysis System"
    )
    
    parser.add_argument(
        '-s', '--symbol',
        type=str,
        default='BTCUSDT',
        help='Trading pair (default: BTCUSDT)'
    )
    
    parser.add_argument(
        '-i', '--interval',
        type=str,
        default='1h',
        choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
        help='Kline interval (default: 1h)'
    )
    
    parser.add_argument(
        '-l', '--lookback',
        type=str,
        default='7d',
        help='Lookback period (e.g., 7d, 24h, 30m)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='File path to save analysis results'
    )
    
    args = parser.parse_args()
    
    try:
        cli = TradingAnalysisCLI()
        cli.run(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Program terminated[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main() 