# Installation Guide

## Prerequisites

- Python 3.10+
- Conda package manager
- Git
- C++ build tools (for TA-Lib)

## Step 1: Create and Activate Conda Environment

```bash
# Create a new conda environment with Python 3.10
conda create -n crypto_analysis python=3.10

# Activate the environment
conda activate crypto_analysis
```

## Step 2: Install TA-Lib

TA-Lib requires special installation steps because it has system-level dependencies.

### For Ubuntu/Debian:

```bash
# Download and build TA-Lib from source
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure
make
sudo make install

# You might need to run this if you get shared library errors
sudo ldconfig
```

### For macOS:

```bash
# Using Homebrew
brew install ta-lib
```

### For Windows:

Download the pre-built binary from [here](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip), unzip it, and:
1. Copy the contents to `C:\ta-lib`
2. Add `C:\ta-lib\bin` to your PATH environment variable

## Step 3: Install Python Dependencies

After TA-Lib system installation is complete, install the Python packages:

```bash
# Install TA-Lib Python package first
conda install -c conda-forge ta-lib

# Install other dependencies
pip install -r requirements.txt
```

Current dependencies in requirements.txt:
```
binance-connector==3.12.0
python-dotenv==1.0.0
pandas==2.0.3
openai==1.3.6
TA-Lib==0.4.27
```

## Common Issues

### TA-Lib Installation Fails

If you encounter issues installing TA-Lib:

1. Make sure you have build tools installed:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install build-essential
   ```

2. If you get "ta_lib.h: No such file or directory":
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev
   ```

3. If the Python package fails to install, try installing from conda-forge:
   ```bash
   conda install -c conda-forge ta-lib
   ```

### Binance Connector Version Issues

If you encounter issues with binance-connector installation:
1. Make sure you're using the correct version that matches the Binance API
2. You might need to install it directly from GitHub if PyPI version is outdated

## Environment Variables

Create a `.env` file in the project root with the following variables:
```
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
OPENAI_API_KEY=your_openai_api_key
```

## Verifying Installation

To verify your installation:

```python
import talib
import pandas as pd
from binance.spot import Spot
import openai

# If no errors occur, installation is successful
``` 