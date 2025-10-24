"""
Forward Testing Mode - Paper Trading
Runs the bot in real-time but WITHOUT placing actual orders
Shows you exactly what the bot would do with live market data
"""
import ccxt
from config import Config
from datetime import datetime, time as dt_time
import pytz
import time

class ForwardTest:
    """Forward testing with live data but no real orders"""
    
    def __init__(self):
        """Initialize forward test"""
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
        
        if Config.TESTNET:
            self.exchange.set_sandbox_mode(True)
        
        self.markets = self.exchange.load_markets()
        
        # Strategy parameters
        self.sl_multiplier = 1.5
        self.tp_multiplier = 0.08  # 8% remaining (92% decay)
        self.lot_size = 10
        
        # Times
        self.entry_time = dt_time(16, 0)   # 4:00 PM
        self.exit_time = dt_time(17, 25)   # 5:25 PM
        self.timezone = pytz.timezone('Asia/Kolkata')
        
        # Position tracking
        self.position_entered = False
        self.positions = {
            'call': None,
            'put': None
        }
        self.entry_premiums = {
            'call': 0,
            'put': 0
        }
        
        print("\n" + "="*80)
        print("🧪 FORWARD TESTING MODE - PAPER TRADING")
        print("="*80)
        print("⚠️  NO REAL ORDERS WILL BE PLACED")
        print("This simulates real-time trading with live market data")
        print("="*80)
        print(f"\n📊 Configuration:")
        print(f"   Lot Size: {self.lot_size} lots per leg")
        print(f"   Entry: {self.entry_time.strftime('%I:%M %p')} IST")
        print(f"   Exit: {self.exit_time.strftime('%I:%M %p')} IST")
        print(f"   SL: {self.sl_multiplier*100}% | TP: 92% decay (to {self.tp_multiplier*100}%)")
    
    def get_current_btc_price(self):
        """Get current BTC/USD price"""
        try:
            ticker = self.exchange.fetch_ticker('BTC/USD:USD')
            return ticker['last']
        except Exception as e:
            print(f"Error fetching BTC price: {e}")
            return None
    
    def get_option_symbols(self):
        """Get all BTC option symbols"""
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
        """Extract strike from symbol"""
        try:
            parts = symbol.split('-')
            if len(parts) >= 3:
                return float(parts[-2])
            return None
        except:
            return None
    
    def extract_expiry(self, symbol):
        """Extract expiry from symbol"""
        try:
            parts = symbol.split('-')
            if len(parts) >= 2:
                return parts[1]
            return None
        except:
            return None
    
    def find_otm_strikes(self, current_price):
        """Find 1 strike OTM from ATM"""
        options = self.get_option_symbols()
        
        if not options:
            return None, None
        
        # Get nearest expiry
        expiries = sorted(set([opt['expiry'] for opt in options if opt['expiry']]))
        if not expiries:
            return None, None
        expiry = expiries[0]
        
        # Filter options
        calls = [opt for opt in options if opt['type'] == 'call' and opt['expiry'] == expiry and opt['strike']]
        puts = [opt for opt in options if opt['type'] == 'put' and opt['expiry'] == expiry and opt['strike']]
        
        calls.sort(key=lambda x: x['strike'])
        puts.sort(key=lambda x: x['strike'])
        
        # Find ATM
        all_strikes = sorted(set([opt['strike'] for opt in options if opt['strike']]))
        atm_strike = min(all_strikes, key=lambda x: abs(x - current_price))
        
        # Find 1 OTM from ATM
        otm_call = None
        for call in calls:
            if call['strike'] > atm_strike:
                otm_call = call
                break
        
        otm_put = None
        for put in reversed(puts):
            if put['strike'] < atm_strike:
                otm_put = put
                break
        
        return otm_call, otm_put, atm_strike
    
    def get_option_price(self, symbol):
        """Get current option premium"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            return None
    
    def enter_positions(self):
        """Simulate entering positions"""
        print("\n" + "="*80)
        print(f"🚀 ENTERING POSITIONS - {datetime.now(self.timezone).strftime('%Y-%m-%d %I:%M:%S %p')}")
        print("="*80)
        
        # Get BTC price
        btc_price = self.get_current_btc_price()
        if not btc_price:
            print("❌ Failed to get BTC price")
            return False
        
        print(f"\n💰 Current BTC Price: ${btc_price:,.2f}")
        
        # Find strikes
        result = self.find_otm_strikes(btc_price)
        if not result or len(result) != 3:
            print("❌ Failed to find suitable options")
            return False
        
        call_opt, put_opt, atm_strike = result
        
        if not call_opt or not put_opt:
            print("❌ Failed to find OTM options")
            return False
        
        print(f"\n🎯 Strike Selection:")
        print(f"   ATM Strike: ${atm_strike:,.0f}")
        print(f"   Call Strike (1 OTM): ${call_opt['strike']:,.0f}")
        print(f"   Put Strike (1 OTM): ${put_opt['strike']:,.0f}")
        
        # Get premiums
        call_premium = self.get_option_price(call_opt['symbol'])
        put_premium = self.get_option_price(put_opt['symbol'])
        
        if not call_premium or not put_premium:
            print("❌ Failed to get premiums")
            return False
        
        # Calculate totals
        call_total = call_premium * self.lot_size
        put_total = put_premium * self.lot_size
        total_premium = call_total + put_total
        
        print(f"\n💵 Entry Premiums:")
        print(f"   Call: ${call_premium:.2f} × {self.lot_size} lots = ${call_total:,.2f}")
        print(f"   Put: ${put_premium:.2f} × {self.lot_size} lots = ${put_total:,.2f}")
        print(f"   Total Premium Collected: ${total_premium:,.2f}")
        
        # Calculate SL/TP
        call_sl = call_premium * self.sl_multiplier
        call_tp = call_premium * self.tp_multiplier
        put_sl = put_premium * self.sl_multiplier
        put_tp = put_premium * self.tp_multiplier
        
        print(f"\n🎯 Stop Loss / Take Profit Levels:")
        print(f"   Call SL: ${call_sl:.2f} ({call_sl * self.lot_size:,.2f} total) | TP: ${call_tp:.2f} ({call_tp * self.lot_size:,.2f} total)")
        print(f"   Put SL: ${put_sl:.2f} ({put_sl * self.lot_size:,.2f} total) | TP: ${put_tp:.2f} ({put_tp * self.lot_size:,.2f} total)")
        
        # Store positions
        self.positions['call'] = {
            'symbol': call_opt['symbol'],
            'strike': call_opt['strike'],
            'entry_premium': call_premium,
            'sl': call_sl,
            'tp': call_tp,
            'quantity': self.lot_size,
            'entry_time': datetime.now(self.timezone)
        }
        
        self.positions['put'] = {
            'symbol': put_opt['symbol'],
            'strike': put_opt['strike'],
            'entry_premium': put_premium,
            'sl': put_sl,
            'tp': put_tp,
            'quantity': self.lot_size,
            'entry_time': datetime.now(self.timezone)
        }
        
        self.entry_premiums['call'] = call_premium
        self.entry_premiums['put'] = put_premium
        self.position_entered = True
        
        print("\n✅ Positions entered (SIMULATED)")
        print("="*80)
        
        return True
    
    def monitor_positions(self):
        """Monitor positions for SL/TP"""
        now = datetime.now(self.timezone)
        
        # Get current prices
        call_pos = self.positions['call']
        put_pos = self.positions['put']
        
        if not call_pos and not put_pos:
            return
        
        call_current = None
        put_current = None
        
        if call_pos:
            call_current = self.get_option_price(call_pos['symbol'])
        
        if put_pos:
            put_current = self.get_option_price(put_pos['symbol'])
        
        # Print status
        print(f"\n[{now.strftime('%I:%M:%S %p')}] Monitoring Positions...")
        
        if call_pos and call_current:
            call_pnl = (call_pos['entry_premium'] - call_current) * self.lot_size
            print(f"   Call: ${call_current:.2f} (Entry: ${call_pos['entry_premium']:.2f}) | P&L: ${call_pnl:+.2f} | SL: ${call_pos['sl']:.2f} | TP: ${call_pos['tp']:.2f}")
            
            # Check SL/TP
            if call_current >= call_pos['sl']:
                print(f"   🛑 CALL STOP LOSS HIT! Closing at ${call_current:.2f}")
                print(f"      Loss: ${call_pnl:+.2f}")
                self.positions['call'] = None
            elif call_current <= call_pos['tp']:
                print(f"   🎯 CALL TAKE PROFIT HIT! Closing at ${call_current:.2f}")
                print(f"      Profit: ${call_pnl:+.2f}")
                self.positions['call'] = None
        
        if put_pos and put_current:
            put_pnl = (put_pos['entry_premium'] - put_current) * self.lot_size
            print(f"   Put: ${put_current:.2f} (Entry: ${put_pos['entry_premium']:.2f}) | P&L: ${put_pnl:+.2f} | SL: ${put_pos['sl']:.2f} | TP: ${put_pos['tp']:.2f}")
            
            # Check SL/TP
            if put_current >= put_pos['sl']:
                print(f"   🛑 PUT STOP LOSS HIT! Closing at ${put_current:.2f}")
                print(f"      Loss: ${put_pnl:+.2f}")
                self.positions['put'] = None
            elif put_current <= put_pos['tp']:
                print(f"   🎯 PUT TAKE PROFIT HIT! Closing at ${put_current:.2f}")
                print(f"      Profit: ${put_pnl:+.2f}")
                self.positions['put'] = None
    
    def exit_positions(self):
        """Exit all positions"""
        print("\n" + "="*80)
        print(f"🏁 EXITING ALL POSITIONS - {datetime.now(self.timezone).strftime('%Y-%m-%d %I:%M:%S %p')}")
        print("="*80)
        
        total_pnl = 0
        
        # Exit call
        if self.positions['call']:
            call_pos = self.positions['call']
            call_current = self.get_option_price(call_pos['symbol'])
            
            if call_current:
                call_pnl = (call_pos['entry_premium'] - call_current) * self.lot_size
                total_pnl += call_pnl
                
                print(f"\n📈 Call Option:")
                print(f"   Symbol: {call_pos['symbol']}")
                print(f"   Entry: ${call_pos['entry_premium']:.2f} | Exit: ${call_current:.2f}")
                print(f"   P&L: ${call_pnl:+.2f}")
                
                self.positions['call'] = None
        
        # Exit put
        if self.positions['put']:
            put_pos = self.positions['put']
            put_current = self.get_option_price(put_pos['symbol'])
            
            if put_current:
                put_pnl = (put_pos['entry_premium'] - put_current) * self.lot_size
                total_pnl += put_pnl
                
                print(f"\n📈 Put Option:")
                print(f"   Symbol: {put_pos['symbol']}")
                print(f"   Entry: ${put_pos['entry_premium']:.2f} | Exit: ${put_current:.2f}")
                print(f"   P&L: ${put_pnl:+.2f}")
                
                self.positions['put'] = None
        
        print(f"\n{'='*80}")
        print(f"💰 TOTAL P&L: ${total_pnl:+.2f}")
        
        if total_pnl > 0:
            print(f"✅ PROFITABLE TRADE!")
        else:
            print(f"❌ LOSING TRADE")
        
        print(f"{'='*80}\n")
        
        self.position_entered = False
    
    def is_entry_time(self):
        """Check if it's entry time"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        
        entry_min = dt_time(self.entry_time.hour, self.entry_time.minute, 0)
        entry_max = dt_time(self.entry_time.hour, self.entry_time.minute, 59)
        
        return entry_min <= current_time <= entry_max
    
    def is_exit_time(self):
        """Check if it's exit time"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        
        return current_time >= self.exit_time
    
    def run(self):
        """Run forward test"""
        print(f"\n⏰ Current Time: {datetime.now(self.timezone).strftime('%I:%M:%S %p')}")
        print(f"⏰ Waiting for entry time: {self.entry_time.strftime('%I:%M %p')} IST")
        print(f"⏰ Exit time: {self.exit_time.strftime('%I:%M %p')} IST")
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                now = datetime.now(self.timezone)
                
                # Check entry time
                if self.is_entry_time() and not self.position_entered:
                    self.enter_positions()
                
                # Monitor positions
                if self.position_entered:
                    self.monitor_positions()
                    
                    # Check exit time
                    if self.is_exit_time():
                        self.exit_positions()
                        print("\n✅ Forward test completed for today")
                        print("Stopping...")
                        break
                else:
                    # Print waiting message
                    if now.second % 30 == 0:
                        print(f"[{now.strftime('%I:%M:%S %p')}] Waiting for entry time...")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Forward test stopped by user")
            
            if self.position_entered:
                print("Exiting open positions...")
                self.exit_positions()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("⚠️  FORWARD TESTING - PAPER TRADING MODE")
    print("="*80)
    print("\nThis will run the bot in REAL-TIME with LIVE market data")
    print("but will NOT place any actual orders.")
    print("\nYou will see:")
    print("  • When positions would be entered (4:00 PM)")
    print("  • Real-time premium updates")
    print("  • SL/TP triggers")
    print("  • Final P&L at exit (5:25 PM)")
    print("\nThis helps you understand how the bot works before going live.")
    print("="*80)
    
    response = input("\nStart forward test? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        tester = ForwardTest()
        tester.run()
    else:
        print("Forward test cancelled")
