"""
Main trading bot for Delta Exchange India
This is a template for your automated trading strategy
"""
import ccxt
from config import Config
import time

class DeltaTradingBot:
    """Trading bot for Delta Exchange India"""
    
    def __init__(self):
        """Initialize the trading bot"""
        # Validate configuration
        Config.validate()
        
        # Initialize exchange
        self.exchange = ccxt.delta({
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
        
        # Set testnet mode if configured
        if Config.TESTNET:
            self.exchange.set_sandbox_mode(True)
            print("Running in TESTNET mode")
        
        # Load markets
        self.markets = self.exchange.load_markets()
        print(f"Bot initialized with {len(self.markets)} markets")
    
    def get_balance(self):
        """Get account balance"""
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
    
    def get_ticker(self, symbol):
        """Get current ticker for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def place_market_order(self, symbol, side, amount):
        """
        Place a market order
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Amount to trade
        """
        try:
            order = self.exchange.create_market_order(symbol, side, amount)
            print(f"Order placed: {side} {amount} {symbol}")
            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def place_limit_order(self, symbol, side, amount, price):
        """
        Place a limit order
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Limit price
        """
        try:
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            print(f"Limit order placed: {side} {amount} {symbol} @ {price}")
            return order
        except Exception as e:
            print(f"Error placing limit order: {e}")
            return None
    
    def get_open_orders(self, symbol=None):
        """Get open orders"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return None
    
    def cancel_order(self, order_id, symbol):
        """Cancel an order"""
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            print(f"Order {order_id} cancelled")
            return result
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return None
    
    def run(self):
        """Main bot loop - implement your strategy here"""
        print("Starting trading bot...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # TODO: Implement your trading strategy here
                # This is just a template - replace with your actual logic
                
                # Example: Get current BTC/USDT price
                # ticker = self.get_ticker('BTC/USDT')
                # if ticker:
                #     print(f"BTC/USDT: {ticker['last']}")
                
                # Sleep for some time before next iteration
                time.sleep(60)  # Wait 60 seconds
                
        except KeyboardInterrupt:
            print("\nBot stopped by user")

if __name__ == "__main__":
    bot = DeltaTradingBot()
    bot.run()
