"""Base collector module."""

import logging
import os
import json
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path

class BaseCollector:
    """Base class for data collectors."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the collector.
        
        Args:
            data_dir: Directory to store downloaded data
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data_dir = data_dir if data_dir else os.path.join(os.getcwd(), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Name of the file
        """
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False)
        self.logger.info(f"Data saved to {filepath}")
    
    def _save_to_json(self, data: Dict[str, Any], filename: str):
        """Save dictionary to JSON file.
        
        Args:
            data: Dictionary to save
            filename: Name of the file
        """
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Data saved to {filepath}") 