# Crypto Trading Analysis System (MVP)

A LLM-powered cryptocurrency trading analysis system that integrates market data and AI analysis to support trading decisions.

## 🌟 Features

- Real-time market data collection (Binance API)
- Technical indicator analysis
- LLM-driven market analysis (OpenAI API support)
- Structured trading recommendations
- Command-line interface

## 🚀 Quick Start

### Requirements

- Python 3.8+
- pip package manager

### Dependencies

#### API Clients
- **python-binance** `>=1.0.19` - Binance API client
- **openai** `>=1.12.0` - OpenAI API client

#### Data Processing
- **pandas** `>=2.0.0` - Data analysis and manipulation
- **numpy** `>=1.24.0` - Numerical computations
- **ta-lib** `>=0.4.28` - Technical analysis indicators

#### Machine Learning
- **scikit-learn** `>=1.3.0` - Machine learning toolkit

#### Web Framework (Future Use)
- **fastapi** `>=0.109.0` - Web API framework
- **uvicorn** `>=0.27.0` - ASGI server

#### Utilities
- **python-dotenv** `>=1.0.0` - Environment variables management
- **pydantic** `>=2.6.0` - Data validation
- **tenacity** `>=8.2.0` - Retry mechanism
- **requests** `>=2.31.0` - HTTP client
- **rich** `>=13.7.0` - Terminal UI enhancement
- **loguru** `>=0.7.0` - Logging management

#### Development Tools (Optional)
- **pytest** `>=8.0.0` - Unit testing
- **pytest-cov** `>=4.1.0` - Test coverage
- **black** `>=24.1.0` - Code formatting
- **flake8** `>=7.0.0` - Code linting
- **mypy** `>=1.8.0` - Type checking
- **isort** `>=5.13.0` - Import sorting

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/crypto-trading-analysis.git
cd crypto-trading-analysis
```

2. Install dependencies
```bash
# Install base dependencies
pip install .

# Install development dependencies (optional)
pip install ".[dev]"
```

3. Configure environment variables
```bash
cp .env.example .env
# Edit .env file with your API keys
```

4. Run the system
```bash
crypto-analysis -s BTCUSDT -i 1h -l 7d
```

## 📁 Project Structure

```
crypto-trading-analysis/
├── src/
│   ├── collectors/         # Data collection modules
│   ├── processors/         # Data processing modules
│   ├── analysis/          # LLM analysis modules
│   └── interface/         # User interface modules
├── tests/                 # Test cases
├── docs/                  # Documentation
├── requirements.txt       # Project dependencies
└── .env                  # Environment configuration
```

## 🔧 Configuration

The system requires the following API keys:

1. Binance API
   - API Key
   - API Secret

2. OpenAI API
   - API Key (supports all OpenAI Chat models)

## 📊 Example Output

```json
{
    "trend_direction": "Bullish Consolidation",
    "confidence_level": 65,
    "trading_suggestion": "Consider scaling in at support levels",
    "risk_management": "Maintain position size below 5% of portfolio"
}
```

## 🛠 Development Guide

For detailed development guidelines, please refer to [CONTRIBUTING.md](./docs/CONTRIBUTING.md)

## 📝 TODO List

- [ ] Add on-chain data analysis
- [ ] Integrate social media sentiment analysis
- [ ] Develop web interface
- [ ] Implement backtesting framework
- [ ] Support additional LLM models and interfaces

## ⚠️ Disclaimer

This system is for research and educational purposes only. It does not constitute financial advice. Users must assume all risks associated with using this system for trading.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details 