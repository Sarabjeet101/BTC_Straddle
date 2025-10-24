"""
Backtest Straddle Strategy for BTCUSD Options
Tests strategy from January 1, 2025 to current date
"""
import ccxt
from config import Config
from datetime import datetime, timedelta, time as dt_time
import pytz
import time as time_module

class StraddleBacktest:
    """Backtest the straddle strategy"""
    
    def __init__(self, start_date, end_date):
        """Initialize backtest"""
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
        
        # Backtest period
        self.start_date = start_date
        self.end_date = end_date
        
        # Results tracking
        self.trades = []
        self.daily_pnl = []
        
    def get_historical_ohlcv(self, symbol, timeframe='1h', since=None, limit=1000):
        """Fetch historical OHLCV data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            return ohlcv
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return None
    
    def get_btc_price_at_time(self, target_datetime):
        """Get BTC price at specific time using historical data"""
        try:
            # Convert to timestamp
            timestamp = int(target_datetime.timestamp() * 1000)
            
            # Fetch OHLCV around that time
            ohlcv = self.exchange.fetch_ohlcv('BTC/USD:USD', '1m', timestamp - 60000, 5)
            
            if ohlcv and len(ohlcv) > 0:
                # Return close price of the candle
                return ohlcv[-1][4]  # Close price
            
            return None
        except Exception as e:
            print(f"Error getting BTC price: {e}")
            return None
    
    def find_options_for_date(self, date_obj):
        """Find available options for a specific date"""
        # Format: YYMMDD
        date_str = date_obj.strftime('%y%m%d')
        
        options = []
        for symbol, market in self.markets.items():
            if 'BTC/USD:USD' in symbol and date_str in symbol:
                if '-C' in symbol or '-P' in symbol:
                    options.append({
                        'symbol': symbol,
                        'strike': self.extract_strike(symbol),
                        'type': 'call' if '-C' in symbol else 'put',
                        'expiry': date_str
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
    
    def find_otm_options(self, btc_price, expiry_date):
        """Find OTM options for given price and expiry"""
        options = self.find_options_for_date(expiry_date)
        
        if not options:
            return None, None
        
        calls = [opt for opt in options if opt['type'] == 'call' and opt['strike']]
        puts = [opt for opt in options if opt['type'] == 'put' and opt['strike']]
        
        calls.sort(key=lambda x: x['strike'])
        puts.sort(key=lambda x: x['strike'])
        
        # Find ATM strike (closest to current price)
        all_strikes = sorted(set([opt['strike'] for opt in options if opt['strike']]))
        atm_strike = min(all_strikes, key=lambda x: abs(x - btc_price))
        
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
        
        return otm_call, otm_put
    
    def get_option_price_at_time(self, symbol, target_datetime):
        """Get option price at specific time"""
        try:
            timestamp = int(target_datetime.timestamp() * 1000)
            
            # Try to fetch ticker or OHLCV
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', timestamp - 60000, 5)
            
            if ohlcv and len(ohlcv) > 0:
                return ohlcv[-1][4]  # Close price
            
            # If no historical data, try current ticker (for recent dates)
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
            
        except Exception as e:
            # print(f"Could not get price for {symbol}: {e}")
            return None
    
    def simulate_trade(self, trade_date):
        """Simulate a single day's trade"""
        print(f"\n{'='*60}")
        print(f"Backtesting: {trade_date.strftime('%Y-%m-%d (%A)')}")
        print(f"{'='*60}")
        
        # Entry time
        entry_datetime = self.timezone.localize(
            datetime.combine(trade_date, self.entry_time)
        )
        
        # Exit time
        exit_datetime = self.timezone.localize(
            datetime.combine(trade_date, self.exit_time)
        )
        
        # Get BTC price at entry
        print(f"\n⏰ Entry Time: {entry_datetime.strftime('%I:%M %p')}")
        btc_price = self.get_btc_price_at_time(entry_datetime)
        
        if not btc_price:
            print("❌ Could not get BTC price - skipping this day")
            return None
        
        print(f"💰 BTC Price: ${btc_price:,.2f}")
        
        # Find OTM options
        call_opt, put_opt = self.find_otm_options(btc_price, trade_date)
        
        if not call_opt or not put_opt:
            print("❌ No suitable options found - skipping this day")
            return None
        
        print(f"\n📊 Selected Options:")
        print(f"   Call: {call_opt['symbol']} (Strike: ${call_opt['strike']:,.0f})")
        print(f"   Put: {put_opt['symbol']} (Strike: ${put_opt['strike']:,.0f})")
        
        # Get entry premiums
        call_premium_entry = self.get_option_price_at_time(call_opt['symbol'], entry_datetime)
        put_premium_entry = self.get_option_price_at_time(put_opt['symbol'], entry_datetime)
        
        if not call_premium_entry or not put_premium_entry:
            print("❌ Could not get entry premiums - skipping this day")
            return None
        
        print(f"\n💵 Entry Premiums:")
        print(f"   Call: ${call_premium_entry:.2f} per lot × {self.lot_size} lots = ${call_premium_entry * self.lot_size:.2f}")
        print(f"   Put: ${put_premium_entry:.2f} per lot × {self.lot_size} lots = ${put_premium_entry * self.lot_size:.2f}")
        print(f"   Total Premium Collected: ${(call_premium_entry + put_premium_entry) * self.lot_size:.2f}")
        
        # Calculate SL/TP levels
        call_sl = call_premium_entry * self.sl_multiplier
        call_tp = call_premium_entry * self.tp_multiplier
        put_sl = put_premium_entry * self.sl_multiplier
        put_tp = put_premium_entry * self.tp_multiplier
        
        print(f"\n🎯 Stop Loss / Take Profit:")
        print(f"   Call SL: ${call_sl:.2f} | TP: ${call_tp:.2f}")
        print(f"   Put SL: ${put_sl:.2f} | TP: ${put_tp:.2f}")
        
        # Simulate monitoring (check every 5 minutes)
        current_time = entry_datetime
        call_exit_price = None
        put_exit_price = None
        call_exit_time = None
        put_exit_time = None
        call_exit_reason = "Time Exit"
        put_exit_reason = "Time Exit"
        
        print(f"\n⏳ Monitoring positions...")
        
        while current_time < exit_datetime:
            current_time += timedelta(minutes=5)
            
            # Check call option
            if call_exit_price is None:
                call_price = self.get_option_price_at_time(call_opt['symbol'], current_time)
                if call_price:
                    if call_price >= call_sl:
                        call_exit_price = call_price
                        call_exit_time = current_time
                        call_exit_reason = "Stop Loss"
                        print(f"   🛑 Call SL hit at {current_time.strftime('%I:%M %p')}: ${call_price:.2f}")
                    elif call_price <= call_tp:
                        call_exit_price = call_price
                        call_exit_time = current_time
                        call_exit_reason = "Take Profit"
                        print(f"   🎯 Call TP hit at {current_time.strftime('%I:%M %p')}: ${call_price:.2f}")
            
            # Check put option
            if put_exit_price is None:
                put_price = self.get_option_price_at_time(put_opt['symbol'], current_time)
                if put_price:
                    if put_price >= put_sl:
                        put_exit_price = put_price
                        put_exit_time = current_time
                        put_exit_reason = "Stop Loss"
                        print(f"   🛑 Put SL hit at {current_time.strftime('%I:%M %p')}: ${put_price:.2f}")
                    elif put_price <= put_tp:
                        put_exit_price = put_price
                        put_exit_time = current_time
                        put_exit_reason = "Take Profit"
                        print(f"   🎯 Put TP hit at {current_time.strftime('%I:%M %p')}: ${put_price:.2f}")
            
            # If both exited, break
            if call_exit_price and put_exit_price:
                break
            
            # Rate limiting
            time_module.sleep(0.1)
        
        # Get exit prices for positions still open
        if call_exit_price is None:
            call_exit_price = self.get_option_price_at_time(call_opt['symbol'], exit_datetime)
            call_exit_time = exit_datetime
            if call_exit_price:
                print(f"   ⏰ Call closed at exit time: ${call_exit_price:.2f}")
        
        if put_exit_price is None:
            put_exit_price = self.get_option_price_at_time(put_opt['symbol'], exit_datetime)
            put_exit_time = exit_datetime
            if put_exit_price:
                print(f"   ⏰ Put closed at exit time: ${put_exit_price:.2f}")
        
        # Calculate P&L
        if call_exit_price and put_exit_price:
            call_pnl = (call_premium_entry - call_exit_price) * self.lot_size
            put_pnl = (put_premium_entry - put_exit_price) * self.lot_size
            total_pnl = call_pnl + put_pnl
            
            print(f"\n📊 Results:")
            print(f"   Call P&L: ${call_pnl:+.2f} ({call_exit_reason})")
            print(f"   Put P&L: ${put_pnl:+.2f} ({put_exit_reason})")
            print(f"   Total P&L: ${total_pnl:+.2f}")
            
            if total_pnl > 0:
                print(f"   ✅ PROFIT")
            else:
                print(f"   ❌ LOSS")
            
            # Record trade
            trade_result = {
                'date': trade_date,
                'btc_price': btc_price,
                'call_symbol': call_opt['symbol'],
                'call_strike': call_opt['strike'],
                'call_entry': call_premium_entry,
                'call_exit': call_exit_price,
                'call_exit_reason': call_exit_reason,
                'call_pnl': call_pnl,
                'put_symbol': put_opt['symbol'],
                'put_strike': put_opt['strike'],
                'put_entry': put_premium_entry,
                'put_exit': put_exit_price,
                'put_exit_reason': put_exit_reason,
                'put_pnl': put_pnl,
                'total_pnl': total_pnl
            }
            
            return trade_result
        
        return None
    
    def run_backtest(self):
        """Run backtest for the entire period"""
        print("\n" + "="*60)
        print("STRADDLE STRATEGY BACKTEST")
        print("="*60)
        print(f"Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        print(f"Strategy: Sell 1-strike OTM Straddle")
        print(f"Lot Size: {self.lot_size} lots per leg")
        print(f"Entry: {self.entry_time.strftime('%I:%M %p')} IST")
        print(f"Exit: {self.exit_time.strftime('%I:%M %p')} IST")
        print(f"SL: {self.sl_multiplier*100}% | TP: 92% decay (to {self.tp_multiplier*100}%)")
        
        # Iterate through each trading day
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Skip weekends (optional, depending on crypto trading hours)
            # if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
            
            result = self.simulate_trade(current_date)
            if result:
                self.trades.append(result)
                self.daily_pnl.append(result['total_pnl'])
            
            current_date += timedelta(days=1)
            
            # Rate limiting
            time_module.sleep(0.5)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print backtest summary"""
        print("\n\n" + "="*60)
        print("BACKTEST SUMMARY")
        print("="*60)
        
        if not self.trades:
            print("No trades executed during this period")
            return
        
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['total_pnl'] > 0])
        losing_trades = len([t for t in self.trades if t['total_pnl'] < 0])
        
        total_pnl = sum(self.daily_pnl)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        max_profit = max(self.daily_pnl) if self.daily_pnl else 0
        max_loss = min(self.daily_pnl) if self.daily_pnl else 0
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        print(f"\n📊 Performance Metrics:")
        print(f"   Total Trades: {total_trades}")
        print(f"   Winning Trades: {winning_trades}")
        print(f"   Losing Trades: {losing_trades}")
        print(f"   Win Rate: {win_rate:.2f}%")
        print(f"\n💰 P&L Summary:")
        print(f"   Total P&L: ${total_pnl:+.2f}")
        print(f"   Average P&L per Trade: ${avg_pnl:+.2f}")
        print(f"   Best Trade: ${max_profit:+.2f}")
        print(f"   Worst Trade: ${max_loss:+.2f}")
        
        # Exit reasons
        call_sl_count = len([t for t in self.trades if t['call_exit_reason'] == 'Stop Loss'])
        call_tp_count = len([t for t in self.trades if t['call_exit_reason'] == 'Take Profit'])
        put_sl_count = len([t for t in self.trades if t['put_exit_reason'] == 'Stop Loss'])
        put_tp_count = len([t for t in self.trades if t['put_exit_reason'] == 'Take Profit'])
        
        print(f"\n🎯 Exit Breakdown:")
        print(f"   Call Options:")
        print(f"      Stop Loss: {call_sl_count}")
        print(f"      Take Profit: {call_tp_count}")
        print(f"      Time Exit: {total_trades - call_sl_count - call_tp_count}")
        print(f"   Put Options:")
        print(f"      Stop Loss: {put_sl_count}")
        print(f"      Take Profit: {put_tp_count}")
        print(f"      Time Exit: {total_trades - put_sl_count - put_tp_count}")
        
        # Print individual trades
        print(f"\n📝 Trade Details:")
        print(f"{'Date':<12} {'BTC Price':<12} {'Call P&L':<12} {'Put P&L':<12} {'Total P&L':<12} {'Result':<8}")
        print("-" * 80)
        
        for trade in self.trades:
            result = "WIN" if trade['total_pnl'] > 0 else "LOSS"
            print(f"{trade['date'].strftime('%Y-%m-%d'):<12} "
                  f"${trade['btc_price']:>9,.0f}  "
                  f"${trade['call_pnl']:>9.2f}  "
                  f"${trade['put_pnl']:>9.2f}  "
                  f"${trade['total_pnl']:>9.2f}  "
                  f"{result:<8}")
        
        print("="*60)

if __name__ == "__main__":
    # Set backtest period
    start_date = datetime(2025, 1, 1)
    end_date = datetime.now()
    
    print("⚠️  NOTE: This backtest requires historical data from Delta Exchange.")
    print("If historical data is not available for all dates, some days will be skipped.\n")
    
    response = input("Start backtest? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        backtest = StraddleBacktest(start_date, end_date)
        backtest.run_backtest()
    else:
        print("Backtest cancelled")
