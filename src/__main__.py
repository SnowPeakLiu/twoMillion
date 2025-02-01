"""
Application entry point
"""
import sys
from pathlib import Path

# Add project root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.interface.cli import main

if __name__ == "__main__":
    main()