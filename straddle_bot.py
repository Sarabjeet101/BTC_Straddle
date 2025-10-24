"""
Straddle Trading Bot for Delta Exchange India
Sells 1 strike OTM straddle on BTCUSD options
Entry: 4:30 PM | Exit: 5:25 PM
SL: 150% of premium | TP: 92% of premium
"""
import ccxt
from config import Config
import time
from datetime import datetime, time as dt_time
import pytz

class StraddleBot:
    """BTCUSD Options Straddle Trading Bot"""
    
    def __init__(self):
        """Initialize the straddle bot"""
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
                'defaultType': 'swap',  # Use derivatives
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
        self.sl_multiplier = 1.5  # 150% of premium
        self.tp_multiplier = 0.08  # 8% remaining (92% decay)
        self.lot_size = 10  # 10 lots = 0.01 BTC (1 BTC = 1000 lots)
        
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
        print(f"   Lot Size: {self.lot_size} lots (0.01 BTC)")
        print(f"   Entry Time: {self.entry_time.strftime('%I:%M %p')}")
        print(f"   Exit Time: {self.exit_time.strftime('%I:%M %p')}")
        print(f"   Stop Loss: {self.sl_multiplier * 100}% of premium")
        print(f"   Take Profit: 92% decay (premium drops to {self.tp_multiplier * 100}%)")
    
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
    
    def find_otm_strikes(self, current_price, expiry=None):
        """Find 1 strike OTM call and put options"""
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
        
        # Sort by strike price
        calls.sort(key=lambda x: x['strike'])
        puts.sort(key=lambda x: x['strike'])
        
        # Find ATM strike (closest to current price)
        all_strikes = sorted(set([opt['strike'] for opt in options if opt['strike']]))
        atm_strike = min(all_strikes, key=lambda x: abs(x - current_price))
        
        print(f"\n🎯 Strike Selection:")
        print(f"   Current BTC Price: ${current_price:,.2f}")
        print(f"   ATM Strike: ${atm_strike:,.0f}")
        
        # Find 1 strike OTM from ATM
        # For call: find first strike ABOVE ATM
        otm_call = None
        for call in calls:
            if call['strike'] > atm_strike:
                otm_call = call
                break
        
        # For put: find first strike BELOW ATM
        otm_put = None
        for put in reversed(puts):
            if put['strike'] < atm_strike:
                otm_put = put
                break
        
        if otm_call and otm_put:
            print(f"   Call Strike (1 OTM): ${otm_call['strike']:,.0f} ({otm_call['symbol']})")
            print(f"   Put Strike (1 OTM): ${otm_put['strike']:,.0f} ({otm_put['symbol']})")
        
        return otm_call, otm_put
    
    def get_option_price(self, symbol):
        """Get current option premium"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
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
    
    def check_sl_tp(self, option_type):
        """Check if stop loss or take profit hit"""
        position = self.active_positions[option_type]
        if not position:
            return False
        
        symbol = position['symbol']
        entry_premium = self.entry_premiums[option_type]
        current_price = self.get_option_price(symbol)
        
        if not current_price:
            return False
        
        # For short positions, profit when price goes down, loss when price goes up
        sl_price = entry_premium * self.sl_multiplier
        tp_price = entry_premium * self.tp_multiplier
        
        if current_price >= sl_price:
            print(f"🛑 Stop Loss hit for {option_type.upper()}: ${current_price:.2f} >= ${sl_price:.2f}")
            self.close_position(symbol, position['quantity'])
            self.active_positions[option_type] = None
            return True
        
        if current_price <= tp_price:
            print(f"🎯 Take Profit hit for {option_type.upper()}: ${current_price:.2f} <= ${tp_price:.2f}")
            self.close_position(symbol, position['quantity'])
            self.active_positions[option_type] = None
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
    
    def enter_straddle(self):
        """Enter straddle positions"""
        print("\n" + "="*60)
        print(f"🚀 ENTERING STRADDLE - {datetime.now(self.timezone).strftime('%Y-%m-%d %I:%M:%S %p')}")
        print("="*60)
        
        # Get current BTC price
        btc_price = self.get_current_btc_price()
        if not btc_price:
            print("Failed to get BTC price")
            return False
        
        # Find OTM strikes
        call_option, put_option = self.find_otm_strikes(btc_price)
        if not call_option or not put_option:
            print("Failed to find OTM options")
            return False
        
        # Sell call option
        print("\n📉 Selling Call Option...")
        call_position = self.sell_option(call_option['symbol'])
        if call_position:
            self.active_positions['call'] = call_position
            self.entry_premiums['call'] = call_position['premium']
            print(f"   Premium per lot: ${call_position['premium']:.2f}")
            print(f"   Total lots: {call_position['quantity']}")
            print(f"   SL: ${call_position['premium'] * self.sl_multiplier:.2f}")
            print(f"   TP: ${call_position['premium'] * self.tp_multiplier:.2f}")
        
        # Sell put option
        print("\n📉 Selling Put Option...")
        put_position = self.sell_option(put_option['symbol'])
        if put_position:
            self.active_positions['put'] = put_position
            self.entry_premiums['put'] = put_position['premium']
            print(f"   Premium per lot: ${put_position['premium']:.2f}")
            print(f"   Total lots: {put_position['quantity']}")
            print(f"   SL: ${put_position['premium'] * self.sl_multiplier:.2f}")
            print(f"   TP: ${put_position['premium'] * self.tp_multiplier:.2f}")
        
        print("\n✓ Straddle entered successfully!")
        return True
    
    def exit_straddle(self):
        """Exit all positions"""
        print("\n" + "="*60)
        print(f"🏁 EXITING STRADDLE - {datetime.now(self.timezone).strftime('%Y-%m-%d %I:%M:%S %p')}")
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
        print("🤖 STRADDLE BOT STARTED")
        print("="*60)
        print(f"Waiting for entry time: {self.entry_time.strftime('%I:%M %p')} IST")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                now = datetime.now(self.timezone)
                current_time_str = now.strftime('%I:%M:%S %p')
                
                # Check if it's entry time and no active positions
                if self.is_entry_time() and not self.has_active_positions():
                    self.enter_straddle()
                
                # Monitor active positions
                if self.has_active_positions():
                    # Check SL/TP for call
                    if self.active_positions['call']:
                        self.check_sl_tp('call')
                    
                    # Check SL/TP for put
                    if self.active_positions['put']:
                        self.check_sl_tp('put')
                    
                    # Check exit time
                    if self.is_exit_time():
                        self.exit_straddle()
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
                self.exit_straddle()

if __name__ == "__main__":
    bot = StraddleBot()
    bot.run()
