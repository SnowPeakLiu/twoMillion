import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.binance_api_key = os.getenv('BINANCE_API_KEY')
        self.binance_api_secret = os.getenv('BINANCE_API_SECRET')
        self.openai_api_key = os.getenv('OPENAI_API_KEY') 