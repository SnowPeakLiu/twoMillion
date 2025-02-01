"""
Project installation configuration for the Crypto Trading Analysis System.
A LLM-powered cryptocurrency trading analysis system that integrates market data 
and AI analysis to support trading decisions.
"""

from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crypto-trading-analysis",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="LLM-powered Cryptocurrency Trading Analysis System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crypto-trading-analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-binance>=1.0.19",
        "openai>=1.12.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "ta-lib>=0.4.28",
        "scikit-learn>=1.3.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.6.0",
        "tenacity>=8.2.0",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "loguru>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "black>=24.1.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "isort>=5.13.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "crypto-analysis=src.__main__:main",
        ],
    },
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt"],
    },
    include_package_data=True,
) 