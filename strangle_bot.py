"""
Strangle Trading Bot for Delta Exchange India
Sells CE and PE with premiums closest to $50 each on BTCUSD
Entry: 4:00 PM | Exit: 5:25 PM
SL: Exit if combined premium > 200% of entry
"""
import ccxt
from config import Config
import time
from datetime import datetime, time as dt_time
import pytz

class StrangleBot:
    """BTCUSD Options Strangle Trading Bot"""
    
    def __init__(self):
        """Initialize the strangle bot"""
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
                'defaultType': 'swap',
            },
        })
        
        # Set testnet mode if configured
        if Config.TESTNET:
            self.exchange.set_sandbox_mode(True)
            print("⚠️  Running in TESTNET mode")
        else:
            print("✓ Running in PRODUCTION mode")
        
        # Load markets
        print("Loading markets...")
        self.markets = self.exchange.load_markets()
        print(f"✓ Bot initialized with {len(self.markets)} markets")
        
        # Trading parameters
        self.base_symbol = 'BTC/USD'
        self.target_premium = 50  # Target $50 per leg
        self.sl_multiplier = 3.0  # Stop loss at 300% of entry (200% increase)
        self.lot_size = 5  # 5 lots = 0.005 BTC (1 BTC = 1000 lots)
        
        # Entry and exit times (IST - Indian Standard Time)
        self.entry_time = dt_time(16, 0)   # 4:00 PM
        self.exit_time = dt_time(17, 25)   # 5:25 PM
        self.timezone = pytz.timezone('Asia/Kolkata')  # IST
        
        # Position tracking
        self.active_positions = {
            'call': None,
            'put': None
        }
        self.entry_premiums = {
            'call': 0,
            'put': 0
        }
        
        print(f"\n📊 Strategy Configuration:")
        print(f"   Base: {self.base_symbol}")
        print(f"   Lot Size: {self.lot_size} lots (0.005 BTC)")
        print(f"   Entry Time: {self.entry_time.strftime('%I:%M %p')}")
        print(f"   Exit Time: {self.exit_time.strftime('%I:%M %p')}")
        print(f"   Target Premium: ${self.target_premium} per option")
        print(f"   Stop Loss: {self.sl_multiplier * 100}% of entry premium")
    
    def get_current_btc_price(self):
        """Get current BTC/USD price"""
        try:
            ticker = self.exchange.fetch_ticker('BTC/USD:USD')
            return ticker['last']
        except Exception as e:
            print(f"Error fetching BTC price: {e}")
            return None
    
    def get_option_symbols(self, expiry_date=None):
        """Get all BTC option symbols for a specific expiry"""
        options = []
        for symbol, market in self.markets.items():
            if 'BTC/USD:USD' in symbol and ('-C' in symbol or '-P' in symbol):
                options.append({
                    'symbol': symbol,
                    'strike': self.extract_strike(symbol),
                    'type': 'call' if '-C' in symbol else 'put',
                    'expiry': self.extract_expiry(symbol)
                })
        return options
    
    def extract_strike(self, symbol):
        """Extract strike price from option symbol"""
        try:
            # Format: BTC/USD:USD-YYMMDD-STRIKE-C/P
            parts = symbol.split('-')
            if len(parts) >= 3:
                return float(parts[-2])
            return None
        except:
            return None
    
    def extract_expiry(self, symbol):
        """Extract expiry date from option symbol"""
        try:
            # Format: BTC/USD:USD-YYMMDD-STRIKE-C/P
            parts = symbol.split('-')
            if len(parts) >= 2:
                return parts[1]
            return None
        except:
            return None
    
    def get_option_price(self, symbol):
        """Get current option premium"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    def find_closest_premium_options(self, target_premium=50, expiry=None):
        """Find call and put options with premiums closest to target"""
        options = self.get_option_symbols(expiry)
        
        if not options:
            print("No options found")
            return None, None
        
        # Get today's expiry or nearest expiry if not specified
        if not expiry:
            expiries = sorted(set([opt['expiry'] for opt in options if opt['expiry']]))
            if not expiries:
                print("No expiries found")
                return None, None
            expiry = expiries[0]  # Get nearest expiry
            print(f"Using expiry: {expiry}")
        
        # Filter options for the selected expiry
        calls = [opt for opt in options if opt['type'] == 'call' and opt['expiry'] == expiry and opt['strike']]
        puts = [opt for opt in options if opt['type'] == 'put' and opt['expiry'] == expiry and opt['strike']]
        
        print(f"\n🔍 Searching for options closest to ${target_premium}...")
        
        # Find call option closest to target premium
        best_call = None
        min_call_diff = float('inf')
        
        for call in calls:
            premium = self.get_option_price(call['symbol'])
            if premium:
                diff = abs(premium - target_premium)
                if diff < min_call_diff:
                    min_call_diff = diff
                    best_call = {
                        'symbol': call['symbol'],
                        'strike': call['strike'],
                        'premium': premium,
                        'type': 'call'
                    }
                time.sleep(0.1)  # Rate limiting
        
        # Find put option closest to target premium
        best_put = None
        min_put_diff = float('inf')
        
        for put in puts:
            premium = self.get_option_price(put['symbol'])
            if premium:
                diff = abs(premium - target_premium)
                if diff < min_put_diff:
                    min_put_diff = diff
                    best_put = {
                        'symbol': put['symbol'],
                        'strike': put['strike'],
                        'premium': premium,
                        'type': 'put'
                    }
                time.sleep(0.1)  # Rate limiting
        
        if best_call and best_put:
            print(f"\n🎯 Selected Options:")
            print(f"   Call Strike: ${best_call['strike']:,.0f} @ ${best_call['premium']:.2f}")
            print(f"   Put Strike: ${best_put['strike']:,.0f} @ ${best_put['premium']:.2f}")
            print(f"   Combined Premium: ${best_call['premium'] + best_put['premium']:.2f}")
        
        return best_call, best_put
    
    def sell_option(self, symbol, quantity=None):
        """Sell an option (short position)"""
        if quantity is None:
            quantity = self.lot_size
            
        try:
            # Get current premium
            premium = self.get_option_price(symbol)
            if not premium:
                print(f"Failed to get premium for {symbol}")
                return None
            
            # Place sell order
            order = self.exchange.create_market_order(symbol, 'sell', quantity)
            print(f"✓ Sold {quantity} lots of {symbol} @ ${premium:.2f}")
            
            return {
                'order': order,
                'symbol': symbol,
                'premium': premium,
                'quantity': quantity,
                'side': 'sell'
            }
        except Exception as e:
            print(f"✗ Error selling {symbol}: {e}")
            return None
    
    def close_position(self, symbol, quantity=None):
        """Close option position by buying back"""
        if quantity is None:
            quantity = self.lot_size
            
        try:
            order = self.exchange.create_market_order(symbol, 'buy', quantity)
            current_price = self.get_option_price(symbol)
            print(f"✓ Closed {quantity} lots of {symbol} @ ${current_price:.2f}")
            return order
        except Exception as e:
            print(f"✗ Error closing {symbol}: {e}")
            return None
    
    def check_combined_sl(self):
        """Check if combined premium exceeds stop loss"""
        if not self.active_positions['call'] or not self.active_positions['put']:
            return False
        
        call_symbol = self.active_positions['call']['symbol']
        put_symbol = self.active_positions['put']['symbol']
        
        call_price = self.get_option_price(call_symbol)
        put_price = self.get_option_price(put_symbol)
        
        if not call_price or not put_price:
            return False
        
        # Calculate current combined premium (total for all lots)
        combined_current = call_price + put_price
        
        # Calculate entry combined premium (per option, not multiplied by lots)
        entry_combined = self.entry_premiums['call'] + self.entry_premiums['put']
        
        # SL level is 200% of entry combined premium
        sl_level = entry_combined * self.sl_multiplier
        
        if combined_current >= sl_level:
            print(f"\n🛑 STOP LOSS HIT!")
            print(f"   Entry Combined Premium: ${entry_combined:.2f}")
            print(f"   Current Combined Premium: ${combined_current:.2f}")
            print(f"   SL Level (200%): ${sl_level:.2f}")
            print(f"   Loss per lot: ${combined_current - entry_combined:.2f}")
            print(f"   Total Loss ({self.lot_size} lots): ${(combined_current - entry_combined) * self.lot_size:.2f}")
            
            # Close both positions
            self.close_position(call_symbol, self.active_positions['call']['quantity'])
            self.close_position(put_symbol, self.active_positions['put']['quantity'])
            
            self.active_positions['call'] = None
            self.active_positions['put'] = None
            
            return True
        
        return False
    
    def is_entry_time(self):
        """Check if current time is entry time"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        
        # Check if within 1 minute of entry time
        entry_min = dt_time(self.entry_time.hour, self.entry_time.minute, 0)
        entry_max = dt_time(self.entry_time.hour, self.entry_time.minute, 59)
        
        return entry_min <= current_time <= entry_max
    
    def is_exit_time(self):
        """Check if current time is exit time"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        
        return current_time >= self.exit_time
    
    def has_active_positions(self):
        """Check if there are any active positions"""
        return self.active_positions['call'] is not None or self.active_positions['put'] is not None
    
    def enter_strangle(self):
        """Enter strangle positions"""
        print("\n" + "="*60)
        print(f"🚀 ENTERING STRANGLE - {datetime.now(self.timezone).strftime('%Y-%m-%d %I:%M:%S %p')}")
        print("="*60)
        
        # Get current BTC price
        btc_price = self.get_current_btc_price()
        if not btc_price:
            print("Failed to get BTC price")
            return False
        
        print(f"Current BTC Price: ${btc_price:,.2f}")
        
        # Find options closest to $50 premium
        call_option, put_option = self.find_closest_premium_options(self.target_premium)
        if not call_option or not put_option:
            print("Failed to find suitable options")
            return False
        
        # Sell call option
        print("\n📉 Selling Call Option...")
        call_position = self.sell_option(call_option['symbol'])
        if call_position:
            self.active_positions['call'] = call_position
            self.entry_premiums['call'] = call_position['premium']
            print(f"   Premium: ${call_position['premium']:.2f}")
            print(f"   Lots: {call_position['quantity']}")
        
        # Sell put option
        print("\n📉 Selling Put Option...")
        put_position = self.sell_option(put_option['symbol'])
        if put_position:
            self.active_positions['put'] = put_position
            self.entry_premiums['put'] = put_position['premium']
            print(f"   Premium: ${put_position['premium']:.2f}")
            print(f"   Lots: {put_position['quantity']}")
        
        # Calculate combined entry premium (per option, not total)
        entry_combined = self.entry_premiums['call'] + self.entry_premiums['put']
        sl_level = entry_combined * self.sl_multiplier
        
        print(f"\n💰 Combined Entry Premium: ${entry_combined:.2f}")
        print(f"   Total for {self.lot_size} lots: ${entry_combined * self.lot_size:.2f}")
        print(f"🛑 Stop Loss Level (200%): ${sl_level:.2f}")
        print(f"   Total loss if SL hit: ${(sl_level - entry_combined) * self.lot_size:.2f}")
        
        print("\n✓ Strangle entered successfully!")
        return True
    
    def exit_strangle(self):
        """Exit all positions"""
        print("\n" + "="*60)
        print(f"🏁 EXITING STRANGLE - {datetime.now(self.timezone).strftime('%Y-%m-%d %I:%M:%S %p')}")
        print("="*60)
        
        # Close call position
        if self.active_positions['call']:
            symbol = self.active_positions['call']['symbol']
            quantity = self.active_positions['call']['quantity']
            entry_premium = self.entry_premiums['call']
            
            print(f"\n📈 Closing Call: {symbol}")
            self.close_position(symbol, quantity)
            
            current_price = self.get_option_price(symbol)
            if current_price:
                pnl = (entry_premium - current_price) * quantity
                print(f"   Entry: ${entry_premium:.2f} | Exit: ${current_price:.2f} | P&L: ${pnl:.2f}")
            
            self.active_positions['call'] = None
        
        # Close put position
        if self.active_positions['put']:
            symbol = self.active_positions['put']['symbol']
            quantity = self.active_positions['put']['quantity']
            entry_premium = self.entry_premiums['put']
            
            print(f"\n📈 Closing Put: {symbol}")
            self.close_position(symbol, quantity)
            
            current_price = self.get_option_price(symbol)
            if current_price:
                pnl = (entry_premium - current_price) * quantity
                print(f"   Entry: ${entry_premium:.2f} | Exit: ${current_price:.2f} | P&L: ${pnl:.2f}")
            
            self.active_positions['put'] = None
        
        print("\n✓ All positions closed!")
    
    def run(self):
        """Main bot loop"""
        print("\n" + "="*60)
        print("🤖 STRANGLE BOT STARTED")
        print("="*60)
        print(f"Waiting for entry time: {self.entry_time.strftime('%I:%M %p')} IST")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                now = datetime.now(self.timezone)
                current_time_str = now.strftime('%I:%M:%S %p')
                
                # Check if it's entry time and no active positions
                if self.is_entry_time() and not self.has_active_positions():
                    self.enter_strangle()
                
                # Monitor active positions
                if self.has_active_positions():
                    # Check combined SL
                    if self.check_combined_sl():
                        pass  # Positions already closed in check_combined_sl
                    
                    # Check exit time
                    elif self.is_exit_time():
                        self.exit_strangle()
                    else:
                        # Print status every 30 seconds
                        if now.second % 30 == 0:
                            print(f"[{current_time_str}] Monitoring positions...")
                
                # Sleep for 1 second
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            
            # Close any open positions
            if self.has_active_positions():
                print("Closing open positions...")
                self.exit_strangle()

if __name__ == "__main__":
    bot = StrangleBot()
    bot.run()
