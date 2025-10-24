"""
Configuration module for Delta Exchange India trading bot
Loads API credentials from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for API credentials and settings"""
    
    # Delta Exchange API credentials
    DELTA_API_KEY = os.getenv('DELTA_API_KEY')
    DELTA_API_SECRET = os.getenv('DELTA_API_SECRET')
    
    # Exchange settings
    EXCHANGE_ID = 'delta'  # Delta Exchange ID in CCXT
    
    # Testnet/Production mode
    # Set to True for testnet, False for production
    TESTNET = False
    
    @classmethod
    def validate(cls):
        """Validate that required credentials are set"""
        if not cls.DELTA_API_KEY or not cls.DELTA_API_SECRET:
            raise ValueError(
                "API credentials not found. "
                "Please set DELTA_API_KEY and DELTA_API_SECRET in .env file"
            )
        
        if cls.DELTA_API_KEY == 'your_api_key_here':
            raise ValueError(
                "Please update .env file with your actual API credentials"
            )
        
        return True
