"""
Test connection to Delta Exchange India using CCXT
This script verifies API credentials and exchange connectivity
"""
import ccxt
from config import Config

def test_connection():
    """Test connection to Delta Exchange"""
    
    print("=" * 60)
    print("Delta Exchange India - Connection Test")
    print("=" * 60)
    
    # Validate configuration
    try:
        Config.validate()
        print("✓ Configuration validated")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False
    
    # Initialize exchange
    try:
        exchange = ccxt.delta({
            'apiKey': Config.DELTA_API_KEY,
            'secret': Config.DELTA_API_SECRET,
            'enableRateLimit': True,
            'urls': {
                'api': {
                    'public': 'https://api.india.delta.exchange',
                    'private': 'https://api.india.delta.exchange',
                }
            },
            'options': {
                'defaultType': 'spot',  # Use spot trading
            },
        })
        
        # Set testnet if configured
        if Config.TESTNET:
            exchange.set_sandbox_mode(True)
            print("✓ Running in TESTNET mode")
        else:
            print("✓ Running in PRODUCTION mode")
        
        # Print API endpoint for debugging
        print(f"✓ API Endpoint: https://api.india.delta.exchange")
        
        print(f"✓ Exchange initialized: {exchange.name}")
        
    except Exception as e:
        print(f"✗ Failed to initialize exchange: {e}")
        return False
    
    # Test API connection - fetch markets
    try:
        print("\nFetching markets...")
        markets = exchange.load_markets()
        print(f"✓ Successfully connected! Found {len(markets)} trading pairs")
        
        # Display some popular markets
        print("\nSample markets:")
        count = 0
        for symbol in markets:
            if count < 5:
                print(f"  - {symbol}")
                count += 1
            else:
                break
                
    except Exception as e:
        print(f"✗ Failed to fetch markets: {e}")
        return False
    
    # Test account access - fetch balance
    try:
        print("\nFetching account balance...")
        balance = exchange.fetch_balance()
        print("✓ Successfully fetched account balance")
        
        # Display non-zero balances
        print("\nAccount balances:")
        has_balance = False
        for currency, amount in balance['total'].items():
            if amount > 0:
                print(f"  {currency}: {amount}")
                has_balance = True
        
        if not has_balance:
            print("  (No balances found - account may be empty)")
            
    except Exception as e:
        print(f"✗ Failed to fetch balance: {e}")
        print("  Note: This might be a permission issue with your API key")
        return False
    
    print("\n" + "=" * 60)
    print("Connection test completed successfully!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        test_connection()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
